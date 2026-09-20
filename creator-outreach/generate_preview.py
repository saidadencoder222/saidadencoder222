"""
Builds the real preview PDF attached to the creator outreach pitch.

This has to actually contain useful, standalone content - it's what
proves the "digital product" claim in the email is true, the same
principle as the auto-generated demo sites in biz-outreach.
"""

import os

from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer

OUTPUT_PATH = os.path.join("assets", "listen_first_preview.pdf")

styles = getSampleStyleSheet()

title_style = ParagraphStyle(
    "TitleBig", parent=styles["Title"], fontSize=28, leading=34, spaceAfter=12,
)
subtitle_style = ParagraphStyle(
    "Subtitle", parent=styles["Normal"], fontSize=14, alignment=TA_CENTER,
    textColor="#555555", spaceAfter=6,
)
h1 = ParagraphStyle("H1", parent=styles["Heading1"], fontSize=18, spaceBefore=18, spaceAfter=10)
h2 = ParagraphStyle("H2", parent=styles["Heading2"], fontSize=13, spaceBefore=12, spaceAfter=6,
                     textColor="#1f2937")
body = ParagraphStyle("Body", parent=styles["Normal"], fontSize=11, leading=16, spaceAfter=10)
script_style = ParagraphStyle("Script", parent=styles["Normal"], fontSize=11, leading=16,
                               leftIndent=18, textColor="#374151", spaceAfter=10,
                               backColor="#f3f4f6", borderPadding=8)
footer_style = ParagraphStyle("Footer", parent=styles["Normal"], fontSize=9,
                               textColor="#9ca3af", alignment=TA_CENTER)


def build():
    doc = SimpleDocTemplate(
        OUTPUT_PATH, pagesize=letter,
        topMargin=0.9 * inch, bottomMargin=0.9 * inch,
        leftMargin=0.9 * inch, rightMargin=0.9 * inch,
    )
    story = []

    # Cover
    story.append(Spacer(1, 1.8 * inch))
    story.append(Paragraph("Listen First", title_style))
    story.append(Paragraph("A Parent's Guide to Getting Kids to Actually Listen", subtitle_style))
    story.append(Spacer(1, 0.3 * inch))
    story.append(Paragraph("PREVIEW EDITION - 4 of 12 chapters", subtitle_style))
    story.append(PageBreak())

    # Intro
    story.append(Paragraph("Why \"just listen\" doesn't work", h1))
    story.append(Paragraph(
        "Most advice about getting kids to listen focuses on the wrong moment: what to say "
        "after they've already ignored you. By then, you're both frustrated and it's too late "
        "to prevent the standoff. The four techniques in this preview work earlier - before "
        "the instruction even leaves your mouth - so it lands the first time far more often.",
        body,
    ))
    story.append(Paragraph(
        "None of this requires yelling, bribing, or counting to three. It requires changing "
        "four small habits. Here they are.",
        body,
    ))

    # Chapter 1
    story.append(Paragraph("1. Connect Before You Correct", h1))
    story.append(Paragraph(
        "A child's brain has to feel safe and connected before it can process an instruction. "
        "Giving a direction from across the room, mid-tantrum, or the instant you walk in the "
        "door skips this step entirely - which is why it so often gets ignored.",
        body,
    ))
    story.append(Paragraph("Try this instead:", h2))
    story.append(Paragraph(
        "Get physically close, at their eye level, and make brief contact - a hand on the "
        "shoulder, their name said gently - before you say what you need. This takes under "
        "five seconds and dramatically raises the odds the instruction is actually heard.",
        script_style,
    ))

    # Chapter 2
    story.append(Paragraph("2. Say Less, Not More", h1))
    story.append(Paragraph(
        "\"Okay, so I need you to put your shoes on, and grab your backpack, and don't forget "
        "your water bottle, and hurry up because we're late\" is five instructions stacked into "
        "one breath. A young child processes one at a time. The rest becomes noise.",
        body,
    ))
    story.append(Paragraph("Try this instead:", h2))
    story.append(Paragraph(
        "\"Shoes on.\" Wait. Once it's done: \"Backpack.\" One instruction, one word if possible, "
        "said once. Resist the urge to repeat it three different ways - repetition trains kids "
        "to wait for the third, louder version before responding.",
        script_style,
    ))

    story.append(PageBreak())

    # Chapter 3
    story.append(Paragraph("3. Offer a Choice, Not a Command", h1))
    story.append(Paragraph(
        "Commands invite resistance because they remove all control from the child. A limited "
        "choice keeps you in charge of the outcome while giving them genuine control over how "
        "they get there - which is usually all the resistance was actually about.",
        body,
    ))
    story.append(Paragraph("Try this instead:", h2))
    story.append(Paragraph(
        "Instead of \"Get in the bath now,\" try \"Do you want to walk to the bath or hop like "
        "a bunny?\" Both options end with them in the bath. Only one invites a fight.",
        script_style,
    ))

    # Chapter 4
    story.append(Paragraph("4. Follow Through, Calmly, Every Time", h1))
    story.append(Paragraph(
        "Kids learn what actually happens, not what you say will happen. If \"we're leaving in "
        "five minutes\" is never actually enforced, it stops meaning anything - and neither does "
        "anything else you say after it.",
        body,
    ))
    story.append(Paragraph("Try this instead:", h2))
    story.append(Paragraph(
        "State the boundary once, calmly, and then follow through exactly as stated - even if "
        "that means leaving with one shoe on. The consistency, not the severity, is what builds "
        "the habit of listening the first time.",
        script_style,
    ))

    story.append(Spacer(1, 0.3 * inch))
    story.append(Paragraph(
        "This preview covers 4 of the 12 chapters in the full Listen First guide, which also "
        "covers sibling conflict, public meltdowns, screen-time transitions, and age-specific "
        "scripts from toddler through preteen.",
        body,
    ))
    story.append(Spacer(1, 0.4 * inch))
    story.append(Paragraph("Preview shared for review purposes - not for redistribution.", footer_style))

    doc.build(story)
    print(f"Wrote {OUTPUT_PATH}")


if __name__ == "__main__":
    os.makedirs("assets", exist_ok=True)
    build()
