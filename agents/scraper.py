# agents/scraper.py
# ─────────────────────────────────────────────────────────
#  Job Scraper — Fixed for 403 Bot Detection
#
#  WHAT CHANGED:
#  - Indeed & Jobstreet now use Playwright (real browser)
#    instead of requests — this bypasses 403 bot detection
#  - OnlineJobs.ph uses Playwright too
#  - Remotive.com API added as a bonus source (free, no auth)
#  - All sources have graceful fallback on failure
# ─────────────────────────────────────────────────────────

import re
import time
import logging
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import quote_plus

import requests

from config import SEARCH_KEYWORDS

log = logging.getLogger("scraper")

MAX_PER_KEYWORD = 10
DELAY = 1.5


def _extract_email(text: str):
    match = re.search(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}", text)
    return match.group(0) if match else None


def _matched_keywords(text: str) -> list:
    text_l = text.lower()
    return [kw for kw in SEARCH_KEYWORDS if kw.lower() in text_l]


def _make_browser():
    from playwright.sync_api import sync_playwright
    p = sync_playwright().start()
    browser = p.chromium.launch(
        headless=True,
        args=[
            "--no-sandbox",
            "--disable-blink-features=AutomationControlled",
            "--disable-dev-shm-usage",
        ],
    )
    context = browser.new_context(
        user_agent=(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        ),
        viewport={"width": 1280, "height": 800},
        locale="en-US",
        timezone_id="Asia/Manila",
        extra_http_headers={"Accept-Language": "en-US,en;q=0.9"},
    )
    context.add_init_script("""
        Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
        Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3] });
        window.chrome = { runtime: {} };
    """)
    return p, browser, context


def scrape_indeed(keyword: str, context) -> list:
    jobs = []
    url = (
        f"https://ph.indeed.com/jobs"
        f"?q={quote_plus(keyword)}"
        f"&remotejob=032b3046-06a2-4a6e-9930-bf5c748afa2b"
        f"&sort=date"
    )
    try:
        page = context.new_page()
        page.goto(url, wait_until="domcontentloaded", timeout=25000)
        time.sleep(DELAY)
        cards = page.query_selector_all("div.job_seen_beacon")
        log.info(f"    Indeed: {len(cards)} cards for '{keyword[:30]}'")
        for card in cards[:MAX_PER_KEYWORD]:
            try:
                title_el = card.query_selector("h2.jobTitle a, h2 a[data-jk]")
                if not title_el:
                    continue
                title = title_el.inner_text().strip()
                jk = title_el.get_attribute("data-jk") or ""
                job_url = f"https://ph.indeed.com/viewjob?jk={jk}" if jk else ""
                company_el = card.query_selector("[class*='companyName'], [data-testid='company-name']")
                company = company_el.inner_text().strip() if company_el else "Unknown"
                snippet_el = card.query_selector("[class*='summary'], [class*='snippet']")
                desc = snippet_el.inner_text().strip() if snippet_el else ""
                salary_el = card.query_selector("[class*='salary'], [data-testid='attribute_snippet_testid']")
                salary = salary_el.inner_text().strip() if salary_el else ""
                jobs.append({
                    "title": title, "company": company,
                    "platform": "Indeed PH", "url": job_url,
                    "apply_email": _extract_email(desc),
                    "description": desc, "salary_info": salary,
                    "keywords_matched": _matched_keywords(title + " " + desc),
                })
            except Exception:
                continue
        page.close()
    except Exception as e:
        log.warning(f"    Indeed failed '{keyword[:30]}': {type(e).__name__}: {str(e)[:80]}")
    return jobs


def scrape_jobstreet(keyword: str, context) -> list:
    jobs = []
    url = f"https://ph.jobstreet.com/{quote_plus(keyword)}-jobs?sortmode=ListedDate"
    try:
        page = context.new_page()
        page.goto(url, wait_until="domcontentloaded", timeout=25000)
        time.sleep(DELAY)
        try:
            page.wait_for_selector(
                "article[data-job-id], [data-automation='job-card']",
                timeout=8000
            )
        except Exception:
            pass
        cards = page.query_selector_all(
            "article[data-job-id], [data-automation='job-card'], [data-testid='job-card']"
        )
        log.info(f"    Jobstreet: {len(cards)} cards for '{keyword[:30]}'")
        for card in cards[:MAX_PER_KEYWORD]:
            try:
                title_el = card.query_selector(
                    "[data-automation='job-card-title'] a, "
                    "[data-testid='job-card-title'] a, h3 a, h2 a"
                )
                if not title_el:
                    continue
                title = title_el.inner_text().strip()
                href = title_el.get_attribute("href") or ""
                job_url = href if href.startswith("http") else "https://ph.jobstreet.com" + href
                company_el = card.query_selector(
                    "[data-automation='job-card-company'], "
                    "[data-testid='company-name'], [class*='company']"
                )
                company = company_el.inner_text().strip() if company_el else "Unknown"
                salary_el = card.query_selector("[data-automation='job-card-salary'], [class*='salary']")
                salary = salary_el.inner_text().strip() if salary_el else ""
                jobs.append({
                    "title": title, "company": company,
                    "platform": "Jobstreet PH", "url": job_url,
                    "apply_email": None, "description": "",
                    "salary_info": salary,
                    "keywords_matched": _matched_keywords(title),
                })
            except Exception:
                continue
        page.close()
    except Exception as e:
        log.warning(f"    Jobstreet failed '{keyword[:30]}': {type(e).__name__}: {str(e)[:80]}")
    return jobs


def scrape_onlinejobs(keyword: str, context) -> list:
    jobs = []
    url = f"https://www.onlinejobs.ph/jobseekers/jobsearch?q={quote_plus(keyword)}&jobtype=fulltime"
    try:
        page = context.new_page()
        page.goto(url, wait_until="domcontentloaded", timeout=25000)
        time.sleep(DELAY + 1)
        try:
            page.wait_for_selector(".job-post, .jobpost, [class*='jobcard']", timeout=8000)
        except Exception:
            pass
        html = page.content()
        page.close()
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, "html.parser")
        cards = soup.select(".job-post, .jobpost, article, [class*='jobcard'], [class*='job-card']")
        log.info(f"    OnlineJobs: {len(cards)} cards for '{keyword[:30]}'")
        for card in cards[:MAX_PER_KEYWORD]:
            try:
                title_el = card.select_one("h2 a, h3 a, .job-title a, [class*='title'] a")
                if not title_el:
                    continue
                title = title_el.get_text(strip=True)
                href = title_el.get("href", "")
                job_url = href if href.startswith("http") else "https://www.onlinejobs.ph" + href
                company_el = card.select_one("[class*='company'], [class*='employer']")
                company = company_el.get_text(strip=True) if company_el else "Private Employer"
                desc_el = card.select_one("[class*='description'], [class*='summary']")
                desc = desc_el.get_text(strip=True) if desc_el else ""
                salary_el = card.select_one("[class*='salary'], [class*='rate'], [class*='pay']")
                salary = salary_el.get_text(strip=True) if salary_el else ""
                jobs.append({
                    "title": title, "company": company,
                    "platform": "OnlineJobs.ph", "url": job_url,
                    "apply_email": _extract_email(desc),
                    "description": desc, "salary_info": salary,
                    "keywords_matched": _matched_keywords(title + " " + desc),
                })
            except Exception:
                continue
    except Exception as e:
        log.warning(f"    OnlineJobs failed '{keyword[:30]}': {type(e).__name__}: {str(e)[:80]}")
    return jobs


_remotive_cache: dict = {}
REMOTIVE_CATEGORIES = ["customer-support", "data", "software-dev", "all-other"]

REMOTIVE_TARGET_KEYWORDS = [
    "python", "automation", "ai", "machine learning", "backend",
    "developer", "engineer", "integration", "data",
]

def _fetch_remotive_category(cat: str) -> list:
    """Fetch and filter one Remotive category. Safe to run in a thread."""
    if cat in _remotive_cache:
        return _remotive_cache[cat]
    batch = []
    try:
        r = requests.get(
            f"https://remotive.com/api/remote-jobs?category={cat}&limit=30",
            headers={"User-Agent": "JobAIAgent/1.0"},
            timeout=12,
        )
        if r.status_code != 200:
            return []
        for j in r.json().get("jobs", []):
            title_raw = j.get("title", "")
            tags = " ".join(j.get("tags", []))
            desc_raw = re.sub(r"<[^>]+>", " ", j.get("description", ""))[:600]
            combo = (title_raw + " " + tags).lower()
            if not any(kw in combo for kw in REMOTIVE_TARGET_KEYWORDS):
                continue
            batch.append({
                "title": title_raw,
                "company": j.get("company_name", "Unknown"),
                "platform": "Remotive.com",
                "url": j.get("url", ""),
                "apply_email": _extract_email(desc_raw),
                "description": desc_raw,
                "salary_info": j.get("salary", "") or "",
                "keywords_matched": _matched_keywords(title_raw + " " + tags),
            })
        _remotive_cache[cat] = batch
        log.info(f"    Remotive [{cat}]: {len(batch)} relevant jobs")
    except Exception as e:
        log.warning(f"    Remotive [{cat}] failed: {e}")
    return batch


def scrape_remotive() -> list:
    """All Remotive categories fetched concurrently.
    Cross-category duplicates are removed by scrape_all's global dedup."""
    jobs = []
    with ThreadPoolExecutor(max_workers=len(REMOTIVE_CATEGORIES)) as pool:
        for batch in pool.map(_fetch_remotive_category, REMOTIVE_CATEGORIES):
            jobs += batch
    return jobs


def _scrape_site(site_name: str, scrape_fn) -> list:
    """
    Run every keyword against one site inside its own Playwright
    instance. Each site gets a dedicated thread, so keywords stay
    sequential per domain (polite) while the three sites overlap.
    Playwright sync objects are not thread-safe, so nothing here is
    shared across threads.
    """
    jobs = []
    pw = browser = context = None
    try:
        pw, browser, context = _make_browser()
    except Exception as e:
        log.error(f"  [{site_name}] browser launch failed: {e}")
        log.error("   Fix: run  python -m playwright install chromium")
        return jobs

    try:
        for i, keyword in enumerate(SEARCH_KEYWORDS, 1):
            log.info(f"  [{site_name} {i}/{len(SEARCH_KEYWORDS)}] '{keyword}'")
            try:
                jobs += scrape_fn(keyword, context)
            except Exception as e:
                log.warning(f"  [{site_name}] '{keyword[:30]}' failed: {e}")
    finally:
        for obj in (context, browser):
            try:
                if obj:
                    obj.close()
            except Exception:
                pass
        try:
            if pw:
                pw.stop()
        except Exception:
            pass
    return jobs


def scrape_all() -> list:
    """All three browser sites + the Remotive API scraped concurrently.
    Wall time is the slowest single site instead of the sum of all four."""
    sites = [
        ("Indeed",     scrape_indeed),
        ("Jobstreet",  scrape_jobstreet),
        ("OnlineJobs", scrape_onlinejobs),
    ]
    log.info(f"Starting scrape — {len(SEARCH_KEYWORDS)} keywords, "
             f"{len(sites)} sites in parallel + Remotive API")

    all_jobs = []
    seen = set()
    with ThreadPoolExecutor(max_workers=len(sites) + 1) as pool:
        futures = [pool.submit(_scrape_site, name, fn) for name, fn in sites]
        futures.append(pool.submit(scrape_remotive))
        for fut in futures:
            try:
                batch = fut.result()
            except Exception as e:
                log.warning(f"  Scrape worker crashed: {e}")
                continue
            for job in batch:
                uid = f"{job['title'].lower().strip()}|{job['company'].lower().strip()}"
                if uid not in seen and job["title"].strip():
                    seen.add(uid)
                    all_jobs.append(job)

    log.info(f"Scrape complete — {len(all_jobs)} unique jobs total")

    if not all_jobs:
        log.warning(
            "\nZero jobs collected. Troubleshoot:\n"
            "   1. Run: python -m playwright install chromium\n"
            "   2. Check your internet connection\n"
            "   3. Use 'Add Job Manually' in the dashboard as a workaround\n"
        )

    return all_jobs
