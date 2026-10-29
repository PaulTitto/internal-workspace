# backend/routes/share_bp.py
# Blueprint untuk share token: generate link baca-saja & public board endpoint.
import secrets
from datetime import datetime, timedelta

from flask import Blueprint, jsonify, request, g

from models import db, Team, TeamMembership, ShareToken, Issue, Sprint
from auth_microsoft import require_microsoft_sso

share_bp = Blueprint("share_bp", __name__, url_prefix="/api/v1")


def _get_user_team(user_oid, team_id):
    """Helper: ambil tim + membership. Kembalikan (team, membership, error) tuple."""
    team = Team.query.get(team_id)
    if not team:
        return None, None, (jsonify({"error": "Team not found"}), 404)
    membership = TeamMembership.find(user_oid, team_id)
    if not membership:
        return None, None, (jsonify({"error": "You are not a member of this team"}), 403)
    return team, membership, None


@share_bp.route("/teams/<int:team_id>/share-token", methods=["GET", "POST"])
@require_microsoft_sso
def get_or_create_share_token(team_id):
    """
    Ambil share token tetap untuk papan tim.
    Bila sudah ada token aktif, kembalikan token yang sama sehingga link stabil dan tidak berubah-ubah.
    Bila belum ada (atau ?regenerate=true), buat token baru dengan masa berlaku panjang (365 hari).
    """
    team, membership, err = _get_user_team(g.current_user.entra_oid, team_id)
    if err:
        return err

    data = request.get_json(silent=True) or {}
    force_regenerate = (
        request.args.get("regenerate", "").lower() == "true"
        or bool(data.get("regenerate"))
    )

    # Cek apakah sudah ada token aktif untuk tim ini
    existing = (
        ShareToken.query.filter_by(team_id=team.id)
        .order_by(ShareToken.id.desc())
        .first()
    )

    if existing and not existing.is_expired and not force_regenerate:
        return jsonify({
            "shareToken": existing.token,
            "expiresAt": existing.expires_at.strftime("%Y-%m-%d %H:%M:%S"),
            "isNew": False,
        }), 200

    token_str = secrets.token_urlsafe(32)
    share = ShareToken(
        team_id=team.id,
        token=token_str,
        created_by_oid=g.current_user.entra_oid,
        expires_at=datetime.utcnow() + timedelta(days=365),
    )
    db.session.add(share)
    db.session.commit()
    return jsonify({
        "shareToken": token_str,
        "expiresAt": share.expires_at.strftime("%Y-%m-%d %H:%M:%S"),
        "isNew": True,
    }), 201


@share_bp.route("/share/<token>", methods=["GET"])
def public_share_view(token):
    """Public read-only board endpoint — tidak memerlukan autentikasi."""
    share = ShareToken.query.filter_by(token=token).first()
    if not share or share.is_expired:
        return jsonify({"error": "Share link tidak valid atau sudah expired"}), 404

    team = Team.query.get(share.team_id)
    if not team:
        return jsonify({"error": "Team tidak ditemukan"}), 404

    issues = Issue.query.filter_by(team_id=team.id).all()
    sprints = (
        Sprint.query.filter_by(team_id=team.id)
        .order_by(Sprint.sprint_number.asc())
        .all()
    )
    return jsonify({
        "team": team.to_dict(),
        "issues": [i.to_dict() for i in issues],
        "sprints": [s.to_dict() for s in sprints],
        "readOnly": True,
    }), 200
