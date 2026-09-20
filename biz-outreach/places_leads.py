"""
Finds businesses with no real website via the Google Places API (legacy
Text Search + Place Details - both officially supported, unlike scraping
Google Search result pages directly, which violates Google's ToS).

Places API never returns an email address. Some very small businesses put
a Facebook/Instagram page URL in the "website" field instead of a real
site; when that happens, we do a plain public fetch of that page and look
for an email the business itself published (e.g. in its About text) -
the same conservative pattern used for YouTube channel descriptions.
Expect a low hit rate: most listings with no real site simply don't
publish an email anywhere we can compliantly read.
"""

import re
import time

import requests

EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
SOCIAL_DOMAINS = ("facebook.com", "instagram.com")

TEXT_SEARCH_URL = "https://maps.googleapis.com/maps/api/place/textsearch/json"
DETAILS_URL = "https://maps.googleapis.com/maps/api/place/details/json"


def _extract_email(text: str):
    match = EMAIL_RE.search(text or "")
    return match.group(0) if match else None


def _is_social_link(url: str) -> bool:
    return any(domain in url for domain in SOCIAL_DOMAINS)


def _public_page_email(url: str, session: requests.Session):
    try:
        resp = session.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        resp.raise_for_status()
    except requests.RequestException:
        return None
    return _extract_email(resp.text)


def find_businesses_without_website(api_key: str, query: str, *, max_results: int = 40):
    session = requests.Session()
    leads = []
    page_token = None

    while len(leads) < max_results:
        params = {"query": query, "key": api_key}
        if page_token:
            params["pagetoken"] = page_token
            time.sleep(2)  # Google requires a short delay before a next_page_token is valid

        resp = session.get(TEXT_SEARCH_URL, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        status = data.get("status")
        if status not in ("OK", "ZERO_RESULTS"):
            raise RuntimeError(f"Places API error: {status} {data.get('error_message', '')}")

        for item in data.get("results", []):
            if len(leads) >= max_results:
                break

            place_id = item["place_id"]
            details_resp = session.get(DETAILS_URL, params={
                "place_id": place_id,
                "fields": "name,formatted_address,formatted_phone_number,website,type",
                "key": api_key,
            }, timeout=10)
            details_resp.raise_for_status()
            details = details_resp.json().get("result", {})

            website = details.get("website")
            if website and not _is_social_link(website):
                continue  # already has a real website, not a lead for this campaign

            email = None
            email_source = None
            if website and _is_social_link(website):
                email = _public_page_email(website, session)
                if email:
                    email_source = website.split("/")[2]

            types = details.get("types") or item.get("types") or []
            leads.append({
                "place_id": place_id,
                "name": details.get("name", item.get("name")),
                "address": details.get("formatted_address", item.get("formatted_address")),
                "phone": details.get("formatted_phone_number"),
                "category": types[0] if types else None,
                "email": email,
                "email_source": email_source,
            })

        page_token = data.get("next_page_token")
        if not page_token:
            break

    return leads
