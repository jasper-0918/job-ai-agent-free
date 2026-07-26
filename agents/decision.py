# agents/decision.py
# ─────────────────────────────────────────────────────────
#  Job Evaluator + Scam Detector
#  Uses Groq (free) instead of paid APIs
# ─────────────────────────────────────────────────────────

import os
import json
import re
import time
import logging
from concurrent.futures import ThreadPoolExecutor
from groq import Groq
from config import (
    USER_PROFILE, SCAM_KEYWORDS,
    SCORE_AUTO_APPLY, SCORE_ASK_USER,
    GROQ_MODEL_SMART,
    EVAL_BATCH_SIZE, EVAL_MAX_WORKERS,
)

log = logging.getLogger("decision")

# Groq client (loaded once)
_client = None

def _get_client() -> Groq:
    global _client
    if _client is None:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key or api_key == "your_groq_api_key_here":
            raise ValueError(
                "GROQ_API_KEY not set.\n"
                "Get your FREE key at: https://console.groq.com\n"
                "Then add it to your .env file."
            )
        _client = Groq(api_key=api_key)
    return _client


# ── Stage 1: Fast rule-based scam check ──────────────────

def quick_scam_check(job: dict) -> bool:
    """
    Check job text against known scam keywords.
    Returns True if it is clearly a scam.
    No API call — instant.
    """
    text = (
        job.get("title", "") + " " +
        job.get("description", "") + " " +
        job.get("company", "")
    ).lower()

    for kw in SCAM_KEYWORDS:
        if kw.lower() in text:
            log.info(f"  [SCAM RULE] '{kw}' — {job['title'][:50]}")
            return True
    return False


# ── Stage 2: AI evaluation via Groq ──────────────────────

def evaluate_job(job: dict) -> dict:
    """
    Send job to Groq/LLaMA for evaluation.
    Returns: { score, scam, decision, reason }

    decision values:
      AUTO_APPLY  — strong match, bot can apply automatically
      ASK_USER    — decent match, ask human first
      REJECT      — scam or completely irrelevant
      IGNORE      — not relevant enough
    """
    # Fast check first — save API calls for real evaluation
    if quick_scam_check(job):
        return {
            "score":    0,
            "scam":     "yes",
            "decision": "REJECT",
            "reason":   "Matched scam keyword filter."
        }

    prompt = f"""You are a job evaluator for a Filipino job seeker.

CANDIDATE:
Name: {USER_PROFILE['name']}
Education: {USER_PROFILE['education']}
Skills: {', '.join(USER_PROFILE['skills'])}
Preferred roles: {', '.join(USER_PROFILE['preferred_roles'])}
Minimum salary: ${USER_PROFILE['min_hourly_usd']}/hr or PHP {USER_PROFILE['min_monthly_php']}/month
Experience: {'; '.join(USER_PROFILE['experience'])}

JOB:
Title: {job.get('title', 'N/A')}
Company: {job.get('company', 'Unknown')}
Platform: {job.get('platform', 'N/A')}
Salary: {job.get('salary_info', 'Not specified')}
Apply email: {job.get('apply_email', 'None')}
Description: {job.get('description', 'No description')[:600]}

SCAM RED FLAGS TO DETECT:
- Requires payment to apply
- Unrealistic salary for easy work
- Only contact via Telegram or WhatsApp
- No company name or website
- MLM / network marketing
- Vague description with no real tasks listed

EVALUATE and respond ONLY in this exact JSON format, no extra text:
{{
  "score": 72,
  "scam": "no",
  "decision": "ASK_USER",
  "reason": "Good match for VA role but description is vague about actual tasks."
}}

score: 0-100 (how well does this match the candidate?)
scam: "yes" / "no" / "suspicious"
decision: "AUTO_APPLY" / "ASK_USER" / "REJECT" / "IGNORE"
reason: one sentence explaining your decision"""

    try:
        client = _get_client()
        response = client.chat.completions.create(
            model=GROQ_MODEL_SMART,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=200,
        )

        raw = response.choices[0].message.content.strip()

        # Strip markdown code blocks if model wrapped it
        raw = re.sub(r"```json\s*", "", raw)
        raw = re.sub(r"```\s*", "", raw)

        # Extract JSON even if there's extra text around it
        json_match = re.search(r"\{.*?\}", raw, re.DOTALL)
        if json_match:
            raw = json_match.group(0)

        data = json.loads(raw)

        return {
            "score":    max(0, min(100, int(data.get("score", 0)))),
            "scam":     str(data.get("scam", "unknown")),
            "decision": str(data.get("decision", "IGNORE")),
            "reason":   str(data.get("reason", ""))[:200],
        }

    except json.JSONDecodeError:
        log.warning(f"JSON parse failed for '{job.get('title', '')}' — using fallback")
        return _fallback_score(job)
    except Exception as e:
        log.error(f"Groq API error: {e}")
        return _fallback_score(job)


# ── Batched evaluation (fast path) ───────────────────────

def _normalize(data: dict) -> dict:
    return {
        "score":    max(0, min(100, int(data.get("score", 0)))),
        "scam":     str(data.get("scam", "unknown")),
        "decision": str(data.get("decision", "IGNORE")),
        "reason":   str(data.get("reason", ""))[:200],
    }


def _candidate_block() -> str:
    return (
        f"Name: {USER_PROFILE['name']}\n"
        f"Education: {USER_PROFILE['education']}\n"
        f"Skills: {', '.join(USER_PROFILE['skills'])}\n"
        f"Preferred roles: {', '.join(USER_PROFILE['preferred_roles'])}\n"
        f"Minimum salary: ${USER_PROFILE['min_hourly_usd']}/hr "
        f"or PHP {USER_PROFILE['min_monthly_php']}/month\n"
        f"Experience: {'; '.join(USER_PROFILE['experience'])}"
    )


def _batch_prompt(chunk: list) -> str:
    job_blocks = []
    for n, job in enumerate(chunk, 1):
        job_blocks.append(
            f"JOB {n}:\n"
            f"Title: {job.get('title', 'N/A')}\n"
            f"Company: {job.get('company', 'Unknown')}\n"
            f"Platform: {job.get('platform', 'N/A')}\n"
            f"Salary: {job.get('salary_info', 'Not specified')}\n"
            f"Apply email: {job.get('apply_email', 'None')}\n"
            f"Description: {job.get('description', 'No description')[:400]}"
        )
    return f"""You are a job evaluator for a Filipino job seeker.

CANDIDATE:
{_candidate_block()}

{chr(10).join(job_blocks)}

SCAM RED FLAGS TO DETECT:
- Requires payment to apply
- Unrealistic salary for easy work
- Only contact via Telegram or WhatsApp
- No company name or website
- MLM / network marketing
- Vague description with no real tasks listed

Evaluate EVERY job independently. Respond ONLY with a JSON array,
one object per job in the same order, no extra text:
[
  {{"id": 1, "score": 72, "scam": "no", "decision": "ASK_USER", "reason": "one sentence"}},
  {{"id": 2, ...}}
]

score: 0-100 (match to the candidate)
scam: "yes" / "no" / "suspicious"
decision: "AUTO_APPLY" / "ASK_USER" / "REJECT" / "IGNORE"
The array must contain exactly {len(chunk)} objects."""


def _extract_json_array(raw: str) -> list:
    raw = re.sub(r"```json\s*", "", raw)
    raw = re.sub(r"```\s*", "", raw)
    match = re.search(r"\[.*\]", raw, re.DOTALL)
    if not match:
        raise json.JSONDecodeError("no JSON array found", raw, 0)
    return json.loads(match.group(0))


def _call_with_backoff(prompt: str, max_tokens: int, attempts: int = 3) -> str:
    """One Groq call with retry on rate limits (free tier throttles)."""
    client = _get_client()
    for attempt in range(attempts):
        try:
            response = client.chat.completions.create(
                model=GROQ_MODEL_SMART,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                max_tokens=max_tokens,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            msg = str(e).lower()
            retriable = "429" in msg or "rate limit" in msg or "rate_limit" in msg
            if not retriable or attempt == attempts - 1:
                raise
            wait = 2 ** (attempt + 1)
            log.warning(f"Rate limited, retrying in {wait}s...")
            time.sleep(wait)


def _evaluate_chunk(chunk: list) -> list:
    """Evaluate one chunk of jobs in a single LLM call.
    Falls back to per-job evaluation if the batch response is unusable."""
    try:
        raw = _call_with_backoff(_batch_prompt(chunk), max_tokens=120 * len(chunk))
        items = _extract_json_array(raw)
        if len(items) != len(chunk):
            raise ValueError(f"expected {len(chunk)} results, got {len(items)}")
        return [_normalize(item) for item in items]
    except Exception as e:
        log.warning(f"Batch of {len(chunk)} failed ({e}) — falling back to per-job")
        return [evaluate_job(job) for job in chunk]


def evaluate_jobs_batch(jobs: list) -> list:
    """
    Evaluate many jobs fast: local scam filter first, then batched
    LLM calls (EVAL_BATCH_SIZE jobs per call) running concurrently
    (EVAL_MAX_WORKERS calls in flight). Results align with input order.
    """
    if not jobs:
        return []

    results = [None] * len(jobs)
    pending = []
    for i, job in enumerate(jobs):
        if quick_scam_check(job):
            results[i] = {
                "score": 0, "scam": "yes", "decision": "REJECT",
                "reason": "Matched scam keyword filter.",
            }
        else:
            pending.append(i)

    chunks = [pending[i:i + EVAL_BATCH_SIZE]
              for i in range(0, len(pending), EVAL_BATCH_SIZE)]
    if chunks:
        log.info(f"Evaluating {len(pending)} jobs in {len(chunks)} batched calls "
                 f"({EVAL_MAX_WORKERS} concurrent)")
        with ThreadPoolExecutor(max_workers=EVAL_MAX_WORKERS) as pool:
            for idx_chunk, evals in zip(
                chunks,
                pool.map(lambda c: _evaluate_chunk([jobs[i] for i in c]), chunks),
            ):
                for i, ev in zip(idx_chunk, evals):
                    results[i] = ev

    return results


def _fallback_score(job: dict) -> dict:
    """
    Rule-based scoring used when AI call fails.
    No API needed — runs offline.
    """
    score = 0
    title_desc = (job.get("title", "") + " " + job.get("description", "")).lower()

    for skill in USER_PROFILE["skills"]:
        if skill.lower() in title_desc:
            score += 8

    for role in USER_PROFILE["preferred_roles"]:
        if role.lower() in title_desc:
            score += 12

    score = min(score, 70)  # cap at 70 for rule-based

    decision = "AUTO_APPLY" if score >= SCORE_AUTO_APPLY else \
               "ASK_USER"   if score >= SCORE_ASK_USER   else "IGNORE"

    return {
        "score":    score,
        "scam":     "unknown",
        "decision": decision,
        "reason":   "Scored by keyword matching (AI unavailable).",
    }


# ── Stage 3: Final action decision ───────────────────────

def final_decision(ai_data: dict) -> str:
    """
    Translate AI evaluation into a system action.
    Returns: AUTO_APPLY | ASK_USER | REJECT | IGNORE
    """
    if ai_data.get("scam") == "yes":
        return "REJECT"

    score = ai_data.get("score", 0)
    ai_dec = ai_data.get("decision", "IGNORE")

    if score >= SCORE_AUTO_APPLY and ai_dec == "AUTO_APPLY":
        return "AUTO_APPLY"
    if score >= SCORE_ASK_USER:
        return "ASK_USER"
    if ai_dec == "REJECT":
        return "REJECT"

    return "IGNORE"
