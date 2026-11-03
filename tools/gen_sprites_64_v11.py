#!/usr/bin/env python3
"""v1.1 Ink-Pixel Inn — tiezhang + qinshi at v0.9-r2 density.

Iron-palm healer + qin nun. Same frame map / pose exaggeration as r2.
Does NOT overwrite qingyi / langren / xiaoer.

Frame map:
  0–1 idle | 2–5 walk | 6–8 windup | 9–12 strike | 13–14 hurt | 15–17 parry
"""
from __future__ import annotations

from pathlib import Path
from PIL import Image

ROOT = Path("/workspace/wuxia-inn")
OUT = ROOT / "assets" / "sprites" / "64"
PREV = ROOT / "assets" / "_preview"

INK = (0x1A, 0x15, 0x10, 255)
INK_SOFT = (0x3D, 0x32, 0x26, 255)
NIGHT = (0x2A, 0x22, 0x18, 255)
FRAME = (0x5A, 0x4A, 0x32, 255)
PAPER = (0xE8, 0xD5, 0xA8, 255)
PAPER_L = (0xF4, 0xE6, 0xC4, 255)
PAPER_D = (0xD4, 0xBC, 0x8A, 255)
CREAM = (0xFF, 0xF8, 0xEE, 255)
CINN = (0xA6, 0x1B, 0x1B, 255)
CINN_B = (0xC4, 0x2B, 0x2B, 255)
BLOOD = (0x8B, 0x29, 0x42, 255)
GOLD = (0xC9, 0xA2, 0x27, 255)
LOESS = (0xB8, 0x86, 0x0B, 255)
JADE = (0x2F, 0x6B, 0x4F, 255)
JADE_B = (0x3D, 0x8F, 0x66, 255)
WOOD = (0x5C, 0x40, 0x30, 255)
WOOD_L = (0x8B, 0x69, 0x14, 255)
SKY = (0x6A, 0x9A, 0xB8, 255)
MTN = (0x4A, 0x7A, 0x58, 255)
MIST = (0x8A, 0x7A, 0x60, 255)
SKIN = (0xE8, 0xC4, 0xA0, 255)
SKIN_D = (0xC0, 0x90, 0x70, 255)
TEAL = (0x2A, 0x6A, 0x6A, 255)
TEAL_B = (0x4A, 0x9A, 0x9A, 255)
ROBE_R = (0xA0, 0x40, 0x40, 255)
VIOLET = (0x5A, 0x40, 0x60, 255)
TRANS = (0, 0, 0, 0)

PALETTE_SET = {
    INK[:3], INK_SOFT[:3], NIGHT[:3], FRAME[:3], PAPER[:3], PAPER_L[:3], PAPER_D[:3],
    CREAM[:3], CINN[:3], CINN_B[:3], BLOOD[:3], GOLD[:3], LOESS[:3], JADE[:3], JADE_B[:3],
    WOOD[:3], WOOD_L[:3], SKY[:3], MTN[:3], MIST[:3], SKIN[:3], SKIN_D[:3],
    TEAL[:3], TEAL_B[:3], ROBE_R[:3], VIOLET[:3],
}

FS = 64


def new_frame():
    return Image.new("RGBA", (FS, FS), TRANS)


def px(img, x, y, c):
    if 0 <= x < img.width and 0 <= y < img.height and c[3] > 0:
        img.putpixel((int(x), int(y)), c)


def rect(img, x0, y0, x1, y1, c):
    for y in range(max(0, int(y0)), min(img.height, int(y1))):
        for x in range(max(0, int(x0)), min(img.width, int(x1))):
            px(img, x, y, c)


def hline(img, x0, x1, y, c):
    for x in range(int(x0), int(x1)):
        px(img, x, y, c)


def vline(img, x, y0, y1, c):
    for y in range(int(y0), int(y1)):
        px(img, x, y, c)


def outline_rect(img, x0, y0, x1, y1, c=INK):
    hline(img, x0, x1, y0, c)
    hline(img, x0, x1, y1 - 1, c)
    vline(img, x0, y0, y1, c)
    vline(img, x1 - 1, y0, y1, c)


# ---------- shared ----------
def shoe(img, x, y, wide=False):
    w = 11 if wide else 9
    rect(img, x, y, x + w, y + 5, INK_SOFT)
    rect(img, x + 1, y + 1, x + w - 1, y + 3, NIGHT)
    hline(img, x, x + w, y + 4, INK)
    # toe right + cuff highlight
    px(img, x + w, y + 1, INK_SOFT)
    px(img, x + w, y + 2, INK)
    px(img, x + w - 1, y, CREAM)
    hline(img, x + 1, x + w - 2, y, FRAME)


def hand(img, x, y, skin=SKIN, fist=False):
    if fist:
        rect(img, x, y, x + 5, y + 5, skin)
        outline_rect(img, x, y, x + 5, y + 5, INK)
        px(img, x + 2, y + 2, SKIN_D)
        px(img, x + 3, y + 3, SKIN_D)
    else:
        rect(img, x, y, x + 4, y + 4, skin)
        outline_rect(img, x, y, x + 4, y + 4, INK)
        px(img, x + 4, y + 1, skin)
        px(img, x + 3, y + 2, SKIN_D)


def sleeve_cuff(img, x0, x1, y, robe, cuff=PAPER_L):
    hline(img, x0, x1, y, cuff)
    hline(img, x0, x1, y + 1, cuff)
    hline(img, x0 + 1, x1 - 1, y + 2, robe)


def robe_folds(img, x0, x1, y0, y1, fold=NIGHT, hi=None):
    """Interior density r2: seam + dense staggered folds + side ticks + hem scallops."""
    mid = (x0 + x1) // 2
    vline(img, mid, y0, y1, fold)
    if hi:
        vline(img, mid + 1, y0 + 1, y1 - 1, hi)
        vline(img, mid - 1, y0 + 3, y1 - 2, fold)
    for i, yy in enumerate(range(y0 + 1, y1 - 1, 3)):
        inset = 1 + (i % 3)
        hline(img, x0 + 1 + inset, x1 - 1 - inset, yy, fold)
        if hi:
            px(img, x0 + 2 + inset, yy + 1, hi)
            px(img, x1 - 3 - inset, yy + 1, hi)
            if i % 2 == 0:
                px(img, mid + 2, yy, hi)
    for yy in range(y0, y1, 2):
        px(img, x0 + 1, yy, fold)
        px(img, x1 - 2, yy, fold)
        if yy % 4 == 0:
            px(img, x0 + 2, yy + 1, fold)
            px(img, x1 - 3, yy + 1, fold)


def sleeve_folds(img, x0, x1, y0, y1, fold=NIGHT, hi=None):
    """Dense sleeve wrinkles along arm."""
    for i, yy in enumerate(range(y0 + 1, y1 - 1, 3)):
        hline(img, x0 + 1, x1 - 1, yy, fold)
        if hi:
            px(img, x0 + 2, yy + 1, hi)
    vline(img, (x0 + x1) // 2, y0, y1, fold)


def hem_layers(img, x0, x1, y, robe, fold=NIGHT, hi=None):
    """Multi-layer robe hem scallop."""
    hline(img, x0, x1, y, fold)
    hline(img, x0 + 1, x1 - 1, y + 1, hi or robe)
    hline(img, x0 + 2, x1 - 2, y + 2, fold)
    hline(img, x0 + 3, x1 - 3, y + 3, robe)
    # scallop ticks
    for x in range(x0 + 3, x1 - 3, 4):
        px(img, x, y + 1, fold)
        px(img, x + 1, y + 2, hi or robe)


def belt(img, x0, x1, y, main=WOOD_L, buckle=GOLD, hang=True):
    rect(img, x0, y, x1, y + 4, main)
    hline(img, x0, x1, y, INK)
    hline(img, x0, x1, y + 3, WOOD if main != WOOD else NIGHT)
    mid = (x0 + x1) // 2
    rect(img, mid - 2, y - 1, mid + 3, y + 5, buckle)
    outline_rect(img, mid - 2, y - 1, mid + 3, y + 5, INK)
    px(img, mid, y + 1, CREAM)
    px(img, mid + 1, y + 2, CREAM)
    px(img, x0 + 2, y + 1, INK)
    px(img, x1 - 3, y + 1, INK)
    if hang:
        rect(img, mid + 4, y + 4, mid + 7, y + 11, main)
        px(img, mid + 5, y + 10, buckle)


def open_palm(img, x, y, skin=SKIN, glow=None):
    """Open palm facing right — strike silhouette cue."""
    rect(img, x, y, x + 7, y + 6, skin)
    outline_rect(img, x, y, x + 7, y + 6, INK)
    # fingers spread
    px(img, x + 7, y, skin)
    px(img, x + 8, y + 1, skin)
    px(img, x + 7, y + 2, skin)
    px(img, x + 8, y + 3, skin)
    px(img, x + 7, y + 4, skin)
    px(img, x + 6, y + 1, SKIN_D)
    px(img, x + 5, y + 3, SKIN_D)
    if glow:
        px(img, x + 9, y + 1, glow)
        px(img, x + 10, y + 2, glow)
        px(img, x + 9, y + 3, CREAM)
        px(img, x + 8, y - 1, glow)


# ============================================================
# TIEZHANG — iron-palm healer, double-bun, red robe, jade pouch
# ============================================================
def tz_head(img, cx, cy):
    # hair mass + double bun
    rect(img, cx - 8, cy + 2, cx + 9, cy + 9, INK)
    rect(img, cx - 10, cy + 4, cx + 10, cy + 9, INK)
    # left bun
    rect(img, cx - 12, cy - 2, cx - 4, cy + 6, INK)
    rect(img, cx - 10, cy - 4, cx - 6, cy - 1, INK)
    px(img, cx - 8, cy - 2, GOLD)
    px(img, cx - 7, cy, CINN_B)
    # right bun
    rect(img, cx + 4, cy - 4, cx + 14, cy + 6, INK)
    rect(img, cx + 6, cy - 6, cx + 12, cy - 2, INK)
    px(img, cx + 10, cy - 2, GOLD)
    px(img, cx + 12, cy + 2, CINN_B)
    px(img, cx + 11, cy, LOESS)
    # red hair ribbon
    rect(img, cx - 4, cy + 1, cx + 6, cy + 4, CINN)
    hline(img, cx - 4, cx + 6, cy + 2, CINN_B)
    # face
    rect(img, cx - 7, cy + 9, cx + 9, cy + 19, SKIN)
    for fx, fy in [(-5, 9), (-2, 9), (1, 9), (4, 9), (6, 9), (-3, 10), (3, 10)]:
        px(img, cx + fx, cy + fy, INK)
    rect(img, cx - 10, cy + 9, cx - 7, cy + 16, INK)
    rect(img, cx + 8, cy + 9, cx + 11, cy + 14, INK)
    # eyes
    px(img, cx - 2, cy + 13, INK); px(img, cx - 1, cy + 13, INK)
    px(img, cx + 3, cy + 13, INK); px(img, cx + 4, cy + 13, INK); px(img, cx + 5, cy + 13, INK)
    px(img, cx - 2, cy + 11, INK_SOFT); px(img, cx + 3, cy + 11, INK)
    px(img, cx + 7, cy + 15, SKIN_D); px(img, cx + 6, cy + 16, SKIN_D)
    hline(img, cx - 5, cx + 7, cy + 18, SKIN_D)
    rect(img, cx - 3, cy + 19, cx + 5, cy + 23, SKIN)
    vline(img, cx - 10, cy + 4, cy + 16, INK)
    vline(img, cx + 10, cy + 4, cy + 14, INK)


def tz_pouch(img, x, y):
    """Jade medicine pouch at hip — readable prop."""
    rect(img, x, y, x + 12, y + 14, JADE_B)
    outline_rect(img, x, y, x + 12, y + 14, INK)
    rect(img, x + 2, y + 2, x + 10, y + 10, JADE)
    px(img, x + 4, y + 4, GOLD)
    px(img, x + 7, y + 6, CREAM)
    px(img, x + 5, y + 8, JADE_B)
    # strap
    rect(img, x + 2, y - 3, x + 5, y + 1, WOOD)
    px(img, x + 3, y - 2, WOOD_L)


def tz_palm_glow(img, x, y, big=False):
    """Shock-palm impact ring."""
    open_palm(img, x, y, SKIN, JADE_B)
    if big:
        for dx, dy, c in [(10, 0, JADE_B), (12, 1, CREAM), (11, 3, GOLD),
                          (9, -2, JADE_B), (13, 2, CREAM), (10, 5, JADE),
                          (8, -3, GOLD), (14, 0, CREAM), (12, 4, JADE_B)]:
            px(img, x + dx, y + dy, c)


def tiezhang_draw(img, pose):
    breath = pose.get("breath", 0)
    bx = pose.get("bx", 0)
    by = pose.get("by", 0)
    cx = 22 + bx
    cy = 3 + by + breath
    tz_head(img, cx, cy)

    ty = 24 + by + breath
    # shoulders
    rect(img, cx - 11, ty, cx + 12, ty + 4, ROBE_R)
    hline(img, cx - 10, cx + 11, ty, CINN_B)
    px(img, cx - 11, ty, GOLD)
    px(img, cx + 11, ty + 1, BLOOD)
    # collar
    rect(img, cx - 4, ty, cx + 6, ty + 5, PAPER_L)
    rect(img, cx - 3, ty + 1, cx + 5, ty + 4, PAPER)
    rect(img, cx - 9, ty + 2, cx - 4, ty + 7, BLOOD)
    rect(img, cx + 6, ty + 2, cx + 11, ty + 7, BLOOD)
    # torso
    rect(img, cx - 10, ty + 4, cx + 12, ty + 24, ROBE_R)
    robe_folds(img, cx - 10, cx + 12, ty + 6, ty + 24, BLOOD, CINN_B)
    rect(img, cx - 2, ty + 5, cx + 1, ty + 16, NIGHT)
    belt(img, cx - 10, cx + 12, ty + 15, BLOOD, GOLD, hang=True)
    rect(img, cx - 10, ty + 13, cx + 12, ty + 15, NIGHT)
    # medicine pouch (right hip) — skip during extreme strikes if needed
    if pose.get("kind") not in ("strike",) or pose.get("phase", 0) >= 3:
        tz_pouch(img, cx + 10, ty + 16)
    else:
        tz_pouch(img, cx + 8, ty + 18)

    lift_l = pose.get("lift_l", 0)
    lift_r = pose.get("lift_r", 0)
    ly = ty + 24
    lx0 = cx - 9 - (4 if lift_l else 0) - (2 if pose.get("stride_l") else 0)
    rect(img, lx0, ly - lift_l, lx0 + 8, ly + 14 - lift_l, ROBE_R)
    hline(img, lx0 + 1, lx0 + 7, ly - lift_l + 5, BLOOD)
    hline(img, lx0 + 1, lx0 + 7, ly - lift_l + 9, CINN_B)
    rx0 = cx + 1 + (4 if lift_r else 0) + (2 if pose.get("stride_r") else 0)
    rect(img, rx0, ly - lift_r, rx0 + 8, ly + 14 - lift_r, ROBE_R)
    hline(img, rx0 + 1, rx0 + 7, ly - lift_r + 5, BLOOD)
    hline(img, rx0 + 1, rx0 + 7, ly - lift_r + 9, CINN_B)
    hem_layers(img, cx - 11, cx + 13, ly + 1, ROBE_R, BLOOD, CINN_B)
    if lift_l:
        px(img, lx0 - 2, ly - lift_l + 1, ROBE_R); px(img, lx0 - 1, ly - lift_l, BLOOD)
    if lift_r:
        px(img, rx0 + 8, ly - lift_r + 1, ROBE_R); px(img, rx0 + 9, ly - lift_r, BLOOD)
    shoe(img, lx0 - 1, ly + 14 - lift_l)
    shoe(img, rx0, ly + 14 - lift_r)

    kind = pose.get("kind", "idle")

    if kind == "idle":
        rect(img, cx - 15, ty + 3, cx - 9, ty + 15, ROBE_R)
        rect(img, cx - 16, ty + 13, cx - 10, ty + 19, ROBE_R)
        sleeve_cuff(img, cx - 16, cx - 10, ty + 15, ROBE_R)
        hand(img, cx - 16, ty + 17, SKIN)
        # front arm near pouch, open palm ready
        rect(img, cx + 10, ty + 5, cx + 16, ty + 15, ROBE_R)
        sleeve_folds(img, cx + 10, cx + 16, ty + 6, ty + 14, BLOOD, CINN_B)
        sleeve_cuff(img, cx + 10, cx + 16, ty + 13, ROBE_R)
        open_palm(img, cx + 14, ty + 12, SKIN)

    elif kind == "walk":
        if lift_l:
            rect(img, cx + 10, ty + 1, cx + 17, ty + 12, ROBE_R)
            sleeve_cuff(img, cx + 10, cx + 17, ty + 10, ROBE_R)
            open_palm(img, cx + 15, ty + 9, SKIN)
            rect(img, cx - 15, ty + 7, cx - 9, ty + 17, ROBE_R)
            hand(img, cx - 16, ty + 15, SKIN)
        else:
            rect(img, cx - 17, ty + 1, cx - 9, ty + 12, ROBE_R)
            sleeve_cuff(img, cx - 17, cx - 9, ty + 10, ROBE_R)
            hand(img, cx - 17, ty + 10, SKIN)
            rect(img, cx + 10, ty + 7, cx + 16, ty + 17, ROBE_R)
            open_palm(img, cx + 14, ty + 14, SKIN)

    elif kind == "windup":
        phase = pose.get("phase", 0)
        # both palms cocked HIGH-BACK — iron palm coil
        rect(img, cx - 18, ty - 8, cx - 6, ty + 4, ROBE_R)
        sleeve_folds(img, cx - 18, cx - 6, ty - 7, ty + 3, BLOOD, CINN_B)
        open_palm(img, cx - 20, ty - 4, SKIN, JADE)
        rect(img, cx - 6, ty - 10, cx + 6, ty + 0, ROBE_R)
        sleeve_folds(img, cx - 6, cx + 6, ty - 9, ty - 1, BLOOD, CINN_B)
        open_palm(img, cx - 8, ty - 12, SKIN, JADE_B)
        # coat flare back
        rect(img, cx + 12, ty + 14, cx + 18, ty + 26, ROBE_R)
        robe_folds(img, cx + 12, cx + 18, ty + 15, ty + 25, BLOOD, CINN_B)
        rect(img, cx - 16, ty + 16, cx - 10, ty + 28, ROBE_R)
        for dx, dy in [(14, 18), (16, 20), (17, 22), (-13, 20), (-15, 23)]:
            px(img, cx + dx, ty + dy, CINN_B if dx > 0 else BLOOD)
        # rear planted mass
        rect(img, cx - 16, ly + 4, cx - 4, ly + 14, ROBE_R)
        hline(img, cx - 15, cx - 5, ly + 8, BLOOD)
        if phase >= 1:
            rect(img, cx + 2, ly - 8, cx + 10, ly + 6, ROBE_R)
            hline(img, cx + 3, cx + 9, ly - 4, BLOOD)
        # qi spark at coiled palms
        if phase >= 1:
            px(img, cx - 18, ty - 8, JADE_B)
            px(img, cx - 16, ty - 10, CREAM)
            px(img, cx - 6, ty - 14, GOLD)

    elif kind == "strike":
        phase = pose.get("phase", 0)
        if phase == 0:
            rect(img, cx - 14, ty - 4, cx - 4, ty + 8, ROBE_R)
            sleeve_folds(img, cx - 14, cx - 4, ty - 3, ty + 7, BLOOD, CINN_B)
            open_palm(img, cx - 14, ty + 2, SKIN)
            rect(img, cx + 6, ty - 6, cx + 16, ty + 6, ROBE_R)
            sleeve_cuff(img, cx + 6, cx + 16, ty + 4, ROBE_R)
            open_palm(img, cx + 14, ty - 2, SKIN, JADE_B)
            rect(img, cx - 14, ty + 16, cx - 8, ty + 26, ROBE_R)
        elif phase == 1:
            # === HIT FRAME — full arm thrust + shock palm ===
            rect(img, cx - 14, ty + 8, cx - 4, ty + 18, ROBE_R)
            sleeve_folds(img, cx - 14, cx - 4, ty + 9, ty + 17, BLOOD, CINN_B)
            hand(img, cx - 14, ty + 16, SKIN)
            rect(img, cx + 6, ty + 0, cx + 24, ty + 10, ROBE_R)
            sleeve_folds(img, cx + 6, cx + 24, ty + 1, ty + 9, BLOOD, CINN_B)
            sleeve_cuff(img, cx + 16, cx + 24, ty + 8, ROBE_R)
            tz_palm_glow(img, cx + 22, ty + 2, big=True)
            # forward coat stretch
            rect(img, cx + 12, ty + 14, cx + 20, ty + 24, ROBE_R)
            robe_folds(img, cx + 12, cx + 20, ty + 15, ty + 23, BLOOD, CINN_B)
            # palm-shock arc trail
            for i in range(0, 18, 3):
                px(img, cx + 28 + i // 2, ty + 1 - i // 6, JADE_B)
                px(img, cx + 29 + i // 2, ty + 3 + i // 8, CREAM)
                px(img, cx + 27 + i // 2, ty + 5, JADE)
            for i, (dx, dy) in enumerate([(-2, 2), (-4, 0), (-6, 3), (-3, -2)]):
                px(img, cx + 4 + dx, ty + 4 + dy, JADE_B if i % 2 == 0 else CREAM)
        elif phase == 2:
            rect(img, cx - 10, ty + 10, cx - 2, ty + 20, ROBE_R)
            hand(img, cx - 10, ty + 18, SKIN)
            rect(img, cx + 8, ty + 2, cx + 24, ty + 12, ROBE_R)
            sleeve_folds(img, cx + 8, cx + 24, ty + 3, ty + 11, BLOOD, CINN_B)
            tz_palm_glow(img, cx + 22, ty + 4, big=True)
            rect(img, cx + 10, ty + 14, cx + 18, ty + 24, ROBE_R)
        else:
            rect(img, cx - 13, ty + 5, cx - 5, ty + 15, ROBE_R)
            hand(img, cx - 13, ty + 13, SKIN)
            rect(img, cx + 8, ty + 5, cx + 15, ty + 15, ROBE_R)
            open_palm(img, cx + 14, ty + 12, SKIN)

    elif kind == "hurt":
        phase = pose.get("phase", 0)
        if phase == 0:
            rect(img, cx + 10, ty - 5, cx + 18, ty + 7, ROBE_R)
            hand(img, cx + 16, ty - 6, SKIN)
            rect(img, cx - 15, ty + 9, cx - 7, ty + 19, ROBE_R)
            hand(img, cx - 16, ty + 17, SKIN)
        else:
            rect(img, cx + 11, ty + 5, cx + 20, ty + 15, ROBE_R)
            hand(img, cx + 18, ty + 13, SKIN)
            rect(img, cx - 14, ty + 3, cx - 6, ty + 13, ROBE_R)
            hand(img, cx - 15, ty + 11, SKIN)
        for dx, dy, c in [
            (6, 6, CINN_B), (10, 10, BLOOD), (2, 14, CINN_B),
            (14, 8, BLOOD), (8, 16, BLOOD), (12, 4, CINN_B),
            (-2, 12, BLOOD), (16, 12, CINN), (4, 18, BLOOD),
        ]:
            px(img, cx + dx, ty + dy, c)

    elif kind == "parry":
        phase = pose.get("phase", 0)
        shake = pose.get("shake", 0)
        if phase < 2:
            # both palms UP — iron-palm guard overhead
            rect(img, cx - 16, ty - 10, cx - 6, ty + 2, ROBE_R)
            sleeve_folds(img, cx - 16, cx - 6, ty - 9, ty + 1, BLOOD, CINN_B)
            open_palm(img, cx - 12, ty - 14, SKIN, JADE)
            rect(img, cx + 2, ty - 12, cx + 14, ty + 0, ROBE_R)
            sleeve_folds(img, cx + 2, cx + 14, ty - 11, ty - 1, BLOOD, CINN_B)
            open_palm(img, cx + 10 + shake, ty - 16, SKIN, JADE_B)
            # palm-guard glow above head
            for dx, dy, c in [(0, -20, JADE_B), (4, -22, CREAM), (2, -18, GOLD),
                              (-2, -21, JADE), (6, -19, CREAM)]:
                px(img, cx + 4 + shake + dx, ty + dy, c)
            rect(img, cx - 14, ty + 18, cx - 6, ty + 26, ROBE_R)
            rect(img, cx + 8, ty + 18, cx + 16, ty + 26, ROBE_R)
            if phase == 1:
                for dx, dy, c in [(0, -24, CREAM), (5, -26, GOLD), (3, -28, JADE_B),
                                  (-3, -25, CREAM), (7, -22, GOLD)]:
                    px(img, cx + 6 + shake + dx, ty + dy, c)
        else:
            # dodge deep left — palm cross-guard
            rect(img, cx - 18, ty + 2, cx - 8, ty + 14, ROBE_R)
            sleeve_folds(img, cx - 18, cx - 8, ty + 3, ty + 13, BLOOD, CINN_B)
            open_palm(img, cx - 18, ty + 10, SKIN)
            rect(img, cx - 4, ty - 4, cx + 8, ty + 8, ROBE_R)
            open_palm(img, cx + 6, ty - 2, SKIN, JADE_B)
            rect(img, cx - 18, ty + 16, cx - 8, ty + 28, ROBE_R)
            robe_folds(img, cx - 18, cx - 8, ty + 17, ty + 27, BLOOD, CINN_B)

    vline(img, cx - 11, ty, ty + 22, INK)
    vline(img, cx + 11, ty, ty + 18, INK)


# ============================================================
# QINSHI — qin nun, violet+paper robe, fuchen (whisk)
# ============================================================
def qs_head(img, cx, cy):
    """Shaved crown + paper-light fringe / violet marks — nun silhouette."""
    # bald/paper dome
    rect(img, cx - 8, cy + 2, cx + 9, cy + 8, PAPER_L)
    rect(img, cx - 10, cy + 4, cx + 10, cy + 8, PAPER_L)
    rect(img, cx - 6, cy - 2, cx + 7, cy + 2, PAPER)
    hline(img, cx - 8, cx + 8, cy + 2, PAPER_D)
    # violet forehead mark / beads
    px(img, cx - 1, cy + 4, VIOLET)
    px(img, cx + 1, cy + 4, VIOLET)
    px(img, cx, cy + 3, GOLD)
    px(img, cx + 2, cy + 5, VIOLET)
    # side hair wisps (paper-light)
    rect(img, cx - 10, cy + 8, cx - 7, cy + 16, PAPER_L)
    rect(img, cx + 8, cy + 8, cx + 11, cy + 14, PAPER_L)
    # face
    rect(img, cx - 7, cy + 8, cx + 9, cy + 18, SKIN)
    # calm eyes
    px(img, cx - 2, cy + 12, INK); px(img, cx - 1, cy + 12, INK)
    px(img, cx + 3, cy + 12, INK); px(img, cx + 4, cy + 12, INK); px(img, cx + 5, cy + 12, INK)
    px(img, cx - 2, cy + 10, INK_SOFT); px(img, cx + 3, cy + 10, INK_SOFT)
    px(img, cx + 7, cy + 14, SKIN_D)
    hline(img, cx - 5, cx + 7, cy + 17, SKIN_D)
    rect(img, cx - 3, cy + 18, cx + 5, cy + 22, SKIN)
    # ink edge
    hline(img, cx - 8, cx + 8, cy + 2, INK)
    vline(img, cx - 10, cy + 4, cy + 16, INK)
    vline(img, cx + 10, cy + 4, cy + 14, INK)


def qs_whisk_vert(img, hx, hy, tip_up=True):
    """Fuchen — wood handle + long paper/cream hair tuft."""
    # handle
    rect(img, hx, hy, hx + 3, hy + 16, WOOD)
    vline(img, hx + 1, hy + 1, hy + 15, WOOD_L)
    # ring / binding
    rect(img, hx - 1, hy - 2, hx + 4, hy + 2, GOLD)
    outline_rect(img, hx - 1, hy - 2, hx + 4, hy + 2, INK)
    px(img, hx + 1, hy - 1, CREAM)
    if tip_up:
        # hair mass up
        rect(img, hx - 3, hy - 22, hx + 6, hy - 2, PAPER_L)
        rect(img, hx - 4, hy - 18, hx + 7, hy - 6, PAPER)
        # strands
        for i, ox in enumerate((-3, -1, 1, 3, 5, -2, 2, 4)):
            px(img, hx + ox, hy - 22 - (i % 3), PAPER_L)
            px(img, hx + ox, hy - 20 - (i % 2), CREAM if i % 2 == 0 else PAPER_D)
        px(img, hx + 1, hy - 24, CREAM)
        px(img, hx - 2, hy - 23, VIOLET)  # violet thread
    else:
        # hair hanging down
        rect(img, hx - 3, hy + 14, hx + 6, hy + 34, PAPER_L)
        rect(img, hx - 4, hy + 16, hx + 7, hy + 30, PAPER)
        for i, ox in enumerate((-3, -1, 1, 3, 5)):
            px(img, hx + ox, hy + 32 + (i % 2), PAPER_L)
            px(img, hx + ox + 1, hy + 30, CREAM)
        px(img, hx + 2, hy + 33, VIOLET)


def qs_whisk_back(img, hx, hy, lean=0):
    """Windup: whisk cocked high-back, hair streaming up-left."""
    rect(img, hx, hy, hx + 4, hy + 8, WOOD)
    vline(img, hx + 1, hy + 1, hy + 7, WOOD_L)
    rect(img, hx - 2, hy - 2, hx + 6, hy + 2, GOLD)
    outline_rect(img, hx - 2, hy - 2, hx + 6, hy + 2, INK)
    for i in range(20):
        x = hx - (i // 2) - lean * 2
        y = hy - 4 - i
        rect(img, x - 1, y, x + 5, y + 2, PAPER_L)
        px(img, x, y, PAPER_D)
        if i % 2 == 0:
            px(img, x + 2, y, CREAM)
        if i % 3 == 0:
            px(img, x - 2, y + 1, PAPER)
    px(img, hx - 10 - lean * 2, hy - 24, CREAM)
    px(img, hx - 8 - lean * 2, hy - 26, VIOLET)
    px(img, hx - 12 - lean * 2, hy - 22, PAPER_L)


def qs_whisk_slash(img, hx, hy, length=22, dy=0, flash=False):
    """Horizontal whisk sweep — hair trails as soft-looking hard pixels."""
    rect(img, hx - 3, hy, hx + 2, hy + 5, WOOD)
    vline(img, hx - 2, hy + 1, hy + 4, WOOD_L)
    rect(img, hx + 1, hy - 2, hx + 5, hy + 6, GOLD)
    outline_rect(img, hx + 1, hy - 2, hx + 5, hy + 6, INK)
    # hair sweep body
    rect(img, hx + 5, hy - 1 + dy, hx + 5 + length, hy + 5 + dy, PAPER_L)
    hline(img, hx + 5, hx + 5 + length, hy - 1 + dy, PAPER_D)
    hline(img, hx + 5, hx + 5 + length, hy + 4 + dy, PAPER)
    # strand tips / arc
    for i in range(0, length, 2):
        px(img, hx + 6 + i, hy - 3 + dy - (i // 8), CREAM)
        px(img, hx + 7 + i, hy + 6 + dy + (i // 10), PAPER_L)
        if i % 4 == 0:
            px(img, hx + 6 + i, hy + 2 + dy, VIOLET)
    tip = hx + 4 + length
    px(img, tip, hy + 1 + dy, CREAM)
    px(img, tip + 1, hy + 2 + dy, PAPER_L)
    px(img, tip, hy - 1 + dy, CREAM)
    if flash:
        for dx, dy2, c in [(-1, -3, CREAM), (1, -2, GOLD), (2, 1, CREAM),
                           (0, 5, VIOLET), (-2, -4, PAPER_L), (3, 0, CREAM)]:
            px(img, tip + dx, hy + dy + dy2, c)


def qinshi_draw(img, pose):
    breath = pose.get("breath", 0)
    bx = pose.get("bx", 0)
    by = pose.get("by", 0)
    cx = 22 + bx
    cy = 3 + by + breath
    qs_head(img, cx, cy)

    ty = 24 + by + breath
    # violet upper shoulders
    rect(img, cx - 11, ty, cx + 12, ty + 5, VIOLET)
    hline(img, cx - 10, cx + 11, ty, GOLD)
    px(img, cx - 11, ty, PAPER_L)
    px(img, cx + 11, ty + 1, GOLD)
    # collar paper
    rect(img, cx - 4, ty, cx + 6, ty + 5, PAPER_L)
    rect(img, cx - 3, ty + 1, cx + 5, ty + 4, PAPER)
    # violet torso upper
    rect(img, cx - 10, ty + 4, cx + 12, ty + 12, VIOLET)
    robe_folds(img, cx - 10, cx + 12, ty + 5, ty + 12, NIGHT, GOLD)
    # paper-light lower robe
    rect(img, cx - 11, ty + 12, cx + 13, ty + 26, PAPER_L)
    robe_folds(img, cx - 11, cx + 13, ty + 13, ty + 26, PAPER_D, PAPER)
    # sash
    belt(img, cx - 10, cx + 12, ty + 11, GOLD, CREAM, hang=True)
    # violet outer sleeve flaps at sides (idle cue)
    rect(img, cx - 12, ty + 4, cx - 9, ty + 20, VIOLET)
    hline(img, cx - 12, cx - 9, ty + 18, PAPER_L)

    lift_l = pose.get("lift_l", 0)
    lift_r = pose.get("lift_r", 0)
    ly = ty + 26
    lx0 = cx - 9 - (4 if lift_l else 0) - (2 if pose.get("stride_l") else 0)
    rect(img, lx0, ly - lift_l, lx0 + 8, ly + 12 - lift_l, PAPER_L)
    hline(img, lx0 + 1, lx0 + 7, ly - lift_l + 5, PAPER_D)
    rx0 = cx + 1 + (4 if lift_r else 0) + (2 if pose.get("stride_r") else 0)
    rect(img, rx0, ly - lift_r, rx0 + 8, ly + 12 - lift_r, PAPER_L)
    hline(img, rx0 + 1, rx0 + 7, ly - lift_r + 5, PAPER_D)
    hem_layers(img, cx - 12, cx + 14, ly + 1, PAPER_L, PAPER_D, PAPER)
    if lift_l:
        px(img, lx0 - 2, ly - lift_l + 1, PAPER_L)
    if lift_r:
        px(img, rx0 + 8, ly - lift_r + 1, PAPER_L)
    shoe(img, lx0 - 1, ly + 12 - lift_l)
    shoe(img, rx0, ly + 12 - lift_r)

    kind = pose.get("kind", "idle")

    if kind == "idle":
        rect(img, cx - 15, ty + 3, cx - 9, ty + 15, VIOLET)
        rect(img, cx - 16, ty + 13, cx - 10, ty + 19, VIOLET)
        sleeve_cuff(img, cx - 16, cx - 10, ty + 15, VIOLET, PAPER_L)
        hand(img, cx - 16, ty + 17, SKIN)
        rect(img, cx + 10, ty + 5, cx + 16, ty + 15, VIOLET)
        sleeve_folds(img, cx + 10, cx + 16, ty + 6, ty + 14, NIGHT, GOLD)
        sleeve_cuff(img, cx + 10, cx + 16, ty + 13, VIOLET, PAPER_L)
        hand(img, cx + 12, ty + 13, SKIN, fist=True)
        qs_whisk_vert(img, cx + 16, ty + 8, tip_up=False)

    elif kind == "walk":
        if lift_l:
            rect(img, cx + 10, ty + 1, cx + 17, ty + 12, VIOLET)
            sleeve_cuff(img, cx + 10, cx + 17, ty + 10, VIOLET, PAPER_L)
            hand(img, cx + 15, ty + 10, SKIN)
            rect(img, cx - 15, ty + 7, cx - 9, ty + 17, VIOLET)
            hand(img, cx - 16, ty + 15, SKIN)
        else:
            rect(img, cx - 17, ty + 1, cx - 9, ty + 12, VIOLET)
            sleeve_cuff(img, cx - 17, cx - 9, ty + 10, VIOLET, PAPER_L)
            hand(img, cx - 17, ty + 10, SKIN)
            rect(img, cx + 10, ty + 7, cx + 16, ty + 17, VIOLET)
            hand(img, cx + 12, ty + 15, SKIN, fist=True)
        qs_whisk_vert(img, cx + 16, ty + 10, tip_up=False)

    elif kind == "windup":
        phase = pose.get("phase", 0)
        # arms high-back gripping whisk
        rect(img, cx - 18, ty - 8, cx - 6, ty + 4, VIOLET)
        sleeve_folds(img, cx - 18, cx - 6, ty - 7, ty + 3, NIGHT, GOLD)
        hand(img, cx - 20, ty - 2, SKIN, fist=True)
        rect(img, cx - 6, ty - 10, cx + 4, ty + 0, VIOLET)
        sleeve_folds(img, cx - 6, cx + 4, ty - 9, ty - 1, NIGHT, GOLD)
        hand(img, cx - 8, ty - 8, SKIN, fist=True)
        rect(img, cx + 12, ty + 14, cx + 18, ty + 26, PAPER_L)
        robe_folds(img, cx + 12, cx + 18, ty + 15, ty + 25, PAPER_D, PAPER)
        rect(img, cx - 16, ty + 16, cx - 10, ty + 28, PAPER_L)
        qs_whisk_back(img, cx - 14, ty - 2, lean=phase + 1)
        rect(img, cx - 16, ly + 4, cx - 4, ly + 14, PAPER_L)
        hline(img, cx - 15, cx - 5, ly + 8, PAPER_D)
        if phase >= 1:
            rect(img, cx + 2, ly - 8, cx + 10, ly + 6, PAPER_L)
            px(img, cx - 16, ty - 12, CREAM)
            px(img, cx - 14, ty - 14, VIOLET)

    elif kind == "strike":
        phase = pose.get("phase", 0)
        if phase == 0:
            rect(img, cx - 14, ty - 4, cx - 4, ty + 8, VIOLET)
            sleeve_folds(img, cx - 14, cx - 4, ty - 3, ty + 7, NIGHT, GOLD)
            hand(img, cx - 14, ty + 2, SKIN, fist=True)
            rect(img, cx + 6, ty - 6, cx + 16, ty + 6, VIOLET)
            hand(img, cx + 13, ty - 2, SKIN, fist=True)
            qs_whisk_slash(img, cx + 14, ty - 2, length=16, dy=-2)
            rect(img, cx - 14, ty + 16, cx - 8, ty + 26, PAPER_L)
        elif phase == 1:
            # === HIT FRAME — whisk fully extended sweep ===
            rect(img, cx - 14, ty + 8, cx - 4, ty + 18, VIOLET)
            sleeve_folds(img, cx - 14, cx - 4, ty + 9, ty + 17, NIGHT, GOLD)
            hand(img, cx - 14, ty + 16, SKIN)
            rect(img, cx + 6, ty + 0, cx + 22, ty + 10, VIOLET)
            sleeve_folds(img, cx + 6, cx + 22, ty + 1, ty + 9, NIGHT, GOLD)
            sleeve_cuff(img, cx + 16, cx + 22, ty + 8, VIOLET, PAPER_L)
            hand(img, cx + 20, ty + 2, SKIN, fist=True)
            qs_whisk_slash(img, cx + 22, ty + 3, length=28, dy=-2, flash=True)
            rect(img, cx + 12, ty + 14, cx + 20, ty + 24, PAPER_L)
            robe_folds(img, cx + 12, cx + 20, ty + 15, ty + 23, PAPER_D, PAPER)
            for i, (dx, dy) in enumerate([(-2, 2), (-4, 0), (-6, 3), (-3, -2)]):
                px(img, cx + 4 + dx, ty + 4 + dy, CREAM if i % 2 == 0 else VIOLET)
        elif phase == 2:
            rect(img, cx - 10, ty + 10, cx - 2, ty + 20, VIOLET)
            hand(img, cx - 10, ty + 18, SKIN)
            rect(img, cx + 8, ty + 2, cx + 22, ty + 12, VIOLET)
            sleeve_folds(img, cx + 8, cx + 22, ty + 3, ty + 11, NIGHT, GOLD)
            hand(img, cx + 20, ty + 4, SKIN, fist=True)
            qs_whisk_slash(img, cx + 22, ty + 5, length=26, dy=1, flash=True)
            rect(img, cx + 10, ty + 14, cx + 18, ty + 24, PAPER_L)
        else:
            rect(img, cx - 13, ty + 5, cx - 5, ty + 15, VIOLET)
            hand(img, cx - 13, ty + 13, SKIN)
            rect(img, cx + 8, ty + 5, cx + 15, ty + 15, VIOLET)
            hand(img, cx + 11, ty + 13, SKIN, fist=True)
            qs_whisk_vert(img, cx + 15, ty + 8, tip_up=False)

    elif kind == "hurt":
        phase = pose.get("phase", 0)
        if phase == 0:
            rect(img, cx + 10, ty - 5, cx + 18, ty + 7, VIOLET)
            hand(img, cx + 16, ty - 6, SKIN)
            rect(img, cx - 15, ty + 9, cx - 7, ty + 19, VIOLET)
            hand(img, cx - 16, ty + 17, SKIN)
            qs_whisk_vert(img, cx + 6, ty + 12, tip_up=False)
        else:
            rect(img, cx + 11, ty + 5, cx + 20, ty + 15, VIOLET)
            hand(img, cx + 18, ty + 13, SKIN)
            rect(img, cx - 14, ty + 3, cx - 6, ty + 13, VIOLET)
            hand(img, cx - 15, ty + 11, SKIN)
            qs_whisk_vert(img, cx - 2, ty + 14, tip_up=False)
        for dx, dy, c in [
            (6, 6, CINN_B), (10, 10, BLOOD), (2, 14, CINN_B),
            (14, 8, BLOOD), (8, 16, BLOOD), (12, 4, CINN_B),
            (-2, 12, BLOOD), (16, 12, CINN), (4, 18, BLOOD),
        ]:
            px(img, cx + dx, ty + dy, c)

    elif kind == "parry":
        phase = pose.get("phase", 0)
        shake = pose.get("shake", 0)
        if phase < 2:
            # whisk HIGH overhead guard
            rect(img, cx - 16, ty - 10, cx - 6, ty + 2, VIOLET)
            sleeve_folds(img, cx - 16, cx - 6, ty - 9, ty + 1, NIGHT, GOLD)
            hand(img, cx - 10, ty - 12, SKIN, fist=True)
            rect(img, cx + 2, ty - 12, cx + 14, ty + 0, VIOLET)
            sleeve_folds(img, cx + 2, cx + 14, ty - 11, ty - 1, NIGHT, GOLD)
            hand(img, cx + 8 + shake, ty - 14, SKIN, fist=True)
            qs_whisk_vert(img, cx + 6 + shake, ty - 6, tip_up=True)
            rect(img, cx - 14, ty + 18, cx - 6, ty + 26, PAPER_L)
            rect(img, cx + 8, ty + 18, cx + 16, ty + 26, PAPER_L)
            if phase == 1:
                for dx, dy, c in [(0, -28, CREAM), (4, -26, GOLD), (2, -24, PAPER_L),
                                  (6, -30, VIOLET), (-2, -26, CREAM)]:
                    px(img, cx + 6 + shake + dx, ty + dy, c)
        else:
            # dodge — whisk across body
            rect(img, cx - 18, ty + 2, cx - 8, ty + 14, VIOLET)
            sleeve_folds(img, cx - 18, cx - 8, ty + 3, ty + 13, NIGHT, GOLD)
            hand(img, cx - 18, ty + 12, SKIN)
            rect(img, cx - 4, ty - 4, cx + 8, ty + 8, VIOLET)
            hand(img, cx + 4, ty - 2, SKIN, fist=True)
            qs_whisk_slash(img, cx + 6, ty + 0, length=18, dy=2, flash=False)
            rect(img, cx - 18, ty + 16, cx - 8, ty + 28, PAPER_L)
            robe_folds(img, cx - 18, cx - 8, ty + 17, ty + 27, PAPER_D, PAPER)

    vline(img, cx - 11, ty, ty + 22, INK)
    vline(img, cx + 11, ty, ty + 18, INK)


# ============================================================
# assembly (tiezhang + qinshi only)
# ============================================================
def poses_v11():
    """Same exaggeration as v0.9 r2."""
    poses = []
    poses.append({"kind": "idle", "breath": 0, "bx": 0, "by": 0})
    poses.append({"kind": "idle", "breath": 1, "bx": 0, "by": 0})
    poses.append({"kind": "walk", "breath": 0, "lift_l": 12, "stride_l": 1, "bx": -2})
    poses.append({"kind": "walk", "breath": 0, "lift_l": 4, "bx": 0})
    poses.append({"kind": "walk", "breath": 0, "lift_r": 12, "stride_r": 1, "bx": 2})
    poses.append({"kind": "walk", "breath": 1, "lift_r": 4, "bx": 0})
    poses.append({"kind": "windup", "phase": 0, "breath": 0, "bx": -4, "by": 2, "lift_l": 2})
    poses.append({"kind": "windup", "phase": 1, "breath": 0, "bx": -8, "by": 2, "lift_r": 10})
    poses.append({"kind": "windup", "phase": 2, "breath": 1, "bx": -10, "by": 3, "lift_r": 12})
    poses.append({"kind": "strike", "phase": 0, "breath": 0, "bx": -6, "by": 0})
    poses.append({"kind": "strike", "phase": 1, "breath": 0, "bx": -4, "by": 0, "lift_r": 10, "stride_r": 1})
    poses.append({"kind": "strike", "phase": 2, "breath": 1, "bx": -2, "by": 0, "lift_l": 6})
    poses.append({"kind": "strike", "phase": 3, "breath": 0, "bx": -4})
    poses.append({"kind": "hurt", "phase": 0, "breath": 0, "bx": -8, "lift_l": 6})
    poses.append({"kind": "hurt", "phase": 1, "breath": 1, "bx": -12, "by": 2, "lift_r": 4})
    poses.append({"kind": "parry", "phase": 0, "breath": 0, "shake": 0, "bx": 2, "by": 3, "lift_l": 4, "lift_r": 4})
    poses.append({"kind": "parry", "phase": 1, "breath": 0, "shake": 3, "bx": 0, "by": 3, "lift_l": 5, "lift_r": 5})
    poses.append({"kind": "parry", "phase": 2, "breath": 1, "shake": 0, "bx": -10, "by": 1, "lift_l": 8})
    return poses


DRAWERS = {"tiezhang": tiezhang_draw, "qinshi": qinshi_draw}


def make_sheet(char_id: str) -> Image.Image:
    sheet = Image.new("RGBA", (18 * FS, FS), TRANS)
    drawer = DRAWERS[char_id]
    poses = poses_v11()
    assert len(poses) == 18
    for i, pose in enumerate(poses):
        frame = new_frame()
        drawer(frame, pose)
        sheet.paste(frame, (i * FS, 0), frame)
    return sheet


def count_oob(img: Image.Image):
    n = 0
    samples = []
    for y in range(img.height):
        for x in range(img.width):
            p = img.getpixel((x, y))
            if p[3] == 0:
                continue
            if p[:3] not in PALETTE_SET:
                n += 1
                if len(samples) < 8:
                    samples.append((x, y, "#{:02X}{:02X}{:02X}".format(*p[:3])))
    return n, samples


def visible_pixels(sheet, i):
    x0 = i * FS
    return sum(1 for y in range(FS) for x in range(x0, x0 + FS) if sheet.getpixel((x, y))[3] > 0)


def colors_used(sheet):
    used = set()
    for y in range(sheet.height):
        for x in range(sheet.width):
            p = sheet.getpixel((x, y))
            if p[3] > 0:
                used.add("#{:02X}{:02X}{:02X}".format(*p[:3]))
    return sorted(used)


def preview_scale(src, path, scale=2, paper=True):
    big = src.resize((src.width * scale, src.height * scale), Image.Resampling.NEAREST)
    if paper:
        bg = Image.new("RGBA", big.size, PAPER)
        bg.paste(big, (0, 0), big)
        bg.save(path)
    else:
        big.save(path)
    return path


def crop_frame(sheet, i):
    return sheet.crop((i * FS, 0, (i + 1) * FS, FS))


def write_readme():
    readme = OUT / "README.md"
    text = readme.read_text(encoding="utf-8") if readme.exists() else ""
    # update tiezhang/qinshi rows if present
    import re
    def set_row(txt, name, status):
        pat = rf"\| `{name}\.png` \|[^\n]+\n"
        row = f"| `{name}.png` | **1152×64** | **{status}** | `tools/gen_sprites_64_v11.py` |\n"
        if re.search(pat, txt):
            return re.sub(pat, row, txt)
        return txt
    text = set_row(text, "tiezhang", "v1.1 精修（震掌／藥囊）")
    text = set_row(text, "qinshi", "v1.1 精修（拂塵／梵紫）")
    if "## v1.1" not in text:
        note = """
## v1.1 鐵掌／琴師

- `tiezhang`：醫袍紅＋藥綠囊；攻擊＝蓄掌／震掌（無劍）
- `qinshi`：梵紫＋素袍；道具＝拂塵；攻擊＝橫掃
- 姿勢誇張對齊 v0.9 r2；生成：`tools/gen_sprites_64_v11.py`
- 報告：`_gen_report_v11.txt`

"""
        text = text.rstrip() + "\n" + note
    readme.write_text(text, encoding="utf-8")


def make_compare(sheet, cid):
    def paper_x3(fr):
        big = fr.resize((192, 192), Image.Resampling.NEAREST)
        bg = Image.new("RGBA", (192, 192), PAPER)
        bg.paste(big, (0, 0), big)
        return bg
    strip = Image.new("RGBA", (192 * 4 + 12, 192), PAPER_D)
    for i, idx in enumerate([0, 7, 10, 15]):
        strip.paste(paper_x3(crop_frame(sheet, idx)), (i * (192 + 4), 0))
    strip.save(PREV / f"64_{cid}_compare_v11.png")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    PREV.mkdir(parents=True, exist_ok=True)
    report = ["# v1.1 sprite gen report (tiezhang + qinshi)", ""]
    total_oob = 0
    frame_labels = [
        "idle0", "idle1", "walk0", "walk1", "walk2", "walk3",
        "windup0", "windup1", "windup2",
        "strike0", "strike1", "strike2", "strike3",
        "hurt0", "hurt1", "parry0", "parry1", "parry2",
    ]
    key_preview = {
        "idle": 0, "windup": 7, "strike": 10, "hurt": 13,
        "parry": 15, "parry_dodge": 17, "walk": 2,
    }

    # snapshot hashes of untouched sheets
    import hashlib
    untouched = {}
    for cid in ("qingyi", "langren", "xiaoer"):
        fp = OUT / f"{cid}.png"
        if fp.exists():
            untouched[cid] = hashlib.md5(fp.read_bytes()).hexdigest()

    for cid in ("tiezhang", "qinshi"):
        sheet = make_sheet(cid)
        assert sheet.size == (1152, 64), sheet.size
        oob, samples = count_oob(sheet)
        total_oob += oob
        used = colors_used(sheet)
        path = OUT / f"{cid}.png"
        sheet.save(path)
        preview_scale(sheet, PREV / f"64_{cid}_x2.png", 2)
        for name, idx in key_preview.items():
            fr = crop_frame(sheet, idx)
            preview_scale(fr, PREV / f"64_{cid}_{name}_x2.png", 2)
            preview_scale(fr, PREV / f"64_{cid}_{name}_x3.png", 3)
        make_compare(sheet, cid)
        report.append(f"## {cid}")
        report.append(f"path: {path}")
        report.append(f"size: {sheet.size}")
        report.append(f"oob: {oob}")
        if samples:
            report.append(f"oob_samples: {samples}")
        report.append(f"palette_used ({len(used)}): {', '.join(used)}")
        report.append("frames:")
        for i, lab in enumerate(frame_labels):
            vp = visible_pixels(sheet, i)
            empty = " EMPTY!" if vp == 0 else ""
            report.append(f"  {i:02d} {lab}: visible={vp}{empty}")
        report.append("")
        print(f"{cid}: size={sheet.size} oob={oob} colors={len(used)}")

    for cid, h in untouched.items():
        now = hashlib.md5((OUT / f"{cid}.png").read_bytes()).hexdigest()
        assert now == h, f"FORBIDDEN overwrite of {cid}"
        report.append(f"untouched_ok: {cid} md5={h}")

    report.append(f"TOTAL_OOB={total_oob}")
    (OUT / "_gen_report_v11.txt").write_text("\n".join(report) + "\n", encoding="utf-8")
    write_readme()
    print(f"TOTAL_OOB={total_oob}")
    if total_oob != 0:
        raise SystemExit(f"palette oob={total_oob}")
    print("OK")


if __name__ == "__main__":
    main()
