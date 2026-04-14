# agents/cover_letter.py
# ─────────────────────────────────────────────────────────
#  Cover Letter Generator
#  Uses Groq (free) to write personalized emails per job
# ─────────────────────────────────────────────────────────

import os
import logging
from groq import Groq
from config import USER_PROFILE, GROQ_MODEL_FAST

log = logging.getLogger("cover_letter")

_client = None

def _get_client() -> Groq:
    global _client
    if _client is None:
        _client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    return _client


def generate_cover_letter(job: dict) -> str:
    """
    Generate a personalized email cover letter for a specific job.
    Uses Groq (LLaMA 3) — completely free.
    Falls back to a template if API is unavailable.
    """
    prompt = f"""Write a professional job application email body for the following job.

APPLICANT INFO:
Name: {USER_PROFILE['name']}
Phone: {USER_PROFILE['phone']}
Email: {USER_PROFILE['email']}
Education: {USER_PROFILE['education']}
Experience: {'; '.join(USER_PROFILE['experience'])}
Top skills: {', '.join(USER_PROFILE['skills'][:10])}
Projects: {'; '.join(USER_PROFILE['projects'][:2])}
Certifications: {', '.join(USER_PROFILE['certifications'][:2])}

JOB DETAILS:
Title: {job.get('title', 'N/A')}
Company: {job.get('company', 'the company')}
Description: {job.get('description', '')[:400]}

WRITING RULES:
- Write ONLY the email body text, nothing else
- Start with "Good day," or "Dear Hiring Team,"
- Keep it under 180 words — short and direct
- Highlight 2-3 skills most relevant to THIS specific job
- Mention one specific project or achievement that fits the role
- End with your name, phone, and email on separate lines
- Do NOT write a subject line
- Do NOT say "I am a fresh graduate with no experience"
- Sound confident and genuine, not like a template
- Tone: {USER_PROFILE['tone']}

Write the email body now:"""

    try:
        client = _get_client()
        response = client.chat.completions.create(
            model=GROQ_MODEL_FAST,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=400,
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        log.error(f"Cover letter generation failed: {e}")
        return _fallback_letter(job)


def _fallback_letter(job: dict) -> str:
    """Template fallback if Groq API is unavailable."""
    return f"""Good day, {job.get('company', 'Hiring Team')},

I am Jasper John C. Paitan, a Computer Engineering graduate from La Salle University – Ozamiz and recent software intern at Benpos Systems, where I handled system software updates, defect resolution, and client deployments. I am applying for the {job.get('title', 'position')} role.

I bring hands-on experience in Python automation, AI model development using TensorFlow and HuggingFace Transformers, and cybersecurity fundamentals through my Google Cloud and Cisco certifications. I work independently, communicate clearly in writing, and deliver results without needing to be guided step by step.

My CV is attached for your review.

Respectfully,
{USER_PROFILE['name']}
{USER_PROFILE['phone']}
{USER_PROFILE['email']}"""
