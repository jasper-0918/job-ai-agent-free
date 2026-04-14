# agents/worker.py
# ─────────────────────────────────────────────────────────
#  Worker Agent — Your Digital Clone
#  Uses Groq (free) to complete tasks you delegate to it
#
#  Example tasks:
#    "Write a follow-up email to CargoBoss, I applied 5 days ago"
#    "Summarize this job post and tell me if I should apply: [paste]"
#    "Draft a reply to this interview invite: [paste email]"
#    "List 5 questions to prepare for a customer service interview"
# ─────────────────────────────────────────────────────────

import os
import logging
from groq import Groq
from config import USER_PROFILE, GROQ_MODEL_SMART

log = logging.getLogger("worker")

_client = None

def _get_client() -> Groq:
    global _client
    if _client is None:
        _client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    return _client

SYSTEM_PROMPT = f"""You are a smart AI assistant acting as the digital clone of {USER_PROFILE['name']}.

About {USER_PROFILE['name']}:
- Education: {USER_PROFILE['education']}
- Skills: {', '.join(USER_PROFILE['skills'][:12])}
- Experience: {'; '.join(USER_PROFILE['experience'])}
- Tone when writing: {USER_PROFILE['tone']}
- Location: {USER_PROFILE['location']}

Your job:
1. Complete tasks delegated by {USER_PROFILE['name']}
2. Write in their voice and style when drafting emails
3. Be practical and direct — no fluff
4. If a task requires a personal decision, flag it clearly

Structure your response as:
STATUS: DONE / NEEDS_REVIEW / CANNOT_COMPLETE
RESULT:
[your output here]
FLAGS:
[anything the human needs to check or decide — leave blank if none]"""


def execute_task(task: str, context: str = "") -> dict:
    """
    Execute a task using Groq/LLaMA.

    Args:
        task: Plain English description of what to do
        context: Optional reference text (email, job post, etc.)

    Returns:
        { status, result, flags }
    """
    full_prompt = task
    if context.strip():
        full_prompt += f"\n\nContext / Reference:\n{context}"

    try:
        client = _get_client()
        response = client.chat.completions.create(
            model=GROQ_MODEL_SMART,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": full_prompt},
            ],
            temperature=0.5,
            max_tokens=800,
        )
        raw = response.choices[0].message.content.strip()

        # Parse structured response
        status = "DONE"
        result = raw
        flags  = ""

        if "STATUS:" in raw:
            lines        = raw.split("\n")
            result_lines = []
            flag_lines   = []
            section      = None

            for line in lines:
                if line.startswith("STATUS:"):
                    status = line.replace("STATUS:", "").strip()
                elif line.startswith("RESULT:"):
                    section = "result"
                    val = line.replace("RESULT:", "").strip()
                    if val:
                        result_lines.append(val)
                elif line.startswith("FLAGS:"):
                    section = "flags"
                    val = line.replace("FLAGS:", "").strip()
                    if val:
                        flag_lines.append(val)
                elif section == "result":
                    result_lines.append(line)
                elif section == "flags":
                    flag_lines.append(line)

            result = "\n".join(result_lines).strip() or raw
            flags  = "\n".join(flag_lines).strip()

        return {"status": status, "result": result, "flags": flags}

    except Exception as e:
        log.error(f"Task execution failed: {e}")
        return {
            "status": "CANNOT_COMPLETE",
            "result": "",
            "flags":  f"Error: {str(e)}",
        }


def process_queue(db) -> list:
    """Process all pending tasks from the database."""
    pending = db.get_pending_tasks()
    if not pending:
        log.info("No pending tasks.")
        return []

    log.info(f"Processing {len(pending)} task(s)...")
    results = []

    for task in pending:
        log.info(f"  Task #{task['id']}: {task['description'][:60]}")
        outcome = execute_task(task["description"])
        db.complete_task(task["id"], outcome["result"])
        results.append({"task_id": task["id"], **outcome})

        if outcome["flags"]:
            log.warning(f"  ⚠️  Needs review: {outcome['flags'][:80]}")
        else:
            log.info(f"  ✅ Done: {outcome['status']}")

    return results
