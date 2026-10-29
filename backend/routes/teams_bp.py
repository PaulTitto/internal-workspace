# backend/routes/teams_bp.py
# Blueprint Controller REST API untuk Multi-Tim:
# onboarding (/me), create team (+ auto Sprint 1-4 + Admin membership),
# join via invite code, member list, dan generate invite code (Admin only).
from datetime import datetime, timedelta

from flask import Blueprint, jsonify, request, g

from models import (
    db,
    Team,
    TeamMembership,
    TeamInvite,
    Sprint,
    Issue,
    Epic,
    TEAM_ROLES,
    SPRINT_STATES,
    DEFAULT_INVITE_TTL_DAYS,
    normalize_team_key,
)
from auth_microsoft import require_microsoft_sso

teams_bp = Blueprint("teams_bp", __name__, url_prefix="/api/v1")


def get_user_team(user_oid, team_id):
    """Tim milik user + membership-nya. 404 bila tim tidak ada, 403 bila bukan anggota."""
    team = Team.query.get(team_id)
    if not team:
        return None, None, (jsonify({"error": "Team not found"}), 404)
    membership = TeamMembership.find(user_oid, team_id)
    if not membership:
        return None, None, (jsonify({"error": "You are not a member of this team"}), 403)
    return team, membership, None


# ---------------------------------------------------------------- Onboarding
@teams_bp.route("/me", methods=["GET"])
@require_microsoft_sso
def get_me():
    """Endpoint onboarding pertama kali setelah SSO: user + daftar keanggotaan tim."""
    user = g.current_user
    memberships = (
        TeamMembership.query.filter_by(user_oid=user.entra_oid)
        .order_by(TeamMembership.joined_at.asc())
        .all()
    )
    teams_payload = []
    for m in memberships:
        data = m.team.to_dict(include_counts=True)
        # Kode invite aktif tim (untuk ditampilkan di Team Selector)
        active_invite = (
            TeamInvite.query.filter_by(team_id=m.team_id)
            .order_by(TeamInvite.expires_at.desc())
            .first()
        )
        data["inviteCode"] = active_invite.invite_code if active_invite else None
        teams_payload.append(data)
    return jsonify(
        {
            "user": user.to_dict(),
            "memberships": [m.to_dict() for m in memberships],
            "teams": teams_payload,
            "hasTeams": len(memberships) > 0,
        }
    ), 200


# --------------------------------------------------------------- Create team
@teams_bp.route("/teams", methods=["GET"])
@require_microsoft_sso
def list_my_teams():
    memberships = TeamMembership.query.filter_by(user_oid=g.current_user.entra_oid).all()
    return jsonify([m.team.to_dict(include_counts=True) for m in memberships]), 200


@teams_bp.route("/teams", methods=["POST"])
@require_microsoft_sso
def create_team():
    """
    Buat tim baru:
      1. Simpan row ke tabel `teams`.
      2. Pembuat otomatis terdaftar sebagai role 'Admin' di `team_memberships`.
      3. Auto-generate Sprint 1 s/d 4 di tabel `sprints` (Sprint 1 = active).
    Tidak ada mock team: workspace baru benar-benar kosong.
    """
    data = request.get_json() or {}
    name = (data.get("name") or "").strip()
    description = (data.get("description") or "").strip()

    if not name:
        return jsonify({"error": "Team name is required"}), 400

    try:
        key = normalize_team_key(data.get("key"))
    except ValueError as err:
        return jsonify({"error": str(err)}), 400

    if Team.query.filter_by(key=key).first():
        return jsonify({"error": f"Team key '{key}' is already taken"}), 409
    if Team.query.filter_by(name=name).first():
        return jsonify({"error": f"Team name '{name}' is already taken"}), 409

    team = Team(
        key=key,
        name=name,
        description=description,
        created_by_oid=g.current_user.entra_oid,
    )
    db.session.add(team)
    db.session.flush()  # dapatkan team.id untuk membership & sprints

    db.session.add(
        TeamMembership(team_id=team.id, user_oid=g.current_user.entra_oid, role="Admin")
    )
    team.generate_default_sprints()
    db.session.commit()

    # Auto-create default invite code for the new team
    invite = TeamInvite(
        team_id=team.id,
        invite_code=Team.next_invite_code(team.key),
        role="Developer",
        created_by_oid=g.current_user.entra_oid,
        expires_at=datetime.utcnow() + timedelta(days=DEFAULT_INVITE_TTL_DAYS),
    )
    db.session.add(invite)
    db.session.commit()

    return jsonify(
        {
            **team.to_dict(include_counts=True),
            "yourRole": "Admin",
            "sprints": [s.to_dict() for s in team.sprints],
            "defaultInviteCode": invite.invite_code,
        }
    ), 201


# ------------------------------------------------ Update / Delete Team
@teams_bp.route("/teams/<int:team_id>", methods=["PUT"])
@require_microsoft_sso
def update_team(team_id):
    """Update detail tim (name, description, key) — hanya Admin tim."""
    team, membership, err = get_user_team(g.current_user.entra_oid, team_id)
    if err:
        return err
    if membership.role != "Admin":
        return jsonify({"error": "Only team Admins can update team details"}), 403

    data = request.get_json() or {}
    name = (data.get("name") or "").strip()
    description = (data.get("description") or "").strip()
    key = data.get("key")

    if name:
        existing = Team.query.filter(Team.name == name, Team.id != team.id).first()
        if existing:
            return jsonify({"error": f"Team name '{name}' is already taken"}), 409
        team.name = name

    if "description" in data:
        team.description = description

    if key:
        try:
            norm_key = normalize_team_key(key)
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
        existing_key = Team.query.filter(Team.key == norm_key, Team.id != team.id).first()
        if existing_key:
            return jsonify({"error": f"Team key '{norm_key}' is already taken"}), 409
        team.key = norm_key

    db.session.commit()
    return jsonify(
        {
            **team.to_dict(include_counts=True),
            "yourRole": membership.role,
            "role": membership.role,
        }
    ), 200


@teams_bp.route("/teams/<int:team_id>", methods=["DELETE"])
@require_microsoft_sso
def delete_team(team_id):
    """Hapus tim secara permanen beserta semua sprint, issue, dan membership-nya (hanya Admin tim)."""
    team, membership, err = get_user_team(g.current_user.entra_oid, team_id)
    if err:
        return err
    if membership.role != "Admin":
        return jsonify({"error": "Only team Admins can delete this team"}), 403

    team_name = team.name
    team_id_val = team.id
    db.session.delete(team)
    db.session.commit()
    return jsonify({"deleted": team_name, "id": team_id_val}), 200


# ------------------------------------------------- Join via kode invite
@teams_bp.route("/teams/join", methods=["POST"])
@require_microsoft_sso
def join_team_by_invite():
    """Join tim sebagai Developer/Member memakai kode invite dari Admin tim."""
    data = request.get_json() or {}
    code = (data.get("inviteCode") or "").strip().upper()
    if not code:
        return jsonify({"error": "Invite code is required"}), 400

    invite = TeamInvite.query.filter_by(invite_code=code).first()
    if not invite:
        return jsonify({"error": "Invalid invite code"}), 404
    if invite.is_expired:
        return jsonify({"error": "This invite code has expired"}), 410

    user_oid = g.current_user.entra_oid
    existing = TeamMembership.find(user_oid, invite.team_id)
    if existing:
        return jsonify({"error": "You are already a member of this team"}), 409

    membership = TeamMembership(team_id=invite.team_id, user_oid=user_oid, role=invite.role)
    db.session.add(membership)
    db.session.commit()

    team = Team.query.get(invite.team_id)
    return jsonify(
        {
            "team": team.to_dict(include_counts=True),
            "membership": membership.to_dict(),
            "message": f"You joined '{team.name}' as {invite.role}",
        }
    ), 201


# --------------------------------------------------------------- Members
@teams_bp.route("/teams/<int:team_id>/members", methods=["GET"])
@require_microsoft_sso
def list_members(team_id):
    team, _, err = get_user_team(g.current_user.entra_oid, team_id)
    if err:
        return err
    members = TeamMembership.query.filter_by(team_id=team.id).order_by(TeamMembership.joined_at.asc()).all()
    return jsonify(
        {
            "team": team.to_dict(),
            "members": [m.to_dict() for m in members],
            "yourRole": TeamMembership.find(g.current_user.entra_oid, team.id).role,
        }
    ), 200


# --------------------------------------------------------------- Invites
@teams_bp.route("/teams/<int:team_id>/invites", methods=["GET"])
@require_microsoft_sso
def list_invites(team_id):
    """Daftar kode invite aktif — hanya untuk Admin tim."""
    team, membership, err = get_user_team(g.current_user.entra_oid, team_id)
    if err:
        return err
    if membership.role != "Admin":
        return jsonify({"error": "Only team Admins can view invite codes"}), 403

    invites = TeamInvite.query.filter_by(team_id=team.id).order_by(TeamInvite.created_at.desc()).all()
    return jsonify([i.to_dict() for i in invites]), 200


@teams_bp.route("/teams/<int:team_id>/invites", methods=["POST"])
@require_microsoft_sso
def create_invite(team_id):
    """Generate kode invite baru (format INVITE-<KEY>-XXXX) — hanya Admin tim."""
    team, membership, err = get_user_team(g.current_user.entra_oid, team_id)
    if err:
        return err
    if membership.role != "Admin":
        return jsonify({"error": "Only team Admins can generate invite codes"}), 403

    data = request.get_json() or {}
    role = data.get("role", "Developer")
    if role not in TEAM_ROLES or role == "Admin":
        return jsonify({"error": f"Invite role must be one of {['Developer', 'Viewer']}"}), 400

    ttl_days = int(data.get("expiresInDays", DEFAULT_INVITE_TTL_DAYS))
    if not 1 <= ttl_days <= 30:
        return jsonify({"error": "expiresInDays must be between 1 and 30"}), 400

    invite = TeamInvite(
        team_id=team.id,
        invite_code=Team.next_invite_code(team.key),
        role=role,
        created_by_oid=g.current_user.entra_oid,
        expires_at=datetime.utcnow() + timedelta(days=ttl_days),
    )
    db.session.add(invite)
    db.session.commit()

    return jsonify(invite.to_dict()), 201


# --------------------------------------------------------------- Sprints
@teams_bp.route("/teams/<int:team_id>/sprints", methods=["GET"])
@require_microsoft_sso
def list_sprints(team_id):
    team, _, err = get_user_team(g.current_user.entra_oid, team_id)
    if err:
        return err
    sprints = Sprint.query.filter_by(team_id=team.id).order_by(Sprint.sprint_number.asc()).all()
    return jsonify([s.to_dict() for s in sprints]), 200


@teams_bp.route("/teams/<int:team_id>/sprints", methods=["POST"])
@require_microsoft_sso
def create_sprint(team_id):
    """Buat sprint baru (Admin) — nomor sprint otomatis max+1, state awal 'future'."""
    team, membership, err = get_user_team(g.current_user.entra_oid, team_id)
    if err:
        return err
    if membership.role != "Admin":
        return jsonify({"error": "Only team Admins can create sprints"}), 403

    data = request.get_json() or {}
    max_number = db.session.query(db.func.max(Sprint.sprint_number)).filter_by(team_id=team.id).scalar() or 0
    number = max_number + 1
    name = (data.get("name") or f"Sprint {number}").strip()
    goal = (data.get("goal") or "").strip()

    sprint = Sprint(team_id=team.id, sprint_number=number, name=name, state="future", goal=goal)
    db.session.add(sprint)
    db.session.commit()
    return jsonify(sprint.to_dict()), 201


@teams_bp.route("/teams/<int:team_id>/sprints/<int:sprint_id>/complete", methods=["POST"])
@require_microsoft_sso
def complete_sprint(team_id, sprint_id):
    """Complete sprint (Admin): state -> done, issue belum selesai kembali ke backlog,
    lalu sprint 'future' bernomor terkecil otomatis menjadi active."""
    team, membership, err = get_user_team(g.current_user.entra_oid, team_id)
    if err:
        return err
    if membership.role != "Admin":
        return jsonify({"error": "Only team Admins can complete sprints"}), 403

    sprint = Sprint.query.filter_by(id=sprint_id, team_id=team.id).first()
    if not sprint:
        return jsonify({"error": "Sprint not found"}), 404
    if sprint.state != "active":
        return jsonify({"error": "Hanya sprint yang sedang active yang bisa di-complete"}), 400

    sprint.state = "done"
    # Issue yang belum selesai kembali ke backlog (sprint_id -> NULL)
    moved = (Issue.query.filter_by(sprint_id=sprint.id)
             .filter(Issue.status != "DONE").all())
    for issue in moved:
        issue.sprint_id = None
    # Aktifkan otomatis sprint future berikutnya (nomor terkecil), ala Jira
    next_sprint = (Sprint.query.filter_by(team_id=team.id, state="future")
                   .order_by(Sprint.sprint_number.asc()).first())
    if next_sprint:
        next_sprint.state = "active"
    db.session.commit()
    return jsonify({"completed": sprint.to_dict(),
                    "movedToBacklog": [i.issue_key for i in moved],
                    "nextActive": next_sprint.to_dict() if next_sprint else None}), 200


@teams_bp.route("/teams/<int:team_id>/sprints/<int:sprint_id>", methods=["DELETE"])
@require_microsoft_sso
def delete_sprint(team_id, sprint_id):
    """Hapus sprint (Admin). Issue di dalamnya TIDAK terhapus — pindah ke backlog."""
    team, membership, err = get_user_team(g.current_user.entra_oid, team_id)
    if err:
        return err
    if membership.role != "Admin":
        return jsonify({"error": "Only team Admins can delete sprints"}), 403

    sprint = Sprint.query.filter_by(id=sprint_id, team_id=team.id).first()
    if not sprint:
        return jsonify({"error": "Sprint not found"}), 404

    was_active = sprint.state == "active"
    moved_keys = [i.issue_key for i in sprint.issues]
    for issue in sprint.issues:  # issue dipindah ke backlog, bukan dihapus
        issue.sprint_id = None
    db.session.delete(sprint)
    if was_active:  # sprint aktif terhapus -> aktifkan future berikutnya
        next_sprint = (Sprint.query.filter_by(team_id=team.id, state="future")
                       .order_by(Sprint.sprint_number.asc()).first())
        if next_sprint:
            next_sprint.state = "active"
    db.session.commit()
    return jsonify({"deleted": sprint.name, "movedToBacklog": moved_keys}), 200


@teams_bp.route("/teams/<int:team_id>/sprints/<int:sprint_id>", methods=["PUT"])
@require_microsoft_sso
def update_sprint(team_id, sprint_id):
    """Update state/goal sprint (active, future, done) — hanya Admin tim.
    Aturan Jira-lite: hanya boleh ada SATU sprint active per tim —
    sprint active lain otomatis dikembalikan ke future."""
    team, membership, err = get_user_team(g.current_user.entra_oid, team_id)
    if err:
        return err
    if membership.role != "Admin":
        return jsonify({"error": "Only team Admins can update sprints"}), 403

    sprint = Sprint.query.filter_by(id=sprint_id, team_id=team.id).first()
    if not sprint:
        return jsonify({"error": "Sprint not found"}), 404

    data = request.get_json() or {}
    if "state" in data:
        if data["state"] not in SPRINT_STATES:
            return jsonify({"error": f"Sprint state must be one of {list(SPRINT_STATES)}"}), 400
        sprint.state = data["state"]
        if sprint.state == "active":
            # Sprint yang mulai: set rentang tanggal default 2 minggu bila kosong
            if not sprint.start_date:
                sprint.start_date = datetime.utcnow().date()
            if not sprint.end_date:
                sprint.end_date = sprint.start_date + timedelta(days=13)
            Sprint.query.filter(Sprint.team_id == team.id,
                                Sprint.id != sprint.id,
                                Sprint.state == "active").update({"state": "future"})
    if "goal" in data:
        sprint.goal = data["goal"]
    if "name" in data and data["name"].strip():
        sprint.name = data["name"].strip()
    for field in ("startDate", "endDate"):
        if field in data:
            try:
                setattr(sprint, "start_date" if field == "startDate" else "end_date",
                        datetime.strptime(data[field], "%Y-%m-%d").date() if data[field] else None)
            except (ValueError, TypeError):
                return jsonify({"error": f"{field} harus format YYYY-MM-DD"}), 400
    db.session.commit()
    return jsonify(sprint.to_dict()), 200


# ------------------------------------------------- Seed & Export (demo tools)
@teams_bp.route("/teams/<int:team_id>/seed", methods=["POST"])
@require_microsoft_sso
def seed_team(team_id):
    """Seed konten demo ala Jira: 1 epic + 8 issue tersebar di sprint & backlog.
    Hanya Admin; ditolak 409 bila tim sudah punya issue (tidak menimpa data)."""
    team, membership, err = get_user_team(g.current_user.entra_oid, team_id)
    if err:
        return err
    if membership.role != "Admin":
        return jsonify({"error": "Only team Admins can seed demo data"}), 403
    if Issue.query.filter_by(team_id=team.id).count() > 0:
        return jsonify({"error": "Tim ini sudah punya issue — seed dibatalkan agar data tidak dobel"}), 409

    epic = Epic(epic_key=f"{team.key}-EPIC-1",
                badge_class="bg-blue-100 text-blue-800")
    db.session.add(epic)
    db.session.flush()

    sprints = {s.sprint_number: s for s in team.sprints}
    now = datetime.utcnow().date()

    def sprint_id(n):
        return sprints[n].id if n in sprints else None

    demo = [
        # (sprint#, type, summary, status, priority, sp, assignee)
        (1, "Story", f"Setup pipeline CI/CD {team.key}", "DONE", "High", 5, True),
        (1, "Task", "Desain skema database rekonsiliasi", "IN PROGRESS", "Medium", 3, True),
        (1, "Bug", "Fix race condition pada worker queue", "IN REVIEW", "High", 2, False),
        (1, "Story", "Auth service integrasi SSO", "TO DO", "High", 8, True),
        (2, "Task", "Dashboard monitoring transaksi QRIS", "TO DO", "Medium", 5, False),
        (2, "Story", "Implementasi auto-refund engine", "TO DO", "High", 8, True),
        (3, "Bug", "Selisih pembulatan rounding IDR", "TO DO", "Medium", 3, False),
        (4, "Story", "Laporan harian ekspor Excel/PDF", "TO DO", "Medium", 5, True),
        (4, "Task", "Audit trail untuk refund manual", "TO DO", "Low", 3, False),
    ]
    active_number = next((n for n, s in sprints.items() if s.state == "active"), 1)
    num = Issue.next_issue_number(team.id)
    for sprint_n, type_, summary, status, priority, sp, mine in demo:
        s_id = sprint_id(sprint_n)
        if sprint_n < active_number and s_id is None:
            s_id = None
        db.session.add(Issue(
            team_id=team.id, sprint_id=s_id, issue_number=num,
            issue_key=f"{team.key}-{num}", type=type_, summary=summary,
            description=f"Issue demo hasil Seed DB untuk {team.name}.",
            status=status if sprint_n <= active_number else "TO DO",
            priority=priority, epic_key=epic.epic_key, story_points=sp,
            assignee_oid=g.current_user.entra_oid if mine else None,
            reporter_upn=g.current_user.upn_email,
        ))
        num += 1
    # Set tanggal sprint aktif supaya badge "hari tersisa" muncul
    for s in sprints.values():
        if s.state == "active" and not s.start_date:
            s.start_date = now - timedelta(days=1)
            s.end_date = now + timedelta(days=6)
    db.session.commit()
    return jsonify({"seeded": len(demo), "epic": epic.epic_key}), 201


@teams_bp.route("/teams/<int:team_id>/export", methods=["GET"])
@require_microsoft_sso
def export_team(team_id):
    """Export seluruh data tim dalam satu JSON (untuk backup / Export DB Dump)."""
    team, _, err = get_user_team(g.current_user.entra_oid, team_id)
    if err:
        return err
    issues = Issue.query.filter_by(team_id=team.id).all()
    return jsonify({
        "exportedAt": datetime.utcnow().isoformat(),
        "team": team.to_dict(include_counts=True),
        "members": [m.to_dict() for m in team.memberships],
        "sprints": [s.to_dict() for s in team.sprints],
        "issues": [i.to_dict() for i in issues],
        "subtasks": [st.to_dict() for i in issues for st in i.subtasks],
        "comments": [cm.to_dict() for i in issues for cm in i.comments],
    }), 200
