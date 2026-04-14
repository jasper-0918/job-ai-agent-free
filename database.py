# db/database.py
import sqlite3
import json
import logging
from datetime import datetime
from pathlib  import Path

log = logging.getLogger("db")


class Database:
    def __init__(self, path: str = "./job_agent.db"):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._migrate()

    def _migrate(self):
        self.conn.executescript("""
            CREATE TABLE IF NOT EXISTS jobs (
                id               INTEGER PRIMARY KEY AUTOINCREMENT,
                title            TEXT NOT NULL,
                company          TEXT DEFAULT 'Unknown',
                platform         TEXT NOT NULL,
                url              TEXT,
                apply_email      TEXT,
                description      TEXT,
                salary_info      TEXT,
                keywords_matched TEXT,
                ai_score         INTEGER DEFAULT 0,
                ai_scam          TEXT    DEFAULT 'unknown',
                ai_decision      TEXT    DEFAULT 'PENDING',
                ai_reason        TEXT,
                status           TEXT    DEFAULT 'pending',
                cover_letter     TEXT,
                applied_at       TEXT,
                found_at         TEXT NOT NULL,
                updated_at       TEXT NOT NULL,
                UNIQUE(title, company, platform)
            );

            CREATE TABLE IF NOT EXISTS responses (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                from_email  TEXT,
                from_name   TEXT,
                subject     TEXT,
                category    TEXT,
                snippet     TEXT,
                received_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS tasks (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                description  TEXT NOT NULL,
                status       TEXT DEFAULT 'pending',
                result       TEXT,
                created_at   TEXT NOT NULL,
                completed_at TEXT
            );
        """)
        self.conn.commit()

    # ── Jobs ──────────────────────────────────────────────

    def add_job(self, job: dict) -> int | None:
        """Insert a job. Returns row id or None if duplicate."""
        now = datetime.utcnow().isoformat()
        try:
            cur = self.conn.execute("""
                INSERT INTO jobs
                    (title, company, platform, url, apply_email, description,
                     salary_info, keywords_matched, found_at, updated_at)
                VALUES (?,?,?,?,?,?,?,?,?,?)
            """, (
                job.get("title", ""),
                job.get("company", "Unknown"),
                job.get("platform", ""),
                job.get("url", ""),
                job.get("apply_email"),
                job.get("description", ""),
                job.get("salary_info", ""),
                json.dumps(job.get("keywords_matched", [])),
                now, now,
            ))
            self.conn.commit()
            return cur.lastrowid
        except sqlite3.IntegrityError:
            return None

    def update_ai(self, job_id: int, ai: dict):
        self.conn.execute("""
            UPDATE jobs SET
                ai_score=?, ai_scam=?, ai_decision=?, ai_reason=?,
                status='evaluated', updated_at=?
            WHERE id=?
        """, (
            ai.get("score", 0), ai.get("scam", "unknown"),
            ai.get("decision", "IGNORE"), ai.get("reason", ""),
            datetime.utcnow().isoformat(), job_id,
        ))
        self.conn.commit()

    def update_status(self, job_id: int, status: str, cover: str = None):
        now = datetime.utcnow().isoformat()
        if status == "applied":
            self.conn.execute(
                "UPDATE jobs SET status=?, applied_at=?, cover_letter=?, updated_at=? WHERE id=?",
                (status, now, cover, now, job_id)
            )
        else:
            self.conn.execute(
                "UPDATE jobs SET status=?, updated_at=? WHERE id=?",
                (status, now, job_id)
            )
        self.conn.commit()

    def get_evaluated(self) -> list:
        rows = self.conn.execute("""
            SELECT * FROM jobs
            WHERE status='evaluated' AND ai_scam != 'yes'
            ORDER BY ai_score DESC
        """).fetchall()
        return [dict(r) for r in rows]

    def get_all(self, limit: int = 200) -> list:
        rows = self.conn.execute(
            "SELECT * FROM jobs ORDER BY found_at DESC LIMIT ?", (limit,)
        ).fetchall()
        return [dict(r) for r in rows]

    def get_by_id(self, job_id: int) -> dict | None:
        r = self.conn.execute("SELECT * FROM jobs WHERE id=?", (job_id,)).fetchone()
        return dict(r) if r else None

    # ── Responses ─────────────────────────────────────────

    def log_response(self, r: dict):
        self.conn.execute("""
            INSERT INTO responses
                (from_email, from_name, subject, category, snippet, received_at)
            VALUES (?,?,?,?,?,?)
        """, (
            r.get("from_email"), r.get("from_name"), r.get("subject"),
            r.get("category"), r.get("snippet"),
            r.get("received_at", datetime.utcnow().isoformat())
        ))
        self.conn.commit()

    def get_responses(self) -> list:
        rows = self.conn.execute(
            "SELECT * FROM responses ORDER BY received_at DESC"
        ).fetchall()
        return [dict(r) for r in rows]

    # ── Tasks ─────────────────────────────────────────────

    def add_task(self, description: str) -> int:
        cur = self.conn.execute(
            "INSERT INTO tasks (description, created_at) VALUES (?,?)",
            (description, datetime.utcnow().isoformat())
        )
        self.conn.commit()
        return cur.lastrowid

    def complete_task(self, task_id: int, result: str):
        self.conn.execute(
            "UPDATE tasks SET status='done', result=?, completed_at=? WHERE id=?",
            (result, datetime.utcnow().isoformat(), task_id)
        )
        self.conn.commit()

    def get_pending_tasks(self) -> list:
        rows = self.conn.execute(
            "SELECT * FROM tasks WHERE status='pending' ORDER BY created_at"
        ).fetchall()
        return [dict(r) for r in rows]

    # ── Stats ─────────────────────────────────────────────

    def get_stats(self) -> dict:
        r = self.conn.execute("""
            SELECT
                COUNT(*) as total,
                SUM(CASE WHEN status='applied'    THEN 1 ELSE 0 END) as applied,
                SUM(CASE WHEN ai_scam='yes'       THEN 1 ELSE 0 END) as scams,
                SUM(CASE WHEN ai_decision='AUTO_APPLY' THEN 1 ELSE 0 END) as auto_eligible,
                SUM(CASE WHEN ai_decision='ASK_USER'   THEN 1 ELSE 0 END) as needs_review,
                SUM(CASE WHEN status='pending'    THEN 1 ELSE 0 END) as pending
            FROM jobs
        """).fetchone()
        resp      = self.conn.execute("SELECT COUNT(*) n FROM responses").fetchone()
        interviews = self.conn.execute(
            "SELECT COUNT(*) n FROM responses WHERE category='interview'"
        ).fetchone()
        return {
            "total_found":   r["total"] or 0,
            "applied":       r["applied"] or 0,
            "scams_caught":  r["scams"] or 0,
            "auto_eligible": r["auto_eligible"] or 0,
            "needs_review":  r["needs_review"] or 0,
            "pending":       r["pending"] or 0,
            "responses":     resp["n"] or 0,
            "interviews":    interviews["n"] or 0,
        }

    def close(self):
        self.conn.close()
