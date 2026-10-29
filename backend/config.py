# backend/config.py
# Modul Konfigurasi Terpisah untuk Database SQLAlchemy & Microsoft Entra ID SSO
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "jiravue-enterprise-secret-key")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///jiravue.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # SQLite tidak mendukung pool_size/max_overflow (pool-nya SingletonThreadPool),
    # opsi itu hanya berlaku untuk server DB (Postgres/MySQL).
    if SQLALCHEMY_DATABASE_URI.startswith("sqlite"):
        SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}
    else:
        SQLALCHEMY_ENGINE_OPTIONS = {
            "pool_pre_ping": True,
            "pool_recycle": 300,
            "pool_size": 10,
            "max_overflow": 20,
        }

    # Microsoft Entra ID OAuth2 / OIDC Settings
    AZURE_TENANT_ID = os.getenv("AZURE_TENANT_ID", "72f988bf-86f1-41af-91ab-2d7cd011db47")
    AZURE_CLIENT_ID = os.getenv("AZURE_CLIENT_ID", "a8f412c0-3b91-4e7a-9c1d-55f802e19a11")
    JWKS_URI = f"https://login.microsoftonline.com/{AZURE_TENANT_ID}/discovery/v2.0/keys"
    ISSUER = f"https://login.microsoftonline.com/{AZURE_TENANT_ID}/v2.0"

    # ---- OAuth 2.0 multi-provider (Google & GitHub) ----
    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
    GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
    GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID", "")
    GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET", "")
    FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")
    BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:5000")
    GOOGLE_AUTH_BASE = os.getenv("GOOGLE_AUTH_BASE", "https://accounts.google.com/o/oauth2/v2/auth")
    GOOGLE_TOKEN_URL = os.getenv("GOOGLE_TOKEN_URL", "https://oauth2.googleapis.com/token")
    GOOGLE_USERINFO_URL = os.getenv("GOOGLE_USERINFO_URL", "https://openidconnect.googleapis.com/v1/userinfo")
    GITHUB_AUTH_BASE = os.getenv("GITHUB_AUTH_BASE", "https://github.com/login/oauth/authorize")
    GITHUB_TOKEN_URL = os.getenv("GITHUB_TOKEN_URL", "https://github.com/login/oauth/access_token")
    GITHUB_API_BASE = os.getenv("GITHUB_API_BASE", "https://api.github.com")

    # JWT sesi internal (HS256, diterbitkan backend setelah OAuth callback sukses).
    APP_JWT_ISSUER = "jiravue"
    APP_JWT_AUDIENCE = "jiravue-api"
    APP_JWT_TTL_HOURS = 12

    # ---- SMTP Email Notification Settings (@mention in comments) ----
    SMTP_HOST = os.getenv("SMTP_HOST", "")
    SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
    SMTP_USER = os.getenv("SMTP_USER", "")
    SMTP_PASS = os.getenv("SMTP_PASS", "")
    SMTP_FROM = os.getenv("SMTP_FROM", os.getenv("SMTP_USER", "noreply@jiravue.local"))
    SMTP_USE_TLS = os.getenv("SMTP_USE_TLS", "true").lower() in ("true", "1", "yes")
