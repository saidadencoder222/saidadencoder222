"""
Builds a per-creator monetization/growth audit PDF from real, verifiable
YouTube data only (see youtube_leads.py) - upload consistency, recent
view averages, and bio link presence. Findings are computed, not
fabricated: a channel with no red flags gets an honest "looks solid"
page rather than an invented problem.
"""

import io
import os

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas as pdfcanvas
from reportlab.platypus import HRFlowable, Paragraph, SimpleDocTemplate, Spacer
from pypdf import PdfReader, PdfWriter

FONT_DIR_DEJAVU = "/usr/share/fonts/truetype/dejavu"
FONT_DIR_LIBERATION = "/usr/share/fonts/truetype/liberation"
DEFAULT_ACCENT = "#1f2937"
RECENT_VIDEO_SAMPLE = 6

_FONTS_REGISTERED = False


def _register_fonts():
    global _FONTS_REGISTERED
    if _FONTS_REGISTERED:
        return
    pdfmetrics.registerFont(TTFont("Serif", os.path.join(FONT_DIR_DEJAVU, "DejaVuSerif.ttf")))
    pdfmetrics.registerFont(TTFont("Serif-Bold", os.path.join(FONT_DIR_DEJAVU, "DejaVuSerif-Bold.ttf")))
    pdfmetrics.registerFont(TTFont("Sans", os.path.join(FONT_DIR_LIBERATION, "LiberationSans-Regular.ttf")))
    pdfmetrics.registerFont(TTFont("Sans-Bold", os.path.join(FONT_DIR_LIBERATION, "LiberationSans-Bold.ttf")))
    pdfmetrics.registerFont(TTFont("Sans-Italic", os.path.join(FONT_DIR_LIBERATION, "LiberationSans-Italic.ttf")))
    _FONTS_REGISTERED = True


styles = getSampleStyleSheet()


def _styles(accent_hex: str):
    accent = colors.HexColor(accent_hex)
    return {
        "h1": ParagraphStyle("H1", parent=styles["Heading1"], fontName="Serif-Bold",
                              fontSize=17, leading=21, spaceBefore=16, spaceAfter=8,
                              textColor=accent),
        "h2": ParagraphStyle("H2", parent=styles["Heading2"], fontName="Sans-Bold",
                              fontSize=12, spaceBefore=10, spaceAfter=5,
                              textColor=colors.HexColor("#1f2937")),
        "body": ParagraphStyle("Body", parent=styles["Normal"], fontName="Sans",
                                fontSize=10.5, leading=15.5, spaceAfter=9,
                                textColor=colors.HexColor("#27272a")),
        "stat": ParagraphStyle("Stat", parent=styles["Normal"], fontName="Sans",
                                fontSize=10.5, leading=15.5, leftIndent=14,
                                textColor=colors.HexColor("#374151"), spaceAfter=6,
                                backColor=colors.HexColor("#f3f4f6"), borderPadding=8),
        "footer": ParagraphStyle("Footer", parent=styles["Normal"], fontName="Sans-Italic",
                                  fontSize=9, textColor=colors.HexColor("#9ca3af"),
                                  alignment=TA_CENTER),
        "accent": accent,
    }


def build_observations(lead: dict) -> list:
    """Computed findings only - never invents a problem a channel doesn't have."""
    obs = []
    avg_gap = lead.get("upload_gap_days_avg")
    stdev = lead.get("upload_gap_days_stdev")
    subs = lead.get("subscriber_count")
    avg_views = lead.get("avg_recent_views")

    if avg_gap is not None:
        if stdev is not None and avg_gap > 0 and stdev > avg_gap * 0.6:
            obs.append((
                "Inconsistent upload cadence",
                f"Your last {RECENT_VIDEO_SAMPLE} uploads are spaced {avg_gap:.1f} days apart on "
                f"average, but that varies by roughly {stdev:.1f} days. A predictable schedule tends "
                f"to get rewarded by the algorithm and builds the \"check back\" habit faster than "
                f"irregular posting does.",
            ))
        elif avg_gap > 14:
            obs.append((
                "Long gaps between uploads",
                f"Your recent uploads average {avg_gap:.1f} days apart. Wider gaps mean fewer chances "
                f"to get surfaced and slower compounding for any funnel or list tied to the channel.",
            ))

    if lead.get("has_link_in_bio") is False:
        obs.append((
            "No link anywhere in your channel bio",
            "Your channel description doesn't include a link. That's a free, always-visible "
            "placement sitting empty - right now anyone who checks your About tab has nowhere to "
            "go, whether that's a lead magnet, waitlist, or your main offer.",
        ))

    if avg_views is not None and subs:
        ratio = avg_views / max(subs, 1)
        if ratio < 0.03:
            obs.append((
                "Low view-to-subscriber ratio",
                f"Recent videos average about {avg_views:,} views against {subs:,} subscribers - "
                f"under 3%. That usually points to either a thumbnail/title mismatch or an audience "
                f"that's outgrown what's currently resonating.",
            ))

    return obs


def _build_cover(accent_hex: str, channel_title: str) -> bytes:
    buf = io.BytesIO()
    c = pdfcanvas.Canvas(buf, pagesize=letter)
    width, height = letter
    accent = colors.HexColor(accent_hex)

    c.setFillColor(accent)
    c.rect(0, 0, width, height, fill=1, stroke=0)
    c.setFillColor(colors.Color(1, 1, 1, alpha=0.06))
    c.circle(width * 0.85, height * 0.85, 2.2 * inch, fill=1, stroke=0)
    c.setFillColor(colors.Color(1, 1, 1, alpha=0.05))
    c.circle(width * 0.12, height * 0.12, 1.7 * inch, fill=1, stroke=0)

    title_y = height - 2.8 * inch
    c.setStrokeColor(colors.white)
    c.setLineWidth(1)
    c.line(width / 2 - 0.6 * inch, title_y + 0.55 * inch, width / 2 + 0.6 * inch, title_y + 0.55 * inch)

    c.setFillColor(colors.white)
    c.setFont("Serif-Bold", 27)
    c.drawCentredString(width / 2, title_y, "Monetization & Growth Audit")

    c.setFont("Sans", 13)
    c.drawCentredString(width / 2, title_y - 0.42 * inch, f"Prepared for {channel_title}")

    c.setFont("Sans-Italic", 10.5)
    c.drawCentredString(width / 2, title_y - 0.85 * inch,
                         "Based on publicly available YouTube data only")

    c.setFont("Sans", 9.5)
    c.drawCentredString(width / 2, 1 * inch, "A free audit, not a sales page")

    c.save()
    buf.seek(0)
    return buf.read()


def _header_footer(accent_hex: str):
    accent = colors.HexColor(accent_hex)

    def draw(canv, doc):
        canv.saveState()
        width, _ = letter
        canv.setFillColor(accent)
        canv.rect(0, letter[1] - 0.12 * inch, width, 0.12 * inch, fill=1, stroke=0)
        canv.setFont("Sans", 8.5)
        canv.setFillColor(colors.HexColor("#9ca3af"))
        canv.drawRightString(width - 0.9 * inch, 0.55 * inch, f"Growth Audit - {doc.page}")
        canv.restoreState()

    return draw


def _build_body(accent_hex: str, lead: dict) -> bytes:
    s = _styles(accent_hex)
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=letter,
        topMargin=1.0 * inch, bottomMargin=0.9 * inch,
        leftMargin=0.9 * inch, rightMargin=0.9 * inch,
    )
    story = []

    story.append(Paragraph("Your channel snapshot", s["h1"]))
    story.append(HRFlowable(width="100%", color=s["accent"], thickness=1.2, spaceAfter=10))

    subs = lead.get("subscriber_count")
    avg_views = lead.get("avg_recent_views")
    gap_avg = lead.get("upload_gap_days_avg")
    has_link = lead.get("has_link_in_bio")

    snapshot_lines = []
    if subs is not None:
        snapshot_lines.append(f"Subscribers: {subs:,}")
    if avg_views is not None:
        snapshot_lines.append(f"Avg. views, last {RECENT_VIDEO_SAMPLE} uploads: {avg_views:,}")
    if gap_avg is not None:
        snapshot_lines.append(f"Avg. days between uploads: {gap_avg:.1f}")
    snapshot_lines.append(f"Link in channel bio: {'Yes' if has_link else 'No'}")

    story.append(Paragraph("<br/>".join(snapshot_lines), s["stat"]))
    story.append(Spacer(1, 0.15 * inch))

    story.append(Paragraph("What I noticed", s["h1"]))
    observations = build_observations(lead)
    if observations:
        for heading, text in observations:
            story.append(Paragraph(heading, s["h2"]))
            story.append(Paragraph(text, s["body"]))
    else:
        story.append(Paragraph(
            "Your posting cadence and bio setup look solid from the outside - no obvious gaps in "
            "the public fundamentals. The bigger opportunity from here is probably in monetization "
            "structure rather than the marketing basics.",
            s["body"],
        ))

    story.append(Spacer(1, 0.1 * inch))
    story.append(Paragraph("Monetization avenues worth layering in", s["h1"]))
    story.append(HRFlowable(width="100%", color=s["accent"], thickness=1.2, spaceAfter=10))
    story.append(Paragraph(
        "General options that tend to fit a channel like this one, roughly in order of setup "
        "effort - not a claim about what you're already doing, just what's worth a look:",
        s["body"],
    ))
    avenues = [
        ("Digital course or cohort", "The highest-leverage option once you have consistent watch time - "
                                       "packages what you already teach for free into a paid, structured version."),
        ("1:1 or small-group coaching", "Fastest to launch with no product build - directly monetizes the "
                                          "trust you've already built on camera."),
        ("Paid community or membership", "Recurring revenue from the audience that wants more than the "
                                           "free content, without building a full course."),
        ("Affiliate/referral partnerships", "Lowest effort - monetizes tools or platforms you already "
                                              "recommend on camera anyway."),
        ("Sponsored content", "Works once view counts are consistent enough for brands to plan around."),
    ]
    for name, desc in avenues:
        story.append(Paragraph(name, s["h2"]))
        story.append(Paragraph(desc, s["body"]))

    story.append(Spacer(1, 0.25 * inch))
    story.append(Paragraph(
        "This audit was generated from your channel's public YouTube data only - upload timing, "
        "recent view counts, and your channel description. It doesn't reflect your other "
        "platforms, funnel, or anything not visible on YouTube itself.",
        s["footer"],
    ))

    page_decorator = _header_footer(accent_hex)
    doc.build(story, onFirstPage=page_decorator, onLaterPages=page_decorator)
    buf.seek(0)
    return buf.read()


def build(output_path: str, *, lead: dict, accent_color: str = DEFAULT_ACCENT):
    _register_fonts()
    cover_bytes = _build_cover(accent_color, lead["title"])
    body_bytes = _build_body(accent_color, lead)

    writer = PdfWriter()
    for page in PdfReader(io.BytesIO(cover_bytes)).pages:
        writer.add_page(page)
    for page in PdfReader(io.BytesIO(body_bytes)).pages:
        writer.add_page(page)

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    with open(output_path, "wb") as f:
        writer.write(f)

    print(f"Wrote {output_path}")
