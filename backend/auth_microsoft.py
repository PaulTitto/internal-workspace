# backend/auth_microsoft.py
# Decorator Auth Serbaguna:
#   1. JWT sesi internal (HS256) — diterbitkan backend setelah OAuth 2.0
#      Google/GitHub callback sukses (lihat auth_oauth.py).
#   2. Token asli Microsoft Entra ID (RS256 via JWKS) — kompatibel dengan
#      jalur SSO MSAL frontend yang sudah ada.
# Keduanya meng-upsert user ke tabel users_entra_id dan set g.current_user.
from datetime import datetime
from functools import wraps
import jwt
from jwt import PyJWKClient
from flask import request, jsonify, g, current_app
from models import db, UserEntraID


def _decode_app_session_token(token):
    """Validasi JWT sesi internal; kembalikan claims atau None."""
    cfg = current_app.config
    try:
        return jwt.decode(
            token,
            cfg["SECRET_KEY"],
            algorithms=["HS256"],
            audience=cfg["APP_JWT_AUDIENCE"],
            issuer=cfg["APP_JWT_ISSUER"],
        )
    except jwt.PyJWTError:
        return None


def _decode_entra_token(token):
    """Validasi token Entra ID via JWKS; raise jika tidak valid."""
    jwks_client = PyJWKClient(current_app.config["JWKS_URI"])
    signing_key = jwks_client.get_signing_key_from_jwt(token)
    client_id = current_app.config["AZURE_CLIENT_ID"]
    return jwt.decode(
        token,
        signing_key.key,
        algorithms=["RS256"],
        audience=[client_id, f"api://{client_id}"],
        issuer=current_app.config["ISSUER"],
    )


def require_microsoft_sso(f):
    """Wajib Bearer token: sesi internal (Google/GitHub) ATAU Entra ID (MSAL)."""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "Missing Bearer token"}), 401

        token = auth_header.split(" ")[1]

        # ---- Jalur 1: sesi internal dari OAuth Google/GitHub ----
        claims = _decode_app_session_token(token)
        if claims:
            user = UserEntraID.query.filter_by(entra_oid=claims["sub"]).first()
            if not user:
                db.session.rollback()
                return jsonify({"error": "User sesi tidak ditemukan"}), 401
            user.last_sso_login = datetime.utcnow()
            db.session.commit()
            g.current_user = user
            return f(*args, **kwargs)

        # ---- Jalur 2: token Entra ID asli (SSO MSAL) ----
        try:
            claims = _decode_entra_token(token)

            # Sinkronisasi otomatis user Microsoft Entra ID ke tabel users_entra_id
            oid = claims.get("oid")
            upn = claims.get("preferred_username") or claims.get("upn")
            name = claims.get("name", upn)
            roles = claims.get("roles", ["Jira.Developer"])

            user = UserEntraID.query.filter_by(entra_oid=oid).first()
            if not user:
                user = UserEntraID(
                    entra_oid=oid,
                    upn_email=upn,
                    display_name=name,
                    entra_role=roles[0] if roles else "Jira.Developer",
                    tenant_id=claims.get("tid"),
                    auth_provider="azure",
                )
                db.session.add(user)
            else:
                user.last_sso_login = datetime.utcnow()
            db.session.commit()

            g.current_user = user
        except Exception as err:
            db.session.rollback()
            return jsonify({"error": "Invalid auth token", "detail": str(err)}), 401

        return f(*args, **kwargs)
    return decorated
