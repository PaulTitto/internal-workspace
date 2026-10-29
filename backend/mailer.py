# backend/mailer.py
# Modul pengiriman notifikasi email untuk mention komentar (@mention) ala Jira
import os
import re
import smtplib
import threading
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime

from config import Config

# Regex untuk mendeteksi email setelah tanda @: contoh @techoppa14@gmail.com atau @john.doe@example.com
EMAIL_MENTION_REGEX = re.compile(r'@([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)')


def extract_mentioned_emails(comment_text, team_members=None):
    """
    Ekstrak daftar alamat email yang di-mention di dalam teks komentar.
    1. Mendeteksi mention format @email@domain.com
    2. Mendeteksi mention format @NamaLengkap jika cocok dengan nama member di tim
    """
    if not comment_text:
        return []

    mentioned = set()

    # 1. Regex untuk @user@domain.com
    matches = EMAIL_MENTION_REGEX.findall(comment_text)
    for m in matches:
        mentioned.add(m.strip().lower())

    # 2. Cek apakah ada member tim yang di-mention berdasarkan nama (misal: "@PTD official")
    if team_members:
        lower_text = comment_text.lower()
        for member in team_members:
            user = member.user if hasattr(member, 'user') else None
            if user:
                name = (user.display_name or '').strip().lower()
                email = (user.upn_email or '').strip().lower()
                if name and f"@{name}" in lower_text:
                    if email:
                        mentioned.add(email)

    return list(mentioned)


def send_mention_email_async(
    recipient_email,
    commenter_name,
    commenter_email,
    issue_key,
    issue_summary,
    comment_body,
    team_name="JiraVue Team",
    team_key="FIN",
):
    """Kirim email secara asynchronous via threading agar tidak memblokir response HTTP."""
    thread = threading.Thread(
        target=_send_mention_email_worker,
        args=(
            recipient_email,
            commenter_name,
            commenter_email,
            issue_key,
            issue_summary,
            comment_body,
            team_name,
            team_key,
        ),
        daemon=True,
    )
    thread.start()


def _send_mention_email_worker(
    recipient_email,
    commenter_name,
    commenter_email,
    issue_key,
    issue_summary,
    comment_body,
    team_name,
    team_key,
):
    """Worker fungsi pengiriman email via SMTP."""
    smtp_host = os.getenv("SMTP_HOST", Config.SMTP_HOST if hasattr(Config, "SMTP_HOST") else "")
    smtp_port = int(os.getenv("SMTP_PORT", getattr(Config, "SMTP_PORT", 587)))
    smtp_user = os.getenv("SMTP_USER", getattr(Config, "SMTP_USER", ""))
    smtp_pass = os.getenv("SMTP_PASS", getattr(Config, "SMTP_PASS", ""))
    smtp_from = os.getenv("SMTP_FROM", getattr(Config, "SMTP_FROM", smtp_user or "noreply@jiravue.local"))
    smtp_tls = os.getenv("SMTP_USE_TLS", "true").lower() in ("true", "1", "yes")
    frontend_url = os.getenv("FRONTEND_URL", getattr(Config, "FRONTEND_URL", "http://localhost:5173"))

    subject = f"[{team_key}] {commenter_name} menyebut Anda di issue {issue_key}: {issue_summary}"

    # HTML Email Template bergaya Jira
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8">
      <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; color: #172B4D; background-color: #F4F5F7; margin: 0; padding: 20px; }}
        .card {{ max-width: 600px; margin: 0 auto; background: #ffffff; border-radius: 8px; border: 1px solid #DFE1E6; overflow: hidden; }}
        .header {{ background: #0052CC; padding: 18px 24px; color: #ffffff; }}
        .header h1 {{ margin: 0; font-size: 16px; font-weight: 700; }}
        .content {{ padding: 24px; }}
        .issue-title {{ font-size: 16px; font-weight: 700; color: #172B4D; margin-bottom: 8px; }}
        .badge {{ background: #DEEBFF; color: #0052CC; font-family: monospace; font-size: 12px; font-weight: bold; padding: 2px 6px; rounded: 4px; }}
        .comment-box {{ background: #FAFBFC; border-left: 3px solid #0052CC; border-radius: 4px; padding: 14px 16px; margin: 18px 0; color: #172B4D; font-size: 14px; line-height: 1.5; }}
        .meta {{ font-size: 12px; color: #6B778C; margin-top: 4px; }}
        .btn {{ display: inline-block; background: #0052CC; color: #ffffff !important; text-decoration: none; padding: 10px 18px; border-radius: 4px; font-size: 13px; font-weight: 600; margin-top: 14px; }}
        .footer {{ padding: 16px 24px; background: #FAFBFC; border-top: 1px solid #EBECF0; font-size: 11px; color: #6B778C; text-align: center; }}
      </style>
    </head>
    <body>
      <div class="card">
        <div class="header">
          <h1>JiraVue • Notifikasi Komentar Tim</h1>
        </div>
        <div class="content">
          <div class="issue-title">
            <span class="badge">{issue_key}</span> {issue_summary}
          </div>
          <div class="meta">
            Tim: <strong>{team_name}</strong> • Disebut oleh: <strong>{commenter_name}</strong> ({commenter_email})
          </div>

          <p style="margin-top: 16px; font-size: 13px; color: #42526E;">
            <strong>{commenter_name}</strong> menyebut akun Anda dalam komentar issue berikut:
          </p>

          <div class="comment-box">
            "{comment_body}"
          </div>

          <a href="{frontend_url}" class="btn">Buka Issue di JiraVue →</a>
        </div>
        <div class="footer">
          Email otomatis dari JiraVue. Anda menerima email ini karena akun Anda di-mention dalam diskusi issue.
        </div>
      </div>
    </body>
    </html>
    """

    plain_content = f"""
JiraVue Notification
=========================================
Issue: [{issue_key}] {issue_summary}
Tim: {team_name}
Disebut oleh: {commenter_name} ({commenter_email})

Komentar:
"{comment_body}"

Buka di JiraVue: {frontend_url}
    """

    # Bila SMTP belum dikonfigurasi di .env, kita lakukan simulasi pengiriman dan log ke console server
    if not smtp_host or not smtp_user:
        print("\n" + "=" * 65)
        print("📨 [MAIL SIMULATION - @MENTION EMAIL NOTIFICATION]")
        print(f"To      : {recipient_email}")
        print(f"Subject : {subject}")
        print(f"From    : {commenter_name} <{commenter_email}>")
        print(f"Issue   : {issue_key} ({issue_summary})")
        print(f"Body    :\n{comment_body}")
        print("💡 Catatan: Untuk mengirim email sungguhan, atur SMTP_HOST, SMTP_USER, dan SMTP_PASS di backend/.env")
        print("=" * 65 + "\n")
        return

    # Kirim sungguhan via SMTP
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"JiraVue Notification <{smtp_from}>"
        msg["To"] = recipient_email
        msg.attach(MIMEText(plain_content, "plain", "utf-8"))
        msg.attach(MIMEText(html_content, "html", "utf-8"))

        if smtp_port == 465:
            server = smtplib.SMTP_SSL(smtp_host, smtp_port, timeout=10)
        else:
            server = smtplib.SMTP(smtp_host, smtp_port, timeout=10)
            if smtp_tls:
                server.starttls()

        if smtp_user and smtp_pass:
            server.login(smtp_user, smtp_pass)

        server.sendmail(smtp_from, [recipient_email], msg.as_string())
        server.quit()
        print(f"✅ [MAIL SENT] Berhasil mengirim email notifikasi mention ke {recipient_email}")
    except Exception as err:
        print(f"❌ [MAIL ERROR] Gagal mengirim email ke {recipient_email}: {err}")


def send_otp_email_async(recipient_email, otp_code):
    """Kirim kode OTP login secara asynchronous via background thread."""
    thread = threading.Thread(
        target=_send_otp_email_worker,
        args=(recipient_email, otp_code),
        daemon=True,
    )
    thread.start()


def _send_otp_email_worker(recipient_email, otp_code):
    smtp_host = os.getenv("SMTP_HOST") or getattr(Config, "SMTP_HOST", "")
    smtp_port = int(os.getenv("SMTP_PORT") or getattr(Config, "SMTP_PORT", 587))
    smtp_user = os.getenv("SMTP_USER") or getattr(Config, "SMTP_USER", "")
    smtp_pass = os.getenv("SMTP_PASS") or getattr(Config, "SMTP_PASS", "")
    smtp_from = os.getenv("SMTP_FROM") or getattr(Config, "SMTP_FROM", smtp_user or "noreply@company.com")
    smtp_tls = str(os.getenv("SMTP_USE_TLS") or getattr(Config, "SMTP_USE_TLS", "true")).lower() == "true"

    subject = f"Kode Verifikasi Login Anda: {otp_code}"

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8">
      <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #f4f6f9; margin: 0; padding: 24px; color: #172b4d; }}
        .card {{ max-width: 480px; margin: 0 auto; background: #ffffff; border-radius: 12px; border: 1px solid #dfe1e6; padding: 32px; box-shadow: 0 4px 12px rgba(9,30,66,0.08); text-align: center; }}
        .logo {{ font-size: 16px; font-weight: 800; color: #1226AA; letter-spacing: -0.5px; margin-bottom: 20px; }}
        h2 {{ font-size: 20px; color: #080e2f; margin: 0 0 12px 0; }}
        p {{ font-size: 14px; color: #5e6c84; line-height: 1.6; margin: 0 0 24px 0; }}
        .otp-box {{ display: inline-block; background: #EEF2FF; border: 2px dashed #1226AA; border-radius: 12px; padding: 16px 32px; font-family: 'Courier New', Courier, monospace; font-size: 32px; font-weight: 800; letter-spacing: 8px; color: #1226AA; margin: 12px 0 24px 0; }}
        .expiry {{ font-size: 12px; color: #8993a4; margin-bottom: 24px; }}
        .footer {{ font-size: 11px; color: #97a0af; border-t: 1px solid #ebecf0; pt: 16px; margin-top: 24px; }}
      </style>
    </head>
    <body>
      <div class="card">
        <div class="logo">INTERNAL WORKSPACE</div>
        <h2>Kode Verifikasi Masuk (OTP)</h2>
        <p>Gunakan kode verifikasi satu kali (OTP) di bawah ini untuk masuk ke akun Anda:</p>
        <div class="otp-box">{otp_code}</div>
        <div class="expiry">⏱️ Kode ini hanya berlaku selama <strong>5 menit</strong>. Jangan bagikan kode ini kepada siapa pun.</div>
        <div class="footer">
          Jika Anda tidak merasa meminta kode ini, abaikan email ini dengan aman.
        </div>
      </div>
    </body>
    </html>
    """

    plain_content = f"""
Kode Verifikasi Masuk (OTP)
===========================
Kode OTP Anda: {otp_code}

Kode ini hanya berlaku selama 5 menit.
Jika Anda tidak meminta kode ini, silakan abaikan.
    """

    # Simulasi bila SMTP belum diisi
    if not smtp_host or not smtp_user:
        print("\n" + "=" * 65)
        print("🔐 [OTP SIMULATION - LOGIN VERIFICATION CODE]")
        print(f"To      : {recipient_email}")
        print(f"OTP CODE: >>> {otp_code} <<<")
        print("⏱️ Berlaku : 5 Menit")
        print("💡 Catatan: Untuk mengirim email sungguhan, atur SMTP_HOST, SMTP_USER, dan SMTP_PASS di backend/.env")
        print("=" * 65 + "\n")
        return

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"Internal Workspace <{smtp_from}>"
        msg["To"] = recipient_email
        msg.attach(MIMEText(plain_content, "plain", "utf-8"))
        msg.attach(MIMEText(html_content, "html", "utf-8"))

        if smtp_port == 465:
            server = smtplib.SMTP_SSL(smtp_host, smtp_port, timeout=10)
        else:
            server = smtplib.SMTP(smtp_host, smtp_port, timeout=10)
            if smtp_tls:
                server.starttls()

        if smtp_user and smtp_pass:
            server.login(smtp_user, smtp_pass)

        server.sendmail(smtp_from, [recipient_email], msg.as_string())
        server.quit()
        print(f"✅ [OTP SENT] Berhasil mengirim kode OTP ke {recipient_email}")
    except Exception as err:
        print(f"❌ [OTP ERROR] Gagal mengirim email OTP ke {recipient_email}: {err}")
