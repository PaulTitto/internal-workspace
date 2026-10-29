# backend/routes/issues_bp.py
# Blueprint Controller REST API untuk Issues, Subtasks, dan Comments.
# Semua issue ter-scope ke tim: key per-tim (FIN-101), membership wajib,
# Viewer read-only (tidak bisa create/update/delete).
from flask import Blueprint, jsonify, request, g

from models import db, Issue, Subtask, Comment, Team, TeamMembership
from auth_microsoft import require_microsoft_sso

issues_bp = Blueprint("issues_bp", __name__, url_prefix="/api/v1/teams/<int:team_id>/issues")

WRITE_ROLES = ("Admin", "Developer")


def require_membership(write=False):
    """Return (team, issue?, error_response). Membership di table team_memberships wajib."""
    team = Team.query.get(g.team_id)
    if not team:
        return None, None, (jsonify({"error": "Team not found"}), 404)
    membership = TeamMembership.find(g.current_user.entra_oid, team.id)
    if not membership:
        return None, None, (jsonify({"error": "You are not a member of this team"}), 403)
    if write and membership.role not in WRITE_ROLES:
        return None, None, (jsonify({"error": "Viewers cannot modify issues"}), 403)
    return team, membership, None


def _get_team_issue(team_id, issue_key):
    return Issue.query.filter_by(team_id=team_id, issue_key=issue_key).first()


# ---------------------------------------------------------------- List
@issues_bp.route("", methods=["GET"])
@require_microsoft_sso
def list_team_issues(team_id):
    g.team_id = team_id
    team, _, err = require_membership(write=False)
    if err:
        return err

    query = Issue.query.filter_by(team_id=team.id)
    sprint_id = request.args.get("sprintId", type=int)
    if sprint_id:
        query = query.filter(Issue.sprint_id == sprint_id)
    issues = query.order_by(Issue.issue_number.desc()).all()
    return jsonify([i.to_dict() for i in issues]), 200


# ---------------------------------------------------------------- Create
@issues_bp.route("", methods=["POST"])
@require_microsoft_sso
def create_team_issue(team_id):
    g.team_id = team_id
    team, _, err = require_membership(write=True)
    if err:
        return err

    data = request.get_json() or {}
    summary = (data.get("summary") or "").strip()
    if not summary:
        return jsonify({"error": "Summary is required"}), 400

    sprint_id = data.get("sprintId")
    if sprint_id:
        from models import Sprint

        if not Sprint.query.filter_by(id=sprint_id, team_id=team.id).first():
            return jsonify({"error": "Sprint not found in this team"}), 400

    issue_number = Issue.next_issue_number(team.id)
    issue = Issue(
        team_id=team.id,
        sprint_id=sprint_id,
        issue_number=issue_number,
        issue_key=Issue.build_issue_key(team, issue_number),
        type=data.get("type", "Story"),
        summary=summary,
        description=data.get("description", ""),
        status=data.get("status", "TO DO"),
        priority=data.get("priority", "Medium"),
        epic_key=data.get("epic"),
        story_points=int(data.get("storyPoints", 3)),
        assignee_oid=data.get("assigneeOid"),
        reporter_upn=g.current_user.upn_email,
        in_sprint=bool(data.get("inSprint", True)),
    )
    db.session.add(issue)
    db.session.commit()
    return jsonify(issue.to_dict()), 201


# ---------------------------------------------------------------- Update
@issues_bp.route("/<string:issue_key>", methods=["PUT"])
@require_microsoft_sso
def update_team_issue(team_id, issue_key):
    g.team_id = team_id
    team, _, err = require_membership(write=True)
    if err:
        return err

    issue = _get_team_issue(team.id, issue_key)
    if not issue:
        return jsonify({"error": "Issue not found"}), 404

    data = request.get_json() or {}
    for field in ["type", "summary", "description", "status", "priority", "in_sprint"]:
        if field in data:
            setattr(issue, field, data[field])
    if "storyPoints" in data:
        issue.story_points = int(data["storyPoints"])
    if "sprintId" in data:
        if data["sprintId"] is not None:
            from models import Sprint

            if not Sprint.query.filter_by(id=data["sprintId"], team_id=team.id).first():
                return jsonify({"error": "Sprint not found in this team"}), 400
        issue.sprint_id = data["sprintId"]
    if "assigneeOid" in data:
        # Assignee harus anggota tim yang sama
        if data["assigneeOid"] and not TeamMembership.find(data["assigneeOid"], team.id):
            return jsonify({"error": "Assignee is not a member of this team"}), 400
        issue.assignee_oid = data["assigneeOid"]

    db.session.commit()
    return jsonify(issue.to_dict()), 200


# ---------------------------------------------------------------- Delete
@issues_bp.route("/<string:issue_key>", methods=["DELETE"])
@require_microsoft_sso
def delete_team_issue(team_id, issue_key):
    g.team_id = team_id
    team, _, err = require_membership(write=True)
    if err:
        return err

    issue = _get_team_issue(team.id, issue_key)
    if not issue:
        return jsonify({"error": "Issue not found"}), 404
    db.session.delete(issue)
    db.session.commit()
    return "", 204


# ---------------------------------------------------------------- Subtasks
@issues_bp.route("/<string:issue_key>/subtasks", methods=["POST"])
@require_microsoft_sso
def add_subtask(team_id, issue_key):
    g.team_id = team_id
    team, _, err = require_membership(write=True)
    if err:
        return err
    issue = _get_team_issue(team.id, issue_key)
    if not issue:
        return jsonify({"error": "Issue not found"}), 404
    data = request.get_json() or {}
    subtask = Subtask(issue_id=issue.id, title=(data.get("title") or "").strip() or "New subtask")
    db.session.add(subtask)
    db.session.commit()
    return jsonify(issue.to_dict()), 201


@issues_bp.route("/<string:issue_key>/subtasks/<int:subtask_id>", methods=["PATCH"])
@require_microsoft_sso
def update_subtask(team_id, issue_key, subtask_id):
    g.team_id = team_id
    team, _, err = require_membership(write=True)
    if err:
        return err
    issue = _get_team_issue(team.id, issue_key)
    if not issue:
        return jsonify({"error": "Issue not found"}), 404
    subtask = Subtask.query.filter_by(id=subtask_id, issue_id=issue.id).first()
    if not subtask:
        return jsonify({"error": "Subtask not found"}), 404
    data = request.get_json() or {}
    if "done" in data:
        subtask.is_done = bool(data["done"])
    if "title" in data:
        subtask.title = str(data["title"]).strip()
    db.session.commit()
    return jsonify(issue.to_dict()), 200


@issues_bp.route("/<string:issue_key>/subtasks/<int:subtask_id>", methods=["DELETE"])
@require_microsoft_sso
def delete_subtask(team_id, issue_key, subtask_id):
    g.team_id = team_id
    team, _, err = require_membership(write=True)
    if err:
        return err
    issue = _get_team_issue(team.id, issue_key)
    if not issue:
        return jsonify({"error": "Issue not found"}), 404
    subtask = Subtask.query.filter_by(id=subtask_id, issue_id=issue.id).first()
    if not subtask:
        return jsonify({"error": "Subtask not found"}), 404
    db.session.delete(subtask)
    db.session.commit()
    return jsonify(issue.to_dict()), 200


# ---------------------------------------------------------------- Comments
@issues_bp.route("/<string:issue_key>/comments", methods=["POST"])
@require_microsoft_sso
def add_comment(team_id, issue_key):
    g.team_id = team_id
    team, _, err = require_membership(write=True)
    if err:
        return err
    issue = _get_team_issue(team.id, issue_key)
    if not issue:
        return jsonify({"error": "Issue not found"}), 404
    data = request.get_json() or {}
    body_text = (data.get("body") or "").strip()
    if not body_text:
        return jsonify({"error": "Comment body is required"}), 400

    comment = Comment(
        issue_id=issue.id,
        author_upn=g.current_user.upn_email or "unknown",
        author_oid=g.current_user.entra_oid,
        body=body_text,
    )
    db.session.add(comment)
    db.session.commit()

    # Deteksi dan kirim notifikasi email untuk mention (@mention) secara aman
    mentioned_emails = []
    try:
        from mailer import extract_mentioned_emails, send_mention_email_async

        memberships = list(team.memberships) if team and team.memberships else []
        mentioned_emails = extract_mentioned_emails(body_text, memberships)

        current_email = (g.current_user.upn_email or "").strip().lower()
        commenter_name = g.current_user.display_name or g.current_user.upn_email or "Rekan Tim"
        commenter_email = g.current_user.upn_email or "noreply@srkk.com"

        for email_addr in mentioned_emails:
            if current_email and email_addr.lower() == current_email:
                continue
            send_mention_email_async(
                recipient_email=email_addr,
                commenter_name=commenter_name,
                commenter_email=commenter_email,
                issue_key=issue.issue_key,
                issue_summary=issue.summary,
                comment_body=body_text,
                team_name=team.name,
                team_key=team.key,
            )
    except Exception as mail_err:
        print(f"[MAIL WARN] Gagal memproses mention email: {mail_err}")

    res_data = issue.to_dict()
    res_data["mentioned"] = mentioned_emails
    return jsonify(res_data), 201
