"""
Builds the preview PDF attached to the creator outreach pitch, with a
personalized cover per creator (their own accent color, drawn/derived -
see personalize.py - rather than an identical document for everyone).

Content has to actually be real and useful, same principle as the
auto-generated demo sites in biz-outreach - this proves the "digital
product" claim in the email is true.

Uses embedded serif/sans fonts (DejaVu Serif for headings, Liberation
Sans for body) instead of the PDF built-in Helvetica default, and a
thin accent-colored header bar on every body page for a more designed,
less "default reportlab doc" look - all from fonts already on disk, no
network dependency.
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
from reportlab.platypus import (Flowable, HRFlowable, PageBreak, Paragraph,
                                 SimpleDocTemplate, Spacer)
from pypdf import PdfReader, PdfWriter

FONT_DIR_DEJAVU = "/usr/share/fonts/truetype/dejavu"
FONT_DIR_LIBERATION = "/usr/share/fonts/truetype/liberation"

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


class IconBadge(Flowable):
    """A small drawn (not fetched) numbered circle badge - a real generated
    image with zero network dependency or copyright risk."""

    def __init__(self, number: int, color_hex: str, size: float = 0.44 * inch):
        super().__init__()
        self.number = number
        self.color = colors.HexColor(color_hex)
        self.size = size
        self.width = size
        self.height = size

    def draw(self):
        c = self.canv
        c.setFillColor(self.color)
        c.circle(self.size / 2, self.size / 2, self.size / 2, fill=1, stroke=0)
        c.setFillColor(colors.white)
        c.setFont("Serif-Bold", self.size * 0.5)
        c.drawCentredString(self.size / 2, self.size / 2 - self.size * 0.17, str(self.number))


DEFAULT_OUTPUT = os.path.join("assets", "listen_first_preview.pdf")
DEFAULT_ACCENT = "#1f2937"

styles = getSampleStyleSheet()


def _styles(accent_hex: str):
    accent = colors.HexColor(accent_hex)
    return {
        "h1": ParagraphStyle("H1", parent=styles["Heading1"], fontName="Serif-Bold",
                              fontSize=19, leading=23, spaceBefore=18, spaceAfter=10,
                              textColor=accent),
        "h2": ParagraphStyle("H2", parent=styles["Heading2"], fontName="Sans-Bold",
                              fontSize=12, spaceBefore=12, spaceAfter=6,
                              textColor=colors.HexColor("#1f2937")),
        "body": ParagraphStyle("Body", parent=styles["Normal"], fontName="Sans",
                                fontSize=10.5, leading=16, spaceAfter=10,
                                textColor=colors.HexColor("#27272a")),
        "script": ParagraphStyle("Script", parent=styles["Normal"], fontName="Sans",
                                  fontSize=10.5, leading=16, leftIndent=18,
                                  textColor=colors.HexColor("#374151"), spaceAfter=10,
                                  backColor=colors.HexColor("#f3f4f6"), borderPadding=10),
        "footer": ParagraphStyle("Footer", parent=styles["Normal"], fontName="Sans-Italic",
                                  fontSize=9, textColor=colors.HexColor("#9ca3af"),
                                  alignment=TA_CENTER),
        "accent": accent,
    }


def _build_cover(accent_hex: str, channel_title: str, avatar_path: str = None) -> bytes:
    """Draws a full-bleed colored cover page, personalized per creator via
    accent color (and their own avatar when one is available/reachable)."""
    buf = io.BytesIO()
    c = pdfcanvas.Canvas(buf, pagesize=letter)
    width, height = letter
    accent = colors.HexColor(accent_hex)

    c.setFillColor(accent)
    c.rect(0, 0, width, height, fill=1, stroke=0)

    # Decorative layered circles - drawn, not fetched, so this always
    # renders regardless of network access to any image host.
    c.setFillColor(colors.Color(1, 1, 1, alpha=0.06))
    c.circle(width * 0.85, height * 0.88, 2.2 * inch, fill=1, stroke=0)
    c.setFillColor(colors.Color(1, 1, 1, alpha=0.05))
    c.circle(width * 0.1, height * 0.1, 1.6 * inch, fill=1, stroke=0)
    c.setFillColor(colors.Color(1, 1, 1, alpha=0.04))
    c.circle(width * 0.5, height * 0.42, 3 * inch, fill=1, stroke=0)

    if avatar_path and os.path.exists(avatar_path):
        avatar_size = 1.4 * inch
        c.drawImage(
            avatar_path,
            (width - avatar_size) / 2, height - 2.6 * inch,
            width=avatar_size, height=avatar_size, mask="auto",
        )
        title_y = height - 3.4 * inch
    else:
        title_y = height - 2.7 * inch

    # Thin rule above the title, a common editorial/book-cover motif.
    c.setStrokeColor(colors.white)
    c.setLineWidth(1)
    c.line(width / 2 - 0.6 * inch, title_y + 0.55 * inch, width / 2 + 0.6 * inch, title_y + 0.55 * inch)

    c.setFillColor(colors.white)
    c.setFont("Serif-Bold", 32)
    c.drawCentredString(width / 2, title_y, "Listen First")

    c.setFont("Sans", 13)
    c.drawCentredString(width / 2, title_y - 0.42 * inch,
                         "A Parent's Guide to Getting Kids to Actually Listen")

    if channel_title:
        c.setFont("Sans-Italic", 11.5)
        c.drawCentredString(width / 2, title_y - 0.92 * inch, f"Prepared for {channel_title}")

    c.setFont("Sans", 9.5)
    c.drawCentredString(width / 2, 1 * inch, "PREVIEW EDITION   |   4 of 12 chapters")

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
        canv.drawRightString(width - 0.9 * inch, 0.55 * inch, f"Listen First - Preview - {doc.page}")
        canv.restoreState()

    return draw


def _build_body(accent_hex: str) -> bytes:
    s = _styles(accent_hex)
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=letter,
        topMargin=1.0 * inch, bottomMargin=0.9 * inch,
        leftMargin=0.9 * inch, rightMargin=0.9 * inch,
    )
    story = []

    story.append(Paragraph("Why “just listen” doesn't work", s["h1"]))
    story.append(HRFlowable(width="100%", color=s["accent"], thickness=1.2, spaceAfter=12))
    story.append(Paragraph(
        "Most advice about getting kids to listen focuses on the wrong moment: what to say "
        "after they've already ignored you. By then, you're both frustrated and it's too late "
        "to prevent the standoff. The four techniques in this preview work earlier - before "
        "the instruction even leaves your mouth - so it lands the first time far more often.",
        s["body"],
    ))
    story.append(Paragraph(
        "None of this requires yelling, bribing, or counting to three. It requires changing "
        "four small habits. Here they are.",
        s["body"],
    ))

    story.append(IconBadge(1, accent_hex))
    story.append(Paragraph("Connect Before You Correct", s["h1"]))
    story.append(Paragraph(
        "A child's brain has to feel safe and connected before it can process an instruction. "
        "Giving a direction from across the room, mid-tantrum, or the instant you walk in the "
        "door skips this step entirely - which is why it so often gets ignored.",
        s["body"],
    ))
    story.append(Paragraph("Try this instead:", s["h2"]))
    story.append(Paragraph(
        "Get physically close, at their eye level, and make brief contact - a hand on the "
        "shoulder, their name said gently - before you say what you need. This takes under "
        "five seconds and dramatically raises the odds the instruction is actually heard.",
        s["script"],
    ))

    story.append(IconBadge(2, accent_hex))
    story.append(Paragraph("Say Less, Not More", s["h1"]))
    story.append(Paragraph(
        "\"Okay, so I need you to put your shoes on, and grab your backpack, and don't forget "
        "your water bottle, and hurry up because we're late\" is five instructions stacked into "
        "one breath. A young child processes one at a time. The rest becomes noise.",
        s["body"],
    ))
    story.append(Paragraph("Try this instead:", s["h2"]))
    story.append(Paragraph(
        "\"Shoes on.\" Wait. Once it's done: \"Backpack.\" One instruction, one word if possible, "
        "said once. Resist the urge to repeat it three different ways - repetition trains kids "
        "to wait for the third, louder version before responding.",
        s["script"],
    ))

    story.append(PageBreak())

    story.append(IconBadge(3, accent_hex))
    story.append(Paragraph("Offer a Choice, Not a Command", s["h1"]))
    story.append(HRFlowable(width="100%", color=s["accent"], thickness=1.2, spaceAfter=12))
    story.append(Paragraph(
        "Commands invite resistance because they remove all control from the child. A limited "
        "choice keeps you in charge of the outcome while giving them genuine control over how "
        "they get there - which is usually all the resistance was actually about.",
        s["body"],
    ))
    story.append(Paragraph("Try this instead:", s["h2"]))
    story.append(Paragraph(
        "Instead of \"Get in the bath now,\" try \"Do you want to walk to the bath or hop like "
        "a bunny?\" Both options end with them in the bath. Only one invites a fight.",
        s["script"],
    ))

    story.append(IconBadge(4, accent_hex))
    story.append(Paragraph("Follow Through, Calmly, Every Time", s["h1"]))
    story.append(Paragraph(
        "Kids learn what actually happens, not what you say will happen. If \"we're leaving in "
        "five minutes\" is never actually enforced, it stops meaning anything - and neither does "
        "anything else you say after it.",
        s["body"],
    ))
    story.append(Paragraph("Try this instead:", s["h2"]))
    story.append(Paragraph(
        "State the boundary once, calmly, and then follow through exactly as stated - even if "
        "that means leaving with one shoe on. The consistency, not the severity, is what builds "
        "the habit of listening the first time.",
        s["script"],
    ))

    story.append(Spacer(1, 0.3 * inch))
    story.append(Paragraph(
        "This preview covers 4 of the 12 chapters in the full Listen First guide, which also "
        "covers sibling conflict, public meltdowns, screen-time transitions, and age-specific "
        "scripts from toddler through preteen.",
        s["body"],
    ))
    story.append(Paragraph(
        "Note: this preview is text-only. The finished guide includes illustrations throughout - "
        "this early copy doesn't, so treat it as an example of the writing and content rather "
        "than the final polished layout.",
        s["footer"],
    ))
    story.append(Spacer(1, 0.4 * inch))
    story.append(Paragraph("Preview shared for review purposes - not for redistribution.", s["footer"]))

    page_decorator = _header_footer(accent_hex)
    doc.build(story, onFirstPage=page_decorator, onLaterPages=page_decorator)
    buf.seek(0)
    return buf.read()


def build(output_path: str = DEFAULT_OUTPUT, *, channel_title: str = None,
          accent_color: str = DEFAULT_ACCENT, avatar_path: str = None):
    _register_fonts()
    cover_bytes = _build_cover(accent_color, channel_title, avatar_path)
    body_bytes = _build_body(accent_color)

    writer = PdfWriter()
    for page in PdfReader(io.BytesIO(cover_bytes)).pages:
        writer.add_page(page)
    for page in PdfReader(io.BytesIO(body_bytes)).pages:
        writer.add_page(page)

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    with open(output_path, "wb") as f:
        writer.write(f)

    print(f"Wrote {output_path}")


if __name__ == "__main__":
    build()
