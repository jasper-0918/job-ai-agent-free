"""
Job AI Agent FREE — Main Orchestrator
=======================================
All tools used here are completely free.

Commands:
  python main.py scrape      — Scrape jobs + AI evaluate
  python main.py apply       — Send pending applications
  python main.py inbox       — Scan Gmail for responses
  python main.py worker      — Process task queue
  python main.py dashboard   — Print stats summary
  python main.py run         — Full cycle (all of the above)
  python main.py server      — Launch web dashboard
"""

import argparse
import logging
import os
import sys
from pathlib import Path

# Load .env before anything else
from dotenv import load_dotenv
load_dotenv()

# Logging setup
Path("logs").mkdir(exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(message)s",
    datefmt="%H:%M:%S",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("./logs/agent.log", mode="a"),
    ]
)
log = logging.getLogger("main")

from db.database        import Database
from agents.scraper     import scrape_all
from agents.decision    import evaluate_job
from agents.cover_letter import generate_cover_letter
from agents.apply       import send_application
from agents.inbox       import scan_inbox
from agents.worker      import process_queue
from config             import MAX_AUTO_APPLIES_PER_DAY, SCORE_AUTO_APPLY


def check_env() -> bool:
    """Make sure required .env values are set."""
    ok = True
    checks = {
        "GROQ_API_KEY":      "Get free key at https://console.groq.com",
        "GMAIL_ADDRESS":     "Your Gmail address",
        "GMAIL_APP_PASSWORD":"App Password from myaccount.google.com/apppasswords",
    }
    for key, hint in checks.items():
        val = os.getenv(key, "")
        if not val or "your_" in val.lower():
            log.error(f"Missing {key} in .env — {hint}")
            ok = False
    return ok


def cmd_scrape(db: Database) -> int:
    log.info("=" * 50)
    log.info("SCRAPING JOBS")
    log.info("=" * 50)

    jobs      = scrape_all()
    new_count = 0

    for job in jobs:
        job_id = db.add_job(job)
        if not job_id:
            continue   # duplicate

        new_count += 1
        log.info(f"  [{new_count}] Evaluating: {job['title'][:45]} @ {job['company'][:25]}")

        ai = evaluate_job(job)
        db.update_ai(job_id, ai)

        icon = {"AUTO_APPLY": "✅", "ASK_USER": "⚠️",
                "REJECT": "❌", "IGNORE": "  "}.get(ai["decision"], "  ")
        log.info(f"       {icon} {ai['decision']}  score={ai['score']}  scam={ai['scam']}")
        if ai["reason"]:
            log.info(f"          {ai['reason'][:70]}")

    log.info(f"\n  Done. {new_count} new jobs added.")
    return new_count


def cmd_apply(db: Database) -> int:
    log.info("=" * 50)
    log.info("APPLYING TO JOBS")
    log.info("=" * 50)

    jobs    = db.get_evaluated()
    applied = 0
    manual  = []

    for job in jobs:
        decision = job.get("ai_decision", "IGNORE")
        score    = job.get("ai_score", 0)

        if not job.get("apply_email"):
            log.info(f"  [MANUAL] {job['title'][:40]} — no email, visit: {job.get('url','')[:50]}")
            manual.append(job)
            db.update_status(job["id"], "manual_required")
            continue

        if decision == "AUTO_APPLY" and score >= SCORE_AUTO_APPLY:
            if applied >= MAX_AUTO_APPLIES_PER_DAY:
                log.warning(f"  Daily limit ({MAX_AUTO_APPLIES_PER_DAY}) reached.")
                break

            log.info(f"  [AUTO] Applying: {job['title'][:40]}")
            cover  = generate_cover_letter(job)
            result = send_application(job, cover, MAX_AUTO_APPLIES_PER_DAY)

            if result["sent"]:
                db.update_status(job["id"], "applied", cover)
                applied += 1
            else:
                log.warning(f"  ❌ Failed: {result['error']}")
                db.update_status(job["id"], "apply_failed")

        elif decision == "ASK_USER":
            log.info(f"  [REVIEW NEEDED] {job['title'][:40]}")
            log.info(f"    Email: {job['apply_email']}")
            log.info(f"    Reason: {job.get('ai_reason', '')[:60]}")
            manual.append(job)
            db.update_status(job["id"], "awaiting_approval")

    log.info(f"\n  Applied: {applied} | Manual review: {len(manual)}")
    return applied


def cmd_inbox(db: Database) -> list:
    log.info("=" * 50)
    log.info("SCANNING GMAIL INBOX")
    log.info("=" * 50)

    results = scan_inbox(lookback_days=30)
    for r in results:
        db.log_response(r)
        emoji = {"interview": "🎉", "assessment": "📝",
                 "rejected": "❌", "followup": "📬"}.get(r["category"], "📧")
        log.info(f"  {emoji} [{r['category'].upper()}] {r['subject'][:50]}")
        log.info(f"       From: {r['from_name']} <{r['from_email']}>")

    log.info(f"\n  {len(results)} job-related emails found.")
    return results


def cmd_worker(db: Database) -> list:
    log.info("=" * 50)
    log.info("WORKER AGENT — TASK QUEUE")
    log.info("=" * 50)
    results = process_queue(db)
    if not results:
        log.info("  No pending tasks. Add tasks via the dashboard.")
    return results


def cmd_dashboard(db: Database):
    s = db.get_stats()
    print("\n" + "=" * 50)
    print("  JOB AI AGENT — STATS")
    print("=" * 50)
    print(f"  Jobs found        : {s['total_found']}")
    print(f"  Applied           : {s['applied']}")
    print(f"  Scams caught      : {s['scams_caught']}")
    print(f"  Auto-eligible     : {s['auto_eligible']}")
    print(f"  Needs your review : {s['needs_review']}")
    print(f"  Email responses   : {s['responses']}")
    print(f"  Interviews        : {s['interviews']} 🎉")
    print("=" * 50 + "\n")


def cmd_server():
    import threading, webbrowser, uvicorn
    def open_browser():
        import time; time.sleep(1.5)
        webbrowser.open("http://127.0.0.1:8000")
    log.info("Starting server at http://127.0.0.1:8000")
    threading.Thread(target=open_browser, daemon=True).start()
    uvicorn.run("api.app:app", host="127.0.0.1", port=8000, reload=False)


def main():
    parser = argparse.ArgumentParser(
        description="Job AI Agent FREE — Autonomous job hunting"
    )
    parser.add_argument(
        "command",
        choices=["scrape", "apply", "inbox", "worker",
                 "dashboard", "run", "server"]
    )
    args = parser.parse_args()

    if args.command == "server":
        cmd_server()
        return

    if not check_env():
        print("\n  Fix the .env errors above, then try again.\n")
        sys.exit(1)

    db = Database()

    if   args.command == "scrape":    cmd_scrape(db)
    elif args.command == "apply":     cmd_apply(db)
    elif args.command == "inbox":     cmd_inbox(db)
    elif args.command == "worker":    cmd_worker(db)
    elif args.command == "dashboard": cmd_dashboard(db)
    elif args.command == "run":
        cmd_scrape(db)
        cmd_apply(db)
        cmd_inbox(db)
        cmd_worker(db)
        cmd_dashboard(db)

    db.close()


if __name__ == "__main__":
    main()
