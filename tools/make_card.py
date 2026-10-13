#!/usr/bin/env python3
"""Build the Glamis Dunes Rentals email signature as sliced images.

Dark mode in email apps (Front, Gmail, Outlook, Apple Mail) recolors HTML
backgrounds and text but leaves images alone, so the whole card is drawn as
images. It is cut into slices so the phone, email and website lines each keep
their own link.

Usage:
  python3 tools/make_card.py --name "Matt Gordon" --email matt@glamisrent.com

Writes shared slices to common/ (once) and the person's slices plus their
signature.html to people/<slug>/.
"""
import argparse
import os
import re
from PIL import Image, ImageDraw, ImageFont

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = "https://raw.githubusercontent.com/mgordoness/glamis-email-signature/main"
K = 2  # images are stored at 2x and shown at 1x so they stay sharp on phones

SAND_TINT = (243, 240, 233)
SAND = (150, 134, 101)
BROWN = (58, 53, 42)
BAR_TEXT = (205, 191, 159)
INK = (51, 51, 51)
NAVY = (6, 74, 115)

FONT_DIR = "/usr/share/fonts/truetype/liberation"
BOLD = os.path.join(FONT_DIR, "LiberationSans-Bold.ttf")
REG = os.path.join(FONT_DIR, "LiberationSans-Regular.ttf")
ARROW_FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

PHONE = "(760) 573-6825"
PHONE_TEL = "+17605736825"
WEB = "glamisrent.com"
WEB_URL = "https://glamisrent.com"

# Layout in display pixels (matches the approved HTML design)
W = 560
TOP_H = 187          # 18 pad + 151 logo + 18 pad
LEFT_W = 228         # logo column incl. padding and the sand divider
RIGHT_W = W - LEFT_W
TEXT_X = 7           # text starts 7px into the right column (235 overall)
BLOCK_TOP = 39       # text block is vertically centred in the 187px band
NAME_H = BLOCK_TOP + 24 + 16 + 9   # 88: top pad + name + title + gap
LINE_H = 20
BOTTOM_H = TOP_H - NAME_H - 3 * LINE_H  # 39
BAR_H = 36


def font(path, px):
    return ImageFont.truetype(path, px * K)


def canvas(w, h, color=SAND_TINT):
    return Image.new("RGB", (w * K, h * K), color)


def draw_tracked(d, x, baseline, text, f, fill, track=0.0):
    """Draw text on a baseline with letter-spacing (track in display px)."""
    for ch in text:
        d.text((x, baseline), ch, font=f, fill=fill, anchor="ls")
        x += d.textlength(ch, font=f) + track * K
    return x


def baseline_for(top, line_h, f):
    asc, desc = f.getmetrics()
    return top * K + (line_h * K - (asc + desc)) / 2 + asc


def save(img, rel):
    path = os.path.join(REPO, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    img.save(path, optimize=True)
    return rel


def make_common():
    out = {}
    # Logo column: Glamis + BRP Experiences block plus the sand divider
    img = canvas(LEFT_W, TOP_H)
    logo = Image.open(os.path.join(REPO, "glamis-brp-signature-logo.png")).convert("RGB")
    logo = logo.resize((170 * K, 151 * K), Image.LANCZOS)
    img.paste(logo, (22 * K, 18 * K))
    d = ImageDraw.Draw(img)
    text_block_h = 24 + 16 + 9 + 3 * LINE_H
    d.rectangle([214 * K, BLOCK_TOP * K, 217 * K - 1, (BLOCK_TOP + text_block_h) * K - 1], fill=SAND)
    out["logo"] = save(img, "common/logo-block.png")

    out["call"] = save(contact_line("CALL", PHONE, INK, False), "common/call.png")
    out["web"] = save(contact_line("WEB", WEB, NAVY, True), "common/web.png")
    out["bottom"] = save(canvas(RIGHT_W, BOTTOM_H), "common/bottom.png")

    bar = canvas(W, BAR_H, BROWN)
    d = ImageDraw.Draw(bar)
    f = font(BOLD, 12)
    base = baseline_for(0, BAR_H, f)
    x = draw_tracked(d, 22 * K, base, "START YOUR ADVENTURE ", f, BAR_TEXT, 2)
    # Liberation Sans has no arrow glyph, so the arrow comes from DejaVu Sans
    d.text((x, base), "→", font=font(ARROW_FONT, 13), fill=BAR_TEXT, anchor="ls")
    out["bar"] = save(bar, "common/bar.png")
    return out


def contact_line(label, value, value_color, value_bold):
    img = canvas(RIGHT_W, LINE_H)
    d = ImageDraw.Draw(img)
    fv = font(BOLD if value_bold else REG, 13)
    fl = font(BOLD, 10)
    base = baseline_for(0, LINE_H, fv)
    x = draw_tracked(d, TEXT_X * K, base, label, fl, SAND, 1.5)
    x += d.textlength("  ", font=fl)
    d.text((x, base), value, font=fv, fill=value_color, anchor="ls")
    return img


def make_person(name, email, slug):
    img = canvas(RIGHT_W, NAME_H)
    d = ImageDraw.Draw(img)
    fn = font(BOLD, 20)
    d.text((TEXT_X * K, baseline_for(BLOCK_TOP, 24, fn)), name, font=fn, fill=BROWN, anchor="ls")
    ft = font(BOLD, 11)
    draw_tracked(d, TEXT_X * K, baseline_for(BLOCK_TOP + 24, 16, ft), "GLAMIS DUNES RENTALS", ft, SAND, 2)
    name_rel = save(img, f"people/{slug}/name.png")
    email_rel = save(contact_line("EMAIL", email, INK, False), f"people/{slug}/email.png")
    return name_rel, email_rel


def cell_img(rel, w, h, alt, href=None):
    img = (f'<img src="{RAW}/{rel}" width="{w}" height="{h}" alt="{alt}" '
           f'style="display:block;border:0;outline:none;width:{w}px;height:{h}px;">')
    if href:
        img = f'<a href="{href}" target="_blank" style="text-decoration:none;">{img}</a>'
    return f'<td style="padding:0;line-height:0;font-size:0;">{img}</td>'


def signature_html(c, name, email, name_rel, email_rel):
    t = 'cellpadding="0" cellspacing="0" border="0"'
    right = (f'<table {t} width="{RIGHT_W}" style="border-collapse:collapse;width:{RIGHT_W}px;"><tbody>'
             f'<tr>{cell_img(name_rel, RIGHT_W, NAME_H, f"{name} | Glamis Dunes Rentals")}</tr>'
             f'<tr>{cell_img(c["call"], RIGHT_W, LINE_H, "Call " + PHONE, "tel:" + PHONE_TEL)}</tr>'
             f'<tr>{cell_img(email_rel, RIGHT_W, LINE_H, "Email " + email, "mailto:" + email)}</tr>'
             f'<tr>{cell_img(c["web"], RIGHT_W, LINE_H, WEB, WEB_URL)}</tr>'
             f'<tr>{cell_img(c["bottom"], RIGHT_W, BOTTOM_H, "")}</tr>'
             '</tbody></table>')
    return (f'<table {t} width="{W}" style="border-collapse:collapse;width:{W}px;"><tbody>'
            f'<tr>{cell_img(c["logo"], LEFT_W, TOP_H, "Glamis Dunes Rentals | BRP Experiences", WEB_URL)}'
            f'<td style="padding:0;line-height:0;font-size:0;vertical-align:top;">{right}</td></tr>'
            f'<tr><td colspan="2" style="padding:0;line-height:0;font-size:0;">'
            f'<a href="{WEB_URL}" target="_blank" style="text-decoration:none;">'
            f'<img src="{RAW}/{c["bar"]}" width="{W}" height="{BAR_H}" alt="Start your adventure at glamisrent.com" '
            f'style="display:block;border:0;outline:none;width:{W}px;height:{BAR_H}px;"></a></td></tr>'
            '</tbody></table>')


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--name", required=True)
    p.add_argument("--email", required=True)
    a = p.parse_args()
    slug = re.sub(r"[^a-z0-9]+", "-", a.name.lower()).strip("-")
    common = make_common()
    name_rel, email_rel = make_person(a.name, a.email, slug)
    html = signature_html(common, a.name, a.email, name_rel, email_rel)
    path = os.path.join(REPO, f"people/{slug}/signature.html")
    with open(path, "w") as fh:
        fh.write(html + "\n")
    print(path)


if __name__ == "__main__":
    main()
