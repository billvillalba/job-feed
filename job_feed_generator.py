"""
Job Search RSS Feed Generator
==============================
Searches Greenhouse, Lever, and Ashby job boards for matching roles
and outputs a local RSS feed file you can open in any RSS reader.

HOW TO USE:
1. Open your terminal
2. Navigate to Desktop: cd ~/Desktop
3. Run: python3 job_feed_generator.py
4. Upload the resulting jobs_feed.xml to your GitHub repo —
   Inoreader will refresh automatically.
"""

import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
import time

# ─────────────────────────────────────────────
# YOUR SEARCH TERMS
# ─────────────────────────────────────────────
JOB_TERMS = [
    "service design",
    "design strategy",
    "experience strategy",
    "cx strategy",
    "experience architect",
    "staff product designer",
    "principal product designer",
    "senior product designer",
    "design lead",
    "transformation design",
    "innovation design",
    "strategic designer",
    "design strategist",
    "care journey designer",
    "care delivery design",
    "care model design"
    "healthcare product designer",
    "healthcare product strategy",
    "population health strategy",
    "civic product designer",
    "design researcher",
    "digital transformation",
    "customer experience",
    "consumer experience",
    "clinical experience",
    "CX",
    "UX",
    "patient experience",
    "healthcare system",
    "experience design",
    "design research",
    "customer insight",
    "consumer insight",
    "patient insight",
    "member insight",
    "workflow systems",
    "behavioral analytics",
    "behavioral health program design",
    "behavioral health transformation",
    "behavioral health innovation",
    "ux designer",
    "cx designer",
    "ux strategist",
    "cx strategist",
    "enterprise ux",
]

# ─────────────────────────────────────────────
# YOUR COMPANIES
#
# NOT INCLUDED (use Workday, custom boards, or no active ATS found):
#   Providence Health, Geisinger, Intermountain, Northwell, UPMC,
#   Stanford Health Care, Cedars-Sinai, Iora Health (acquired by One Medical),
#   Quartet Health (rebranded/restructured), Mindstrong Health (shut down),
#   Dispatch Health, Arnold Ventures, MacArthur Foundation, Kresge Foundation,
#   Commonwealth Fund, Adelade, Chewy, Instacart, EmblemHealth,
#   Pfizer, Johnson & Johnson, Centene, Slalom, Publicis Sapient, EPAM,
#   Nearform, Schmidt Futures, Irrational Labs, Rosebud, Televeda, Athenahealth,
#   Cityblock Health, Devoted Health, Charlie Health, Teladoc Health
# ─────────────────────────────────────────────
COMPANIES = [
    # ── Behavioral Health ──
    {"name": "Lyra Health",         "slug": "lyrahealth",           "ats": "lever"},
    {"name": "Headspace Health",    "slug": "hs",                   "ats": "greenhouse"},
    {"name": "Spring Health",       "slug": "springhealth66",       "ats": "greenhouse"},
    {"name": "SonderMind",          "slug": "smus",                 "ats": "greenhouse"},
    {"name": "Brightline",          "slug": "hellobrightline",      "ats": "ashby"},
    {"name": "Talkspace",           "slug": "talkspace",            "ats": "greenhouse"},
    {"name": "Headway",             "slug": "headway",              "ats": "greenhouse"},
    {"name": "Grow Therapy",        "slug": "growtherapy",          "ats": "greenhouse"},
    {"name": "Alma Mental Health",  "slug": "alma",                 "ats": "greenhouse"},
    {"name": "Calm",                "slug": "calm",                 "ats": "greenhouse"},
    {"name": "Rula",                "slug": "rula",                 "ats": "ashby"},
    {"name": "Octave Health",       "slug": "octave",               "ats": "greenhouse"},
    {"name": "Equip Health",        "slug": "equip",                "ats": "ashby"},
    {"name": "Modern Health",       "slug": "modernhealth",         "ats": "greenhouse"},
    {"name": "Valera Health",       "slug": "valerahealth",         "ats": "greenhouse"},
    
    # __ Women's & Reproductive Health __
    {"name": "Maven Clinic",        "slug": "mavenclinic",          "ats": "greenhouse"},
    {"name": "Carrot Fertility",    "slug": "carrotfertility",      "ats": "greenhouse"},
    {"name": "Midi Health",         "slug": "midihealth",           "ats": "greenhouse"},
    {"name": "Oula Health",         "slug": "oulahealth",           "ats": "greenhouse"},

    # ── Health Tech & Digital Health ──
    {"name": "Carbon Health",       "slug": "carbonhealth",         "ats": "lever"},
    {"name": "Included Health",     "slug": "includedhealth",       "ats": "lever"},
    {"name": "Omada Health",        "slug": "omadahealth",          "ats": "greenhouse"},
    {"name": "Hims & Hers",         "slug": "hims-and-hers",        "ats": "ashby"},
    {"name": "Virta Health",        "slug": "virtahealth",          "ats": "ashby"},
    {"name": "Pearl Health",        "slug": "pearlhealth",          "ats": "ashby"},
    {"name": "Abridge",             "slug": "abridge",              "ats": "ashby"},
    {"name": "One Medical",         "slug": "onemedical",           "ats": "greenhouse"},
    {"name": "Cohere Health",       "slug": "coherehealth",              "ats": "greenhouse"},
    {"name": "Ambience Healthcare", "slug": "ambiencehealthcare",        "ats": "ashby"},
    {"name": "Medallion",           "slug": "medallionakafirstlayerai",  "ats": "greenhouse"},
    {"name": "Nabla",               "slug": "nabla",                     "ats": "ashby"},
    {"name": "Cadence Health",      "slug": "cadencehealth",             "ats": "greenhouse"},
    {"name": "Hippocratic AI",      "slug": "Hippocratic AI",            "ats": "ashby"},
    {"name": "Truveta",             "slug": "truveta",                   "ats": "greenhouse"},
    {"name": "Tomorrow Health",     "slug": "tomorrowhealth",            "ats": "greenhouse"},
    {"name": "Lantern Care",        "slug": "employerdirecthealthcare",  "ats": "greenhouse"},
    {"name": "Sprinter Health",     "slug": "SprinterHealth",            "ats": "lever"},
    {"name": "Parsley Health",      "slug": "parsleyhealth",             "ats": "greenhouse"},
    {"name": "Rapid SOS",           "slug": "rapidsos",                  "ats": "greenhouse"},
    {"name": "Solace Health",       "slug": "Solace",                    "ats": "ashby"},
    {"name": "Avalere Health",      "slug": "avalerehealth",             "ats": "lever"},

    # ── Service Design & Innovation Consultancies ──
    {"name": "IDEO",                "slug": "ideo",                 "ats": "greenhouse"},
    {"name": "Huge",                "slug": "hugeinc",              "ats": "greenhouse"},
    {"name": "Thoughtworks",        "slug": "thoughtworks",         "ats": "greenhouse"},

    # ── Public Sector / Civic Tech ──
    {"name": "Code for America",    "slug": "codeforamerica",       "ats": "greenhouse"},
    {"name": "Nava PBC",            "slug": "nava",                 "ats": "lever"},
    {"name": "Oddball",             "slug": "oddball",              "ats": "greenhouse"},
    
    # ── Tech Companies ──
    {"name": "Stripe",              "slug": "stripe",               "ats": "greenhouse"},
    {"name": "Airbnb",              "slug": "airbnb",               "ats": "greenhouse"},
    {"name": "Notion",              "slug": "notion",               "ats": "ashby"},
    {"name": "Reddit",              "slug": "reddit",               "ats": "greenhouse"},

    # ── Foundations & Social Impact ──
    {"name": "Chan Zuckerberg Initiative", "slug": "chanzuckerberginitiative", "ats": "greenhouse"},
]

OUTPUT_FILE = "jobs_feed.xml"

GREENHOUSE_URLS = [
    "https://boards-api.greenhouse.io/v1/boards/{slug}/jobs",
    "https://job-boards.greenhouse.io/{slug}/jobs",
]


def title_matches(title: str) -> bool:
    title_lower = title.lower()
    return any(term.lower() in title_lower for term in JOB_TERMS)


def fetch_greenhouse_jobs(company: dict) -> list:
    slug = company["slug"]
    for url_template in GREENHOUSE_URLS:
        url = url_template.format(slug=slug)
        try:
            r = requests.get(url, timeout=10)
            if r.status_code == 404:
                continue
            r.raise_for_status()
            data = r.json()
            jobs = []
            for job in data.get("jobs", []):
                title = job.get("title", "")
                if title_matches(title):
                    jobs.append({
                        "title": title,
                        "company": company["name"],
                        "url": job.get("absolute_url", "") or job.get("url", ""),
                        "location": job.get("location", {}).get("name", "Not specified"),
                        "updated": job.get("updated_at", ""),
                        "id": str(job.get("id", "")),
                    })
            return jobs
        except Exception:
            continue
    print(f"  ⚠️  {company['name']}: board not found (slug may be wrong)")
    return []


def fetch_lever_jobs(company: dict) -> list:
    slug = company["slug"]
    url = f"https://api.lever.co/v0/postings/{slug}?mode=json"
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 404:
            print(f"  ⚠️  {company['name']}: board not found (slug may be wrong)")
            return []
        r.raise_for_status()
        data = r.json()
        jobs = []
        for job in data:
            title = job.get("text", "")
            if title_matches(title):
                jobs.append({
                    "title": title,
                    "company": company["name"],
                    "url": job.get("hostedUrl", ""),
                    "location": job.get("categories", {}).get("location", "Not specified"),
                    "updated": datetime.fromtimestamp(
                        job.get("createdAt", 0) / 1000, tz=timezone.utc
                    ).isoformat() if job.get("createdAt") else "",
                    "id": job.get("id", ""),
                })
        return jobs
    except Exception as e:
        print(f"  ❌  {company['name']} (Lever): {e}")
        return []


def fetch_ashby_jobs(company: dict) -> list:
    slug = company["slug"]
    url = f"https://api.ashbyhq.com/posting-api/job-board/{slug}"
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 404:
            print(f"  ⚠️  {company['name']}: board not found (slug may be wrong)")
            return []
        r.raise_for_status()
        data = r.json()
        jobs = []
        for job in data.get("jobPostings", []):
            title = job.get("title", "")
            if title_matches(title):
                jobs.append({
                    "title": title,
                    "company": company["name"],
                    "url": job.get("jobUrl", ""),
                    "location": job.get("locationName", "Not specified"),
                    "updated": job.get("publishedDate", ""),
                    "id": job.get("id", ""),
                })
        return jobs
    except Exception as e:
        print(f"  ❌  {company['name']} (Ashby): {e}")
        return []


def build_rss(jobs: list) -> str:
    rss = ET.Element("rss", version="2.0")
    channel = ET.SubElement(rss, "channel")
    ET.SubElement(channel, "title").text = "Job Search Feed"
    ET.SubElement(channel, "link").text = "https://example.com"
    ET.SubElement(channel, "description").text = (
        f"Matching jobs as of {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    )
    seen_urls = set()
    for job in jobs:
        url = job["url"]
        if url in seen_urls:
            continue
        seen_urls.add(url)
        item = ET.SubElement(channel, "item")
        ET.SubElement(item, "title").text = f"{job['title']} — {job['company']}"
        ET.SubElement(item, "link").text = url
        ET.SubElement(item, "guid").text = url
        ET.SubElement(item, "description").text = (
            f"<b>{job['company']}</b><br/>"
            f"Location: {job['location']}<br/>"
            f"<a href='{url}'>View Job</a>"
        )
        if job.get("updated"):
            ET.SubElement(item, "pubDate").text = job["updated"]
    ET.indent(rss, space="  ")
    return ET.tostring(rss, encoding="unicode", xml_declaration=True)


def main():
    print("=" * 50)
    print("  Job Search RSS Feed Generator")
    print("=" * 50)
    all_jobs = []
    for company in COMPANIES:
        ats = company.get("ats", "greenhouse")
        print(f"Checking {company['name']} ({ats})...")
        if ats == "greenhouse":
            jobs = fetch_greenhouse_jobs(company)
        elif ats == "lever":
            jobs = fetch_lever_jobs(company)
        elif ats == "ashby":
            jobs = fetch_ashby_jobs(company)
        else:
            print(f"  ⚠️  Unknown ATS '{ats}' for {company['name']}, skipping.")
            jobs = []
        if jobs:
            print(f"  ✅  Found {len(jobs)} matching job(s)")
        all_jobs.extend(jobs)
        time.sleep(0.3)

    print()
    print(f"Total matching jobs found: {len(all_jobs)}")
    rss_content = build_rss(all_jobs)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(rss_content)
    print(f"RSS feed saved to: {OUTPUT_FILE}")
    print()
    print("Upload jobs_feed.xml to GitHub and Inoreader will refresh automatically.")


if __name__ == "__main__":
    main()
