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
    "name":       "Jasper John C. Paitan",
    "email":      "jasperjohn.paitan@lsu.edu.ph",
    "phone":      "+63 949 407 9802",
    "location":   "Ozamiz City, Misamis Occidental, Philippines",
    "linkedin":   "linkedin.com/in/jasper-john-paitan-11641337b",

    # ── Your Background ────────────────────────────────
    # CHANGE these to match your actual experience
    "education": (
        "Bachelor of Science in Computer Engineering, "
        "La Salle University – Ozamiz (2022–present)"
    ),
    "experience": [
        "Software Development Intern at Benpos Systems (Feb–Apr 2026): "
        "maintained system software, resolved defects, coordinated client deployments."
    ],
    "projects": [
        "Automatic Plastic Bottle Segregation System — "
        "TensorFlow + Edge Impulse real-time image classifier (Thesis 2025)",
        "AI Document Organizer — Python + HuggingFace Transformers + OpenCV",
        "Job AI Agent — Autonomous job hunting assistant (this project)",
    ],
    "certifications": [
        "Google Cloud Cybersecurity Certificate (Feb 2026)",
        "Cisco Junior Cybersecurity Analyst (Mar 2026)",
        "Machining NC II – TESDA",
    ],

    # ── Skills ─────────────────────────────────────────
    # ADD or REMOVE skills that match your actual abilities
    "skills": [
        "python", "automation", "cybersecurity", "machine learning",
        "tensorflow", "edge impulse", "opencv", "sql", "c", "c++",
        "javascript", "data analysis", "git", "linux",
        "virtual assistant", "technical support", "data entry",
        "ai", "fastapi", "sqlite",
    ],

    # ── Job Preferences ────────────────────────────────
    # ADD roles you are willing to do
    "preferred_roles": [
        "virtual assistant", "va", "python developer",
        "automation", "technical support", "data analyst",
        "cybersecurity analyst trainee", "it support",
        "ai automation assistant", "customer service representative",
        "csr", "non voice", "data entry", "software developer",
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
    "python developer entry level",
    "data entry no experience",
    "IT support fresh graduate",
    "cybersecurity analyst trainee",
    "AI assistant remote",
]

# ─────────────────────────────────────────────────────────
#  GROQ MODEL SETTINGS
#  llama-3.1-8b-instant — fast, free, good for short tasks
#  llama-3.3-70b-versatile — smarter, still free, slightly slower
# ─────────────────────────────────────────────────────────
GROQ_MODEL_FAST  = "llama-3.1-8b-instant"    # for cover letters (speed)
GROQ_MODEL_SMART = "llama-3.3-70b-versatile"  # for job evaluation (accuracy)
