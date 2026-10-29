-- backend/schema.sql
-- DDL Skema Relasional Database (PostgreSQL / Azure SQL / MySQL)
-- Arsitektur multi-tim: teams <- team_memberships, team_invites, sprints, issues.
-- Tidak ada data mock: workspace baru mulai dari kosong.

CREATE TABLE users_entra_id (
    id SERIAL PRIMARY KEY,
    entra_oid VARCHAR(64) NOT NULL UNIQUE,
    upn_email VARCHAR(150) NOT NULL UNIQUE,
    display_name VARCHAR(120) NOT NULL,
    job_title VARCHAR(120) DEFAULT 'Software Engineer',
    entra_role VARCHAR(64) DEFAULT 'Jira.Developer',
    tenant_id VARCHAR(64) NOT NULL,
    last_sso_login TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE teams (
    id SERIAL PRIMARY KEY,
    key VARCHAR(10) NOT NULL UNIQUE,             -- prefix issue key, contoh: FIN
    name VARCHAR(120) NOT NULL UNIQUE,
    description TEXT,
    created_by_oid VARCHAR(64) NOT NULL REFERENCES users_entra_id(entra_oid) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE team_memberships (
    id SERIAL PRIMARY KEY,
    team_id INTEGER NOT NULL REFERENCES teams(id) ON DELETE CASCADE,
    user_oid VARCHAR(64) NOT NULL REFERENCES users_entra_id(entra_oid) ON DELETE CASCADE,
    role VARCHAR(16) NOT NULL DEFAULT 'Developer',   -- Admin / Developer / Viewer
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_team_user UNIQUE (team_id, user_oid)
);

CREATE TABLE team_invites (
    id SERIAL PRIMARY KEY,
    team_id INTEGER NOT NULL REFERENCES teams(id) ON DELETE CASCADE,
    invite_code VARCHAR(64) NOT NULL UNIQUE,         -- contoh: INVITE-FIN-8899
    role VARCHAR(16) NOT NULL DEFAULT 'Developer',
    created_by_oid VARCHAR(64) NOT NULL REFERENCES users_entra_id(entra_oid),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL
);

CREATE TABLE sprints (
    id SERIAL PRIMARY KEY,
    team_id INTEGER NOT NULL REFERENCES teams(id) ON DELETE CASCADE,
    sprint_number INTEGER NOT NULL,
    name VARCHAR(120) NOT NULL,                      -- 'Sprint 1'..'Sprint 4' (auto saat tim dibuat)
    state VARCHAR(16) NOT NULL DEFAULT 'future',     -- future / active / done
    goal TEXT,
    CONSTRAINT uq_team_sprint_number UNIQUE (team_id, sprint_number)
);

CREATE TABLE epics (
    id SERIAL PRIMARY KEY,
    epic_key VARCHAR(64) NOT NULL UNIQUE,
    badge_class VARCHAR(100) NOT NULL
);

CREATE TABLE issues (
    id SERIAL PRIMARY KEY,
    team_id INTEGER NOT NULL REFERENCES teams(id) ON DELETE CASCADE,
    sprint_id INTEGER REFERENCES sprints(id) ON DELETE SET NULL,
    issue_number INTEGER NOT NULL,                   -- nomor urut per tim (101, 102, ...)
    issue_key VARCHAR(24) NOT NULL UNIQUE,           -- '<team.key>-<issue_number>', contoh: FIN-101
    type VARCHAR(24) NOT NULL DEFAULT 'Story',
    summary VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(32) NOT NULL DEFAULT 'TO DO',
    priority VARCHAR(24) NOT NULL DEFAULT 'Medium',
    epic_key VARCHAR(64) REFERENCES epics(epic_key) ON DELETE SET NULL,
    story_points INTEGER NOT NULL DEFAULT 3,
    assignee_oid VARCHAR(64) REFERENCES users_entra_id(entra_oid) ON DELETE SET NULL,
    reporter_upn VARCHAR(150) NOT NULL,
    in_sprint BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_team_issue_number UNIQUE (team_id, issue_number)
);

CREATE TABLE subtasks (
    id SERIAL PRIMARY KEY,
    issue_id INTEGER NOT NULL REFERENCES issues(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    is_done BOOLEAN NOT NULL DEFAULT FALSE,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE comments (
    id SERIAL PRIMARY KEY,
    issue_id INTEGER NOT NULL REFERENCES issues(id) ON DELETE CASCADE,
    author_upn VARCHAR(150) NOT NULL,
    author_oid VARCHAR(64) NOT NULL,
    body TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX ix_team_memberships_user ON team_memberships(user_oid);
CREATE INDEX ix_team_invites_expires ON team_invites(expires_at);
CREATE INDEX ix_issues_team ON issues(team_id);
CREATE INDEX ix_issues_sprint ON issues(sprint_id);
