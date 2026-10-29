# backend/models.py
# Modul Model Database Relasional (SQLAlchemy ORM)
# Arsitektur multi-tim: teams -> team_memberships -> users, sprints per tim,
# issues ter-scope per tim dengan issue key per-tim (contoh: FIN-101).
import re
import secrets
from datetime import datetime

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Role yang valid di dalam sebuah tim
TEAM_ROLES = ("Admin", "Developer", "Viewer")
# Sprint state: future -> active -> done
SPRINT_STATES = ("future", "active", "done")
DEFAULT_SPRINT_COUNT = 4
DEFAULT_INVITE_TTL_DAYS = 7


def utcnow():
    return datetime.utcnow()


def generate_invite_code(team_key):
    """Format kode invite: INVITE-<KEY>-<4 digit acak>, contoh INVITE-FIN-8899."""
    return f"INVITE-{team_key.upper()}-{secrets.randbelow(10000):04d}"


def normalize_team_key(raw_key):
    """Key tim: 2-10 huruf kapital A-Z saja (contoh: FIN, DATAOPS)."""
    key = (raw_key or "").strip().upper()
    if not re.fullmatch(r"[A-Z]{2,10}", key):
        raise ValueError("Team key must be 2-10 uppercase letters (A-Z), e.g. 'FIN'")
    return key


class UserEntraID(db.Model):
    __tablename__ = "users_entra_id"
    id = db.Column(db.Integer, primary_key=True)
    entra_oid = db.Column(db.String(64), unique=True, nullable=False, index=True)
    upn_email = db.Column(db.String(150), unique=True, nullable=False, index=True)
    display_name = db.Column(db.String(120), nullable=False)
    job_title = db.Column(db.String(120), default="Software Engineer")
    entra_role = db.Column(db.String(64), default="Jira.Developer")
    tenant_id = db.Column(db.String(64), nullable=False)
    # Penyedia identitas: 'azure' (SSO) / 'google' / 'github' (OAuth 2.0)
    auth_provider = db.Column(db.String(16), nullable=False, default="azure", server_default="azure")
    last_sso_login = db.Column(db.DateTime, default=utcnow)

    memberships = db.relationship("TeamMembership", backref="user", lazy="joined")

    def to_dict(self):
        return {
            "id": self.id,
            "oid": self.entra_oid,
            "email": self.upn_email,
            "name": self.display_name,
            "role": self.job_title,
            "entraRole": self.entra_role,
        }


class Team(db.Model):
    __tablename__ = "teams"
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(10), unique=True, nullable=False, index=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    description = db.Column(db.Text, default="")
    created_by_oid = db.Column(
        db.String(64), db.ForeignKey("users_entra_id.entra_oid", ondelete="CASCADE"), nullable=False, index=True
    )
    created_at = db.Column(db.DateTime, default=utcnow)

    memberships = db.relationship("TeamMembership", backref="team", cascade="all, delete-orphan", lazy="joined")
    sprints = db.relationship(
        "Sprint", backref="team", cascade="all, delete-orphan", lazy="joined", order_by="Sprint.sprint_number"
    )
    invites = db.relationship("TeamInvite", backref="team", cascade="all, delete-orphan", lazy="joined")
    issues = db.relationship("Issue", backref="team", cascade="all, delete-orphan", lazy="select")
    share_tokens = db.relationship("ShareToken", backref="team", cascade="all, delete-orphan", lazy="select")

    def generate_default_sprints(self, count=DEFAULT_SPRINT_COUNT):
        """Auto-generate Sprint 1..N (default 4) saat tim dibuat."""
        for number in range(1, count + 1):
            db.session.add(
                Sprint(
                    team_id=self.id,
                    sprint_number=number,
                    name=f"Sprint {number}",
                    state="active" if number == 1 else "future",
                    goal="",
                )
            )

    @staticmethod
    def next_invite_code(team_key):
        """Kode invite unik global (retry bila collision)."""
        for _ in range(5):
            code = generate_invite_code(team_key)
            if not TeamInvite.query.filter_by(invite_code=code).first():
                return code
        raise RuntimeError("Gagal menghasilkan kode invite unik")

    def to_dict(self, include_counts=False):
        data = {
            "id": self.id,
            "key": self.key,
            "name": self.name,
            "description": self.description,
            "createdByOid": self.created_by_oid,
            "createdAt": self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else None,
        }
        if include_counts:
            data["memberCount"] = len(self.memberships)
            data["issueCount"] = len(self.issues)
            data["activeSprint"] = next(
                (s.to_dict() for s in self.sprints if s.state == "active"), None
            )
        return data


class TeamMembership(db.Model):
    __tablename__ = "team_memberships"
    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.Integer, db.ForeignKey("teams.id", ondelete="CASCADE"), nullable=False, index=True)
    user_oid = db.Column(
        db.String(64), db.ForeignKey("users_entra_id.entra_oid", ondelete="CASCADE"), nullable=False, index=True
    )
    role = db.Column(db.String(16), nullable=False, default="Developer")
    joined_at = db.Column(db.DateTime, default=utcnow)

    __table_args__ = (db.UniqueConstraint("team_id", "user_oid", name="uq_team_user"),)

    @staticmethod
    def find(user_oid, team_id):
        return TeamMembership.query.filter_by(user_oid=user_oid, team_id=team_id).first()

    def to_dict(self):
        return {
            "id": self.id,
            "teamId": self.team_id,
            "userOid": self.user_oid,
            "role": self.role,
            "joinedAt": self.joined_at.strftime("%Y-%m-%d %H:%M:%S") if self.joined_at else None,
            "user": self.user.to_dict() if self.user else None,
        }


class TeamInvite(db.Model):
    __tablename__ = "team_invites"
    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.Integer, db.ForeignKey("teams.id", ondelete="CASCADE"), nullable=False, index=True)
    invite_code = db.Column(db.String(64), unique=True, nullable=False, index=True)
    role = db.Column(db.String(16), nullable=False, default="Developer")
    created_by_oid = db.Column(db.String(64), db.ForeignKey("users_entra_id.entra_oid"), nullable=False)
    created_at = db.Column(db.DateTime, default=utcnow)
    expires_at = db.Column(db.DateTime, nullable=False, index=True)

    @property
    def is_expired(self):
        return self.expires_at < utcnow()

    def to_dict(self):
        return {
            "id": self.id,
            "teamId": self.team_id,
            "inviteCode": self.invite_code,
            "role": self.role,
            "createdByOid": self.created_by_oid,
            "expiresAt": self.expires_at.strftime("%Y-%m-%d %H:%M:%S"),
            "expired": self.is_expired,
        }


class Sprint(db.Model):
    __tablename__ = "sprints"
    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.Integer, db.ForeignKey("teams.id", ondelete="CASCADE"), nullable=False, index=True)
    sprint_number = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(16), nullable=False, default="future")
    goal = db.Column(db.Text, default="")
    start_date = db.Column(db.Date, nullable=True)
    end_date = db.Column(db.Date, nullable=True)

    issues = db.relationship("Issue", backref="sprint", lazy="select")

    __table_args__ = (db.UniqueConstraint("team_id", "sprint_number", name="uq_team_sprint_number"),)

    def to_dict(self):
        return {
            "id": self.id,
            "teamId": self.team_id,
            "sprintNumber": self.sprint_number,
            "name": self.name,
            "state": self.state,
            "goal": self.goal,
            "startDate": self.start_date.isoformat() if self.start_date else None,
            "endDate": self.end_date.isoformat() if self.end_date else None,
        }


class Epic(db.Model):
    __tablename__ = "epics"
    id = db.Column(db.Integer, primary_key=True)
    epic_key = db.Column(db.String(64), unique=True, nullable=False, index=True)
    badge_class = db.Column(db.String(100), default="bg-blue-100 text-blue-800")


class Issue(db.Model):
    __tablename__ = "issues"
    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.Integer, db.ForeignKey("teams.id", ondelete="CASCADE"), nullable=False, index=True)
    sprint_id = db.Column(db.Integer, db.ForeignKey("sprints.id", ondelete="SET NULL"), nullable=True, index=True)
    issue_number = db.Column(db.Integer, nullable=False, default=1)
    issue_key = db.Column(db.String(24), unique=True, nullable=False, index=True)
    type = db.Column(db.String(24), nullable=False, default="Story")
    summary = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, default="")
    status = db.Column(db.String(32), nullable=False, default="TO DO", index=True)
    priority = db.Column(db.String(24), nullable=False, default="Medium")
    epic_key = db.Column(db.String(64), db.ForeignKey("epics.epic_key", ondelete="SET NULL"), nullable=True)
    story_points = db.Column(db.Integer, default=3)
    assignee_oid = db.Column(
        db.String(64), db.ForeignKey("users_entra_id.entra_oid", ondelete="SET NULL"), nullable=True
    )
    reporter_upn = db.Column(db.String(150), nullable=False)
    in_sprint = db.Column(db.Boolean, default=True, index=True)
    created_at = db.Column(db.DateTime, default=utcnow)
    updated_at = db.Column(db.DateTime, default=utcnow, onupdate=utcnow)

    subtasks = db.relationship("Subtask", backref="issue", cascade="all, delete-orphan", lazy="joined")
    comments = db.relationship("Comment", backref="issue", cascade="all, delete-orphan", lazy="joined")

    __table_args__ = (db.UniqueConstraint("team_id", "issue_number", name="uq_team_issue_number"),)

    @staticmethod
    def next_issue_number(team_id):
        last = (
            db.session.query(db.func.max(Issue.issue_number))
            .filter(Issue.team_id == team_id)
            .scalar()
        )
        return (last or 100) + 1

    @staticmethod
    def build_issue_key(team, issue_number):
        return f"{team.key}-{issue_number}"

    def to_dict(self):
        return {
            "dbId": self.id,
            "key": self.issue_key,
            "teamId": self.team_id,
            "sprintId": self.sprint_id,
            "type": self.type,
            "summary": self.summary,
            "description": self.description,
            "status": self.status,
            "priority": self.priority,
            "epic": self.epic_key,
            "storyPoints": self.story_points,
            "assigneeOid": self.assignee_oid,
            "reporterEmail": self.reporter_upn,
            "inSprint": self.in_sprint,
            "subtasks": [s.to_dict() for s in self.subtasks],
            "comments": [c.to_dict() for c in self.comments],
            "updatedAt": self.updated_at.strftime("%Y-%m-%d %H:%M:%S") if self.updated_at else None,
        }


class Subtask(db.Model):
    __tablename__ = "subtasks"
    id = db.Column(db.Integer, primary_key=True)
    issue_id = db.Column(db.Integer, db.ForeignKey("issues.id", ondelete="CASCADE"), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    is_done = db.Column(db.Boolean, default=False)
    updated_at = db.Column(db.DateTime, default=utcnow, onupdate=utcnow)

    def to_dict(self):
        return {"id": self.id, "title": self.title, "done": self.is_done}


class Comment(db.Model):
    __tablename__ = "comments"
    id = db.Column(db.Integer, primary_key=True)
    issue_id = db.Column(db.Integer, db.ForeignKey("issues.id", ondelete="CASCADE"), nullable=False)
    author_upn = db.Column(db.String(150), nullable=False)
    author_oid = db.Column(db.String(64), nullable=False)
    body = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "author": self.author_upn,
            "text": self.body,
            "time": self.created_at.strftime("%Y-%m-%d %H:%M") if self.created_at else None,
        }


class ShareToken(db.Model):
    __tablename__ = "share_tokens"
    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.Integer, db.ForeignKey("teams.id", ondelete="CASCADE"), nullable=False, index=True)
    token = db.Column(db.String(64), unique=True, nullable=False, index=True)
    created_by_oid = db.Column(db.String(64), nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)

    @property
    def is_expired(self):
        return self.expires_at < utcnow()


class EmailOtp(db.Model):
    __tablename__ = "email_otps"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), nullable=False, index=True)
    otp_code = db.Column(db.String(6), nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    is_used = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=utcnow)

    @property
    def is_expired(self):
        return self.expires_at < utcnow()
