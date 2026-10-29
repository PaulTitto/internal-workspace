# backend/auth_oauth.py
# OAuth 2.0 Authorization Code Flow multi-provider (Google & GitHub).
# Alur: frontend -> /auth/<provider>/login (redirect ke IdP) -> IdP callback ke
# /auth/<provider>/callback -> token ditukar -> user di-upsert -> backend
# menerbitkan JWT sesi internal (HS256) -> redirect ke frontend (#fragment).
import secrets
from datetime import datetime, timedelta
from urllib.parse import urlencode

import jwt
import requests
from flask import Blueprint, current_app, jsonify, redirect, request

from models import db, UserEntraID

auth_bp = Blueprint("auth_bp", __name__, url_prefix="/api/v1/auth")

PROVIDERS = ("google", "github")


def _provider_config(provider):
    """Kembalikan (client_id, client_secret) atau None jika provider belum dikonfigurasi."""
    cfg = current_app.config
    if provider == "google":
        cid, csec = cfg.get("GOOGLE_CLIENT_ID"), cfg.get("GOOGLE_CLIENT_SECRET")
    elif provider == "github":
        cid, csec = cfg.get("GITHUB_CLIENT_ID"), cfg.get("GITHUB_CLIENT_SECRET")
    else:
        return None
    if not cid or not csec:
        return None
    return cid, csec


def _issue_session_token(user, provider):
    """JWT sesi internal aplikasi — digunakan oleh decorator require_auth."""
    cfg = current_app.config
    now = datetime.utcnow()
    payload = {
        "iss": cfg["APP_JWT_ISSUER"],
        "aud": cfg["APP_JWT_AUDIENCE"],
        "sub": user.entra_oid,
        "provider": provider,
        "name": user.display_name,
        "email": user.upn_email,
        "iat": now,
        "exp": now + timedelta(hours=cfg["APP_JWT_TTL_HOURS"]),
    }
    return jwt.encode(payload, cfg["SECRET_KEY"], algorithm="HS256")


@auth_bp.get("/<provider>/login")
def oauth_login(provider):
    if provider not in PROVIDERS:
        return jsonify({"error": f"Provider tidak dikenal: {provider}"}), 404
    pc = _provider_config(provider)
    if not pc:
        return jsonify({
            "error": f"OAuth {provider} belum dikonfigurasi",
            "hint": f"Set {'GOOGLE' if provider == 'google' else 'GITHUB'}_CLIENT_ID "
                    f"dan {'GOOGLE' if provider == 'google' else 'GITHUB'}_CLIENT_SECRET di backend/.env",
        }), 503
    client_id, _ = pc
    cfg = current_app.config
    redirect_uri = f"{cfg['BACKEND_URL']}/api/v1/auth/{provider}/callback"
    # state anti-CSRF: JWT pendek-umur berisi nonce, diverifikasi di callback.
    state = jwt.encode(
        {"provider": provider, "nonce": secrets.token_urlsafe(16),
         "exp": datetime.utcnow() + timedelta(minutes=10)},
        cfg["SECRET_KEY"], algorithm="HS256",
    )
    if provider == "google":
        params = {
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": "openid email profile",
            "state": state,
            "access_type": "online",
            "prompt": "select_account",
        }
        return redirect(f"{cfg['GOOGLE_AUTH_BASE']}?{urlencode(params)}")
    # github
    params = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "scope": "read:user user:email",
        "state": state,
    }
    return redirect(f"{cfg['GITHUB_AUTH_BASE']}?{urlencode(params)}")


def _exchange_google(code, pc):
    cfg = current_app.config
    resp = requests.post(cfg["GOOGLE_TOKEN_URL"], data={
        "code": code,
        "client_id": pc[0],
        "client_secret": pc[1],
        "redirect_uri": f"{cfg['BACKEND_URL']}/api/v1/auth/google/callback",
        "grant_type": "authorization_code",
    }, timeout=15)
    resp.raise_for_status()
    access_token = resp.json()["access_token"]
    info = requests.get(cfg["GOOGLE_USERINFO_URL"],
                        headers={"Authorization": f"Bearer {access_token}"}, timeout=15)
    info.raise_for_status()
    p = info.json()
    return {"sub": p["sub"], "email": p.get("email"), "name": p.get("name") or p.get("email")}


def _exchange_github(code, pc):
    cfg = current_app.config
    resp = requests.post(cfg["GITHUB_TOKEN_URL"], data={
        "code": code,
        "client_id": pc[0],
        "client_secret": pc[1],
        "redirect_uri": f"{cfg['BACKEND_URL']}/api/v1/auth/github/callback",
    }, headers={"Accept": "application/json"}, timeout=15)
    resp.raise_for_status()
    access_token = resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {access_token}", "Accept": "application/vnd.github+json"}
    user = requests.get(f"{cfg['GITHUB_API_BASE']}/user", headers=headers, timeout=15)
    user.raise_for_status()
    p = user.json()
    email = p.get("email")
    if not email:  # email primer bisa privat — ambil dari endpoint emails
        emails = requests.get(f"{cfg['GITHUB_API_BASE']}/user/emails", headers=headers, timeout=15)
        if emails.ok:
            primary = next((e for e in emails.json() if e.get("primary")), None)
            email = primary["email"] if primary else None
    return {"sub": str(p["id"]), "email": email, "name": p.get("name") or p.get("login")}


@auth_bp.get("/<provider>/callback")
def oauth_callback(provider):
    if provider not in PROVIDERS:
        return jsonify({"error": f"Provider tidak dikenal: {provider}"}), 404
    pc = _provider_config(provider)
    if not pc:
        return jsonify({"error": f"OAuth {provider} belum dikonfigurasi"}), 503
    if request.args.get("error"):
        return jsonify({"error": "IdP menolak login",
                        "detail": request.args.get("error_description")}), 400
    code, state = request.args.get("code"), request.args.get("state")
    if not code or not state:
        return jsonify({"error": "Parameter code/state hilang"}), 400
    try:
        claims = jwt.decode(state, current_app.config["SECRET_KEY"],
                            algorithms=["HS256"], issuer=None)
    except jwt.PyJWTError as err:
        return jsonify({"error": "State OAuth tidak valid (kemungkinan CSRF/expired)",
                        "detail": str(err)}), 400
    if claims.get("provider") != provider:
        return jsonify({"error": "State provider mismatch"}), 400

    try:
        profile = _exchange_google(code, pc) if provider == "google" else _exchange_github(code, pc)
    except Exception as err:
        return jsonify({"error": f"Gagal menukar kode dengan {provider}", "detail": str(err)}), 502

    email = profile["email"]
    if not email:
        return jsonify({"error": "Provider tidak mengembalikan email — akses email wajib"}), 400

    # Upser user: identitas unik = "<provider>:<sub>" di kolom entra_oid.
    oid = f"{provider}:{profile['sub']}"
    user = UserEntraID.query.filter_by(entra_oid=oid).first()
    if not user:
        user = UserEntraID(
            entra_oid=oid,
            upn_email=email,
            display_name=profile["name"] or email.split("@")[0],
            tenant_id=provider,
            auth_provider=provider,
        )
        db.session.add(user)
    else:
        user.last_sso_login = datetime.utcnow()
        user.display_name = profile["name"] or user.display_name
    db.session.commit()

    token = _issue_session_token(user, provider)
    # Token dikirim via fragment (#) — tidak ikut terkirim ke server / logs.
    return redirect(f"{current_app.config['FRONTEND_URL']}/#token={token}")
