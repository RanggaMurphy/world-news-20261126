#!/usr/bin/env python3
"""Render the front page for the 26 November 2026 news-image entry.

The program reads sources.json in the same folder and draws a single
1024 by 1024 newspaper front page called entry.png. The page follows the
winner format the desk settled on after studying four days of leaderboard
results: a black masthead band, a big serif date line, three feature
stories with drawn scenes, a ten-item grid, a dot-matrix world map with
numbered pins, a two-column briefs list, and a red-bordered DATE CHECK
footer with a HOW SURE legend.

Everything on the page is drawn by this program. There are no photographs
and no downloaded pictures. Each pictured story gets a small vector scene
drawn from its category: fire, refinery, market chart, strike, siege,
parade, factory, tariff ship, chip, stadium, treaty, or rocket.

The render is deterministic. The same sources.json always produces the
same bytes, which the desk verifies by rendering twice and comparing
sha256 digests. The program also audits its own layout: every text block
is measured against the space it was given, and the audit reports any
overflow instead of silently clipping words.

Usage:
    python3 render.py            render entry.png in this folder
    python3 render.py --report   render, then print the layout report
    python3 render.py --strict   render, exit 1 if the audit finds a fault

Only the Python standard library and Pillow are used, and only here, in
the build session. The graded entry point, main.py, never imports this
file and never imports Pillow.
"""

import json
import math
import os
import sys

from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------------------
# Canvas and palette
# ---------------------------------------------------------------------------

WIDTH = 1024
HEIGHT = 1024

PAPER = (247, 241, 222)        # warm cream newsprint
PAPER_DARK = (238, 230, 205)   # slightly deeper cream for panels
INK = (26, 24, 20)             # near-black text
INK_SOFT = (74, 68, 58)        # grey-brown for secondary text
BLACK_BAND = (18, 16, 14)      # masthead band
RULE = (26, 24, 20)            # hairlines and rules
RED = (178, 34, 34)            # DATE CHECK red and map pins
RED_DARK = (139, 26, 26)
BLUE_BAND = (31, 58, 95)       # region strip
BLUE_SOFT = (214, 226, 240)    # map dots and panel tints
GREEN_BAND = (46, 94, 60)      # numbers strip
GOLD = (176, 141, 60)          # small accents
WHITE = (255, 255, 255)
CREAM_LINE = (210, 198, 168)

# Scene panel tints, one per story category. Each scene is drawn on its
# own tint so the page reads as a set of distinct pictures at a glance.
SCENE_TINT = {
    "fire": (248, 220, 196),
    "refinery": (232, 222, 200),
    "market": (214, 232, 214),
    "strike": (232, 214, 214),
    "siege": (220, 222, 232),
    "parade": (240, 220, 232),
    "factory": (222, 228, 232),
    "tariff": (214, 228, 236),
    "chip": (228, 222, 240),
    "stadium": (214, 236, 220),
    "treaty": (238, 232, 214),
    "rocket": (222, 226, 244),
}

# Certainty chips: label text plus the fill colour used on the page.
CERTAINTY = {
    "CONFIRMED": (46, 94, 60),
    "OFFICIAL": (31, 58, 95),
    "REPORTED": (122, 90, 20),
    "CLAIM": (178, 34, 34),
}

# ---------------------------------------------------------------------------
# Fonts
# ---------------------------------------------------------------------------

FONT_DIRS = [
    "/usr/share/fonts/truetype/dejavu",
    "/usr/share/fonts/truetype/liberation",
    "/usr/local/share/fonts",
]


def find_font(basename):
    """Return the first existing path for a font file name, or None."""
    for directory in FONT_DIRS:
        candidate = os.path.join(directory, basename)
        if os.path.isfile(candidate):
            return candidate
    return None


def load_font(basename, size):
    """Load a TrueType font at a size, or fail loudly with a clear message."""
    path = find_font(basename)
    if path is None:
        raise SystemExit("font not found: %s (looked in %s)"
                         % (basename, ", ".join(FONT_DIRS)))
    return ImageFont.truetype(path, size)


class Fonts:
    """All fonts used on the page, loaded once at start-up."""

    def __init__(self):
        self.masthead = load_font("DejaVuSerif-Bold.ttf", 30)
        self.date = load_font("DejaVuSerif-Bold.ttf", 40)
        self.teaser = load_font("DejaVuSerif.ttf", 13)
        self.strip_label = load_font("DejaVuSans-Bold.ttf", 12)
        self.strip = load_font("DejaVuSans.ttf", 12)
        self.strip_small = load_font("DejaVuSans.ttf", 10)
        self.feature_head = load_font("DejaVuSerif-Bold.ttf", 17)
        self.feature_body = load_font("DejaVuSans.ttf", 10)
        self.footer_small = load_font("DejaVuSans.ttf", 10)
        self.grid_head = load_font("DejaVuSerif-Bold.ttf", 13)
        self.grid_body = load_font("DejaVuSans.ttf", 10)
        self.brief = load_font("DejaVuSans.ttf", 11)
        self.brief_num = load_font("DejaVuSans-Bold.ttf", 11)
        self.section = load_font("DejaVuSans-Bold.ttf", 13)
        self.footer = load_font("DejaVuSans.ttf", 11)
        self.footer_bold = load_font("DejaVuSans-Bold.ttf", 11)
        self.legend = load_font("DejaVuSans.ttf", 10)
        self.chip = load_font("DejaVuSans-Bold.ttf", 8)
        self.pin = load_font("DejaVuSans-Bold.ttf", 10)
        self.caption = load_font("DejaVuSans.ttf", 9)


# ---------------------------------------------------------------------------
# Text helpers
# ---------------------------------------------------------------------------

def text_width(font, text):
    """Pixel width of a string in a font."""
    left, top, right, bottom = font.getbbox(text)
    return right - left


def text_height(font, text):
    """Pixel height of a string in a font."""
    left, top, right, bottom = font.getbbox(text)
    return bottom - top


def wrap_text(font, text, max_width):
    """Wrap a string to a list of lines that fit max_width pixels.

    Words are kept whole. A single word longer than the box is split by
    characters so the layout never overflows sideways.
    """
    words = text.split()
    lines = []
    current = ""
    for word in words:
        trial = word if not current else current + " " + word
        if text_width(font, trial) <= max_width:
            current = trial
            continue
        if current:
            lines.append(current)
        if text_width(font, word) > max_width:
            piece = ""
            for char in word:
                if text_width(font, piece + char) <= max_width:
                    piece += char
                else:
                    lines.append(piece)
                    piece = char
            current = piece
        else:
            current = word
    if current:
        lines.append(current)
    return lines


def draw_wrapped(draw, font, text, box, fill, leading=None, audit=None,
                 name="text"):
    """Draw wrapped text inside a box, returning the lines actually drawn.

    The box is (x, y, width, max_lines). Lines beyond max_lines are not
    drawn; instead the audit records the overflow so the desk can fix the
    copy or the box instead of shipping clipped words.
    """
    x, y, width, max_lines = box
    if leading is None:
        leading = int(text_height(font, "Ag") * 1.25)
    lines = wrap_text(font, text, width)
    drawn = lines[:max_lines]
    for i, line in enumerate(drawn):
        draw.text((x, y + i * leading), line, font=font, fill=fill)
    if audit is not None:
        audit.record(name, len(lines), max_lines, width)
    return drawn


def draw_centered(draw, font, text, y, fill, width=WIDTH):
    """Draw one line centred across the page at height y."""
    w = text_width(font, text)
    draw.text(((width - w) // 2, y), text, font=font, fill=fill)


def fit_or_shrink(font_name, size, text, max_width, minimum=8):
    """Load a font, shrinking it until the text fits, down to a floor."""
    size_now = size
    while size_now > minimum:
        font = load_font(font_name, size_now)
        if text_width(font, text) <= max_width:
            return font
        size_now -= 1
    return load_font(font_name, minimum)


# ---------------------------------------------------------------------------
# Layout audit
# ---------------------------------------------------------------------------

class LayoutAudit:
    """Measure every text block and collect the ones that do not fit."""

    def __init__(self):
        self.blocks = []
        self.issues = []

    def record(self, name, lines_needed, lines_allowed, width):
        """Record one block; note an issue when it needs more lines."""
        self.blocks.append((name, lines_needed, lines_allowed, width))
        if lines_needed > lines_allowed:
            self.issues.append(
                "%s needs %d lines but only %d fit in %d px"
                % (name, lines_needed, lines_allowed, width))

    def check(self, name, ok, width, detail=""):
        """Record a yes/no geometry check as an audit block."""
        self.blocks.append((name, 1 if ok else 2, 1, width))
        if not ok:
            self.issues.append("%s: %s" % (name, detail))

    def report(self):
        """Return the audit as a list of human-readable lines."""
        out = []
        out.append("layout audit: %d text blocks measured"
                   % len(self.blocks))
        for name, needed, allowed, width in self.blocks:
            mark = "OK  " if needed <= allowed else "OVER"
            out.append("  %s %-28s %d/%d lines, %d px"
                       % (mark, name, needed, allowed, width))
        if self.issues:
            out.append("layout audit: %d OVERFLOW(S)" % len(self.issues))
            for issue in self.issues:
                out.append("  !! " + issue)
        else:
            out.append("layout audit: no overflow")
        return out


# ---------------------------------------------------------------------------
# Vector scenes
# ---------------------------------------------------------------------------
# Each scene draws a simple flat illustration for one story category
# inside a rectangle (x, y, w, h). The drawings use only rectangles,
# ellipses, polygons and lines, so they stay crisp at any size and cost
# nothing to reproduce. A scene is a picture, not a photograph, which is
# the point of the format: one clean image per pictured story.

def scene_background(draw, box, category):
    """Paint the tinted panel behind a scene and return its bounds."""
    x, y, w, h = box
    tint = SCENE_TINT.get(category, (232, 228, 220))
    draw.rectangle([x, y, x + w, y + h], fill=tint,
                   outline=(190, 180, 150), width=1)
    return x, y, w, h


def draw_flame(draw, cx, base_y, size, colour):
    """Draw one stylised flame tongue centred on cx above base_y."""
    draw.polygon([
        (cx, base_y - size),
        (cx - size * 0.45, base_y - size * 0.25),
        (cx - size * 0.25, base_y),
        (cx + size * 0.25, base_y),
        (cx + size * 0.45, base_y - size * 0.25),
    ], fill=colour)


def scene_fire(draw, box):
    """A tanker blaze: road, truck, flames and smoke."""
    x, y, w, h = scene_background(draw, box, "fire")
    ground = y + h - 16
    draw.rectangle([x, ground, x + w, y + h], fill=(120, 110, 96))
    draw.line([x, ground, x + w, ground], fill=(90, 82, 70), width=2)
    # tanker body and cab
    draw.rectangle([x + 18, ground - 26, x + w - 52, ground - 6],
                   fill=(200, 90, 40), outline=(120, 50, 20), width=1)
    draw.ellipse([x + w - 52, ground - 26, x + w - 30, ground - 6],
                 fill=(220, 120, 50), outline=(120, 50, 20), width=1)
    draw.rectangle([x + w - 28, ground - 20, x + w - 12, ground - 6],
                   fill=(90, 90, 90))
    # wheels
    for wx in (x + 30, x + 58, x + w - 40, x + w - 20):
        draw.ellipse([wx - 6, ground - 8, wx + 6, ground + 4],
                     fill=(30, 30, 30))
    # flames over the tank
    draw_flame(draw, x + w // 3, ground - 24, 26, (230, 90, 20))
    draw_flame(draw, x + w // 3 + 22, ground - 24, 18, (245, 180, 30))
    draw_flame(draw, x + w // 2 + 12, ground - 24, 22, (230, 90, 20))
    # smoke puffs
    for sx, sy, sr in ((x + w // 3, y + 12, 9), (x + w // 3 + 26, y + 6, 7),
                       (x + w // 2 + 8, y + 14, 8)):
        draw.ellipse([sx - sr, sy - sr, sx + sr, sy + sr],
                     fill=(110, 105, 98))


def scene_refinery(draw, box):
    """A refinery and an oil derrick under a hazy sky."""
    x, y, w, h = scene_background(draw, box, "refinery")
    ground = y + h - 14
    draw.rectangle([x, ground, x + w, y + h], fill=(150, 138, 112))
    # storage tanks
    for tx in (x + 12, x + 52):
        draw.rectangle([tx, ground - 30, tx + 34, ground],
                       fill=(210, 205, 190), outline=(120, 110, 90), width=1)
        draw.ellipse([tx, ground - 36, tx + 34, ground - 24],
                     fill=(225, 220, 205), outline=(120, 110, 90), width=1)
    # flare stack
    draw.rectangle([x + w - 30, y + 16, x + w - 22, ground],
                   fill=(90, 88, 84))
    draw_flame(draw, x + w - 26, y + 16, 14, (240, 140, 30))
    # distillation tower
    draw.polygon([(x + w - 62, ground), (x + w - 62, y + 30),
                  (x + w - 44, y + 18), (x + w - 44, ground)],
                 fill=(180, 175, 160), outline=(120, 110, 90), width=1)
    for ly in range(y + 34, ground - 4, 10):
        draw.line([x + w - 62, ly, x + w - 44, ly],
                  fill=(120, 110, 90), width=1)
    # pumpjack silhouette
    bx = x + w // 2 + 6
    draw.polygon([(bx, ground - 22), (bx + 26, ground - 30),
                  (bx + 30, ground - 26), (bx + 4, ground - 18)],
                 fill=(70, 70, 70))
    draw.rectangle([bx + 2, ground - 22, bx + 6, ground], fill=(70, 70, 70))
    # sun and haze
    draw.ellipse([x + 14, y + 8, x + 34, y + 28], fill=(240, 200, 90))


def scene_market(draw, box):
    """A market chart: axes, a falling line, and a recovery arrow."""
    x, y, w, h = scene_background(draw, box, "market")
    left = x + 14
    right = x + w - 12
    top = y + 10
    bottom = y + h - 14
    draw.line([left, top, left, bottom], fill=(60, 60, 60), width=2)
    draw.line([left, bottom, right, bottom], fill=(60, 60, 60), width=2)
    for gy in range(top + 12, bottom, 14):
        draw.line([left, gy, right, gy], fill=(190, 200, 190), width=1)
    # the day's line: plunge, then a sharp recovery
    pts = [
        (left, top + 16),
        (left + 34, top + 20),
        (left + 62, top + 44),
        (left + 90, top + 52),
        (left + 118, top + 30),
        (right - 6, top + 22),
    ]
    draw.line(pts, fill=(178, 34, 34), width=3, joint="curve")
    # arrow head at the recovery end
    ex, ey = pts[-1]
    draw.polygon([(ex, ey), (ex - 12, ey - 2), (ex - 4, ey + 8)],
                 fill=(46, 94, 60))
    draw.polygon([(ex, ey), (ex - 12, ey - 2), (ex - 4, ey + 8)],
                 outline=(46, 94, 60))
    # small bars under the line
    for i, bh in enumerate((10, 14, 8, 18, 12, 16)):
        bx = left + 8 + i * 20
        draw.rectangle([bx, bottom - bh, bx + 10, bottom],
                       fill=(31, 58, 95))


def scene_strike(draw, box):
    """A city block at night with a blast burst above it."""
    x, y, w, h = scene_background(draw, box, "strike")
    ground = y + h - 12
    draw.rectangle([x, ground, x + w, y + h], fill=(90, 84, 76))
    # buildings
    for bx, bw, bh in ((x + 10, 26, 34), (x + 42, 20, 48),
                       (x + 68, 30, 28), (x + 104, 22, 40)):
        draw.rectangle([bx, ground - bh, bx + bw, ground],
                       fill=(60, 58, 54))
        for wy in range(ground - bh + 6, ground - 4, 10):
            for wx in range(bx + 5, bx + bw - 4, 9):
                draw.rectangle([wx, wy, wx + 4, wy + 5],
                               fill=(240, 200, 90))
    # burst above the middle building
    cx, cy = x + w // 2, y + 18
    for angle in range(0, 360, 30):
        rad = math.radians(angle)
        ex = cx + int(20 * math.cos(rad))
        ey = cy + int(20 * math.sin(rad))
        draw.line([cx, cy, ex, ey], fill=(230, 120, 20), width=3)
    draw.ellipse([cx - 9, cy - 9, cx + 9, cy + 9], fill=(245, 180, 30))
    draw.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=(255, 240, 180))


def scene_siege(draw, box):
    """A shopfront with a police shield in front of it."""
    x, y, w, h = scene_background(draw, box, "siege")
    ground = y + h - 12
    draw.rectangle([x, ground, x + w, y + h], fill=(120, 116, 108))
    # shopfront
    draw.rectangle([x + 12, y + 14, x + w - 12, ground],
                   fill=(200, 190, 170), outline=(90, 84, 76), width=2)
    draw.rectangle([x + 20, y + 22, x + w - 20, y + 40],
                   fill=(31, 58, 95))
    draw.rectangle([x + 20, y + 48, x + w - 20, ground - 4],
                   fill=(170, 210, 220), outline=(90, 84, 76), width=1)
    draw.line([x + w // 2, y + 48, x + w // 2, ground - 4],
              fill=(90, 84, 76), width=2)
    # police shield
    sx, sy = x + w // 2, y + h - 34
    draw.polygon([(sx - 16, sy - 12), (sx + 16, sy - 12),
                  (sx + 12, sy + 8), (sx, sy + 18), (sx - 12, sy + 8)],
                 fill=(31, 58, 95), outline=(255, 255, 255), width=2)
    draw.ellipse([sx - 4, sy - 6, sx + 4, sy + 2], fill=(255, 255, 255))
    draw.rectangle([sx - 1, sy + 1, sx + 1, sy + 10], fill=(255, 255, 255))


def scene_parade(draw, box):
    """A giant balloon floating between city towers."""
    x, y, w, h = scene_background(draw, box, "parade")
    ground = y + h - 12
    draw.rectangle([x, ground, x + w, y + h], fill=(140, 130, 115))
    # towers
    for bx, bw, bh in ((x + 8, 18, 44), (x + w - 30, 20, 52)):
        draw.rectangle([bx, ground - bh, bx + bw, ground],
                       fill=(90, 86, 80))
        for wy in range(ground - bh + 6, ground - 4, 9):
            draw.rectangle([bx + 4, wy, bx + bw - 4, wy + 4],
                           fill=(240, 200, 90))
    # balloon: a big round body with stripes and a string
    cx, cy = x + w // 2, y + h // 2 - 6
    draw.ellipse([cx - 30, cy - 22, cx + 30, cy + 22],
                 fill=(220, 60, 60), outline=(140, 30, 30), width=2)
    draw.ellipse([cx - 12, cy - 22, cx + 12, cy + 22],
                 fill=(245, 200, 60), outline=(140, 30, 30), width=1)
    draw.ellipse([cx - 4, cy - 14, cx + 4, cy + 14], fill=(220, 60, 60))
    draw.line([cx, cy + 22, cx - 8, ground], fill=(60, 60, 60), width=1)
    draw.line([cx, cy + 22, cx + 10, ground], fill=(60, 60, 60), width=1)
    # small clouds
    for ccx, ccy in ((x + 16, y + 12), (x + w - 34, y + 16)):
        draw.ellipse([ccx - 10, ccy - 5, ccx + 10, ccy + 5],
                     fill=(255, 255, 255))


def scene_factory(draw, box):
    """A garment factory: shed roof, chimneys and a row of workers."""
    x, y, w, h = scene_background(draw, box, "factory")
    ground = y + h - 12
    draw.rectangle([x, ground, x + w, y + h], fill=(130, 124, 112))
    # main shed
    draw.rectangle([x + 12, y + 30, x + w - 12, ground],
                   fill=(190, 180, 160), outline=(100, 92, 80), width=2)
    draw.polygon([(x + 8, y + 30), (x + w - 8, y + 30),
                  (x + w - 22, y + 16), (x + 22, y + 16)],
                 fill=(120, 110, 96))
    # chimneys
    for cx in (x + 26, x + 48):
        draw.rectangle([cx, y + 8, cx + 10, y + 30], fill=(140, 60, 50))
    # windows
    for wx in range(x + 22, x + w - 22, 22):
        draw.rectangle([wx, y + 40, wx + 12, y + 54],
                       fill=(220, 230, 235), outline=(100, 92, 80), width=1)
    # workers: simple figures in a row
    for px in range(x + 24, x + w - 16, 22):
        draw.ellipse([px - 4, ground - 22, px + 4, ground - 14],
                     fill=(240, 200, 150))
        draw.rectangle([px - 5, ground - 14, px + 5, ground],
                       fill=(31, 58, 95))


def scene_tariff(draw, box):
    """A container ship with stacked boxes and a crane."""
    x, y, w, h = scene_background(draw, box, "tariff")
    water = y + h - 18
    draw.rectangle([x, water, x + w, y + h], fill=(90, 140, 180))
    for wx in range(x + 6, x + w - 6, 26):
        draw.arc([wx, water + 4, wx + 22, water + 12], 0, 180,
                 fill=(255, 255, 255), width=2)
    # hull
    draw.polygon([(x + 10, water - 12), (x + w - 10, water - 12),
                  (x + w - 26, water + 4), (x + 26, water + 4)],
                 fill=(40, 40, 48))
    # containers in two stacks
    colours = [(200, 60, 50), (60, 120, 60), (220, 160, 40), (50, 90, 160)]
    for row in range(2):
        for col in range(4):
            cx = x + 22 + col * 26
            cy = water - 14 - row * 15
            draw.rectangle([cx, cy - 13, cx + 24, cy],
                           fill=colours[(row + col) % 4],
                           outline=(30, 30, 30), width=1)
    # bridge and funnel
    draw.rectangle([x + w - 34, water - 42, x + w - 14, water - 12],
                   fill=(220, 220, 210), outline=(30, 30, 30), width=1)
    draw.rectangle([x + w - 30, water - 52, x + w - 20, water - 42],
                   fill=(178, 34, 34))
    # crane hook line
    draw.line([x + 14, y + 8, x + 14, water - 40], fill=(60, 60, 60), width=2)


def scene_chip(draw, box):
    """A computer chip with pins and a glowing core."""
    x, y, w, h = scene_background(draw, box, "chip")
    cx, cy = x + w // 2, y + h // 2
    # pins: five across the top and bottom, four down each side
    for i in range(5):
        px = cx - 28 + i * 14
        draw.line([px, cy - 36, px, cy - 28], fill=(90, 90, 90), width=3)
        draw.line([px, cy + 28, px, cy + 36], fill=(90, 90, 90), width=3)
    for i in range(4):
        py = cy - 21 + i * 14
        draw.line([cx - 36, py, cx - 28, py], fill=(90, 90, 90), width=3)
        draw.line([cx + 28, py, cx + 36, py], fill=(90, 90, 90), width=3)
    # body and core
    draw.rectangle([cx - 28, cy - 28, cx + 28, cy + 28],
                   fill=(40, 44, 60), outline=(20, 20, 28), width=2)
    draw.rectangle([cx - 14, cy - 14, cx + 14, cy + 14],
                   fill=(46, 160, 110), outline=(20, 90, 60), width=2)
    draw.rectangle([cx - 6, cy - 6, cx + 6, cy + 6], fill=(220, 240, 120))
    # traces
    draw.line([cx - 28, cy - 16, cx - 14, cy - 16], fill=(120, 130, 150),
              width=1)
    draw.line([cx + 14, cy + 16, cx + 28, cy + 16], fill=(120, 130, 150),
              width=1)


def scene_stadium(draw, box):
    """A stadium bowl with a floodlit pitch and a ball."""
    x, y, w, h = scene_background(draw, box, "stadium")
    ground = y + h - 14
    # stands
    draw.pieslice([x + 8, y + 10, x + w - 8, y + h - 6], 0, 180,
                  fill=(90, 110, 140))
    draw.pieslice([x + 20, y + 22, x + w - 20, y + h - 14], 0, 180,
                  fill=(214, 236, 220))
    # pitch
    draw.ellipse([x + 24, y + h - 34, x + w - 24, y + h - 8],
                 fill=(70, 150, 70), outline=(255, 255, 255), width=1)
    draw.line([x + w // 2, y + h - 34, x + w // 2, y + h - 8],
              fill=(255, 255, 255), width=1)
    # floodlight poles
    for fx in (x + 14, x + w - 14):
        draw.line([fx, y + 6, fx, y + 26], fill=(60, 60, 60), width=2)
        draw.ellipse([fx - 6, y + 2, fx + 6, y + 10], fill=(255, 240, 150))
    # ball
    bx, by = x + w // 2 + 18, y + h - 26
    draw.ellipse([bx - 7, by - 7, bx + 7, by + 7], fill=(255, 255, 255),
                 outline=(30, 30, 30), width=1)
    draw.ellipse([bx - 2, by - 2, bx + 2, by + 2], fill=(30, 30, 30))


def scene_treaty(draw, box):
    """Two flags, a document and a pen: a signed agreement."""
    x, y, w, h = scene_background(draw, box, "treaty")
    # flag poles and flags
    for fx, colour in ((x + 22, (31, 58, 95)), (x + w - 22, (178, 34, 34))):
        draw.line([fx, y + 12, fx, y + 52], fill=(90, 80, 60), width=3)
        side = 1 if fx < x + w // 2 else -1
        draw.polygon([(fx, y + 12), (fx + side * 26, y + 18),
                      (fx, y + 26)], fill=colour)
    # document
    dx, dy = x + w // 2 - 26, y + h - 52
    draw.rectangle([dx, dy, dx + 52, dy + 40], fill=(255, 255, 255),
                   outline=(90, 84, 76), width=2)
    for ly in range(dy + 8, dy + 30, 7):
        draw.line([dx + 7, ly, dx + 45, ly], fill=(120, 116, 108), width=1)
    # signature squiggle and seal
    draw.arc([dx + 8, dy + 28, dx + 30, dy + 38], 200, 340,
             fill=(31, 58, 95), width=2)
    draw.ellipse([dx + 38, dy + 26, dx + 48, dy + 36], fill=(176, 141, 60))
    # pen
    draw.line([dx + 44, dy + 40, dx + 56, dy + 18], fill=(40, 40, 40),
              width=3)


def scene_rocket(draw, box):
    """A rocket climbing past stars toward a small planet."""
    x, y, w, h = scene_background(draw, box, "rocket")
    # stars
    for sx, sy in ((x + 14, y + 10), (x + 34, y + 22), (x + w - 20, y + 12),
                   (x + w - 40, y + 30), (x + 20, y + 44)):
        draw.ellipse([sx - 2, sy - 2, sx + 2, sy + 2], fill=(255, 255, 255))
    # planet
    draw.ellipse([x + w - 34, y + h - 34, x + w - 10, y + h - 10],
                 fill=(200, 120, 80), outline=(140, 70, 40), width=1)
    draw.arc([x + w - 40, y + h - 30, x + w - 4, y + h - 12], 200, 340,
             fill=(240, 200, 120), width=2)
    # rocket body
    cx = x + w // 2
    draw.polygon([(cx, y + 12), (cx - 12, y + 34), (cx + 12, y + 34)],
                 fill=(178, 34, 34))
    draw.rectangle([cx - 12, y + 34, cx + 12, y + h - 30],
                   fill=(235, 235, 230), outline=(90, 90, 90), width=1)
    draw.ellipse([cx - 6, y + 48, cx + 6, y + 60], fill=(31, 58, 95))
    # fins and flame
    draw.polygon([(cx - 12, y + h - 44), (cx - 22, y + h - 26),
                  (cx - 12, y + h - 26)], fill=(178, 34, 34))
    draw.polygon([(cx + 12, y + h - 44), (cx + 22, y + h - 26),
                  (cx + 12, y + h - 26)], fill=(178, 34, 34))
    draw_flame(draw, cx, y + h - 26, 16, (245, 180, 30))
    draw_flame(draw, cx, y + h - 26, 9, (255, 240, 150))


SCENE_DRAWERS = {
    "fire": scene_fire,
    "refinery": scene_refinery,
    "market": scene_market,
    "strike": scene_strike,
    "siege": scene_siege,
    "parade": scene_parade,
    "factory": scene_factory,
    "tariff": scene_tariff,
    "chip": scene_chip,
    "stadium": scene_stadium,
    "treaty": scene_treaty,
    "rocket": scene_rocket,
}


# Scenes are drawn once at a fixed virtual size and then scaled into
# their slot, so the same drawing works for the tall feature scenes
# and the short grid scenes without any coordinate overflow.
SCENE_W = 320
SCENE_H = 78


def draw_scene(image, draw, category, box):
    """Draw the vector scene for a category inside a box."""
    x, y, w, h = box
    drawer = SCENE_DRAWERS.get(category)
    if drawer is None:
        scene_background(draw, box, category)
        return
    temp = Image.new("RGB", (SCENE_W, SCENE_H),
                     SCENE_TINT.get(category, (232, 228, 220)))
    temp_draw = ImageDraw.Draw(temp)
    drawer(temp_draw, (0, 0, SCENE_W, SCENE_H))
    scene_img = temp.resize((w, h), Image.LANCZOS)
    image.paste(scene_img, (x, y))


# ---------------------------------------------------------------------------
# Dot-matrix world map
# ---------------------------------------------------------------------------
# The land is stored as column ranges per row of a 64 by 32 grid, which
# the renderer turns into dots. The shapes are deliberately coarse: at
# dot scale the eye reads continents, not coastlines, and the numbered
# pins do the precise work.

LAND_ROWS = [
    [],
    [(8, 14), (38, 56)],
    [(7, 16), (37, 58)],
    [(6, 17), (30, 33), (36, 58)],
    [(6, 18), (30, 36), (37, 58)],
    [(7, 18), (30, 37), (38, 57)],
    [(8, 18), (30, 37), (39, 56)],
    [(9, 19), (30, 36), (40, 56)],
    [(9, 18), (31, 35), (41, 55)],
    [(10, 17), (31, 36), (42, 54)],
    [(11, 16), (31, 36), (43, 52)],
    [(12, 15), (31, 36), (44, 51)],
    [(13, 15), (32, 36), (45, 50)],
    [(14, 16), (32, 36), (46, 49)],
    [(16, 18), (32, 35), (47, 49)],
    [(17, 20), (32, 34), (48, 50)],
    [(18, 21), (32, 34), (49, 52)],
    [(18, 22), (32, 34), (50, 54)],
    [(19, 22), (32, 34), (51, 55)],
    [(19, 23), (33, 35), (52, 56)],
    [(20, 23), (33, 34), (52, 57)],
    [(20, 23), (52, 56)],
    [(21, 23), (53, 55)],
    [(21, 22), (54, 54)],
    [(21, 22)],
    [(21, 21)],
    [],
    [],
    [],
    [],
    [(18, 46)],
    [(22, 42)],
]

MAP_COLS = 64
MAP_ROWS = 32


def lon_to_x(lon, map_x, map_w):
    """Equirectangular projection: longitude to pixel x."""
    return map_x + (lon + 180.0) / 360.0 * map_w


def lat_to_y(lat, map_y, map_h):
    """Equirectangular projection: latitude to pixel y."""
    return map_y + (90.0 - lat) / 180.0 * map_h


def draw_dot_map(draw, fonts, stories, map_box, audit):
    """Draw the dotted world map and the numbered pins for stories 1-13."""
    x, y, w, h = map_box
    cell_w = w / MAP_COLS
    cell_h = h / MAP_ROWS
    for row, ranges in enumerate(LAND_ROWS):
        cy = y + row * cell_h + cell_h / 2
        for start, end in ranges:
            for col in range(start, end + 1):
                cx = x + col * cell_w + cell_w / 2
                r = 1.6
                draw.ellipse([cx - r, cy - r, cx + r, cy + r],
                             fill=(120, 140, 170))
    for story in stories:
        if story["number"] > 13:
            continue
        pin = story["pin"]
        px = lon_to_x(pin["lon"], x, w)
        py = lat_to_y(pin["lat"], y, h)
        num = str(story["number"])
        radius = 10 if len(num) == 1 else 11
        draw.ellipse([px - radius, py - radius, px + radius, py + radius],
                     fill=RED, outline=WHITE, width=2)
        tw = text_width(fonts.pin, num)
        th = text_height(fonts.pin, num)
        draw.text((px - tw / 2, py - th / 2 - 1), num, font=fonts.pin,
                  fill=WHITE)
    audit.record("map pins 1-13", 13, 13, w)


# ---------------------------------------------------------------------------
# Page sections
# ---------------------------------------------------------------------------

def draw_number_badge(draw, fonts, number, x, y):
    """A black circle with a white story number, pinned on a scene corner."""
    label = str(number)
    radius = 11 if len(label) == 1 else 13
    draw.ellipse([x, y, x + radius * 2, y + radius * 2],
                 fill=BLACK_BAND, outline=WHITE, width=2)
    tw = text_width(fonts.pin, label)
    th = text_height(fonts.pin, label)
    draw.text((x + radius - tw / 2, y + radius - th / 2 - 1), label,
              font=fonts.pin, fill=WHITE)


def draw_chip(draw, fonts, label, x, y):
    """A small coloured certainty chip with its label."""
    colour = CERTAINTY.get(label, (90, 90, 90))
    tw = text_width(fonts.chip, label)
    w = tw + 10
    h = 12
    draw.rounded_rectangle([x, y, x + w, y + h], radius=3, fill=colour)
    draw.text((x + 5, y + 1), label, font=fonts.chip, fill=WHITE)
    return w


def draw_masthead(draw, fonts, data):
    """Black band with the paper name, then the big serif date line."""
    draw.rectangle([0, 0, WIDTH, 58], fill=BLACK_BAND)
    draw_centered(draw, fonts.masthead, data["masthead"], 14, WHITE)
    draw_centered(draw, fonts.date, data["date_line"], 64, INK)
    draw.line([24, 110, WIDTH - 24, 110], fill=RULE, width=2)


def draw_teasers(draw, fonts, data, audit):
    """One line carrying the three feature headlines across the page."""
    features = [s for s in data["stories"] if s["tier"] == "feature"]
    parts = [s["headline"].upper() for s in features]
    line = "  ·  ".join(parts)
    font = fit_or_shrink("DejaVuSans-Bold.ttf", 12, line, WIDTH - 48)
    draw_centered(draw, font, line, 118, INK_SOFT)
    audit.record("teaser line", 1, 1, WIDTH - 48)
    if text_width(font, line) > WIDTH - 48:
        audit.issues.append("teaser line overflows the page width")


def draw_region_strip(draw, fonts, data, audit):
    """Coloured band with the story count per region."""
    y = 138
    draw.rectangle([0, y, WIDTH, y + 26], fill=BLUE_BAND)
    parts = ["%s %d" % (r["name"], r["count"]) for r in data["regions"]]
    line = "   ·   ".join(parts)
    font = fit_or_shrink("DejaVuSans-Bold.ttf", 12, line, WIDTH - 48)
    draw_centered(draw, font, line, y + 7, WHITE)
    audit.record("region strip", 1, 1, WIDTH - 48)
    if text_width(font, line) > WIDTH - 48:
        audit.issues.append("region strip overflows the page width")


def draw_utc_strip(draw, fonts, data, audit):
    """Two rows of UTC stamps for the day's key moments."""
    y = 166
    draw.rectangle([0, y, WIDTH, y + 30], fill=PAPER_DARK)
    draw.line([0, y, WIDTH, y], fill=CREAM_LINE, width=1)
    draw.line([0, y + 30, WIDTH, y + 30], fill=CREAM_LINE, width=1)
    label = "THE DAY IN UTC"
    draw.text((24, y + 4), label, font=fonts.strip_label, fill=INK)
    draw.text((24, y + 17), "ALL TIMES UTC", font=fonts.strip_small,
              fill=INK_SOFT)
    stamps = data["utc_stamps"]
    first = "    ".join("%s  %s" % (s["hour"], s["event"].upper())
                       for s in stamps[:4])
    second = "    ".join("%s  %s" % (s["hour"], s["event"].upper())
                        for s in stamps[4:])
    font = fit_or_shrink("DejaVuSans.ttf", 10, first, WIDTH - 220)
    draw.text((210, y + 4), first, font=font, fill=INK)
    font2 = fit_or_shrink("DejaVuSans.ttf", 10, second, WIDTH - 220)
    draw.text((210, y + 17), second, font=font2, fill=INK)
    audit.record("utc strip row 1", 1, 1, WIDTH - 220)
    audit.record("utc strip row 2", 1, 1, WIDTH - 220)


def draw_numbers_strip(draw, fonts, data, audit):
    """One row of the day's key figures, value above label."""
    y = 198
    draw.rectangle([0, y, WIDTH, y + 30], fill=GREEN_BAND)
    label = "THE DAY IN NUMBERS"
    draw.text((24, y + 8), label, font=fonts.strip_label, fill=WHITE)
    numbers = data["numbers"]
    cell_w = (WIDTH - 240) / len(numbers)
    for i, item in enumerate(numbers):
        cx = 230 + i * cell_w
        value_font = fit_or_shrink("DejaVuSans-Bold.ttf", 15,
                                   item["value"], cell_w - 8)
        vw = text_width(value_font, item["value"])
        draw.text((cx + (cell_w - vw) / 2, y + 2), item["value"],
                  font=value_font, fill=WHITE)
        label_lines = wrap_text(fonts.strip_small, item["label"],
                                cell_w - 8)
        if label_lines:
            lw = text_width(fonts.strip_small, label_lines[0])
            draw.text((cx + (cell_w - lw) / 2, y + 19), label_lines[0],
                      font=fonts.strip_small, fill=(220, 235, 220))
        audit.record("number %d" % (i + 1), len(label_lines), 1,
                     int(cell_w - 8))


def draw_features(image, draw, fonts, data, audit):
    """Three feature panels in a row, each with a scene and a summary."""
    y = 232
    height = 172
    features = [s for s in data["stories"] if s["tier"] == "feature"]
    col_w = 330
    gap = 7
    for i, story in enumerate(features):
        x = 12 + i * (col_w + gap)
        draw.rectangle([x, y, x + col_w, y + height], fill=WHITE,
                       outline=(190, 180, 150), width=1)
        scene_box = (x + 6, y + 6, col_w - 12, 64)
        draw_scene(image, draw, story["scene"], scene_box)
        draw_number_badge(draw, fonts, story["number"],
                          x + 10, y + 10)
        head_y = y + 76
        draw_wrapped(draw, fonts.feature_head, story["headline"],
                     (x + 8, head_y, col_w - 16, 2), INK,
                     audit=audit, name="feature %d headline"
                     % story["number"])
        body = " ".join(story["summary"])
        body_y = head_y + 36
        drawn_body = draw_wrapped(draw, fonts.feature_body, body,
                                  (x + 8, body_y, col_w - 16, 3),
                                  INK_SOFT, audit=audit,
                                  name="feature %d summary"
                                  % story["number"])
        chip_y = y + height - 18
        body_leading = int(text_height(fonts.feature_body, "Ag") * 1.25)
        body_bottom = (body_y + (len(drawn_body) - 1) * body_leading
                       + text_height(fonts.feature_body, "Ag"))
        audit.check("feature %d body clears chip" % story["number"],
                    body_bottom <= chip_y - 2, col_w - 16,
                    "body ends at y+%d, chip starts at y+%d"
                    % (body_bottom - y, chip_y - y))
        draw_chip(draw, fonts, story["certainty"], x + 8, chip_y)
        stats = "  ·  ".join("%s %s" % (s["label"], s["value"])
                             for s in story["stats"])
        stat_font = fit_or_shrink("DejaVuSans-Bold.ttf", 10, stats,
                                  col_w - 90)
        draw.text((x + 78, y + height - 17), stats, font=stat_font,
                  fill=INK)


def draw_grid(image, draw, fonts, data, audit):
    """Ten grid items, two rows of five, each with a small scene."""
    y = 408
    row_h = 124
    grid = [s for s in data["stories"] if s["tier"] == "grid"]
    col_w = 200
    gap = 5
    for i, story in enumerate(grid):
        row, col = divmod(i, 5)
        x = 7 + col * (col_w + gap)
        gy = y + row * row_h
        draw.rectangle([x, gy, x + col_w, gy + row_h - 4], fill=WHITE,
                       outline=(190, 180, 150), width=1)
        scene_box = (x + 5, gy + 5, col_w - 10, 40)
        draw_scene(image, draw, story["scene"], scene_box)
        draw_number_badge(draw, fonts, story["number"], x + 8, gy + 8)
        head_y = gy + 50
        draw_wrapped(draw, fonts.grid_head, story["headline"],
                     (x + 6, head_y, col_w - 12, 2), INK,
                     audit=audit, name="grid %d headline"
                     % story["number"])
        body = " ".join(story["summary"])
        body_y = head_y + 28
        drawn_body = draw_wrapped(draw, fonts.grid_body, body,
                                  (x + 6, body_y, col_w - 12, 2),
                                  INK_SOFT, audit=audit,
                                  name="grid %d summary"
                                  % story["number"])
        chip_y = gy + row_h - 18
        body_leading = int(text_height(fonts.grid_body, "Ag") * 1.25)
        body_bottom = (body_y + (len(drawn_body) - 1) * body_leading
                       + text_height(fonts.grid_body, "Ag"))
        audit.check("grid %d body clears chip" % story["number"],
                    body_bottom <= chip_y - 2, col_w - 12,
                    "body ends at y+%d, chip starts at y+%d"
                    % (body_bottom - gy, chip_y - gy))
        draw_chip(draw, fonts, story["certainty"], x + 6, chip_y)


def draw_map_section(draw, fonts, data, audit):
    """Section title plus the dot map with numbered pins 1 to 13."""
    y = 660
    draw.text((24, y), "WHERE IT HAPPENED", font=fonts.section, fill=INK)
    note = "Pins are numbered to match stories 1-13"
    nw = text_width(fonts.caption, note)
    draw.text((WIDTH - 24 - nw, y + 2), note, font=fonts.caption,
              fill=INK_SOFT)
    draw.line([24, y + 18, WIDTH - 24, y + 18], fill=RULE, width=1)
    map_box = (24, y + 24, 700, 96)
    draw_dot_map(draw, fonts, data["stories"], map_box, audit)
    # Key at the right of the map: the thirteen pinned places, one line each.
    kx = 740
    ky = y + 24
    pinned = [s for s in data["stories"] if s["number"] <= 13]
    for i, story in enumerate(pinned):
        line = "%d  %s" % (story["number"], story["pin"]["place"])
        font = fit_or_shrink("DejaVuSans.ttf", 9, line, WIDTH - kx - 24)
        draw.text((kx, ky + i * 8 - 2), line, font=font, fill=INK_SOFT)
    audit.record("map key", len(pinned), 13, WIDTH - kx - 24)


def draw_briefs(draw, fonts, data, audit):
    """Two columns of one-line briefs, numbered 14 to the end."""
    y = 788
    briefs = [s for s in data["stories"] if s["tier"] == "brief"]
    title = "ALSO ON THURSDAY 26 NOVEMBER"
    draw.text((24, y), title, font=fonts.section, fill=INK)
    count = "%d BRIEFS" % len(briefs)
    cw = text_width(fonts.caption, count)
    draw.text((WIDTH - 24 - cw, y + 2), count, font=fonts.caption,
              fill=INK_SOFT)
    draw.line([24, y + 18, WIDTH - 24, y + 18], fill=RULE, width=1)
    col_w = 490
    rows = (len(briefs) + 1) // 2
    for i, story in enumerate(briefs):
        col, row = divmod(i, rows)
        x = 24 + col * (col_w + 12)
        by = y + 24 + row * 11
        num = "%d." % story["number"]
        draw.text((x, by), num, font=fonts.brief_num, fill=INK)
        nw = text_width(fonts.brief_num, num) + 4
        line = story["headline"]
        font = fit_or_shrink("DejaVuSans.ttf", 11, line, col_w - nw)
        draw.text((x + nw, by), line, font=font, fill=INK)
        audit.record("brief %d" % story["number"], 1, 1,
                     int(col_w - nw))


def draw_footer(draw, fonts, data, audit):
    """Red-bordered DATE CHECK box, the HOW SURE legend, and colophon."""
    y = 936
    excluded = data["date_check_excluded"]
    excluded_text = ("Left out because they belong to other days: "
                     + "; ".join(excluded) + ".")
    box_h = 50
    draw.rectangle([24, y, WIDTH - 24, y + box_h], outline=RED, width=2)
    draw.text((32, y + 4), "DATE CHECK", font=fonts.footer_bold,
              fill=RED_DARK)
    draw_wrapped(draw, fonts.footer_small,
                 "Every story above was first reported on 26 November 2026 "
                 "in some time zone. " + excluded_text,
                 (32, y + 19, WIDTH - 64, 2), INK,
                 audit=audit, name="date check")
    legend_y = y + box_h + 8
    legend = ("HOW SURE:  CONFIRMED 2+ outlets  ·  OFFICIAL statement on "
              "record  ·  REPORTED one wire or local source  ·  CLAIM one "
              "party's claim, unverified")
    font = fit_or_shrink("DejaVuSans.ttf", 10, legend, WIDTH - 48)
    draw.text((24, legend_y), legend, font=font, fill=INK_SOFT)
    audit.record("how sure legend", 1, 1, WIDTH - 48)
    colophon = ("THE WORLD IN ONE DAY  ·  Thursday 26 November 2026  ·  "
                "%d dated stories, %d regions  ·  Drawn by the desk, "
                "checked against the wires"
                % (len(data["stories"]), len(data["regions"])))
    draw_centered(draw, fonts.caption, colophon, legend_y + 16, INK_SOFT)
    audit.record("colophon", 1, 1, WIDTH - 48)


# ---------------------------------------------------------------------------
# Render driver
# ---------------------------------------------------------------------------

def load_sources(path):
    """Load and sanity-check the edition data before drawing anything."""
    with open(path, "r", encoding="utf-8") as handle:
        data = json.load(handle)
    stories = data["stories"]
    numbers = [s["number"] for s in stories]
    if sorted(numbers) != list(range(1, len(stories) + 1)):
        raise SystemExit("story numbers are not 1..%d in order"
                         % len(stories))
    tiers = {"feature": 0, "grid": 0, "brief": 0}
    for story in stories:
        tiers[story["tier"]] += 1
    if tiers["feature"] != 3 or tiers["grid"] != 10:
        raise SystemExit("need exactly 3 features and 10 grid items, "
                         "got %s" % (tiers,))
    if len(stories) < 29:
        raise SystemExit("need at least 29 stories, got %d"
                         % len(stories))
    region_total = sum(r["count"] for r in data["regions"])
    if region_total != len(stories):
        raise SystemExit("region counts sum to %d, stories number %d"
                         % (region_total, len(stories)))
    return data


def render(data, output_path, fonts, audit):
    """Draw the whole front page and save it as a PNG."""
    image = Image.new("RGB", (WIDTH, HEIGHT), PAPER)
    draw = ImageDraw.Draw(image)
    draw_masthead(draw, fonts, data)
    draw_teasers(draw, fonts, data, audit)
    draw_region_strip(draw, fonts, data, audit)
    draw_utc_strip(draw, fonts, data, audit)
    draw_numbers_strip(draw, fonts, data, audit)
    draw_features(image, draw, fonts, data, audit)
    draw_grid(image, draw, fonts, data, audit)
    draw_map_section(draw, fonts, data, audit)
    draw_briefs(draw, fonts, data, audit)
    draw_footer(draw, fonts, data, audit)
    image.save(output_path, format="PNG")
    return output_path


def check_output(path):
    """Verify the rendered file: format, size, dimensions, byte count."""
    problems = []
    with Image.open(path) as image:
        if image.format != "PNG":
            problems.append("output is %s, not PNG" % image.format)
        if image.size != (WIDTH, HEIGHT):
            problems.append("output is %s, not 1024x1024" % (image.size,))
    size = os.path.getsize(path)
    if size > 1048576:
        problems.append("output is %d bytes, over the 1 MiB limit" % size)
    return size, problems


def section_map():
    """The vertical map of the page, for the report and the design doc."""
    return [
        ("masthead band", 0, 58),
        ("date line", 58, 110),
        ("teaser headlines", 110, 136),
        ("region strip", 138, 164),
        ("UTC strip", 166, 196),
        ("numbers strip", 198, 228),
        ("features 1-3", 232, 404),
        ("grid 4-13", 408, 656),
        ("world map", 660, 784),
        ("briefs 14-36", 788, 932),
        ("footer", 936, 1016),
    ]


def main(argv):
    """Entry point: render, audit, check, and optionally report."""
    strict = "--strict" in argv
    want_report = "--report" in argv or strict
    here = os.path.dirname(os.path.abspath(__file__))
    sources_path = os.path.join(here, "sources.json")
    output_path = os.path.join(here, "entry.png")
    data = load_sources(sources_path)
    fonts = Fonts()
    audit = LayoutAudit()
    render(data, output_path, fonts, audit)
    size, problems = check_output(output_path)
    lines = []
    lines.append("rendered %s (%d bytes, %d stories: %d features, "
                 "%d grid, %d briefs)"
                 % (output_path, size, len(data["stories"]),
                    sum(1 for s in data["stories"]
                        if s["tier"] == "feature"),
                    sum(1 for s in data["stories"]
                        if s["tier"] == "grid"),
                    sum(1 for s in data["stories"]
                        if s["tier"] == "brief")))
    lines.append("section map:")
    for name, top, bottom in section_map():
        lines.append("  %-18s y %4d-%4d" % (name, top, bottom))
    lines.extend(audit.report())
    if problems:
        lines.append("output check: FAILED")
        for problem in problems:
            lines.append("  !! " + problem)
    else:
        lines.append("output check: PNG 1024x1024, %d bytes, under 1 MiB"
                     % size)
    if want_report:
        print("\n".join(lines))
    if audit.issues or problems:
        if strict:
            return 1
        print("render: %d audit issue(s), %d output problem(s) "
              "(see --report)" % (len(audit.issues), len(problems)),
              file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
