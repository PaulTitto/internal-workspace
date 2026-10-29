# backend/routes/agent_bp.py
# Blueprint Controller AI Agent: Menerima Prompt Natural Language & Mengeksekusi Tool ke Database SQLAlchemy
# Ter-scope per tim: hanya issue tim yang dianalisis, dan hanya anggota
# dengan role Admin/Developer yang boleh memicu aksi tulis.
import os
import json
from flask import Blueprint, jsonify, request, g
from google import genai
from models import db, Issue, Team, TeamMembership
from auth_microsoft import require_microsoft_sso

agent_bp = Blueprint("agent_bp", __name__, url_prefix="/api/v1/agent")

WRITE_ROLES = ("Admin", "Developer")


@agent_bp.route("/prompt", methods=["POST"])
@require_microsoft_sso
def execute_agent_prompt():
    payload = request.get_json() or {}
    user_prompt = payload.get("prompt", "")
    team_id = payload.get("teamId")

    # Validasi keanggotaan tim sebelum mengeksekusi aksi apa pun
    team = Team.query.get(team_id)
    if not team:
        return jsonify({"error": "Team not found. Pass a valid teamId."}), 404
    membership = TeamMembership.find(g.current_user.entra_oid, team.id)
    if not membership:
        return jsonify({"error": "You are not a member of this team"}), 403
    if membership.role not in WRITE_ROLES:
        return jsonify({"error": "Viewers cannot run agent actions"}), 403

    # 1. Ambil state tiket TIM INI saja dari Database untuk konteks AI Agent
    current_issues = [i.to_dict() for i in Issue.query.filter_by(team_id=team.id).all()]

    # 2. Panggil Gemini API dengan Structured JSON Schema (Tool Calling)
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    system_instruction = (
        "Kamu adalah JiraVue AI Agent. Terjemahkan perintah natural language user menjadi daftar "
        "actions JSON (CREATE_ISSUE, UPDATE_STATUS, UPDATE_PRIORITY, ADD_SUBTASK, DELETE_ISSUE) "
        "beserta reply penjelasan singkat."
    )

    response = client.models.generate_content(
        model="gemini-3-flash-preview",
        contents=f"Context Issues: {json.dumps(current_issues)}\nUser Prompt: {user_prompt}",
        config={
            "system_instruction": system_instruction,
            "response_mime_type": "application/json",
        },
    )

    plan = json.loads(response.text)
    executed_results = []

    # 3. Eksekusi otomatis setiap action ke Database SQLAlchemy (selalu dalam tim ini)
    for act in plan.get("actions", []):
        action_type = act.get("actionType")
        if action_type == "CREATE_ISSUE":
            issue_number = Issue.next_issue_number(team.id)
            new_issue = Issue(
                team_id=team.id,
                issue_number=issue_number,
                issue_key=Issue.build_issue_key(team, issue_number),
                type=act.get("issueType", "Story"),
                summary=act.get("summary", "New AI Generated Issue"),
                status=act.get("status", "TO DO"),
                priority=act.get("priority", "Medium"),
                epic_key=act.get("epic"),
                story_points=int(act.get("storyPoints", 3)),
                reporter_upn=g.current_user.upn_email,
            )
            db.session.add(new_issue)
            db.session.commit()
            executed_results.append({"key": new_issue.issue_key, "action": "CREATED"})

        elif action_type in ("UPDATE_STATUS", "UPDATE_PRIORITY", "DELETE_ISSUE"):
            issue = Issue.query.filter_by(team_id=team.id, issue_key=act.get("issueKey")).first()
            if not issue:
                continue
            if action_type == "UPDATE_STATUS":
                issue.status = act.get("newStatus", issue.status)
                executed_results.append({"key": issue.issue_key, "action": f"MOVED_TO_{issue.status}"})
            elif action_type == "UPDATE_PRIORITY":
                issue.priority = act.get("newPriority", issue.priority)
                executed_results.append({"key": issue.issue_key, "action": f"PRIORITY_{issue.priority}"})
            else:
                executed_results.append({"key": issue.issue_key, "action": "DELETED"})
                db.session.delete(issue)
            db.session.commit()

    return jsonify({
        "reply": plan.get("reply", "Perintah berhasil dijalankan oleh AI Agent."),
        "executed": executed_results,
    }), 200
