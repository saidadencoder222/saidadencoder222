"""
Finds businesses with no real website via the Google Places API (New) -
Text Search, which returns website/phone/address directly, no separate
Details call needed. Officially supported, unlike scraping Google Search
result pages directly, which violates Google's ToS.

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

SEARCH_URL = "https://places.googleapis.com/v1/places:searchText"
FIELD_MASK = (
    "places.id,places.displayName,places.formattedAddress,"
    "places.nationalPhoneNumber,places.websiteUri,places.types,nextPageToken"
)


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
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": api_key,
        "X-Goog-FieldMask": FIELD_MASK,
    }

    leads = []
    page_token = None

    while len(leads) < max_results:
        body = {"textQuery": query, "pageSize": min(20, max_results - len(leads))}
        if page_token:
            body["pageToken"] = page_token
            time.sleep(2)  # a next page token needs a short delay before it's valid

        resp = session.post(SEARCH_URL, headers=headers, json=body, timeout=10)
        if resp.status_code != 200:
            raise RuntimeError(f"Places API error: {resp.status_code} {resp.text}")
        data = resp.json()
        places_on_page = data.get("places", [])

        # The API can keep returning a nextPageToken even once results are
        # actually exhausted (an empty page with a token pointing nowhere) -
        # an empty page is the reliable signal to stop, not just a missing token.
        if not places_on_page:
            break

        for place in places_on_page:
            if len(leads) >= max_results:
                break

            website = place.get("websiteUri")
            if website and not _is_social_link(website):
                continue  # already has a real website, not a lead for this campaign

            email = None
            email_source = None
            if website and _is_social_link(website):
                email = _public_page_email(website, session)
                if email:
                    email_source = website.split("/")[2]

            types = place.get("types") or []
            leads.append({
                "place_id": place["id"],
                "name": place.get("displayName", {}).get("text", ""),
                "address": place.get("formattedAddress"),
                "phone": place.get("nationalPhoneNumber"),
                "category": types[0] if types else None,
                "email": email,
                "email_source": email_source,
            })

        page_token = data.get("nextPageToken")
        if not page_token:
            break

    return leads
