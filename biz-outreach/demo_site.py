import os
import re

SLUG_RE = re.compile(r"[^a-z0-9]+")


def slugify(name: str, place_id: str) -> str:
    base = SLUG_RE.sub("-", name.lower()).strip("-")
    return f"{base}-{place_id[-8:]}"


def generate_demo(lead: dict, *, template_path: str, output_dir: str, base_url: str):
    """Writes a real one-page site for this lead and returns its public URL.

    The email pitch links here, so this has to actually exist - it's what
    keeps "I built you a demo" true rather than a fabricated claim.
    """
    slug = slugify(lead["name"], lead["place_id"])
    demo_dir = os.path.join(output_dir, slug)
    os.makedirs(demo_dir, exist_ok=True)

    with open(template_path) as f:
        template = f.read()

    category = (lead.get("category") or "local business").replace("_", " ").title()
    html = template.format(
        business_name=lead["name"],
        category=category,
        address=lead.get("address") or "",
        phone=lead.get("phone") or "",
    )

    with open(os.path.join(demo_dir, "index.html"), "w") as f:
        f.write(html)

    demo_url = f"{base_url.rstrip('/')}/{slug}/"
    return slug, demo_url
