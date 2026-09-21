"""Composites a click-worthy thumbnail: the first sourced historical image,
darkened for contrast, with bold title text overlaid.
"""
from PIL import Image, ImageDraw, ImageEnhance, ImageFont

FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def _wrap_text(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if draw.textbbox((0, 0), candidate, font=font)[2] <= max_width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def build_thumbnail(cfg: dict, background_path: str, title_text: str, out_path: str) -> str:
    size = tuple(cfg["thumbnail"]["size"])
    img = Image.open(background_path).convert("RGB").resize(size)
    img = ImageEnhance.Contrast(ImageEnhance.Brightness(img).enhance(0.6)).enhance(1.1)

    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype(FONT_PATH, 88)
    except OSError:
        font = ImageFont.load_default()

    margin = 60
    max_width = size[0] - 2 * margin
    lines = _wrap_text(draw, title_text.upper(), font, max_width)[:4]

    line_height = font.size + 14
    total_height = line_height * len(lines)
    y = (size[1] - total_height) / 2

    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        x = (size[0] - (bbox[2] - bbox[0])) / 2
        for dx in (-4, 0, 4):
            for dy in (-4, 0, 4):
                draw.text((x + dx, y + dy), line, font=font, fill=(0, 0, 0))
        draw.text((x, y), line, font=font, fill=(255, 210, 0))
        y += line_height

    img.save(out_path, quality=92)
    return out_path
