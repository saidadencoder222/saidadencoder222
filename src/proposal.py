"""Renders a per-prospect proposal page from the audit findings."""
import re
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

TEMPLATE_DIR = Path(__file__).resolve().parent.parent / "templates"
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "docs" / "proposals"


def slugify(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return slug or "prospect"


def render_proposal(channel: dict, findings: list[dict], social_proof: list[dict],
                     sender_name: str, booking_link: str, cta_text: str,
                     unsubscribe_link: str = "") -> Path:
    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    template = env.get_template("proposal.html.j2")
    html = template.render(
        channel=channel,
        findings=findings,
        social_proof=social_proof,
        sender_name=sender_name,
        booking_link=booking_link,
        cta_text=cta_text,
        unsubscribe_link=unsubscribe_link,
    )

    slug = slugify(channel["title"])
    out_dir = OUTPUT_DIR / slug
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "index.html"
    out_path.write_text(html, encoding="utf-8")
    return out_path
