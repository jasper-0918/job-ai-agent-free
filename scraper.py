# agents/scraper.py
# ─────────────────────────────────────────────────────────
#  Job Scraper — 100% free
#  Uses requests + BeautifulSoup (no paid API needed)
#  Sources: Indeed PH, Jobstreet PH, OnlineJobs.ph
# ─────────────────────────────────────────────────────────

import time
import re
import logging
from urllib.parse import quote_plus

import requests
from bs4 import BeautifulSoup

from config import SEARCH_KEYWORDS

log = logging.getLogger("scraper")

DELAY = 2.5   # seconds between requests — be polite to servers
MAX_PER_KEYWORD = 10   # max jobs to grab per keyword per site

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}


def _get(url: str) -> BeautifulSoup | None:
    """Fetch a URL and return parsed HTML. Returns None on failure."""
    try:
        time.sleep(DELAY)
        r = requests.get(url, headers=HEADERS, timeout=15)
        r.raise_for_status()
        return BeautifulSoup(r.text, "html.parser")
    except Exception as e:
        log.warning(f"  GET failed: {url[:60]} — {e}")
        return None


def _extract_email(text: str) -> str | None:
    """Find an email address in job text."""
    match = re.search(
        r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}", text
    )
    return match.group(0) if match else None


def _matched_keywords(text: str) -> list:
    text_l = text.lower()
    return [kw for kw in SEARCH_KEYWORDS if kw.lower() in text_l]


# ── Indeed PH ─────────────────────────────────────────────

def scrape_indeed(keyword: str) -> list:
    jobs = []
    url = (
        f"https://ph.indeed.com/jobs"
        f"?q={quote_plus(keyword)}"
        f"&remotejob=032b3046-06a2-4a6e-9930-bf5c748afa2b"
    )
    soup = _get(url)
    if not soup:
        return jobs

    cards = soup.select("div.job_seen_beacon")

    for card in cards[:MAX_PER_KEYWORD]:
        try:
            title_el = card.select_one("h2.jobTitle a")
            if not title_el:
                continue

            title = title_el.get_text(strip=True)
            jk    = title_el.get("data-jk", "")
            url   = f"https://ph.indeed.com/viewjob?jk={jk}" if jk else ""

            company_el = card.select_one("[class*='companyName']")
            company    = company_el.get_text(strip=True) if company_el else "Unknown"

            snippet_el = card.select_one("[class*='summary']")
            desc       = snippet_el.get_text(strip=True) if snippet_el else ""

            jobs.append({
                "title":            title,
                "company":          company,
                "platform":         "Indeed PH",
                "url":              url,
                "apply_email":      _extract_email(desc),
                "description":      desc,
                "salary_info":      "",
                "keywords_matched": _matched_keywords(title + " " + desc),
            })
        except Exception:
            continue

    return jobs


# ── Jobstreet PH ──────────────────────────────────────────

def scrape_jobstreet(keyword: str) -> list:
    jobs = []
    url = (
        f"https://ph.jobstreet.com/jobs"
        f"?q={quote_plus(keyword)}"
        f"&location=Philippines&worktype=remote"
    )
    soup = _get(url)
    if not soup:
        return jobs

    cards = soup.select("article[data-job-id], [data-automation='job-card']")

    for card in cards[:MAX_PER_KEYWORD]:
        try:
            title_el = card.select_one(
                "[data-automation='job-card-title'] a, h3 a, h2 a"
            )
            if not title_el:
                continue

            title = title_el.get_text(strip=True)
            href  = title_el.get("href", "")
            job_url = (
                href if href.startswith("http")
                else "https://ph.jobstreet.com" + href
            )

            company_el = card.select_one(
                "[data-automation='job-card-company'], [class*='company']"
            )
            company = company_el.get_text(strip=True) if company_el else "Unknown"

            jobs.append({
                "title":            title,
                "company":          company,
                "platform":         "Jobstreet PH",
                "url":              job_url,
                "apply_email":      None,
                "description":      "",
                "salary_info":      "",
                "keywords_matched": _matched_keywords(title),
            })
        except Exception:
            continue

    return jobs


# ── OnlineJobs.ph ─────────────────────────────────────────

def scrape_onlinejobs(keyword: str) -> list:
    jobs = []
    url = (
        f"https://www.onlinejobs.ph/jobseekers/jobsearch"
        f"?q={quote_plus(keyword)}"
    )
    soup = _get(url)
    if not soup:
        return jobs

    cards = soup.select(".job-post, article.post, [class*='jobpost']")

    for card in cards[:MAX_PER_KEYWORD]:
        try:
            title_el = card.select_one("h2 a, h3 a, .job-title a")
            if not title_el:
                continue

            title = title_el.get_text(strip=True)
            href  = title_el.get("href", "")
            job_url = (
                href if href.startswith("http")
                else "https://www.onlinejobs.ph" + href
            )

            company_el = card.select_one("[class*='company'], [class*='employer']")
            company    = company_el.get_text(strip=True) if company_el else "Private Employer"

            desc_el = card.select_one("[class*='description'], [class*='summary']")
            desc    = desc_el.get_text(strip=True) if desc_el else ""

            jobs.append({
                "title":            title,
                "company":          company,
                "platform":         "OnlineJobs.ph",
                "url":              job_url,
                "apply_email":      _extract_email(desc),
                "description":      desc,
                "salary_info":      "",
                "keywords_matched": _matched_keywords(title + " " + desc),
            })
        except Exception:
            continue

    return jobs


# ── Main scrape function ───────────────────────────────────

def scrape_all() -> list:
    """
    Scrape all platforms for all keywords.
    Returns deduplicated list of job dicts.
    """
    all_jobs = []
    seen     = set()

    log.info(f"Scraping {len(SEARCH_KEYWORDS)} keywords across 3 platforms...")

    for keyword in SEARCH_KEYWORDS:
        log.info(f"  Searching: '{keyword}'")

        batch = (
            scrape_indeed(keyword)    +
            scrape_jobstreet(keyword) +
            scrape_onlinejobs(keyword)
        )

        for job in batch:
            uid = f"{job['title'].lower().strip()}|{job['company'].lower().strip()}"
            if uid not in seen and job["title"].strip():
                seen.add(uid)
                all_jobs.append(job)

    log.info(f"Scrape done. {len(all_jobs)} unique jobs collected.")
    return all_jobs
