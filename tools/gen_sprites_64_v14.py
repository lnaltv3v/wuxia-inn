#!/usr/bin/env python3
"""v1.4 Ink-Pixel Inn — boss combat + generic enemy sheets (r2 density).

Does NOT overwrite heroes / xiaoer / guest / scenes / fx.

Boss & enemy sheets: 4 frames × 64 = 256×64
  0 idle | 1 windup/ready | 2 strike | 3 hurt
Game draws frame0 via drawImage(img, 0, 0, height, height, ...).
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


NF = 4  # frames per short sheet


def sheet4():
    return Image.new("RGBA", (NF * FS, FS), TRANS)


def paste_frame(sheet, i, fr):
    sheet.paste(fr, (i * FS, 0), fr)


# ============================================================
# shared combat bits
# ============================================================
def feet_pair(img, lx, rx, y, wide=False):
    shoe(img, lx, y, wide=wide)
    shoe(img, rx, y, wide=wide)


def blood_spatters(img, cx, cy, n=8):
    pts = [
        (0, 0, CINN_B), (4, 3, BLOOD), (-3, 5, CINN_B), (7, 1, BLOOD),
        (2, 8, BLOOD), (-5, 2, CINN), (6, 6, CINN_B), (1, 4, BLOOD),
        (9, 4, CINN), (-2, 9, BLOOD),
    ]
    for i, (dx, dy, c) in enumerate(pts[:n]):
        px(img, cx + dx, cy + dy, c)


# ============================================================
# BOSS: heifeng — wild hair, shoulder armor, giant blade
# ============================================================
def hf_head(img, cx, cy):
    # wild flowing hair
    rect(img, cx - 10, cy + 2, cx + 12, cy + 12, INK)
    rect(img, cx - 14, cy + 4, cx + 14, cy + 10, INK)
    for ox, oy in [(-12, -2), (-8, -4), (-2, -6), (4, -5), (10, -3), (14, 0), (-14, 2), (16, 4)]:
        px(img, cx + ox, cy + oy, INK)
        px(img, cx + ox + 1, cy + oy + 1, INK_SOFT)
    # cinnabar headband trailing
    rect(img, cx - 9, cy + 6, cx + 10, cy + 10, CINN_B)
    hline(img, cx - 9, cx + 10, cy + 7, CINN)
    px(img, cx + 11, cy + 8, BLOOD)
    px(img, cx + 13, cy + 9, BLOOD)
    px(img, cx + 15, cy + 10, CINN)
    # face darker skin
    rect(img, cx - 7, cy + 10, cx + 9, cy + 20, SKIN_D)
    px(img, cx - 2, cy + 14, INK); px(img, cx - 1, cy + 14, INK)
    px(img, cx + 3, cy + 14, INK); px(img, cx + 4, cy + 14, INK); px(img, cx + 5, cy + 14, INK)
    px(img, cx + 7, cy + 16, NIGHT)
    hline(img, cx - 5, cx + 7, cy + 19, NIGHT)
    rect(img, cx - 3, cy + 20, cx + 5, cy + 24, SKIN_D)


def hf_blade(img, hx, hy, mode="idle"):
    """Giant dao — thick ink/mist/cinnabar edge."""
    if mode == "back":
        # high-back windup
        for i in range(28):
            x = hx - 2 - i // 3
            y = hy - 4 - i
            rect(img, x, y, x + 8, y + 3, INK)
            rect(img, x + 1, y + 1, x + 6, y + 2, MIST)
            if i % 3 == 0:
                px(img, x + 7, y, CINN_B)
        rect(img, hx - 2, hy + 20, hx + 8, hy + 28, WOOD)
        outline_rect(img, hx - 2, hy + 20, hx + 8, hy + 28, INK)
        px(img, hx + 2, hy - 32, CREAM)
        px(img, hx, hy - 30, CINN_B)
    elif mode == "slash":
        # extended horizontal-ish cut
        rect(img, hx, hy, hx + 6, hy + 8, WOOD)
        outline_rect(img, hx, hy, hx + 6, hy + 8, INK)
        rect(img, hx + 5, hy - 4, hx + 36, hy + 8, INK)
        rect(img, hx + 7, hy - 2, hx + 34, hy + 6, MIST)
        rect(img, hx + 10, hy, hx + 30, hy + 4, CINN_B)
        hline(img, hx + 8, hx + 34, hy - 3, CREAM)
        px(img, hx + 36, hy + 1, CREAM)
        px(img, hx + 35, hy - 2, CINN_B)
        # arc trail
        for i in range(0, 16, 2):
            px(img, hx + 20 + i, hy - 6 - i // 4, CREAM)
            px(img, hx + 18 + i, hy + 8 + i // 5, CINN)
    else:
        # idle vertical giant blade at right
        rect(img, hx, hy, hx + 10, hy + 44, INK)
        rect(img, hx + 2, hy + 2, hx + 8, hy + 40, MIST)
        rect(img, hx + 3, hy + 4, hx + 7, hy + 36, CINN_B)
        vline(img, hx + 1, hy + 2, hy + 42, CREAM)
        rect(img, hx - 2, hy + 40, hx + 12, hy + 48, WOOD)
        outline_rect(img, hx - 2, hy + 40, hx + 12, hy + 48, INK)
        px(img, hx + 4, hy, CINN_B)
        px(img, hx + 5, hy + 2, CREAM)


def heifeng_draw(img, phase):
    """0 idle | 1 windup | 2 strike | 3 hurt"""
    if phase == 0:
        bx, by = 0, 0
        cx, cy = 18, 2
        hf_head(img, cx, cy)
        ty = 24
        # wide shoulder armor
        rect(img, cx - 14, ty, cx + 16, ty + 8, WOOD)
        rect(img, cx - 16, ty + 2, cx - 8, ty + 10, FRAME)
        rect(img, cx + 8, ty + 2, cx + 18, ty + 10, FRAME)
        outline_rect(img, cx - 16, ty + 2, cx - 8, ty + 10, INK)
        outline_rect(img, cx + 8, ty + 2, cx + 18, ty + 10, INK)
        px(img, cx - 14, ty + 4, GOLD)
        px(img, cx + 14, ty + 4, GOLD)
        # torso ink-soft / night
        rect(img, cx - 11, ty + 6, cx + 14, ty + 28, INK_SOFT)
        robe_folds(img, cx - 11, cx + 14, ty + 8, ty + 28, NIGHT, WOOD)
        rect(img, cx - 4, ty + 6, cx + 6, ty + 10, SKIN_D)
        belt(img, cx - 11, cx + 14, ty + 16, FRAME, CINN_B, hang=True)
        # legs
        rect(img, cx - 10, ty + 28, cx - 1, ty + 42, INK_SOFT)
        rect(img, cx + 2, ty + 28, cx + 11, ty + 42, INK_SOFT)
        hem_layers(img, cx - 12, cx + 15, ty + 30, INK_SOFT, NIGHT, WOOD)
        feet_pair(img, cx - 11, cx + 2, ty + 42, wide=True)
        # arms
        rect(img, cx - 18, ty + 8, cx - 10, ty + 20, INK_SOFT)
        hand(img, cx - 18, ty + 18, SKIN_D, fist=True)
        rect(img, cx + 12, ty + 8, cx + 20, ty + 18, INK_SOFT)
        hand(img, cx + 16, ty + 14, SKIN_D, fist=True)
        hf_blade(img, cx + 20, ty - 2, "idle")
        vline(img, cx - 12, ty, ty + 26, INK)
        vline(img, cx + 13, ty, ty + 22, INK)

    elif phase == 1:
        # windup — blade high-back, body coiled left
        cx, cy = 14, 3
        hf_head(img, cx, cy)
        ty = 26
        rect(img, cx - 14, ty, cx + 14, ty + 8, WOOD)
        rect(img, cx - 16, ty + 2, cx - 8, ty + 10, FRAME)
        rect(img, cx + 6, ty + 2, cx + 16, ty + 10, FRAME)
        px(img, cx - 14, ty + 4, GOLD)
        rect(img, cx - 12, ty + 6, cx + 12, ty + 26, INK_SOFT)
        robe_folds(img, cx - 12, cx + 12, ty + 8, ty + 26, NIGHT, WOOD)
        belt(img, cx - 12, cx + 12, ty + 14, FRAME, CINN_B, hang=True)
        # arms high gripping blade
        rect(img, cx - 16, ty - 8, cx - 4, ty + 6, INK_SOFT)
        sleeve_folds(img, cx - 16, cx - 4, ty - 7, ty + 5, NIGHT, WOOD)
        hand(img, cx - 14, ty - 4, SKIN_D, fist=True)
        rect(img, cx - 4, ty - 12, cx + 8, ty + 0, INK_SOFT)
        hand(img, cx - 2, ty - 10, SKIN_D, fist=True)
        hf_blade(img, cx - 8, ty - 6, "back")
        # rear coat flare + planted foot
        rect(img, cx + 10, ty + 16, cx + 18, ty + 30, INK_SOFT)
        robe_folds(img, cx + 10, cx + 18, ty + 17, ty + 29, NIGHT, WOOD)
        rect(img, cx - 14, ty + 26, cx - 2, ty + 40, INK_SOFT)
        rect(img, cx + 0, ty + 20, cx + 10, ty + 36, INK_SOFT)
        feet_pair(img, cx - 15, cx + 2, ty + 40, wide=True)
        # threat sparks
        px(img, cx - 10, ty - 20, CINN_B)
        px(img, cx - 6, ty - 24, CREAM)
        px(img, cx - 12, ty - 18, GOLD)

    elif phase == 2:
        # strike — lunge + giant slash
        cx, cy = 12, 2
        hf_head(img, cx, cy)
        ty = 24
        rect(img, cx - 12, ty, cx + 16, ty + 8, WOOD)
        rect(img, cx - 14, ty + 2, cx - 6, ty + 10, FRAME)
        rect(img, cx + 8, ty + 2, cx + 18, ty + 10, FRAME)
        px(img, cx + 14, ty + 4, GOLD)
        rect(img, cx - 10, ty + 6, cx + 14, ty + 24, INK_SOFT)
        robe_folds(img, cx - 10, cx + 14, ty + 8, ty + 24, NIGHT, WOOD)
        belt(img, cx - 10, cx + 14, ty + 14, FRAME, CINN_B, hang=True)
        # rear arm
        rect(img, cx - 16, ty + 10, cx - 6, ty + 20, INK_SOFT)
        hand(img, cx - 16, ty + 18, SKIN_D, fist=True)
        # strike arm extended
        rect(img, cx + 8, ty + 0, cx + 26, ty + 12, INK_SOFT)
        sleeve_folds(img, cx + 8, cx + 26, ty + 1, ty + 11, NIGHT, WOOD)
        hand(img, cx + 24, ty + 4, SKIN_D, fist=True)
        hf_blade(img, cx + 26, ty + 2, "slash")
        # forward coat + raised lead leg
        rect(img, cx + 10, ty + 16, cx + 20, ty + 28, INK_SOFT)
        robe_folds(img, cx + 10, cx + 20, ty + 17, ty + 27, NIGHT, WOOD)
        rect(img, cx - 10, ty + 24, cx - 0, ty + 40, INK_SOFT)
        rect(img, cx + 2, ty + 16, cx + 12, ty + 32, INK_SOFT)
        feet_pair(img, cx - 11, cx + 4, ty + 40, wide=True)
        for i, (dx, dy) in enumerate([(-2, 2), (-4, 0), (-6, 3)]):
            px(img, cx + 4 + dx, ty + 4 + dy, CINN_B if i % 2 == 0 else CREAM)

    else:
        # hurt — stagger back, blade tip down
        cx, cy = 10, 4
        hf_head(img, cx, cy)
        ty = 26
        rect(img, cx - 12, ty, cx + 14, ty + 24, INK_SOFT)
        robe_folds(img, cx - 12, cx + 14, ty + 2, ty + 24, NIGHT, WOOD)
        rect(img, cx - 14, ty, cx - 6, ty + 8, FRAME)
        rect(img, cx + 6, ty, cx + 16, ty + 8, FRAME)
        belt(img, cx - 12, cx + 14, ty + 14, FRAME, CINN_B, hang=True)
        rect(img, cx + 10, ty - 4, cx + 20, ty + 10, INK_SOFT)
        hand(img, cx + 18, ty - 2, SKIN_D)
        rect(img, cx - 18, ty + 10, cx - 8, ty + 20, INK_SOFT)
        hand(img, cx - 18, ty + 18, SKIN_D)
        # blade dropping
        rect(img, cx + 16, ty + 8, cx + 24, ty + 36, INK)
        rect(img, cx + 18, ty + 10, cx + 22, ty + 32, MIST)
        rect(img, cx + 14, ty + 32, cx + 26, ty + 40, WOOD)
        rect(img, cx - 10, ty + 24, cx + 0, ty + 40, INK_SOFT)
        rect(img, cx + 2, ty + 26, cx + 12, ty + 40, INK_SOFT)
        feet_pair(img, cx - 12, cx + 2, ty + 40)
        blood_spatters(img, cx + 2, ty + 6, 10)


# ============================================================
# BOSS: xieyi — violet, double bun, poison vial, claws
# ============================================================
def xy_head(img, cx, cy):
    # double bun
    rect(img, cx - 8, cy + 2, cx + 9, cy + 9, INK)
    rect(img, cx - 12, cy - 2, cx - 4, cy + 6, INK)
    rect(img, cx + 4, cy - 4, cx + 14, cy + 6, INK)
    px(img, cx - 8, cy - 1, GOLD)
    px(img, cx + 10, cy - 2, GOLD)
    px(img, cx + 11, cy, VIOLET)
    # violet forehead mark
    rect(img, cx - 4, cy + 4, cx + 6, cy + 8, VIOLET)
    px(img, cx, cy + 5, GOLD)
    rect(img, cx - 7, cy + 9, cx + 9, cy + 19, SKIN)
    px(img, cx - 2, cy + 13, INK); px(img, cx - 1, cy + 13, INK)
    px(img, cx + 3, cy + 13, INK); px(img, cx + 4, cy + 13, INK); px(img, cx + 5, cy + 13, INK)
    px(img, cx + 7, cy + 15, SKIN_D)
    hline(img, cx - 5, cx + 7, cy + 18, SKIN_D)
    rect(img, cx - 3, cy + 19, cx + 5, cy + 23, SKIN)


def xy_vial(img, x, y, tipped=False):
    rect(img, x, y, x + 10, y + 16, JADE_B)
    outline_rect(img, x, y, x + 10, y + 16, INK)
    rect(img, x + 2, y + 2, x + 8, y + 12, JADE)
    px(img, x + 4, y + 4, GOLD)
    px(img, x + 6, y + 8, CREAM)
    rect(img, x + 2, y - 3, x + 8, y + 1, WOOD)
    if tipped:
        for i, (dx, dy) in enumerate([(10, 2), (12, 4), (13, 7), (14, 10)]):
            px(img, x + dx, y + dy, JADE_B if i % 2 == 0 else JADE)
            px(img, x + dx + 1, y + dy + 1, CREAM)


def xy_claw(img, x, y, long=False):
    hand(img, x, y, SKIN, fist=True)
    tips = [(6, -2), (8, 0), (7, 3), (5, 5)] if not long else [(8, -3), (11, -1), (12, 2), (10, 5), (7, 7)]
    for dx, dy in tips:
        px(img, x + dx, y + dy, INK)
        px(img, x + dx + 1, y + dy, INK_SOFT)
        if long:
            px(img, x + dx + 2, y + dy + 1, JADE)


def xieyi_draw(img, phase):
    if phase == 0:
        cx, cy = 20, 2
        xy_head(img, cx, cy)
        ty = 24
        rect(img, cx - 11, ty, cx + 13, ty + 24, VIOLET)
        robe_folds(img, cx - 11, cx + 13, ty + 2, ty + 24, NIGHT, GOLD)
        rect(img, cx - 4, ty, cx + 6, ty + 5, PAPER_L)
        belt(img, cx - 11, cx + 13, ty + 12, BLOOD, GOLD, hang=True)
        # vial at hip
        xy_vial(img, cx + 10, ty + 10)
        # back arm
        rect(img, cx - 16, ty + 4, cx - 8, ty + 16, VIOLET)
        hand(img, cx - 16, ty + 14, SKIN)
        # claw forward
        rect(img, cx + 10, ty + 2, cx + 20, ty + 12, VIOLET)
        sleeve_folds(img, cx + 10, cx + 20, ty + 3, ty + 11, NIGHT, GOLD)
        xy_claw(img, cx + 18, ty + 4, long=False)
        rect(img, cx - 10, ty + 24, cx - 1, ty + 40, VIOLET)
        rect(img, cx + 2, ty + 24, cx + 11, ty + 40, VIOLET)
        hem_layers(img, cx - 12, cx + 14, ty + 26, VIOLET, NIGHT, GOLD)
        feet_pair(img, cx - 11, cx + 2, ty + 40)
        vline(img, cx - 12, ty, ty + 22, INK)

    elif phase == 1:
        # windup — vial raised, claws cocked
        cx, cy = 16, 3
        xy_head(img, cx, cy)
        ty = 26
        rect(img, cx - 12, ty, cx + 12, ty + 22, VIOLET)
        robe_folds(img, cx - 12, cx + 12, ty + 2, ty + 22, NIGHT, GOLD)
        rect(img, cx - 4, ty, cx + 6, ty + 4, PAPER_L)
        belt(img, cx - 12, cx + 12, ty + 12, BLOOD, GOLD, hang=True)
        # both arms high
        rect(img, cx - 16, ty - 10, cx - 4, ty + 4, VIOLET)
        sleeve_folds(img, cx - 16, cx - 4, ty - 9, ty + 3, NIGHT, GOLD)
        xy_claw(img, cx - 14, ty - 8, long=True)
        rect(img, cx + 0, ty - 12, cx + 12, ty + 2, VIOLET)
        hand(img, cx + 8, ty - 10, SKIN, fist=True)
        xy_vial(img, cx + 10, ty - 22, tipped=False)
        # poison drip threat
        px(img, cx + 14, ty - 6, JADE_B)
        px(img, cx + 15, ty - 4, JADE)
        px(img, cx + 16, ty - 2, CREAM)
        rect(img, cx + 10, ty + 14, cx + 18, ty + 28, VIOLET)
        rect(img, cx - 14, ty + 22, cx - 2, ty + 38, VIOLET)
        rect(img, cx + 0, ty + 18, cx + 10, ty + 36, VIOLET)
        feet_pair(img, cx - 15, cx + 2, ty + 38)

    elif phase == 2:
        # strike — claw lunge + vial tip pour
        cx, cy = 12, 2
        xy_head(img, cx, cy)
        ty = 24
        rect(img, cx - 10, ty, cx + 14, ty + 22, VIOLET)
        robe_folds(img, cx - 10, cx + 14, ty + 2, ty + 22, NIGHT, GOLD)
        belt(img, cx - 10, cx + 14, ty + 12, BLOOD, GOLD, hang=True)
        rect(img, cx - 16, ty + 8, cx - 6, ty + 18, VIOLET)
        hand(img, cx - 16, ty + 16, SKIN)
        # claw fully extended
        rect(img, cx + 8, ty - 2, cx + 28, ty + 10, VIOLET)
        sleeve_folds(img, cx + 8, cx + 28, ty - 1, ty + 9, NIGHT, GOLD)
        xy_claw(img, cx + 26, ty + 0, long=True)
        # claw slash ticks
        for i in range(0, 14, 2):
            px(img, cx + 34 + i // 2, ty - 2 + i // 4, JADE_B)
            px(img, cx + 35 + i // 2, ty + 2, CREAM)
        xy_vial(img, cx + 4, ty + 8, tipped=True)
        rect(img, cx + 10, ty + 14, cx + 20, ty + 26, VIOLET)
        rect(img, cx - 10, ty + 22, cx + 0, ty + 40, VIOLET)
        rect(img, cx + 2, ty + 14, cx + 12, ty + 32, VIOLET)
        feet_pair(img, cx - 11, cx + 4, ty + 40)

    else:
        cx, cy = 10, 4
        xy_head(img, cx, cy)
        ty = 26
        rect(img, cx - 12, ty, cx + 14, ty + 22, VIOLET)
        robe_folds(img, cx - 12, cx + 14, ty + 2, ty + 22, NIGHT, GOLD)
        belt(img, cx - 12, cx + 14, ty + 12, BLOOD, GOLD, hang=True)
        rect(img, cx + 10, ty - 2, cx + 20, ty + 10, VIOLET)
        hand(img, cx + 18, ty + 0, SKIN)
        rect(img, cx - 18, ty + 8, cx - 8, ty + 18, VIOLET)
        hand(img, cx - 18, ty + 16, SKIN)
        xy_vial(img, cx + 6, ty + 16, tipped=True)
        rect(img, cx - 10, ty + 22, cx + 0, ty + 38, VIOLET)
        rect(img, cx + 2, ty + 24, cx + 12, ty + 38, VIOLET)
        feet_pair(img, cx - 12, cx + 2, ty + 38)
        blood_spatters(img, cx + 2, ty + 6, 8)
        px(img, cx + 8, ty + 10, JADE_B)
        px(img, cx + 10, ty + 14, JADE)


# ============================================================
# BOSS: xueying — blood/night, twin blades, cape
# ============================================================
def xu_head(img, cx, cy):
    rect(img, cx - 9, cy + 1, cx + 10, cy + 10, INK)
    rect(img, cx - 11, cy + 4, cx + 12, cy + 10, INK)
    # blood headband
    rect(img, cx - 8, cy + 6, cx + 9, cy + 10, BLOOD)
    hline(img, cx - 8, cx + 9, cy + 7, CINN_B)
    px(img, cx + 10, cy + 8, CINN)
    px(img, cx + 12, cy + 9, BLOOD)
    rect(img, cx - 7, cy + 10, cx + 9, cy + 20, SKIN_D)
    px(img, cx - 2, cy + 14, INK); px(img, cx - 1, cy + 14, INK)
    px(img, cx + 3, cy + 14, INK); px(img, cx + 4, cy + 14, INK); px(img, cx + 5, cy + 14, INK)
    px(img, cx + 7, cy + 16, NIGHT)
    hline(img, cx - 5, cx + 7, cy + 19, NIGHT)
    rect(img, cx - 3, cy + 20, cx + 5, cy + 24, SKIN_D)


def xu_blade(img, hx, hy, mode="idle", which=0):
    """Twin dagger — sharp thin silhouette."""
    if mode == "back":
        for i in range(18):
            x = hx - i // 2 - which * 2
            y = hy - i
            rect(img, x, y, x + 3, y + 2, MIST)
            px(img, x + 1, y, CREAM)
            if i % 2 == 0:
                px(img, x + 2, y, BLOOD)
        rect(img, hx, hy + 14, hx + 5, hy + 20, WOOD)
    elif mode == "slash":
        rect(img, hx, hy, hx + 4, hy + 5, WOOD)
        length = 22
        rect(img, hx + 3, hy - 1 + which, hx + 3 + length, hy + 3 + which, MIST)
        hline(img, hx + 3, hx + 3 + length, hy - 1 + which, CREAM)
        hline(img, hx + 3, hx + 3 + length, hy + 2 + which, BLOOD)
        px(img, hx + 3 + length, hy + which, CREAM)
        px(img, hx + 4 + length, hy + 1 + which, CINN_B)
        for i in range(0, 10, 2):
            px(img, hx + 8 + i, hy - 3 + which - i // 4, CREAM)
    else:
        # idle crossed / vertical pair
        ox = which * 6
        rect(img, hx + ox, hy, hx + 3 + ox, hy + 28, MIST)
        vline(img, hx + 1 + ox, hy + 1, hy + 26, CREAM)
        vline(img, hx + 2 + ox, hy + 2, hy + 24, BLOOD)
        rect(img, hx - 1 + ox, hy + 26, hx + 5 + ox, hy + 32, WOOD)
        px(img, hx + 1 + ox, hy, CREAM)


def xu_cape(img, cx, ty, flare=0):
    """Shadow cape behind — sharp triangular tips."""
    rect(img, cx - 14 - flare, ty + 4, cx - 6, ty + 30, NIGHT)
    rect(img, cx + 8, ty + 4, cx + 18 + flare, ty + 32, NIGHT)
    for i, oy in enumerate(range(8, 32, 4)):
        px(img, cx - 15 - flare - i % 2, ty + oy, INK)
        px(img, cx + 18 + flare + i % 2, ty + oy + 2, INK)
        px(img, cx + 19 + flare, ty + oy, BLOOD if i % 2 == 0 else NIGHT)


def xueying_draw(img, phase):
    if phase == 0:
        cx, cy = 20, 2
        xu_head(img, cx, cy)
        ty = 24
        xu_cape(img, cx, ty, flare=0)
        rect(img, cx - 10, ty, cx + 12, ty + 24, NIGHT)
        robe_folds(img, cx - 10, cx + 12, ty + 2, ty + 24, INK, BLOOD)
        rect(img, cx - 4, ty, cx + 6, ty + 4, SKIN_D)
        belt(img, cx - 10, cx + 12, ty + 12, CINN, GOLD, hang=True)
        rect(img, cx - 15, ty + 4, cx - 8, ty + 16, NIGHT)
        hand(img, cx - 16, ty + 14, SKIN_D, fist=True)
        rect(img, cx + 10, ty + 2, cx + 18, ty + 14, NIGHT)
        hand(img, cx + 14, ty + 10, SKIN_D, fist=True)
        xu_blade(img, cx + 16, ty - 2, "idle", 0)
        xu_blade(img, cx + 16, ty + 2, "idle", 1)
        rect(img, cx - 9, ty + 24, cx - 0, ty + 40, NIGHT)
        rect(img, cx + 2, ty + 24, cx + 11, ty + 40, NIGHT)
        feet_pair(img, cx - 10, cx + 2, ty + 40)
        vline(img, cx - 11, ty, ty + 22, INK)

    elif phase == 1:
        cx, cy = 16, 3
        xu_head(img, cx, cy)
        ty = 26
        xu_cape(img, cx, ty, flare=4)
        rect(img, cx - 12, ty, cx + 12, ty + 22, NIGHT)
        robe_folds(img, cx - 12, cx + 12, ty + 2, ty + 22, INK, BLOOD)
        belt(img, cx - 12, cx + 12, ty + 12, CINN, GOLD, hang=True)
        rect(img, cx - 16, ty - 10, cx - 4, ty + 4, NIGHT)
        hand(img, cx - 14, ty - 6, SKIN_D, fist=True)
        rect(img, cx - 2, ty - 12, cx + 10, ty + 0, NIGHT)
        hand(img, cx + 4, ty - 10, SKIN_D, fist=True)
        xu_blade(img, cx - 10, ty - 8, "back", 0)
        xu_blade(img, cx + 2, ty - 10, "back", 1)
        rect(img, cx + 10, ty + 14, cx + 18, ty + 30, NIGHT)
        rect(img, cx - 14, ty + 22, cx - 2, ty + 38, NIGHT)
        rect(img, cx + 0, ty + 18, cx + 10, ty + 36, NIGHT)
        feet_pair(img, cx - 15, cx + 2, ty + 38)
        px(img, cx - 8, ty - 22, CREAM)
        px(img, cx - 4, ty - 24, BLOOD)

    elif phase == 2:
        cx, cy = 12, 2
        xu_head(img, cx, cy)
        ty = 24
        xu_cape(img, cx, ty, flare=2)
        rect(img, cx - 10, ty, cx + 14, ty + 22, NIGHT)
        robe_folds(img, cx - 10, cx + 14, ty + 2, ty + 22, INK, BLOOD)
        belt(img, cx - 10, cx + 14, ty + 12, CINN, GOLD, hang=True)
        rect(img, cx - 16, ty + 8, cx - 6, ty + 18, NIGHT)
        hand(img, cx - 16, ty + 16, SKIN_D)
        # dual slash forward
        rect(img, cx + 8, ty - 2, cx + 24, ty + 10, NIGHT)
        sleeve_folds(img, cx + 8, cx + 24, ty - 1, ty + 9, INK, BLOOD)
        hand(img, cx + 22, ty + 0, SKIN_D, fist=True)
        xu_blade(img, cx + 24, ty - 2, "slash", 0)
        xu_blade(img, cx + 22, ty + 6, "slash", 1)
        rect(img, cx + 10, ty + 14, cx + 20, ty + 26, NIGHT)
        rect(img, cx - 10, ty + 22, cx + 0, ty + 40, NIGHT)
        rect(img, cx + 2, ty + 14, cx + 12, ty + 32, NIGHT)
        feet_pair(img, cx - 11, cx + 4, ty + 40)

    else:
        cx, cy = 10, 4
        xu_head(img, cx, cy)
        ty = 26
        xu_cape(img, cx, ty, flare=6)
        rect(img, cx - 12, ty, cx + 14, ty + 22, NIGHT)
        robe_folds(img, cx - 12, cx + 14, ty + 2, ty + 22, INK, BLOOD)
        belt(img, cx - 12, cx + 14, ty + 12, CINN, GOLD, hang=True)
        rect(img, cx + 10, ty - 4, cx + 20, ty + 8, NIGHT)
        hand(img, cx + 18, ty - 2, SKIN_D)
        rect(img, cx - 18, ty + 8, cx - 8, ty + 18, NIGHT)
        hand(img, cx - 18, ty + 16, SKIN_D)
        xu_blade(img, cx + 14, ty + 10, "idle", 0)
        xu_blade(img, cx - 4, ty + 14, "idle", 1)
        rect(img, cx - 10, ty + 22, cx + 0, ty + 38, NIGHT)
        rect(img, cx + 2, ty + 24, cx + 12, ty + 38, NIGHT)
        feet_pair(img, cx - 12, cx + 2, ty + 38)
        blood_spatters(img, cx + 2, ty + 6, 10)


# ============================================================
# ENEMIES — distinct silhouettes, not boss clones
# ============================================================
def en_head_bandit(img, cx, cy, scarf=CINN):
    """Charge/melee: short hair + cloth wrap."""
    rect(img, cx - 8, cy + 3, cx + 9, cy + 10, INK)
    rect(img, cx - 7, cy + 10, cx + 8, cy + 19, SKIN_D)
    rect(img, cx - 8, cy + 8, cx + 9, cy + 12, scarf)
    hline(img, cx - 8, cx + 9, cy + 9, CINN_B if scarf == CINN else FRAME)
    px(img, cx - 2, cy + 14, INK); px(img, cx + 3, cy + 14, INK); px(img, cx + 4, cy + 14, INK)
    hline(img, cx - 4, cx + 6, cy + 18, NIGHT)
    rect(img, cx - 3, cy + 19, cx + 4, cy + 23, SKIN_D)


def en_head_archer(img, cx, cy):
    """Kite: conical bamboo hat silhouette."""
    rect(img, cx - 12, cy + 4, cx + 13, cy + 9, WOOD_L)
    rect(img, cx - 6, cy - 2, cx + 7, cy + 5, WOOD)
    hline(img, cx - 12, cx + 13, cy + 4, INK)
    px(img, cx, cy - 1, GOLD)
    rect(img, cx - 7, cy + 9, cx + 8, cy + 18, SKIN_D)
    px(img, cx - 2, cy + 13, INK); px(img, cx + 3, cy + 13, INK); px(img, cx + 4, cy + 13, INK)
    hline(img, cx - 4, cx + 6, cy + 17, NIGHT)
    rect(img, cx - 3, cy + 18, cx + 4, cy + 22, SKIN_D)


def en_head_melee(img, cx, cy):
    """Melee: short topknot + plain fringe — no scarf (≠ charge)."""
    rect(img, cx - 4, cy - 4, cx + 5, cy + 2, INK)
    rect(img, cx - 2, cy - 8, cx + 3, cy - 2, INK)
    px(img, cx, cy - 6, LOESS)
    rect(img, cx - 8, cy + 2, cx + 9, cy + 10, INK)
    rect(img, cx - 7, cy + 10, cx + 8, cy + 19, SKIN_D)
    px(img, cx - 2, cy + 14, INK); px(img, cx + 3, cy + 14, INK); px(img, cx + 4, cy + 14, INK)
    hline(img, cx - 4, cx + 6, cy + 18, NIGHT)
    rect(img, cx - 3, cy + 19, cx + 4, cy + 23, SKIN_D)


def short_blade(img, hx, hy, mode="idle"):
    if mode == "thrust":
        rect(img, hx, hy, hx + 4, hy + 5, WOOD)
        rect(img, hx + 3, hy + 1, hx + 22, hy + 4, MIST)
        hline(img, hx + 3, hx + 22, hy + 1, CREAM)
        px(img, hx + 22, hy + 2, CREAM)
    elif mode == "back":
        for i in range(14):
            rect(img, hx - i // 2, hy - i, hx + 3 - i // 2, hy + 2 - i, MIST)
        rect(img, hx, hy + 10, hx + 5, hy + 16, WOOD)
    else:
        rect(img, hx, hy, hx + 4, hy + 20, MIST)
        vline(img, hx + 1, hy + 1, hy + 18, CREAM)
        rect(img, hx - 1, hy + 18, hx + 5, hy + 24, WOOD)


def long_dao(img, hx, hy, mode="idle"):
    if mode == "slash":
        rect(img, hx, hy, hx + 5, hy + 6, WOOD)
        rect(img, hx + 4, hy - 2, hx + 28, hy + 6, MIST)
        rect(img, hx + 6, hy, hx + 26, hy + 4, FRAME)
        hline(img, hx + 5, hx + 27, hy - 2, CREAM)
        px(img, hx + 28, hy + 1, CREAM)
        for i in range(0, 12, 2):
            px(img, hx + 12 + i, hy - 4 - i // 5, CREAM)
    elif mode == "back":
        for i in range(22):
            rect(img, hx - i // 3, hy - i, hx + 5 - i // 3, hy + 2 - i, MIST)
            if i % 3 == 0:
                px(img, hx + 5 - i // 3, hy - i, FRAME)
        rect(img, hx, hy + 16, hx + 6, hy + 22, WOOD)
    else:
        rect(img, hx, hy, hx + 6, hy + 32, MIST)
        rect(img, hx + 1, hy + 2, hx + 5, hy + 28, FRAME)
        vline(img, hx + 2, hy + 2, hy + 30, CREAM)
        rect(img, hx - 1, hy + 30, hx + 7, hy + 36, WOOD)


def bow_prop(img, hx, hy, drawn=False):
    """Readable bow: curved tips flare left, grip, string, optional arrow."""
    # upper limb curve
    rect(img, hx - 4, hy - 14, hx + 2, hy - 6, WOOD)
    rect(img, hx - 2, hy - 10, hx + 3, hy - 2, WOOD_L)
    # grip
    rect(img, hx, hy - 2, hx + 4, hy + 8, WOOD)
    vline(img, hx + 1, hy - 1, hy + 7, WOOD_L)
    # lower limb curve
    rect(img, hx - 2, hy + 6, hx + 3, hy + 14, WOOD_L)
    rect(img, hx - 4, hy + 10, hx + 2, hy + 18, WOOD)
    # tip flares
    px(img, hx - 5, hy - 14, FRAME); px(img, hx - 6, hy - 12, FRAME)
    px(img, hx - 5, hy + 17, FRAME); px(img, hx - 6, hy + 15, FRAME)
    # string
    sx = hx + (5 if drawn else 4)
    for i in range(-12, 16, 1):
        px(img, sx, hy + i, MIST)
        if i % 3 == 0:
            px(img, sx + 1, hy + i, CREAM)
    if drawn:
        rect(img, hx + 4, hy + 1, hx + 22, hy + 4, FRAME)
        hline(img, hx + 4, hx + 22, hy + 1, CREAM)
        px(img, hx + 22, hy + 1, CREAM)
        px(img, hx + 23, hy + 2, CREAM)
        rect(img, hx + 2, hy + 0, hx + 5, hy + 5, WOOD)


def dart_fan(img, x, y):
    for i, (dx, dy) in enumerate([(0, 0), (4, -3), (6, 2), (8, -1)]):
        rect(img, x + dx, y + dy, x + dx + 6, y + dy + 2, MIST)
        px(img, x + dx + 6, y + dy, CREAM)


# ---------- charge ----------
def enemy_charge_draw(img, phase):
    robe = INK_SOFT
    if phase == 0:
        cx, cy = 20, 3
        en_head_bandit(img, cx, cy, CINN)
        ty = 24
        # bulky torso
        rect(img, cx - 12, ty, cx + 14, ty + 26, robe)
        robe_folds(img, cx - 12, cx + 14, ty + 2, ty + 26, NIGHT, WOOD)
        rect(img, cx - 14, ty, cx - 6, ty + 10, FRAME)  # shoulder pad
        rect(img, cx + 8, ty, cx + 16, ty + 10, FRAME)
        px(img, cx - 12, ty + 2, GOLD)
        belt(img, cx - 12, cx + 14, ty + 14, CINN, GOLD, hang=True)
        rect(img, cx - 16, ty + 6, cx - 8, ty + 18, robe)
        hand(img, cx - 16, ty + 16, SKIN_D, fist=True)
        rect(img, cx + 12, ty + 4, cx + 20, ty + 16, robe)
        hand(img, cx + 16, ty + 12, SKIN_D, fist=True)
        short_blade(img, cx + 18, ty + 2, "idle")
        rect(img, cx - 11, ty + 26, cx - 1, ty + 40, robe)
        rect(img, cx + 2, ty + 26, cx + 12, ty + 40, robe)
        hem_layers(img, cx - 13, cx + 15, ty + 28, robe, NIGHT, WOOD)
        feet_pair(img, cx - 12, cx + 2, ty + 40, wide=True)

    elif phase == 1:
        # ready — forward lean, blade back
        cx, cy = 16, 4
        en_head_bandit(img, cx, cy, CINN)
        ty = 26
        rect(img, cx - 12, ty, cx + 14, ty + 24, robe)
        robe_folds(img, cx - 12, cx + 14, ty + 2, ty + 24, NIGHT, WOOD)
        rect(img, cx - 14, ty, cx - 6, ty + 10, FRAME)
        rect(img, cx + 8, ty, cx + 16, ty + 10, FRAME)
        belt(img, cx - 12, cx + 14, ty + 12, CINN, GOLD, hang=True)
        rect(img, cx - 16, ty - 6, cx - 4, ty + 8, robe)
        hand(img, cx - 14, ty - 2, SKIN_D, fist=True)
        short_blade(img, cx - 12, ty - 4, "back")
        rect(img, cx + 10, ty + 6, cx + 18, ty + 18, robe)
        hand(img, cx + 14, ty + 14, SKIN_D, fist=True)
        # forward lean mass
        rect(img, cx + 8, ty + 16, cx + 18, ty + 30, robe)
        rect(img, cx - 12, ty + 24, cx - 0, ty + 38, robe)
        rect(img, cx + 2, ty + 18, cx + 12, ty + 36, robe)
        feet_pair(img, cx - 14, cx + 4, ty + 38, wide=True)

    elif phase == 2:
        # shoulder rush / thrust
        cx, cy = 10, 3
        en_head_bandit(img, cx, cy, CINN)
        ty = 24
        rect(img, cx - 10, ty, cx + 16, ty + 22, robe)
        robe_folds(img, cx - 10, cx + 16, ty + 2, ty + 22, NIGHT, WOOD)
        rect(img, cx + 8, ty - 2, cx + 18, ty + 10, FRAME)  # lead shoulder
        px(img, cx + 14, ty + 2, GOLD)
        belt(img, cx - 10, cx + 16, ty + 12, CINN, GOLD, hang=True)
        rect(img, cx - 16, ty + 10, cx - 6, ty + 20, robe)
        hand(img, cx - 16, ty + 18, SKIN_D)
        rect(img, cx + 10, ty + 2, cx + 28, ty + 12, robe)
        sleeve_folds(img, cx + 10, cx + 28, ty + 3, ty + 11, NIGHT, WOOD)
        hand(img, cx + 26, ty + 4, SKIN_D, fist=True)
        short_blade(img, cx + 28, ty + 2, "thrust")
        # motion ticks
        for i in range(0, 10, 2):
            px(img, cx - 4 - i, ty + 8 + i // 2, FRAME)
        rect(img, cx + 8, ty + 14, cx + 20, ty + 28, robe)
        rect(img, cx - 8, ty + 22, cx + 2, ty + 40, robe)
        rect(img, cx + 4, ty + 12, cx + 14, ty + 32, robe)
        feet_pair(img, cx - 10, cx + 6, ty + 40, wide=True)

    else:
        cx, cy = 10, 5
        en_head_bandit(img, cx, cy, CINN)
        ty = 26
        rect(img, cx - 12, ty, cx + 14, ty + 22, robe)
        robe_folds(img, cx - 12, cx + 14, ty + 2, ty + 22, NIGHT, WOOD)
        belt(img, cx - 12, cx + 14, ty + 12, CINN, GOLD, hang=True)
        rect(img, cx + 10, ty - 2, cx + 20, ty + 10, robe)
        hand(img, cx + 18, ty + 0, SKIN_D)
        rect(img, cx - 18, ty + 8, cx - 8, ty + 18, robe)
        hand(img, cx - 18, ty + 16, SKIN_D)
        short_blade(img, cx + 12, ty + 12, "idle")
        rect(img, cx - 10, ty + 22, cx + 0, ty + 38, robe)
        rect(img, cx + 2, ty + 24, cx + 12, ty + 38, robe)
        feet_pair(img, cx - 12, cx + 2, ty + 38)
        blood_spatters(img, cx + 2, ty + 6, 7)


# ---------- kite ----------
def enemy_kite_draw(img, phase):
    robe = FRAME  # leaner earth-tone, distinct from bosses
    if phase == 0:
        cx, cy = 22, 2
        en_head_archer(img, cx, cy)
        ty = 22
        # slim torso
        rect(img, cx - 8, ty, cx + 10, ty + 24, robe)
        robe_folds(img, cx - 8, cx + 10, ty + 2, ty + 24, NIGHT, WOOD_L)
        rect(img, cx - 3, ty, cx + 5, ty + 4, PAPER)
        belt(img, cx - 8, cx + 10, ty + 12, WOOD, GOLD, hang=False)
        rect(img, cx - 14, ty + 4, cx - 6, ty + 16, robe)
        hand(img, cx - 14, ty + 14, SKIN_D)
        bow_prop(img, cx - 12, ty + 6, drawn=False)
        rect(img, cx + 8, ty + 4, cx + 14, ty + 14, robe)
        hand(img, cx + 12, ty + 12, SKIN_D)
        # quiver
        rect(img, cx + 8, ty + 10, cx + 14, ty + 24, WOOD)
        outline_rect(img, cx + 8, ty + 10, cx + 14, ty + 24, INK)
        px(img, cx + 10, ty + 8, FRAME)
        px(img, cx + 12, ty + 6, CREAM)
        rect(img, cx - 7, ty + 24, cx + 0, ty + 42, robe)
        rect(img, cx + 2, ty + 24, cx + 9, ty + 42, robe)
        hem_layers(img, cx - 9, cx + 11, ty + 26, robe, NIGHT, WOOD_L)
        feet_pair(img, cx - 8, cx + 1, ty + 42)

    elif phase == 1:
        # ready / drawn bow — lean back
        cx, cy = 26, 2
        en_head_archer(img, cx, cy)
        ty = 22
        rect(img, cx - 8, ty, cx + 10, ty + 22, robe)
        robe_folds(img, cx - 8, cx + 10, ty + 2, ty + 22, NIGHT, WOOD_L)
        belt(img, cx - 8, cx + 10, ty + 12, WOOD, GOLD, hang=False)
        # draw arms
        rect(img, cx - 18, ty + 0, cx - 6, ty + 12, robe)
        hand(img, cx - 18, ty + 6, SKIN_D, fist=True)
        rect(img, cx + 6, ty + 2, cx + 14, ty + 12, robe)
        hand(img, cx + 10, ty + 4, SKIN_D, fist=True)
        bow_prop(img, cx - 10, ty + 4, drawn=True)
        # lean back cape-ish flap
        rect(img, cx + 8, ty + 14, cx + 16, ty + 30, robe)
        robe_folds(img, cx + 8, cx + 16, ty + 15, ty + 29, NIGHT, None)
        rect(img, cx - 6, ty + 22, cx + 2, ty + 40, robe)
        rect(img, cx + 2, ty + 24, cx + 10, ty + 42, robe)
        feet_pair(img, cx - 4, cx + 4, ty + 42)
        dart_fan(img, cx + 12, ty + 8)

    elif phase == 2:
        # release / step back strike silhouette
        cx, cy = 28, 2
        en_head_archer(img, cx, cy)
        ty = 22
        rect(img, cx - 8, ty, cx + 10, ty + 22, robe)
        robe_folds(img, cx - 8, cx + 10, ty + 2, ty + 22, NIGHT, WOOD_L)
        belt(img, cx - 8, cx + 10, ty + 12, WOOD, GOLD, hang=False)
        rect(img, cx - 16, ty + 2, cx - 6, ty + 14, robe)
        hand(img, cx - 16, ty + 10, SKIN_D)
        bow_prop(img, cx - 12, ty + 4, drawn=False)
        # flying dart/arrow forward
        rect(img, cx - 28, ty + 6, cx - 8, ty + 9, FRAME)
        px(img, cx - 28, ty + 6, CREAM)
        px(img, cx - 30, ty + 7, CREAM)
        px(img, cx - 10, ty + 5, WOOD)
        rect(img, cx + 8, ty + 4, cx + 16, ty + 14, robe)
        hand(img, cx + 12, ty + 8, SKIN_D)
        # retreat lean
        rect(img, cx + 8, ty + 14, cx + 18, ty + 32, robe)
        rect(img, cx - 4, ty + 22, cx + 4, ty + 40, robe)
        rect(img, cx + 4, ty + 24, cx + 12, ty + 42, robe)
        feet_pair(img, cx + 0, cx + 8, ty + 42)

    else:
        cx, cy = 18, 4
        en_head_archer(img, cx, cy)
        ty = 24
        rect(img, cx - 8, ty, cx + 10, ty + 22, robe)
        robe_folds(img, cx - 8, cx + 10, ty + 2, ty + 22, NIGHT, WOOD_L)
        belt(img, cx - 8, cx + 10, ty + 12, WOOD, GOLD, hang=False)
        rect(img, cx + 8, ty - 2, cx + 16, ty + 10, robe)
        hand(img, cx + 14, ty + 0, SKIN_D)
        rect(img, cx - 16, ty + 8, cx - 6, ty + 18, robe)
        hand(img, cx - 16, ty + 16, SKIN_D)
        bow_prop(img, cx + 6, ty + 12, drawn=False)
        rect(img, cx - 8, ty + 22, cx + 0, ty + 38, robe)
        rect(img, cx + 2, ty + 24, cx + 10, ty + 38, robe)
        feet_pair(img, cx - 10, cx + 2, ty + 38)
        blood_spatters(img, cx + 2, ty + 6, 6)


# ---------- melee ----------
def enemy_melee_draw(img, phase):
    robe = WOOD  # wood-brown tunic — distinct
    if phase == 0:
        cx, cy = 20, 3
        en_head_melee(img, cx, cy)
        ty = 24
        rect(img, cx - 10, ty, cx + 12, ty + 24, robe)
        robe_folds(img, cx - 10, cx + 12, ty + 2, ty + 24, NIGHT, WOOD_L)
        rect(img, cx - 4, ty, cx + 6, ty + 4, PAPER_L)
        belt(img, cx - 10, cx + 12, ty + 12, LOESS, GOLD, hang=True)
        rect(img, cx - 15, ty + 4, cx - 8, ty + 16, robe)
        hand(img, cx - 16, ty + 14, SKIN_D)
        rect(img, cx + 10, ty + 4, cx + 18, ty + 16, robe)
        hand(img, cx + 14, ty + 12, SKIN_D, fist=True)
        long_dao(img, cx + 16, ty - 4, "idle")
        rect(img, cx - 9, ty + 24, cx - 0, ty + 40, robe)
        rect(img, cx + 2, ty + 24, cx + 11, ty + 40, robe)
        hem_layers(img, cx - 11, cx + 13, ty + 26, robe, NIGHT, WOOD_L)
        feet_pair(img, cx - 10, cx + 2, ty + 40)

    elif phase == 1:
        cx, cy = 16, 3
        en_head_melee(img, cx, cy)
        ty = 26
        rect(img, cx - 10, ty, cx + 12, ty + 22, robe)
        robe_folds(img, cx - 10, cx + 12, ty + 2, ty + 22, NIGHT, WOOD_L)
        belt(img, cx - 10, cx + 12, ty + 12, LOESS, GOLD, hang=True)
        rect(img, cx - 16, ty - 8, cx - 4, ty + 6, robe)
        sleeve_folds(img, cx - 16, cx - 4, ty - 7, ty + 5, NIGHT, WOOD_L)
        hand(img, cx - 14, ty - 4, SKIN_D, fist=True)
        long_dao(img, cx - 10, ty - 6, "back")
        rect(img, cx + 8, ty + 6, cx + 16, ty + 16, robe)
        hand(img, cx + 12, ty + 14, SKIN_D)
        rect(img, cx + 8, ty + 16, cx + 16, ty + 30, robe)
        rect(img, cx - 12, ty + 22, cx - 2, ty + 38, robe)
        rect(img, cx + 0, ty + 18, cx + 10, ty + 36, robe)
        feet_pair(img, cx - 14, cx + 2, ty + 38)

    elif phase == 2:
        cx, cy = 12, 2
        en_head_melee(img, cx, cy)
        ty = 24
        rect(img, cx - 10, ty, cx + 14, ty + 22, robe)
        robe_folds(img, cx - 10, cx + 14, ty + 2, ty + 22, NIGHT, WOOD_L)
        belt(img, cx - 10, cx + 14, ty + 12, LOESS, GOLD, hang=True)
        rect(img, cx - 16, ty + 8, cx - 6, ty + 18, robe)
        hand(img, cx - 16, ty + 16, SKIN_D)
        rect(img, cx + 8, ty + 0, cx + 24, ty + 12, robe)
        sleeve_folds(img, cx + 8, cx + 24, ty + 1, ty + 11, NIGHT, WOOD_L)
        hand(img, cx + 22, ty + 4, SKIN_D, fist=True)
        long_dao(img, cx + 24, ty + 2, "slash")
        rect(img, cx + 10, ty + 14, cx + 18, ty + 26, robe)
        rect(img, cx - 10, ty + 22, cx + 0, ty + 40, robe)
        rect(img, cx + 2, ty + 14, cx + 12, ty + 32, robe)
        feet_pair(img, cx - 11, cx + 4, ty + 40)

    else:
        cx, cy = 10, 4
        en_head_melee(img, cx, cy)
        ty = 26
        rect(img, cx - 10, ty, cx + 12, ty + 22, robe)
        robe_folds(img, cx - 10, cx + 12, ty + 2, ty + 22, NIGHT, WOOD_L)
        belt(img, cx - 10, cx + 12, ty + 12, LOESS, GOLD, hang=True)
        rect(img, cx + 10, ty - 2, cx + 18, ty + 10, robe)
        hand(img, cx + 16, ty + 0, SKIN_D)
        rect(img, cx - 16, ty + 8, cx - 6, ty + 18, robe)
        hand(img, cx - 16, ty + 16, SKIN_D)
        long_dao(img, cx + 12, ty + 10, "idle")
        rect(img, cx - 9, ty + 22, cx + 0, ty + 38, robe)
        rect(img, cx + 2, ty + 24, cx + 11, ty + 38, robe)
        feet_pair(img, cx - 11, cx + 2, ty + 38)
        blood_spatters(img, cx + 2, ty + 6, 7)


# ============================================================
# assembly
# ============================================================
BOSS_DRAW = {
    "heifeng": heifeng_draw,
    "xieyi": xieyi_draw,
    "xueying": xueying_draw,
}
ENEMY_DRAW = {
    "charge": enemy_charge_draw,
    "kite": enemy_kite_draw,
    "melee": enemy_melee_draw,
}


def make_short_sheet(drawer) -> Image.Image:
    sheet = sheet4()
    for i in range(NF):
        fr = new_frame()
        drawer(fr, i)
        paste_frame(sheet, i, fr)
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


def crop_frame(sheet, i):
    return sheet.crop((i * FS, 0, (i + 1) * FS, FS))


def make_compare_strip(sheets_named, path):
    """One frame0 from each sheet side by side at x3."""
    n = len(sheets_named)
    cell = 192
    strip = Image.new("RGBA", (cell * n + 4 * (n - 1), cell), PAPER_D)
    for i, (name, sheet) in enumerate(sheets_named):
        fr = crop_frame(sheet, 0).resize((cell, cell), Image.Resampling.NEAREST)
        bg = Image.new("RGBA", (cell, cell), PAPER)
        bg.paste(fr, (0, 0), fr)
        strip.paste(bg, (i * (cell + 4), 0))
    strip.save(path)


def write_readme():
    import re
    readme = OUT / "README.md"
    text = readme.read_text(encoding="utf-8") if readme.exists() else ""
    # update boss row
    text = re.sub(
        r"\| `boss_\*_combat\.png` \|[^\n]+\n",
        "| `boss_*_combat.png` | **256×64** | **v1.4 精修（4 幀 idle／windup／strike／hurt）** | `tools/gen_sprites_64_v14.py` |\n",
        text,
    )
    if "| `enemy_charge.png`" not in text:
        text = text.replace(
            "| `boss_*_combat.png` | **256×64** | **v1.4 精修（4 幀 idle／windup／strike／hurt）** | `tools/gen_sprites_64_v14.py` |\n",
            "| `boss_*_combat.png` | **256×64** | **v1.4 精修（4 幀 idle／windup／strike／hurt）** | `tools/gen_sprites_64_v14.py` |\n"
            "| `enemy_charge.png` | **256×64** | **v1.4 新增（衝鋒 4 幀）** | `tools/gen_sprites_64_v14.py` |\n"
            "| `enemy_kite.png` | **256×64** | **v1.4 新增（拉距 4 幀）** | `tools/gen_sprites_64_v14.py` |\n"
            "| `enemy_melee.png` | **256×64** | **v1.4 新增（近戰 4 幀）** | `tools/gen_sprites_64_v14.py` |\n",
        )
    if "## v1.4" not in text:
        note = """
## v1.4 Boss／敵戰鬥剪影

### 對幀（Boss 與通用敵相同）

| 幀 | Boss | 通用敵 |
|----|------|--------|
| 0 | idle | idle |
| 1 | windup／威嚇 | approach／ready |
| 2 | strike | strike |
| 3 | hurt | hurt |

- 尺寸：**256×64**（4×64）；面向右；硬邊；oob=0
- 遊戲現況：`drawImage(img, 0, 0, h, h, …)` → **先用幀 0**；短表預留動畫
- **heifeng**：墨褐＋血；披髮額帶＋寬肩甲＋巨刀
- **xieyi**：梵紫＋藥綠；雙髻＋毒瓶＋爪
- **xueying**：血／墨黑；雙刃＋影披風
- **charge**：厚重前衝／短刀；**kite**：斗笠弓矢／後撤；**melee**：木褐單刀砍弧

```js
const FRAME = 64;
const sx = frameIndex * FRAME; // 0..3
ctx.drawImage(sheet, sx, 0, FRAME, FRAME, dx, dy, FRAME, FRAME);
```

生成：`tools/gen_sprites_64_v14.py` · 報告：`_gen_report_v14.txt`

"""
        text = text.rstrip() + "\n" + note
    readme.write_text(text, encoding="utf-8")


def main():
    import hashlib
    OUT.mkdir(parents=True, exist_ok=True)
    PREV.mkdir(parents=True, exist_ok=True)
    report = ["# v1.4 sprite gen report (boss + enemy)", ""]
    total_oob = 0

    untouched = {}
    for name in ("qingyi", "langren", "tiezhang", "qinshi", "xiaoer", "guest_sit", "guest_walk"):
        fp = OUT / f"{name}.png"
        if fp.exists():
            untouched[name] = hashlib.md5(fp.read_bytes()).hexdigest()

    labels = ["idle", "windup", "strike", "hurt"]
    boss_sheets = []
    for bid, drawer in BOSS_DRAW.items():
        sheet = make_short_sheet(drawer)
        assert sheet.size == (256, 64), sheet.size
        oob, samples = count_oob(sheet)
        total_oob += oob
        path = OUT / f"boss_{bid}_combat.png"
        sheet.save(path)
        preview_scale(sheet, PREV / f"64_boss_{bid}_x2.png", 2)
        preview_scale(crop_frame(sheet, 0), PREV / f"64_boss_{bid}_idle_x3.png", 3)
        preview_scale(crop_frame(sheet, 2), PREV / f"64_boss_{bid}_strike_x3.png", 3)
        boss_sheets.append((bid, sheet))
        report.append(f"## boss_{bid}")
        report.append(f"path: {path}")
        report.append(f"size: {sheet.size}")
        report.append(f"oob: {oob}")
        if samples:
            report.append(f"oob_samples: {samples}")
        report.append(f"palette_used ({len(colors_used(sheet))}): {', '.join(colors_used(sheet))}")
        for i, lab in enumerate(labels):
            report.append(f"  {i} {lab}: visible={visible_pixels(sheet, i)}")
        report.append("")
        print(f"boss_{bid}: {sheet.size} oob={oob}")

    make_compare_strip(boss_sheets, PREV / "64_boss_compare_v14.png")

    enemy_sheets = []
    elabels = ["idle", "ready", "strike", "hurt"]
    for eid, drawer in ENEMY_DRAW.items():
        sheet = make_short_sheet(drawer)
        assert sheet.size == (256, 64), sheet.size
        oob, samples = count_oob(sheet)
        total_oob += oob
        path = OUT / f"enemy_{eid}.png"
        sheet.save(path)
        preview_scale(sheet, PREV / f"64_enemy_{eid}_x2.png", 2)
        preview_scale(crop_frame(sheet, 0), PREV / f"64_enemy_{eid}_idle_x3.png", 3)
        preview_scale(crop_frame(sheet, 2), PREV / f"64_enemy_{eid}_strike_x3.png", 3)
        enemy_sheets.append((eid, sheet))
        report.append(f"## enemy_{eid}")
        report.append(f"path: {path}")
        report.append(f"size: {sheet.size}")
        report.append(f"oob: {oob}")
        if samples:
            report.append(f"oob_samples: {samples}")
        for i, lab in enumerate(elabels):
            report.append(f"  {i} {lab}: visible={visible_pixels(sheet, i)}")
        report.append("")
        print(f"enemy_{eid}: {sheet.size} oob={oob}")

    make_compare_strip(enemy_sheets, PREV / "64_enemy_compare_v14.png")
    # mixed compare: 3 boss idle + 3 enemy idle
    make_compare_strip(boss_sheets + enemy_sheets, PREV / "64_boss_enemy_compare_v14.png")

    for name, h in untouched.items():
        now = hashlib.md5((OUT / f"{name}.png").read_bytes()).hexdigest()
        assert now == h, f"FORBIDDEN overwrite of {name}"
        report.append(f"untouched_ok: {name}")

    report.append(f"TOTAL_OOB={total_oob}")
    report.append("""
## design
- heifeng: wild hair + cinnabar band + shoulder armor + giant dao
- xieyi: violet double-bun + jade vial + claws
- xueying: blood band + night cape + twin daggers
- charge: bulky + cinnabar scarf + short blade rush
- kite: bamboo hat + bow/darts + lean-back
- melee: wood tunic + long dao slash

## weaknesses
- 4-frame only — no walk cycle for bosses/enemies
- kite arrow flies leftward visually on strike (retreat-facing right body)
- heifeng giant blade can crowd frame edge on slash
- enemy_melee / charge both use bandit head — differ by scarf color + weapon + bulk
""")
    (OUT / "_gen_report_v14.txt").write_text("\n".join(report) + "\n", encoding="utf-8")
    write_readme()
    print(f"TOTAL_OOB={total_oob}")
    if total_oob != 0:
        raise SystemExit(f"palette oob={total_oob}")
    print("OK")


if __name__ == "__main__":
    main()
