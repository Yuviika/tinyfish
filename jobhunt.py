"""
JobHunt - TinyFish-powered job & internship finder.

Search  -> discovers extra careers pages / portals for your query
Agent   -> opens each portal in a real browser, uses its filters, extracts listings
Fetch   -> reads the posting page of top matches to confirm keywords
Then we dedupe, score against your preferences, cache, and print ranked results.
"""
import argparse
import json
import re
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.parse import quote_plus

from tinyfish import TinyFish

client = TinyFish()  # reads TINYFISH_API_KEY from env

CACHE_FILE = Path("jobs_cache.json")
MAX_AGE_HOURS = 6  # results older than this get re-scraped

# Seed portals/careers pages (templates). Listings themselves are always live.
SEEDS = [
    "https://internshala.com/internships/keywords-{q}/",
    "https://www.amazon.jobs/en/search?base_query={q}&loc_query={loc}",
    "https://www.google.com/about/careers/applications/jobs/results/?q={q}&location={loc}",
    "https://jobs.careers.microsoft.com/global/en/search?q={q}&lc={loc}",
]

SCHEMA = {
    "type": "object",
    "properties": {
        "jobs": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "company": {"type": "string"},
                    "location": {"type": "string"},
                    "apply_url": {"type": "string"},
                    "summary": {"type": "string"},
                },
                "required": ["title", "apply_url"],
            },
        }
    },
    "required": ["jobs"],
}

LEVEL_WORDS = {
    "intern": ["intern", "internship", "trainee"],
    "entry": ["junior", "graduate", "entry", "associate", "fresher", "engineer i", "sde 1", "sde i"],
    "mid": ["engineer ii", "sde 2", "sde ii", "mid"],
    "senior": ["senior", "sr.", "staff", "lead", "principal"],
}
SENIOR_WORDS = LEVEL_WORDS["senior"] + ["manager", "director", "head of"]


# ---------- 1. SEARCH: discover more portals ----------
def discover_urls(prefs, n=2):
    query = f"{prefs['role']} {prefs['level']} jobs {prefs['location']} careers apply"
    try:
        res = client.search.query(query)
        items = getattr(res, "results", None) or res
        urls = []
        for it in items:
            u = getattr(it, "url", None) or (it.get("url") if isinstance(it, dict) else None)
            if u:
                urls.append(u)
        return urls[:n]
    except Exception as e:
        print(f"[search] failed: {e}")
        return []


# ---------- 2. AGENT: read a portal ----------
def run_agent(url, prefs):
    goal = (
        f"Find current job or internship openings on this site matching role '{prefs['role']}', "
        f"seniority '{prefs['level']}', location '{prefs['location']}', keywords {prefs['keywords']}. "
        "Use the site's search box or filters if there are any. Return up to 10 REAL openings "
        "visible on the site. For each give title, company, location, apply_url (direct link to "
        "the posting) and a one-line summary."
    )
    try:
        print(f"[agent] starting {url}")
        resp = client.agent.run(url=url, goal=goal, output_schema=SCHEMA)
        result = getattr(resp, "result", None)
        if isinstance(result, str):
            result = json.loads(result)
        jobs = (result or {}).get("jobs", [])
        print(f"[agent] {len(jobs)} jobs from {url}")
        return jobs
    except Exception as e:
        print(f"[agent] failed on {url}: {e}")
        return []


# ---------- 3. FETCH: read a posting page ----------
def fetch_text(url):
    try:
        try:
            resp = client.fetch.get_contents(urls=[url])
        except AttributeError:
            resp = client.fetch.content.get(urls=[url])
        return str(resp).lower()
    except Exception as e:
        print(f"[fetch] failed {url}: {e}")
        return ""


# ---------- dedupe + score ----------
def dedupe(jobs):
    seen, out = set(), []
    for j in jobs:
        url_key = re.sub(r"[?#].*$", "", (j.get("apply_url") or "").lower())
        text_key = re.sub(r"\W+", "", f"{j.get('company','')}{j.get('title','')}{j.get('location','')}".lower())
        if url_key in seen or text_key in seen:
            continue
        seen.add(url_key)
        seen.add(text_key)
        out.append(j)
    return out


def score(job, prefs, extra=""):
    title = (job.get("title") or "").lower()
    loc = (job.get("location") or "").lower()
    blob = f"{title} {(job.get('summary') or '').lower()} {extra}"
    s = 0
    role_words = [w for w in prefs["role"].lower().split() if len(w) > 2]
    s += sum(3 for w in role_words if w in title)
    if prefs["role"].lower() in title:
        s += 5
    if prefs["location"].lower() in loc or "remote" in loc:
        s += 4
    level_hits = LEVEL_WORDS.get(prefs["level"], [])
    if any(w in title for w in level_hits):
        s += 4
    if prefs["level"] in ("intern", "entry") and any(w in title for w in SENIOR_WORDS):
        s -= 6
    s += sum(2 for k in prefs["keywords"] if k and k.lower() in blob)
    return s


# ---------- pipeline with cache ----------
def find_jobs(prefs, force=False):
    if CACHE_FILE.exists() and not force:
        cache = json.loads(CACHE_FILE.read_text(encoding="utf-8"))
        fresh = time.time() - cache["fetched_at"] < MAX_AGE_HOURS * 3600
        if fresh and cache["prefs"] == prefs:
            print("[cache] using fresh cached results")
            return cache["jobs"]

    q, loc = quote_plus(prefs["role"]), quote_plus(prefs["location"])
    urls = [s.format(q=q, loc=loc) for s in SEEDS] + discover_urls(prefs)
    print(f"[plan] scraping {len(urls)} portals in parallel...")

    with ThreadPoolExecutor(max_workers=4) as pool:
        batches = list(pool.map(lambda u: run_agent(u, prefs), urls))
    jobs = dedupe([j for b in batches for j in b])

    # first-pass rank, then confirm top 8 by reading the actual posting page
    for j in jobs:
        j["score"] = score(j, prefs)
    jobs.sort(key=lambda j: j["score"], reverse=True)
    top = [j for j in jobs[:8] if j.get("apply_url")]
    with ThreadPoolExecutor(max_workers=4) as pool:
        texts = list(pool.map(lambda j: fetch_text(j["apply_url"]), top))
    for j, t in zip(top, texts):
        j["score"] = score(j, prefs, extra=t)
    jobs.sort(key=lambda j: j["score"], reverse=True)

    CACHE_FILE.write_text(
        json.dumps({"fetched_at": time.time(), "prefs": prefs, "jobs": jobs}, indent=2),
        encoding="utf-8",
    )
    return jobs


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--role", default="software engineer")
    p.add_argument("--location", default="India")
    p.add_argument("--level", default="intern", choices=list(LEVEL_WORDS))
    p.add_argument("--keywords", default="python")
    p.add_argument("--refresh", action="store_true")
    a = p.parse_args()
    prefs = {
        "role": a.role,
        "location": a.location,
        "level": a.level,
        "keywords": [k.strip() for k in a.keywords.split(",") if k.strip()],
    }
    jobs = find_jobs(prefs, force=a.refresh)
    print(f"\n=== {len(jobs)} deduplicated listings, best match first ===\n")
    for i, j in enumerate(jobs[:20], 1):
        print(f"{i}. [{j.get('score', 0)}] {j.get('title')} @ {j.get('company')} ({j.get('location')})")
        print(f"   {j.get('apply_url')}\n")


if __name__ == "__main__":
    main()