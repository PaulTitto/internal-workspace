# backend/routes/otp_bp.py
# Blueprint untuk autentikasi tanpa password via Kode OTP Email
import random
import re
import uuid
from datetime import timedelta
from flask import Blueprint, jsonify, request
from models import db, EmailOtp, UserEntraID, utcnow
from mailer import send_otp_email_async
from auth_oauth import _issue_session_token

otp_bp = Blueprint("otp_bp", __name__, url_prefix="/api/v1/auth/otp")

EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


@otp_bp.route("/send", methods=["POST"])
def send_otp():
    """Mengirimkan kode 6-digit OTP ke email user."""
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()

    if not email or not EMAIL_REGEX.match(email):
        return jsonify({"error": "Format alamat email tidak valid"}), 400

    # Rate limiting: cegah spam jika OTP terakhir baru saja dikirim (< 30 detik yang lalu)
    recent_otp = (
        EmailOtp.query.filter_by(email=email, is_used=False)
        .order_by(EmailOtp.id.desc())
        .first()
    )
    if recent_otp:
        time_since_creation = (utcnow() - recent_otp.created_at).total_seconds()
        if time_since_creation < 30:
            remaining = int(30 - time_since_creation)
            return (
                jsonify(
                    {
                        "error": f"Harap tunggu {remaining} detik sebelum meminta kode baru."
                    }
                ),
                429,
            )

    # Invalidate OTP lama yang belum terpakai untuk email ini
    EmailOtp.query.filter_by(email=email, is_used=False).update({"is_used": True})

    # Buat 6-digit kode OTP baru
    otp_code = f"{random.randint(100000, 999999)}"
    expires_at = utcnow() + timedelta(minutes=5)

    otp_record = EmailOtp(
        email=email,
        otp_code=otp_code,
        expires_at=expires_at,
        is_used=False,
    )
    db.session.add(otp_record)
    db.session.commit()

    # Kirim email asinkron di thread terpisah
    send_otp_email_async(email, otp_code)

    return (
        jsonify(
            {
                "success": True,
                "message": "Kode verifikasi telah dikirim ke email Anda.",
                "email": email,
            }
        ),
        200,
    )


@otp_bp.route("/verify", methods=["POST"])
def verify_otp():
    """Verifikasi kode OTP 6-digit dan kembalikan token sesi login."""
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    otp_code = (data.get("otp") or "").strip()

    if not email or not EMAIL_REGEX.match(email):
        return jsonify({"error": "Format alamat email tidak valid"}), 400

    if not otp_code or len(otp_code) != 6 or not otp_code.isdigit():
        return jsonify({"error": "Kode OTP harus berupa 6 digit angka"}), 400

    # Cari rekaman OTP yang cocok dan belum digunakan
    record = (
        EmailOtp.query.filter_by(email=email, otp_code=otp_code, is_used=False)
        .order_by(EmailOtp.id.desc())
        .first()
    )

    if not record or record.is_expired:
        return (
            jsonify({"error": "Kode verifikasi tidak valid atau telah kedaluwarsa."}),
            400,
        )

    # Tandai OTP telah digunakan
    record.is_used = True

    # Upsert user di tabel users_entra_id
    user = UserEntraID.query.filter_by(upn_email=email).first()
    if not user:
        raw_name = email.split("@")[0].replace(".", " ").replace("_", " ").title()
        user = UserEntraID(
            entra_oid=f"email_{uuid.uuid4().hex[:16]}",
            upn_email=email,
            display_name=raw_name or "Pengguna",
            job_title="Software Engineer",
            entra_role="Jira.Developer",
            tenant_id="email_otp",
            auth_provider="email_otp",
            last_sso_login=utcnow(),
        )
        db.session.add(user)
    else:
        user.last_sso_login = utcnow()

    db.session.commit()

    # Terbitkan token JWT sesi internal
    token = _issue_session_token(user, "email_otp")

    return (
        jsonify(
            {
                "success": True,
                "message": "Login berhasil",
                "token": token,
                "user": user.to_dict(),
            }
        ),
        200,
    )
