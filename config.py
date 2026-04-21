# config.py
# ─────────────────────────────────────────────────────────
#  YOUR PERSONAL PROFILE
#  Edit the values below to match your info.
#  The AI uses everything here to evaluate jobs
#  and write your cover letters.
# ─────────────────────────────────────────────────────────

USER_PROFILE = {
    # ── Personal Info ──────────────────────────────────
    # CHANGE THESE to your actual info
    "name":       "Your Full Name",
    "email":      "your.email@gmail.com",
    "phone":      "+63 XXX XXX XXXX",
    "location":   "Your City, Philippines",
    "linkedin":   "linkedin.com/in/your-profile",

    # ── Your Background ────────────────────────────────
    # CHANGE these to match your actual experience
    "education": (
        "Your Degree, Your University (Year–Year)"
    ),
    "experience": [
        "Job Title at Company (dates): brief description of what you did."
    ],
    "projects": [
        "Project Name — brief description of what it does",
        "Another Project — brief description",
    ],
    "certifications": [
        "Your Certification Name (Month Year)",
    ],

    # ── Skills ─────────────────────────────────────────
    # ADD or REMOVE skills that match your actual abilities
    "skills": [
        "python", "automation", "data entry", "virtual assistant",
        "email management", "scheduling", "customer service",
        "google workspace", "microsoft office", "research",
        "social media management", "technical support",
    ],

    # ── Job Preferences ────────────────────────────────
    # ADD roles you are willing to do
    "preferred_roles": [
        "virtual assistant", "va", "admin assistant",
        "customer service representative", "csr",
        "data entry", "non voice", "work from home",
        "remote", "technical support", "it support",
    ],

    # CHANGE salary minimums to your preference
    "min_hourly_usd":   3,       # minimum $3/hr USD
    "min_monthly_php":  15000,   # minimum ₱15,000/month

    # ── Writing Style ──────────────────────────────────
    # Describes how your cover letters will sound
    "tone": "professional but personable, confident without being arrogant",
}

# ─────────────────────────────────────────────────────────
#  DECISION THRESHOLDS
#  Adjust these to control how aggressively the bot applies
# ─────────────────────────────────────────────────────────
SCORE_AUTO_APPLY  = 75   # score >= this → bot applies automatically
SCORE_ASK_USER    = 45   # score >= this → bot asks you first
MAX_AUTO_APPLIES_PER_DAY = 10   # max emails sent per day (safety limit)
DELAY_BETWEEN_APPLIES_SEC = 45  # wait between each email send

# ─────────────────────────────────────────────────────────
#  SCAM DETECTION KEYWORDS
#  If any of these appear in a job post → flagged as scam
# ─────────────────────────────────────────────────────────
SCAM_KEYWORDS = [
    "pay to apply", "registration fee", "training fee",
    "send money", "wire transfer", "western union",
    "deposit required", "investment required",
    "telegram only", "whatsapp only",
    "earn $500 daily", "earn $1000 daily", "easy $",
    "get rich", "unlimited earnings",
    "mlm", "network marketing", "downline",
    "bitcoin", "crypto investment",
    "no experience $50/hr", "no experience $100",
]

# ─────────────────────────────────────────────────────────
#  SEARCH KEYWORDS
#  What the scraper will search for on job sites
#  ADD keywords for roles you want to target
# ─────────────────────────────────────────────────────────
SEARCH_KEYWORDS = [
    "virtual assistant fresh graduate",
    "VA no experience Philippines",
    "non voice CSR work from home",
    "customer service representative WFH",
    "technical support fresh graduate",
    "data entry no experience",
    "admin assistant remote Philippines",
    "AI assistant remote",
]

# ─────────────────────────────────────────────────────────
#  GROQ MODEL SETTINGS
#  llama-3.1-8b-instant — fast, free, good for short tasks
#  llama-3.3-70b-versatile — smarter, still free, slightly slower
# ─────────────────────────────────────────────────────────
GROQ_MODEL_FAST  = "llama-3.1-8b-instant"    # for cover letters (speed)
GROQ_MODEL_SMART = "llama-3.3-70b-versatile"  # for job evaluation (accuracy)
