# 🤖 Job AI Agent — Free Version

> An autonomous job hunting assistant that finds listings, detects scams, writes cover letters, sends applications, and monitors your inbox — **using only free tools, no credit card required.**

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)
![Groq](https://img.shields.io/badge/AI-Groq%20%28Free%29-F55036)
![Gmail](https://img.shields.io/badge/Email-Gmail%20%28Free%29-EA4335?logo=gmail)
![SQLite](https://img.shields.io/badge/Database-SQLite-003B57?logo=sqlite)
![FastAPI](https://img.shields.io/badge/API-FastAPI-009688?logo=fastapi)
![License](https://img.shields.io/badge/License-MIT-purple)

---

## 💸 Cost: Completely Free

| Tool | What it does | Cost |
|---|---|---|
| **Groq API** | AI brain — evaluates jobs, writes cover letters, completes tasks | Free |
| **LLaMA 3 (via Groq)** | The actual AI model running the decisions | Free |
| **Gmail** | Sends applications + reads your inbox | Free |
| **Python** | Core language | Free |
| **SQLite** | Stores all jobs, applications, and responses | Free |
| **FastAPI** | Powers the web dashboard | Free |
| **BeautifulSoup** | Scrapes job sites | Free |

> **Why Groq instead of OpenAI?**
> Groq offers a **completely free tier** with no credit card required, running LLaMA 3 models at extremely high speed. OpenAI, Anthropic, and Google Gemini all require a credit card before you can use them.

---

## ✨ What It Does

- Scrapes **Indeed PH**, **Jobstreet PH**, and **OnlineJobs.ph** automatically
- **AI evaluates** each job: scores 0–100, detects scams, decides AUTO_APPLY / ASK_USER / REJECT
- **Writes a personalized cover letter** for each job using your actual background
- **Sends the email application** with your CV attached automatically
- **Flags jobs** that need your approval before applying
- **Scans your Gmail inbox** for interview invites, assessments, and rejections
- **Worker Agent** — type a task in plain English, AI completes it for you
- **Web dashboard** at `http://localhost:8000` — review everything in a browser

---

## 📁 Project Structure

```
job-ai-agent-free/
│
├── main.py              ← Run commands here (START HERE)
├── config.py            ← YOUR profile, skills, job preferences (EDIT THIS)
├── requirements.txt     ← Python packages to install
├── .env.example         ← Template for your API keys (COPY TO .env)
│
├── agents/
│   ├── scraper.py       ← Scrapes Indeed, Jobstreet, OnlineJobs.ph
│   ├── decision.py      ← AI job evaluator + scam detector (uses Groq)
│   ├── cover_letter.py  ← AI cover letter writer (uses Groq)
│   ├── apply.py         ← Gmail SMTP email sender
│   ├── inbox.py         ← Gmail IMAP inbox scanner
│   └── worker.py        ← Task delegation agent (your digital clone)
│
├── api/
│   └── app.py           ← FastAPI backend for the dashboard
│
├── db/
│   └── database.py      ← SQLite database (stores everything)
│
├── frontend/
│   └── index.html       ← Web dashboard UI
│
├── assets/              ← PUT YOUR CV PDF HERE
└── logs/                ← Application logs
```

---

## 🛠️ Installation — Step by Step

### Step 1 — Make sure Python is installed

Open a terminal (Command Prompt on Windows, Terminal on Mac/Linux) and type:

```bash
python --version
```

You should see something like `Python 3.11.x`. If you get an error, download Python from [python.org](https://www.python.org/downloads/) — install version 3.10 or higher.

---

### Step 2 — Download the project

```bash
git clone https://github.com/jasper-john-paitan/job-ai-agent-free.git
cd job-ai-agent-free
```

If you don't have Git, just download the ZIP from GitHub and extract it. Then open a terminal inside that folder.

---

### Step 3 — Install Python packages

```bash
pip install -r requirements.txt
```

This installs everything the bot needs. It takes 1–2 minutes.

> **If you get a "pip not found" error**, try: `python -m pip install -r requirements.txt`

---

### Step 4 — Get your FREE Groq API key

This is the AI brain of the bot. It is completely free — no credit card.

1. Go to **[console.groq.com](https://console.groq.com)**
2. Click **Sign Up** — you can use your Google account
3. Once logged in, click **API Keys** in the left sidebar
4. Click **Create API Key**
5. Give it a name (e.g. "job-agent") and click **Submit**
6. **Copy the key** — it starts with `gsk_...`

Keep this key — you will paste it in the next step.

---

### Step 5 — Set up your Gmail App Password

This lets the bot send emails from your Gmail without using your real password.

**First, enable 2-Step Verification (required):**
1. Go to [myaccount.google.com/security](https://myaccount.google.com/security)
2. Under "How you sign in to Google", click **2-Step Verification**
3. Follow the steps to turn it on

**Then, create an App Password:**
1. Go to [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)
2. In the "App name" box, type: `job-agent`
3. Click **Create**
4. Google shows a **16-character code** like `abcd efgh ijkl mnop`
5. **Copy this code** — you will paste it in the next step

**Enable IMAP (so the bot can read your inbox):**
1. Open Gmail
2. Click the gear icon (⚙️) → **See all settings**
3. Click the **Forwarding and POP/IMAP** tab
4. Under "IMAP access", select **Enable IMAP**
5. Click **Save Changes**

---

### Step 6 — Create your `.env` file

In the project folder, copy the example file:

```bash
# On Windows:
copy .env.example .env

# On Mac/Linux:
cp .env.example .env
```

Now open `.env` with any text editor (Notepad, VS Code, etc.) and fill in your values:

```env
GROQ_API_KEY=gsk_your_key_here          ← paste your Groq key from Step 4
GMAIL_ADDRESS=yourname@gmail.com         ← your Gmail address
GMAIL_APP_PASSWORD=abcdefghijklmnop      ← paste App Password from Step 5 (no spaces)
CV_PATH=./assets/Jasper_John_Paitan_CV.pdf  ← update to your CV filename
```

Save the file.

---

### Step 7 — Add your CV

Copy your CV PDF file into the `assets/` folder.

Then open `.env` and update `CV_PATH` to match your filename:

```env
CV_PATH=./assets/YourName_CV.pdf
```

---

### Step 8 — Edit your profile in `config.py`

Open `config.py` in VS Code or any editor. This file is pre-filled with Jasper's info — **update it to match your own details**.

**What to change:**

```python
USER_PROFILE = {
    "name":     "Your Full Name",          ← CHANGE
    "email":    "your@email.com",          ← CHANGE
    "phone":    "+63 XXX XXX XXXX",        ← CHANGE
    "location": "Your City, Philippines",  ← CHANGE

    "education": "Your degree and school", ← CHANGE

    "experience": [
        "Your job title at Company (dates): brief description"  ← CHANGE
    ],

    "skills": [
        "python", "automation", ...        ← ADD or REMOVE your actual skills
    ],

    "preferred_roles": [
        "virtual assistant", ...           ← ADD roles you want
    ],

    "min_hourly_usd":   3,    ← minimum salary per hour (USD)
    "min_monthly_php":  15000, ← minimum salary per month (PHP)
}
```

**Also check the thresholds at the bottom of `config.py`:**

```python
SCORE_AUTO_APPLY  = 75   # ← Bot auto-applies if score >= this (lower = applies to more jobs)
SCORE_ASK_USER    = 45   # ← Bot asks you if score is between 45-74
MAX_AUTO_APPLIES_PER_DAY = 10   # ← Safety limit per day
```

---

## ▶️ Running the Bot

### Option A — Web Dashboard (Easiest — Recommended)

```bash
python main.py server
```

Your browser opens automatically at **http://localhost:8000**

Use the dashboard to:
- Click **Scrape Jobs** to find new listings
- Review job scores and AI decisions
- Approve applications in the Auto-Apply Queue
- Check inbox responses
- Delegate tasks to the Worker Agent

---

### Option B — Command Line

```bash
# Find and evaluate new jobs from all platforms
python main.py scrape

# Send applications to eligible jobs
python main.py apply

# Scan your Gmail for interview invites and responses
python main.py inbox

# Process your Worker Agent task queue
python main.py worker

# Print a summary of your stats
python main.py dashboard

# Run everything in order (recommended for daily use)
python main.py run
```

---

## ⚙️ How the AI Decides Whether to Apply

Every job goes through this process:

```
Job found by scraper
        │
        ▼
Stage 1: Scam keyword check (instant, free)
  ├── Contains "pay to apply", "Telegram only", "MLM" etc.?
  │       └──▶ REJECT immediately
  │
  ▼
Stage 2: Groq AI evaluation (free API call)
  ├── Reads title, description, your profile
  ├── Returns score 0–100 + scam rating + reasoning
  │
  ▼
Stage 3: Action decision
  ├── Score 75–100  →  AUTO_APPLY   (bot sends email + CV)
  ├── Score 45–74   →  ASK_USER     (you approve in dashboard)
  ├── Score < 45    →  IGNORE       (not relevant)
  └── Scam = yes    →  REJECT       (logged, discarded)
```

---

## 🤖 Worker Agent — Your Digital Clone

In the dashboard, go to the **Worker Agent** tab and type any task. The AI completes it using your background and writing style.

**Example tasks to try:**

```
Write a follow-up email to CargoBoss. I applied 5 days ago and haven't heard back.

Summarize this job post and tell me if I should apply:
[paste the job description here]

Draft a reply to this interview invitation:
[paste the email here]

List 5 questions I should prepare for a virtual assistant interview.

Write a LinkedIn message to introduce myself to a hiring manager at a BPO company.
```

---

## 🌐 Dashboard Tabs

| Tab | What it shows |
|---|---|
| **Dashboard** | Stats: total found, applied, scams caught, interviews |
| **Job Listings** | All scraped jobs with filters (score, decision, status) |
| **Auto-Apply Queue** | Jobs AI wants to apply to — review and approve |
| **Inbox Responses** | Classified emails: interviews, assessments, rejections |
| **Worker Agent** | Type a task, AI completes it |
| **Add Job Manually** | Paste a job post you found — AI evaluates instantly |

---

## 🔧 What Each File Does and What to Change

| File | What it does | What you need to change |
|---|---|---|
| `.env` | Stores your private keys | Fill in ALL 4 values before running |
| `config.py` | Your profile and preferences | Update name, skills, experience, thresholds |
| `agents/decision.py` | AI evaluates jobs via Groq | Nothing — reads from config.py automatically |
| `agents/cover_letter.py` | AI writes cover letters via Groq | Nothing — reads from config.py automatically |
| `agents/scraper.py` | Scrapes job sites | Nothing unless site structure changes |
| `agents/apply.py` | Sends emails with CV via Gmail | Nothing — reads from .env automatically |
| `agents/inbox.py` | Reads Gmail for responses | Nothing — reads from .env automatically |
| `agents/worker.py` | Completes delegated tasks | Nothing — reads from config.py automatically |
| `main.py` | Entry point for all commands | Nothing — do not edit this |
| `db/database.py` | Stores everything in SQLite | Nothing |
| `api/app.py` | Backend for the dashboard | Nothing |
| `frontend/index.html` | The web dashboard UI | Nothing |

---

## 🚨 Troubleshooting

### "GROQ_API_KEY not set" or "get your free key"

Your `.env` file is missing or still has the placeholder text. Open `.env` and replace `your_groq_api_key_here` with your actual key from console.groq.com.

### "Gmail authentication failed"

Three possible causes:
1. You used your real Gmail password instead of an App Password
2. The App Password has spaces in `.env` — remove them: `abcdefghijklmnop` not `abcd efgh ijkl mnop`
3. IMAP is not enabled in Gmail — go to Gmail → Settings → Forwarding and POP/IMAP → Enable IMAP

### "No jobs found after scraping"

Job sites occasionally change their HTML. When this happens, the scraper finds nothing until the CSS selectors are updated. In the meantime, use **Add Job Manually** in the dashboard to paste jobs you find yourself.

### AI returns IGNORE for every job

Lower the threshold in `config.py`:
```python
SCORE_ASK_USER = 35   # try a lower number
```
Also make sure your `skills` list in `config.py` actually matches keywords in the job posts you are targeting.

### "Daily limit reached"

The bot sent the maximum allowed emails for today. This resets tomorrow. To increase it, change `MAX_AUTO_APPLIES_PER_DAY` in `config.py` — but keep it reasonable (under 20) to avoid your Gmail flagging outgoing mail as spam.

### "Module not found" error

Run the install command again:
```bash
pip install -r requirements.txt
```

---

## ⚠️ Strengths

- **Completely free** — zero ongoing cost, no subscription, no credit card
- **Fast AI** — Groq runs LLaMA 3 at extremely high speed (usually under 1 second per job)
- **Scam detection** — catches common Philippine online job scams automatically
- **Personalized applications** — every cover letter is written for that specific job
- **Full control** — you approve all ambiguous applications, nothing is sent blindly
- **Offline fallback** — if the Groq API is down, rule-based scoring takes over automatically
- **No rate limit anxiety** — Groq's free tier is generous enough for daily job hunting

## ⚠️ Limitations

- **Groq free tier limits** — the free tier has token limits per minute and per day. Heavy usage (200+ jobs per day) may hit rate limits and slow down. For typical job hunting (50–100 jobs/day), you will never hit the limit.
- **Scraping can break** — job sites change their HTML periodically. The bot will stop finding jobs until selectors are updated manually.
- **Email-only auto-apply** — only works when a job post has a direct email address. Portal-based jobs (Workday, Greenhouse, company websites) always require manual application.
- **No LinkedIn scraping** — LinkedIn actively blocks scrapers. OnlineJobs.ph and Jobstreet are the best free sources.
- **Gmail required** — the email system only works with Gmail. Outlook, Yahoo, and other providers are not supported.

---

## 🔒 Security Reminder

**Never share or upload these files:**
- `.env` — contains your API key and Gmail App Password
- `job_agent.db` — contains your personal application history
- `assets/` — contains your CV

These are all excluded from Git via `.gitignore`. Do not remove the gitignore entries.

---

## 💡 Daily Workflow Recommendation

**Morning (5 minutes):**
```bash
python main.py run
```
This scrapes new jobs, sends auto-apply emails, checks inbox, and shows your stats.

**Then:**
- Open `http://localhost:8000` to review any jobs flagged as ASK_USER
- Approve or skip them with one click

**When you find a job manually (Facebook group, referral, etc.):**
- Go to dashboard → Add Job Manually
- Paste the job description → AI evaluates and scores it instantly
- If good → click Apply directly from the dashboard

---

## 📄 License

MIT — free to use and modify.

---

## 👤 Author

**Jasper John C. Paitan**
Computer Engineering Graduate — La Salle University Ozamiz
[LinkedIn](https://www.linkedin.com/in/jasper-john-paitan-11641337b) · [Credly](https://www.credly.com/users/jasper-john-paitan)
