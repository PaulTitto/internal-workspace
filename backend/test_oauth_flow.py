# backend/test_oauth_flow.py
# Uji end-to-end OAuth 2.0 Authorization Code Flow (Google & GitHub) tanpa
# internet: stub IdP lokal menggantikan endpoint authorize/token/userinfo.
# Jalankan: .venv/Scripts/python.exe test_oauth_flow.py
import json
import os
import threading
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.request import Request, urlopen

import jwt

STUB_PORT = 8901
STUB = f"http://127.0.0.1:{STUB_PORT}"
SECRET = "test-secret-key"

# Env HARUS diset sebelum config.py / app di-import.
os.environ.update(
    SECRET_KEY=SECRET,
    GOOGLE_CLIENT_ID="stub-google-client",
    GOOGLE_CLIENT_SECRET="stub-google-secret",
    GOOGLE_AUTH_BASE=f"{STUB}/authorize",
    GOOGLE_TOKEN_URL=f"{STUB}/token",
    GOOGLE_USERINFO_URL=f"{STUB}/userinfo",
    GITHUB_CLIENT_ID="stub-gh-client",
    GITHUB_CLIENT_SECRET="stub-gh-secret",
    GITHUB_AUTH_BASE=f"{STUB}/authorize",
    GITHUB_TOKEN_URL=f"{STUB}/token",
    GITHUB_API_BASE=STUB,
    FRONTEND_URL="http://localhost:5173",
)

from app import create_app
from models import db, UserEntraID

STUB_PORT = 8901
STUB = f"http://127.0.0.1:{STUB_PORT}"
SECRET = "test-secret-key"


class StubIdP(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _send(self, code, body, headers=None):
        payload = body.encode() if isinstance(body, str) else json.dumps(body).encode()
        self.send_response(code)
        for k, v in (headers or {}).items():
            self.send_header(k, v)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def do_GET(self):
        # /authorize: langsung "menyetujui" dan redirect ke callback Flask dgn code+state
        if self.path.startswith("/authorize"):
            q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            cb = q["redirect_uri"][0]
            dest = f"{cb}?code=stub-code-123&state={q['state'][0]}"
            self._send(302, "", {"Location": dest})
        elif self.path.startswith("/userinfo"):                      # Google
            self._send(200, {"sub": "stub-sub-42", "email": "budi@google-stub.local",
                             "name": "Budi Stub"})
        elif self.path.startswith("/user/emails"):                   # GitHub (email privat)
            self._send(200, [{"email": "budi@gh-stub.local", "primary": True}])
        elif self.path.startswith("/user"):                          # GitHub
            self._send(200, {"id": 777, "login": "budigh", "name": None, "email": None})
        else:
            self._send(404, {"error": "not found"})

    def do_POST(self):
        if self.path.startswith("/token"):
            self._send(200, {"access_token": "stub-access-token", "token_type": "Bearer"})
        else:
            self._send(404, {"error": "not found"})


def start_stub():
    srv = HTTPServer(("127.0.0.1", STUB_PORT), StubIdP)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv


def main():
    start_stub()
    app = create_app()
    c = app.test_client()
    passed, failed = [], []

    def check(name, cond, extra=""):
        (passed if cond else failed).append(name)
        print(("PASS" if cond else "FAIL"), "-", name, extra)

    # 1. Provider belum dikonfigurasi -> 503 (tanpa env, config default kosong)
    #    (di sini sudah diset, jadi tes langsung alurnya)

    # 2. /login -> redirect ke IdP dengan state
    r = c.get("/api/v1/auth/google/login")
    loc = r.headers.get("Location", "")
    check("google/login redirect 302 ke IdP", r.status_code == 302 and STUB in loc, loc[:60])
    qs = urllib.parse.parse_qs(urllib.parse.urlparse(loc).query)
    check("redirect membawa client_id, scope openid, dan state",
          qs.get("client_id") == ["stub-google-client"]
          and "openid" in qs.get("scope", [""])[0]
          and bool(qs.get("state")))

    # 3. Callback dgn state palsu -> ditolak 400 (anti-CSRF)
    r = c.get("/api/v1/auth/google/callback?code=x&state=forged")
    check("callback state palsu ditolak 400", r.status_code == 400)

    # 4. Callback lengkap (simulasi IdP approve) -> redirect frontend dgn token
    real_state = qs["state"][0]
    r = c.get(f"/api/v1/auth/google/callback?code=stub-code-123&state={real_state}")
    loc = r.headers.get("Location", "")
    check("callback sukses redirect 302 ke frontend", r.status_code == 302
          and loc.startswith("http://localhost:5173/"),
          f"status={r.status_code} loc={loc[:90]} body={r.get_data(as_text=True)[:120]}")
    token = loc.split("token=")[-1]
    claims = jwt.decode(token, SECRET, algorithms=["HS256"],
                        audience="jiravue-api", issuer="jiravue")
    check("JWT sesi valid: sub=google:stub-sub-42, provider=google",
          claims["sub"] == "google:stub-sub-42" and claims["provider"] == "google",
          str({k: claims[k] for k in ("sub", "provider", "email")}))

    # 5. User ter-upsert ke DB dgn auth_provider='google'
    with app.app_context():
        u = UserEntraID.query.filter_by(entra_oid="google:stub-sub-42").first()
        check("user ter-upsert (auth_provider=google, email benar)",
              u is not None and u.auth_provider == "google"
              and u.upn_email == "budi@google-stub.local")

    # 6. /me dengan JWT sesi -> 200 (jalur decorator baru)
    r = c.get("/api/v1/me", headers={"Authorization": f"Bearer {token}"})
    check("/me menerima JWT sesi internal (200)", r.status_code == 200,
          r.get_data(as_text=True)[:80])

    # 7. Token acak -> 401
    r = c.get("/api/v1/me", headers={"Authorization": "Bearer not-a-jwt"})
    check("/me menolak token acak (401)", r.status_code == 401)

    # 8. GitHub: jalur callback + upsert (email diambil dari /user/emails karena privat)
    r = c.get("/api/v1/auth/github/login")
    loc = r.headers.get("Location", "")
    qs = urllib.parse.parse_qs(urllib.parse.urlparse(loc).query)
    r = c.get(f"/api/v1/auth/github/callback?code=stub-code-123&state={qs['state'][0]}")
    loc = r.headers.get("Location", "")
    gh_token = loc.split("token=")[-1] if "token=" in loc else ""
    gh_ok = r.status_code == 302 and gh_token
    check("github/callback sukses redirect dgn token", gh_ok, loc[:70])
    if gh_ok:
        gclaims = jwt.decode(gh_token, SECRET, algorithms=["HS256"],
                             audience="jiravue-api", issuer="jiravue")
        check("JWT github: sub=github:777, email primer dari /user/emails",
              gclaims["sub"] == "github:777" and gclaims["email"] == "budi@gh-stub.local")
        r = c.get("/api/v1/me", headers={"Authorization": f"Bearer {gh_token}"})
        check("/me menerima sesi github (200)", r.status_code == 200)

    # 9. Provider tak dikenal -> 404
    r = c.get("/api/v1/auth/twitter/login")
    check("provider tidak dikenal -> 404", r.status_code == 404)

    print(f"\n{len(passed)} passed, {len(failed)} failed")
    if failed:
        print("FAILED:", failed)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
