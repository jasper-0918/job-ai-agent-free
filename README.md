# 🤖 Job AI Agent — Free Version (Zero Cost, No Credit Card)

> **The same autonomous job hunting bot — rebuilt entirely with free tools. ₱0 to run.**

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)](https://python.org)
[![AI: Groq Free](https://img.shields.io/badge/AI-Groq%20(Free)-F55036)](https://console.groq.com)
[![Email: Gmail Free](https://img.shields.io/badge/Email-Gmail%20(Free)-EA4335?logo=gmail)](https://gmail.com)
[![License](https://img.shields.io/badge/License-MIT-purple)](LICENSE)

---

## 🎬 Watch It In Action

[![Watch Demo on YouTube](https://img.shields.io/badge/▶%20Watch%20Demo-YouTube-FF0000?logo=youtube&logoColor=white)](https://www.youtube.com/watch?v=YOUR_VIDEO_ID)

> **[▶️ Click here to watch the full demo](https://www.youtube.com/watch?v=YOUR_VIDEO_ID)**
>
> The video shows: scraping job sites → AI scoring every listing → scam detection → personalized cover letter generation → auto-applying via email → inbox scanning → full dashboard walkthrough.



---

## 💸 100% Free — Here's the Proof

| Tool | What it does | Monthly Cost |
|---|---|---|
| **Groq API** | AI brain — evaluates jobs, writes cover letters | **Free** |
| **LLaMA 3 (via Groq)** | The AI model making decisions | **Free** |
| **Gmail** | Sends applications + reads inbox replies | **Free** |
| **Python + SQLite** | Core language + database | **Free** |
| **FastAPI** | Powers the web dashboard | **Free** |
| **BeautifulSoup** | Scrapes job platforms | **Free** |
| **Total** | | **₱0/month** |

> This is the free alternative to [job-bot](https://github.com/jasper-0918/job-bot), which uses the paid Claude AI API. The free version uses Groq's free tier (LLaMA 3) instead. Same features, zero cost.

---

## 😩 The Problem This Solves

Job seekers in the Philippines are spending **2–4 hours every single day**:

- Manually checking Indeed, Jobstreet, and OnlineJobs
- Reading through 50+ listings to find 5 worth applying to
- Falling for scam listings that waste hours of their time
- Writing the same cover letter slightly tweaked for each job
- Forgetting to follow up, losing track of applications

**This bot eliminates all of that — at zero cost.**

---

## ✅ What It Does For You

| Before This Bot | After This Bot |
|---|---|
| Check 3 job sites manually every day | All 3 platforms scraped automatically |
| Scroll through 50+ listings | AI filters to only relevant matches |
| Get fooled by scam listings | Two-layer scam detection on every listing |
| Write cover letters manually | AI writes a unique letter per job |
| Apply to 3–5 jobs per day max | Apply to 10–15 jobs per day automatically |
| Forget to check for replies | Inbox scanner tracks every response |
| No record of applications | Full dashboard with complete history |

---

## 📈 Results

- **Saves 2–4 hours daily** — entire job search runs in under 10 minutes
- **10–15 applications per day** without extra effort from you
- **Scam protection** — catches pay-to-apply schemes, MLM traps, and fake listings
- **Personalized cover letters** for every application, not templates
- **Zero ongoing cost** — runs as many times as you want with no bill

---

## 💼 Who This Is For

This tool is ideal for:

- **Job seekers** applying to multiple remote roles who can't afford paid AI tools
- **Virtual assistants** managing job applications for clients on a tight budget
- **Freelancers** who need a consistent opportunity pipeline without spending money
- **Anyone in the Philippines** tired of wasting hours on job hunting and scam listings

> **You don't need to be a programmer.** Setup takes 15 minutes with the step-by-step guide below.

---

## ⚙️ How It Works — Plain English

```
Every time you run the bot:

1. SCRAPES  →  Finds new jobs on Indeed PH, Jobstreet PH, OnlineJobs.ph
2. FILTERS  →  Free AI reads every listing and scores it 0–100
3. DETECTS  →  Scam checker flags suspicious listings instantly
4. DECIDES  →
              Score 75–100 → Bot applies automatically
              Score 45–74  → Bot asks YOU to approve first
              Score below 45 → Skipped (not relevant)
5. APPLIES  →  Sends your personalized email + CV automatically
6. MONITORS →  Reads Gmail inbox, classifies replies (interview/rejection/assessment)
7. LOGS     →  Everything tracked in a dashboard you can review anytime
```

---

## 🖥️ Web Dashboard

A full browser-based dashboard runs at `http://localhost:8000`:

| Tab | What you see |
|---|---|
| **Dashboard** | Stats: jobs found, applied, scams blocked, interviews received |
| **Job Listings** | All scraped jobs with AI scores and decisions |
| **Review Queue** | Jobs needing your approval before sending |
| **Inbox Responses** | Replies auto-classified as interview / assessment / rejection |
| **Worker Agent** | Type any task in plain English — AI completes it for you |
| **Add Job Manually** | Paste a job you found anywhere — AI evaluates it instantly |

---

## 🤖 Worker Agent — Type a Task, AI Does It

```
"Write a follow-up email to CargoBoss — I applied 5 days ago, no reply yet"
"Summarize this job post and tell me if I should apply: [paste here]"
"Draft a reply to this interview invitation: [paste email here]"
"List 5 questions I should prepare for a virtual assistant interview"
"Write a LinkedIn message introducing me to a BPO hiring manager"
```

---

## 🚀 Setup Guide — Step by Step

### Before you start, you need:
- A computer with Python installed ([download here](https://python.org/downloads) — get version 3.10 or higher)
- A Gmail account
- 15 minutes

---

### Step 1 — Download the project

```bash
git clone https://github.com/jasper-0918/job-ai-agent-free.git
cd job-ai-agent-free
pip install -r requirements.txt
```

> No Git? Download the ZIP from GitHub and extract it. Open a terminal inside the extracted folder.

---

### Step 2 — Get your FREE Groq API key (2 minutes, no credit card)

1. Go to **[console.groq.com](https://console.groq.com)**
2. Sign up with your Google account
3. Click **API Keys** → **Create API Key**
4. Give it a name (e.g. "job-agent") → **Submit**
5. Copy the key — it starts with `gsk_...`

---

### Step 3 — Set up Gmail App Password (5 minutes)

This lets the bot send emails from your Gmail without using your real password.

**Enable 2-Step Verification first (required):**
1. Go to [myaccount.google.com/security](https://myaccount.google.com/security)
2. Click **2-Step Verification** → turn it on

**Create an App Password:**
1. Go to [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)
2. Type "job-agent" in the App name box → **Create**
3. Copy the 16-character code (e.g. `abcdefghijklmnop`)

**Enable Gmail IMAP (so the bot can read replies):**
1. Open Gmail → Settings gear ⚙️ → **See all settings**
2. Click **Forwarding and POP/IMAP** tab
3. Under IMAP Access → **Enable IMAP** → **Save Changes**

---

### Step 4 — Create your `.env` file

```bash
# Windows:
copy .env.example .env

# Mac/Linux:
cp .env.example .env
```

Open `.env` and fill in:

```
GROQ_API_KEY=gsk_your_key_here
GMAIL_ADDRESS=yourname@gmail.com
GMAIL_APP_PASSWORD=abcdefghijklmnop
CV_PATH=./assets/YourName_CV.pdf
```

---

### Step 5 — Add your CV

Copy your CV PDF into the `assets/` folder. Update `CV_PATH` in `.env` to match the filename.

---

### Step 6 — Set up your profile in `config.py`

Open `config.py` and update with your real information:

```python
USER_PROFILE = {
    "name":     "Your Full Name",
    "email":    "your@email.com",
    "skills":   ["virtual assistant", "data entry", "email management", ...],
    "preferred_roles": ["virtual assistant", "admin assistant", ...],
    "min_hourly_usd":  3,
    "min_monthly_php": 15000,
}
```

---

### Step 7 — Run it

```bash
python main.py server
```

Your browser opens at **http://localhost:8000**. Click **Scrape New Jobs** to start.

---

## 📋 Recommended Daily Routine

**Every morning (5 minutes):**
```bash
python main.py run
```
Then open `http://localhost:8000` → review and approve any flagged jobs.

**Found a job on Facebook or from a referral?**
→ Dashboard → **Add Job Manually** → paste the post → instant AI evaluation

---

## 🛡️ Scam Protection (Built-In)

**Layer 1 — Instant keyword scan:**
Catches: "registration fee", "training fee", "earn ₱500/day", "Telegram only", "no experience ₱50/hr", generic gmail.com company addresses, MLM language

**Layer 2 — AI deep review:**
Reads the full job post and flags vague descriptions, suspicious salary claims, missing company details, and unusual requirements — with an explanation in your dashboard.

---

## 📁 Project Structure

```
job-ai-agent-free/
├── agents/
│   ├── scraper.py       ← Scrapes Indeed, Jobstreet, OnlineJobs.ph
│   ├── decision.py      ← AI job evaluator + scam detector (Groq)
│   ├── cover_letter.py  ← AI cover letter writer (Groq)
│   ├── apply.py         ← Gmail SMTP email sender
│   ├── inbox.py         ← Gmail IMAP inbox scanner
│   └── worker.py        ← Task delegation agent (your digital clone)
├── api/
│   └── app.py           ← FastAPI backend for the dashboard
├── db/
│   └── database.py      ← SQLite database (stores everything)
├── frontend/
│   └── index.html       ← Web dashboard UI
├── assets/              ← PUT YOUR CV PDF HERE
├── main.py              ← Entry point for all commands
├── config.py            ← YOUR PROFILE — edit this first
├── setup.py             ← One-click setup script
├── requirements.txt     ← Python packages
└── .env.example         ← Template for your API keys
```

---

## ⚠️ Honest Limitations

- **Groq free tier limits** — for typical job hunting (50–100 jobs/day) you'll never hit the limit. Heavy use (200+/day) may slow down.
- **Email-only applying** — auto-send only works when a job post has a direct email. Portal-based jobs need manual action.
- **Scraping can break** — job sites occasionally change their layout. Use "Add Job Manually" while waiting for a fix.
- **Gmail only** — the email system requires Gmail (not Outlook, Yahoo, etc.)

---

## 🔒 Your Data Stays Private

- `.env` (your API key + Gmail password) — excluded from GitHub automatically
- `job_agent.db` (your application history) — stays on your computer only
- `assets/` (your CV) — never uploaded to GitHub

---

## 📬 Want This Automated for Your Business?

If you have repetitive tasks or workflows that need automation, I can build a custom solution.

I specialize in Python automation for small businesses and VAs — application pipelines, document sorting, inbox management, reporting, and more.

👉 **[Connect on LinkedIn](https://www.linkedin.com/in/jasper-john-paitan-11641337b)**
📧 **jasper.paitan0918@gmail.com**
🏅 **[View Certifications](https://www.credly.com/users/jasper-john-paitan)**

---

## 📄 License

MIT — free to use and modify.
