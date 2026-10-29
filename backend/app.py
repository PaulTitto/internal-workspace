# backend/app.py
# Entrypoint Utama Server Backend Python Flask
from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate
from config import Config
from models import db
from routes.issues_bp import issues_bp
from routes.teams_bp import teams_bp
from routes.agent_bp import agent_bp
from routes.share_bp import share_bp
from routes.otp_bp import otp_bp
from auth_oauth import auth_bp

from sqlalchemy import event
from sqlalchemy.engine import Engine

# SQLite tidak mengaktifkan enforcement foreign key secara default.
# Model kita mengandalkan ON DELETE CASCADE, jadi pragma wajib dinyalakan
# di setiap koneksi baru.
@event.listens_for(Engine, "connect")
def _set_sqlite_pragma(dbapi_connection, connection_record):
    if type(dbapi_connection).__module__.startswith("sqlite3"):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app, resources={
        r"/api/*": {"origins": ["http://localhost:5173"], "supports_credentials": True},
    })

    db.init_app(app)
    Migrate(app, db)

    # Registrasi Blueprint Modular:
    #   teams_bp  : onboarding /me, create team, join invite, members, sprints
    #   issues_bp : CRUD issues ter-scope per tim (+ subtasks, comments)
    #   agent_bp  : AI Agent prompt-to-action ter-scope per tim
    app.register_blueprint(teams_bp)
    app.register_blueprint(issues_bp)
    app.register_blueprint(agent_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(share_bp)
    app.register_blueprint(otp_bp)

    with app.app_context():
        # Tidak ada seeding mock: workspace baru 100% kosong sampai user
        # membuat tim sendiri atau join via invite code.
        db.create_all()
        _ensure_sqlite_columns()

    return app


def _ensure_sqlite_columns():
    """Migrasi ringan untuk dev SQLite: db.create_all() tidak pernah ALTER
    tabel yang sudah ada, jadi kolom baru ditambahkan manual & idempotent."""
    if not db.engine.url.get_backend_name().startswith("sqlite"):
        return
    inspector = db.inspect(db.engine)
    with db.engine.begin() as conn:
        sprint_cols = {c["name"] for c in inspector.get_columns("sprints")}
        if "start_date" not in sprint_cols:
            conn.exec_driver_sql("ALTER TABLE sprints ADD COLUMN start_date DATE")
        if "end_date" not in sprint_cols:
            conn.exec_driver_sql("ALTER TABLE sprints ADD COLUMN end_date DATE")

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5001, debug=True)