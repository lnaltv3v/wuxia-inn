#!/usr/bin/env python3
"""v0.9 Ink-Pixel Inn — high-density native 64×64 spritesheets (qingyi + langren).

v0.9 r2 — bigger windup/parry vs idle; denser folds/arcs; clear hit-frame silhouette.
Layout: body biased LEFT so weapon silhouette reads clearly on the RIGHT.

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


# ============================================================
# QINGYI
# ============================================================
def qy_head(img, cx, cy):
    """¾ view facing right — topknot, fringe, ink eyes."""
    # hair dome
    rect(img, cx - 8, cy + 2, cx + 9, cy + 9, INK)
    rect(img, cx - 10, cy + 4, cx + 10, cy + 9, INK)
    # tall topknot
    rect(img, cx - 2, cy - 7, cx + 5, cy + 2, INK)
    rect(img, cx - 4, cy - 3, cx + 6, cy + 2, INK)
    px(img, cx + 1, cy - 9, GOLD)
    px(img, cx + 2, cy - 8, GOLD)
    px(img, cx, cy - 6, LOESS)
    px(img, cx + 3, cy - 5, LOESS)
    px(img, cx + 1, cy - 5, CREAM)
    # cloth wrap under knot
    rect(img, cx - 3, cy, cx + 5, cy + 3, TEAL)
    hline(img, cx - 3, cx + 5, cy + 1, TEAL_B)
    # face (biased right for 3/4)
    rect(img, cx - 7, cy + 9, cx + 9, cy + 19, SKIN)
    # fringe
    for fx, fy in [(-6, 9), (-3, 9), (0, 9), (3, 9), (6, 9), (-5, 10), (1, 10), (5, 10)]:
        px(img, cx + fx, cy + fy, INK)
    # sideburns / rear hair
    rect(img, cx - 10, cy + 9, cx - 7, cy + 17, INK)
    rect(img, cx + 8, cy + 9, cx + 11, cy + 15, INK)
    # ear hint (right side of face in 3/4)
    px(img, cx + 9, cy + 13, SKIN_D)
    px(img, cx + 10, cy + 14, SKIN)
    # eyes — 2px ink, right eye larger feel
    px(img, cx - 2, cy + 13, INK)
    px(img, cx - 1, cy + 13, INK)
    px(img, cx + 3, cy + 13, INK)
    px(img, cx + 4, cy + 13, INK)
    px(img, cx + 5, cy + 13, INK)  # front eye wider
    # brows
    px(img, cx - 2, cy + 11, INK_SOFT)
    px(img, cx + 3, cy + 11, INK_SOFT)
    px(img, cx + 4, cy + 11, INK)
    # cheek + jaw
    px(img, cx + 7, cy + 15, SKIN_D)
    px(img, cx + 6, cy + 16, SKIN_D)
    hline(img, cx - 5, cx + 7, cy + 18, SKIN_D)
    # neck
    rect(img, cx - 3, cy + 19, cx + 5, cy + 23, SKIN)
    # ink edge
    hline(img, cx - 8, cx + 9, cy + 2, INK)
    vline(img, cx - 10, cy + 4, cy + 17, INK)
    vline(img, cx + 10, cy + 4, cy + 15, INK)


def qy_sword_vert(img, hx, hy, tip_down=True):
    """Vertical sheathed/held sword — 4px thick blade readable at ×2."""
    # grip above guard
    rect(img, hx, hy - 11, hx + 4, hy - 2, WOOD)
    vline(img, hx + 1, hy - 10, hy - 2, WOOD_L)
    vline(img, hx + 2, hy - 10, hy - 2, WOOD)
    # wrap rings
    hline(img, hx, hx + 4, hy - 8, FRAME)
    hline(img, hx, hx + 4, hy - 5, FRAME)
    # pommel
    rect(img, hx - 1, hy - 13, hx + 5, hy - 10, GOLD)
    px(img, hx + 1, hy - 12, CREAM)
    px(img, hx + 2, hy - 11, LOESS)
    # guard
    rect(img, hx - 3, hy - 3, hx + 7, hy + 1, GOLD)
    outline_rect(img, hx - 3, hy - 3, hx + 7, hy + 1, INK)
    px(img, hx + 1, hy - 2, CREAM)
    px(img, hx + 3, hy - 1, LOESS)
    # blade body
    if tip_down:
        rect(img, hx, hy, hx + 4, hy + 26, TEAL_B)
        vline(img, hx, hy, hy + 26, INK)
        vline(img, hx + 3, hy, hy + 26, TEAL)
        vline(img, hx + 1, hy + 2, hy + 22, CREAM)  # fuller highlight
        # tip
        px(img, hx + 1, hy + 26, TEAL_B)
        px(img, hx + 2, hy + 26, TEAL_B)
        px(img, hx + 1, hy + 27, CREAM)
        px(img, hx + 2, hy + 27, TEAL_B)
        px(img, hx + 1, hy + 28, TEAL)
    else:
        rect(img, hx, hy - 26, hx + 4, hy, TEAL_B)
        vline(img, hx, hy - 26, hy, INK)
        vline(img, hx + 3, hy - 26, hy, TEAL)
        vline(img, hx + 1, hy - 22, hy - 2, CREAM)
        px(img, hx + 1, hy - 27, CREAM)
        px(img, hx + 2, hy - 26, TEAL_B)


def qy_sword_back(img, hx, hy, lean=0):
    """Windup r2: blade HIGH and BACK — near-vertical behind head, tip up-left."""
    # two-hand grip cluster
    rect(img, hx - 1, hy, hx + 6, hy + 6, WOOD)
    vline(img, hx + 1, hy + 1, hy + 5, WOOD_L)
    hline(img, hx, hx + 5, hy + 2, FRAME)
    rect(img, hx - 4, hy - 3, hx + 9, hy + 2, GOLD)
    outline_rect(img, hx - 4, hy - 3, hx + 9, hy + 2, INK)
    px(img, hx + 2, hy - 1, CREAM)
    px(img, hx + 5, hy, LOESS)
    # steep up-back blade (more vertical than diagonal)
    for i in range(26):
        x = hx - (i // 2) - lean * 2
        y = hy - 4 - i
        rect(img, x, y, x + 4, y + 2, TEAL_B)
        px(img, x, y, INK)
        px(img, x + 3, y, TEAL)
        if i % 2 == 0:
            px(img, x + 1, y, CREAM)
        if i % 4 == 0:
            px(img, x - 1, y + 1, TEAL)  # motion ghost
    tx = hx - (25 // 2) - lean * 2
    ty = hy - 4 - 25
    px(img, tx + 1, ty - 1, CREAM)
    px(img, tx, ty, TEAL_B)
    px(img, tx + 2, ty, TEAL_B)
    px(img, tx + 1, ty - 2, CREAM)


def qy_sword_slash(img, hx, hy, length=22, dy=0, flash=False):
    """Horizontal strike + arc trail (r2 denser)."""
    rect(img, hx - 4, hy - 1, hx + 1, hy + 4, WOOD)
    vline(img, hx - 3, hy, hy + 3, WOOD_L)
    rect(img, hx, hy - 3, hx + 4, hy + 6, GOLD)
    outline_rect(img, hx, hy - 3, hx + 4, hy + 6, INK)
    px(img, hx + 1, hy, CREAM)
    # main blade
    rect(img, hx + 4, hy + dy, hx + 4 + length, hy + 4 + dy, TEAL_B)
    hline(img, hx + 4, hx + 4 + length, hy + dy, INK)
    hline(img, hx + 4, hx + 4 + length, hy + 3 + dy, TEAL)
    hline(img, hx + 5, hx + 3 + length, hy + 1 + dy, CREAM)
    # curved arc ghosts above/below for slash readability
    for i in range(0, length - 2, 3):
        px(img, hx + 6 + i, hy - 2 + dy - (i // 8), TEAL)
        px(img, hx + 7 + i, hy - 3 + dy - (i // 8), TEAL_B)
        px(img, hx + 6 + i, hy + 5 + dy + (i // 10), TEAL)
    tip = hx + 3 + length
    px(img, tip, hy + 1 + dy, CREAM)
    px(img, tip, hy + 2 + dy, TEAL_B)
    px(img, tip - 1, hy - 1 + dy, TEAL_B)
    px(img, tip - 1, hy + 4 + dy, TEAL)
    px(img, tip + 1, hy + 1 + dy, CREAM)
    if flash:
        for dx, dy2, c in [(-2, -3, GOLD), (0, -2, CREAM), (1, 1, CREAM),
                           (-1, 5, GOLD), (-3, -4, TEAL_B), (2, 0, CREAM),
                           (-4, -5, GOLD), (1, 3, TEAL_B), (-2, 6, CREAM)]:
            px(img, tip + dx, hy + dy + dy2, c)


def qy_sword_diag(img, hx, hy):
    """Start of cut — diagonal down-right."""
    rect(img, hx, hy, hx + 4, hy + 5, WOOD)
    rect(img, hx + 3, hy - 2, hx + 8, hy + 4, GOLD)
    outline_rect(img, hx + 3, hy - 2, hx + 8, hy + 4, INK)
    for i in range(18):
        x = hx + 7 + i
        y = hy - 1 + (i // 2)
        rect(img, x, y, x + 3, y + 3, TEAL_B)
        px(img, x, y, INK)
        px(img, x + 2, y + 2, TEAL)
        if i % 2 == 0:
            px(img, x + 1, y + 1, CREAM)
    px(img, hx + 24, hy + 8, CREAM)
    px(img, hx + 25, hy + 9, TEAL_B)


def qingyi_draw(img, pose):
    breath = pose.get("breath", 0)
    bx = pose.get("bx", 0)
    by = pose.get("by", 0)
    # body LEFT-biased so weapon reads on right
    cx = 22 + bx
    cy = 3 + by + breath

    qy_head(img, cx, cy)

    ty = 24 + by + breath  # torso top
    # shoulders — right (front) slightly wider
    rect(img, cx - 11, ty, cx + 12, ty + 4, TEAL)
    hline(img, cx - 10, cx + 11, ty, TEAL_B)
    px(img, cx - 11, ty, PAPER_L)
    px(img, cx + 11, ty + 1, TEAL_B)
    # collar layers
    rect(img, cx - 4, ty, cx + 6, ty + 5, PAPER_L)
    rect(img, cx - 3, ty + 1, cx + 5, ty + 4, PAPER)
    rect(img, cx - 9, ty + 2, cx - 4, ty + 7, TEAL_B)
    rect(img, cx + 6, ty + 2, cx + 11, ty + 7, TEAL_B)
    vline(img, cx - 4, ty + 2, ty + 7, PAPER_D)
    vline(img, cx + 5, ty + 2, ty + 7, NIGHT)
    # torso
    rect(img, cx - 10, ty + 4, cx + 12, ty + 24, TEAL)
    robe_folds(img, cx - 10, cx + 12, ty + 6, ty + 24, NIGHT, TEAL_B)
    # inner lapel shade
    rect(img, cx - 2, ty + 5, cx + 1, ty + 16, NIGHT)
    # belt
    belt(img, cx - 10, cx + 12, ty + 15, WOOD_L, GOLD, hang=True)
    # sash under
    rect(img, cx - 10, ty + 13, cx + 12, ty + 15, NIGHT)

    lift_l = pose.get("lift_l", 0)
    lift_r = pose.get("lift_r", 0)
    ly = ty + 24
    # left leg (rear)
    lx0 = cx - 9 - (4 if lift_l else 0) - (2 if pose.get("stride_l") else 0)
    rect(img, lx0, ly - lift_l, lx0 + 8, ly + 14 - lift_l, TEAL)
    hline(img, lx0 + 1, lx0 + 7, ly - lift_l + 5, NIGHT)
    hline(img, lx0 + 1, lx0 + 7, ly - lift_l + 9, TEAL_B)
    # right leg
    rx0 = cx + 1 + (4 if lift_r else 0) + (2 if pose.get("stride_r") else 0)
    rect(img, rx0, ly - lift_r, rx0 + 8, ly + 14 - lift_r, TEAL)
    hline(img, rx0 + 1, rx0 + 7, ly - lift_r + 5, NIGHT)
    hline(img, rx0 + 1, rx0 + 7, ly - lift_r + 9, TEAL_B)
    # layered hem r2
    hem_layers(img, cx - 11, cx + 13, ly + 1, TEAL, NIGHT, TEAL_B)
    # hem sway
    if lift_l:
        px(img, lx0 - 2, ly - lift_l + 1, TEAL)
        px(img, lx0 - 1, ly - lift_l, NIGHT)
        px(img, lx0 - 2, ly - lift_l + 3, TEAL_B)
    if lift_r:
        px(img, rx0 + 8, ly - lift_r + 1, TEAL)
        px(img, rx0 + 9, ly - lift_r, NIGHT)
        px(img, rx0 + 8, ly - lift_r + 3, TEAL_B)
    shoe(img, lx0 - 1, ly + 14 - lift_l)
    shoe(img, rx0, ly + 14 - lift_r)

    kind = pose.get("kind", "idle")

    if kind == "idle":
        # rear arm
        rect(img, cx - 15, ty + 3, cx - 9, ty + 15, TEAL)
        rect(img, cx - 16, ty + 13, cx - 10, ty + 19, TEAL)
        sleeve_cuff(img, cx - 16, cx - 10, ty + 15, TEAL)
        hand(img, cx - 16, ty + 17, SKIN)
        # front arm near hip
        rect(img, cx + 10, ty + 5, cx + 16, ty + 15, TEAL)
        sleeve_cuff(img, cx + 10, cx + 16, ty + 13, TEAL)
        hand(img, cx + 12, ty + 13, SKIN, fist=True)
        # sword CLEARLY to the right of body
        qy_sword_vert(img, cx + 16, ty + 10, tip_down=True)

    elif kind == "walk":
        if lift_l:
            rect(img, cx + 10, ty + 1, cx + 17, ty + 12, TEAL)
            sleeve_cuff(img, cx + 10, cx + 17, ty + 10, TEAL)
            hand(img, cx + 15, ty + 10, SKIN)
            rect(img, cx - 15, ty + 7, cx - 9, ty + 17, TEAL)
            hand(img, cx - 16, ty + 15, SKIN)
        else:
            rect(img, cx - 17, ty + 1, cx - 9, ty + 12, TEAL)
            sleeve_cuff(img, cx - 17, cx - 9, ty + 10, TEAL)
            hand(img, cx - 17, ty + 10, SKIN)
            rect(img, cx + 10, ty + 7, cx + 16, ty + 17, TEAL)
            hand(img, cx + 12, ty + 15, SKIN, fist=True)
        qy_sword_vert(img, cx + 16, ty + 12, tip_down=True)

    elif kind == "windup":
        phase = pose.get("phase", 0)
        # r2: BOTH arms HIGH-BACK, torso leans rear, coat flares hard
        # rear arm cocked high
        rect(img, cx - 18, ty - 6, cx - 8, ty + 6, TEAL)
        sleeve_folds(img, cx - 18, cx - 8, ty - 5, ty + 5, NIGHT, TEAL_B)
        rect(img, cx - 20, ty - 2, cx - 12, ty + 6, TEAL)
        sleeve_cuff(img, cx - 20, cx - 12, ty + 4, TEAL)
        hand(img, cx - 20, ty + 2, SKIN, fist=True)
        # front arm also back/up on grip
        rect(img, cx - 8, ty - 8, cx + 4, ty + 2, TEAL)
        sleeve_folds(img, cx - 8, cx + 4, ty - 7, ty + 1, NIGHT, TEAL_B)
        hand(img, cx - 10, ty - 6, SKIN, fist=True)
        # dramatic coat flare (back-weighted silhouette)
        rect(img, cx + 12, ty + 14, cx + 18, ty + 26, TEAL)
        robe_folds(img, cx + 12, cx + 18, ty + 15, ty + 25, NIGHT, TEAL_B)
        rect(img, cx - 16, ty + 16, cx - 10, ty + 28, TEAL)
        for dx, dy in [(14, 18), (16, 20), (17, 22), (15, 24), (-13, 20), (-15, 23), (-14, 26)]:
            px(img, cx + dx, ty + dy, TEAL_B if dx > 0 else NIGHT)
        lean = phase + 1
        # sword HIGH behind head — grip near ear height
        qy_sword_back(img, cx - 14, ty - 2, lean=lean)
        # planted rear mass + front toe light (weight back)
        rect(img, cx - 16, ly + 4, cx - 4, ly + 14, TEAL)
        hline(img, cx - 15, cx - 5, ly + 8, NIGHT)
        hline(img, cx - 14, cx - 6, ly + 11, TEAL_B)
        if phase >= 1:
            # front knee bent up — coiled
            rect(img, cx + 2, ly - 8, cx + 10, ly + 6, TEAL)
            hline(img, cx + 3, cx + 9, ly - 4, NIGHT)

    elif kind == "strike":
        phase = pose.get("phase", 0)
        if phase == 0:
            # start cut — blade coming over from back
            rect(img, cx - 14, ty - 4, cx - 4, ty + 8, TEAL)
            sleeve_folds(img, cx - 14, cx - 4, ty - 3, ty + 7, NIGHT, TEAL_B)
            hand(img, cx - 14, ty + 4, SKIN, fist=True)
            rect(img, cx + 6, ty - 6, cx + 16, ty + 6, TEAL)
            sleeve_cuff(img, cx + 6, cx + 16, ty + 4, TEAL)
            hand(img, cx + 13, ty - 2, SKIN, fist=True)
            qy_sword_diag(img, cx + 14, ty - 2)
            # coat still trailing back
            rect(img, cx - 14, ty + 16, cx - 8, ty + 26, TEAL)
        elif phase == 1:
            # === HIT FRAME (frame 10) — unmistakable lunge ===
            # rear arm trailing
            rect(img, cx - 14, ty + 8, cx - 4, ty + 18, TEAL)
            sleeve_folds(img, cx - 14, cx - 4, ty + 9, ty + 17, NIGHT, TEAL_B)
            hand(img, cx - 14, ty + 16, SKIN)
            # front arm FULLY extended right
            rect(img, cx + 6, ty + 0, cx + 22, ty + 10, TEAL)
            sleeve_folds(img, cx + 6, cx + 22, ty + 1, ty + 9, NIGHT, TEAL_B)
            sleeve_cuff(img, cx + 16, cx + 22, ty + 8, TEAL)
            hand(img, cx + 20, ty + 2, SKIN, fist=True)
            # long blade + flash
            qy_sword_slash(img, cx + 22, ty + 3, length=28, dy=-2, flash=True)
            # forward coat stretch
            rect(img, cx + 12, ty + 14, cx + 20, ty + 24, TEAL)
            robe_folds(img, cx + 12, cx + 20, ty + 15, ty + 23, NIGHT, TEAL_B)
            # motion ticks behind
            for i, (dx, dy) in enumerate([(-2, 2), (-4, 0), (-6, 3), (-3, -2)]):
                px(img, cx + 4 + dx, ty + 4 + dy, TEAL_B if i % 2 == 0 else CREAM)
        elif phase == 2:
            # pierce / follow-through — even more forward
            rect(img, cx - 10, ty + 10, cx - 2, ty + 20, TEAL)
            hand(img, cx - 10, ty + 18, SKIN)
            rect(img, cx + 8, ty + 2, cx + 24, ty + 12, TEAL)
            sleeve_folds(img, cx + 8, cx + 24, ty + 3, ty + 11, NIGHT, TEAL_B)
            sleeve_cuff(img, cx + 18, cx + 24, ty + 10, TEAL)
            hand(img, cx + 22, ty + 4, SKIN, fist=True)
            qy_sword_slash(img, cx + 24, ty + 5, length=26, dy=1, flash=True)
            rect(img, cx + 10, ty + 14, cx + 18, ty + 24, TEAL)
        else:
            # recover
            rect(img, cx - 13, ty + 5, cx - 5, ty + 15, TEAL)
            hand(img, cx - 13, ty + 13, SKIN)
            rect(img, cx + 8, ty + 5, cx + 15, ty + 15, TEAL)
            hand(img, cx + 11, ty + 13, SKIN, fist=True)
            qy_sword_vert(img, cx + 15, ty + 10, tip_down=True)

    elif kind == "hurt":
        phase = pose.get("phase", 0)
        if phase == 0:
            rect(img, cx + 10, ty - 5, cx + 18, ty + 7, TEAL)
            hand(img, cx + 16, ty - 6, SKIN)
            rect(img, cx - 15, ty + 9, cx - 7, ty + 19, TEAL)
            hand(img, cx - 16, ty + 17, SKIN)
            qy_sword_vert(img, cx + 8, ty + 14, tip_down=True)
        else:
            rect(img, cx + 11, ty + 5, cx + 20, ty + 15, TEAL)
            hand(img, cx + 18, ty + 13, SKIN)
            rect(img, cx - 14, ty + 3, cx - 6, ty + 13, TEAL)
            hand(img, cx - 15, ty + 11, SKIN)
            qy_sword_vert(img, cx - 2, ty + 16, tip_down=True)
        for dx, dy, c in [
            (6, 6, CINN_B), (10, 10, BLOOD), (2, 14, CINN_B),
            (14, 8, BLOOD), (8, 16, BLOOD), (12, 4, CINN_B),
            (-2, 12, BLOOD), (16, 12, CINN), (4, 18, BLOOD),
        ]:
            px(img, cx + dx, ty + dy, c)

    elif kind == "parry":
        phase = pose.get("phase", 0)
        shake = pose.get("shake", 0)
        # r2: BOTH arms UP — sword high overhead guard (not idle-adjacent)
        if phase < 2:
            # crouched guard — knees bent (lift both via pose), arms overhead
            rect(img, cx - 16, ty - 10, cx - 6, ty + 2, TEAL)
            sleeve_folds(img, cx - 16, cx - 6, ty - 9, ty + 1, NIGHT, TEAL_B)
            hand(img, cx - 10, ty - 12, SKIN, fist=True)
            rect(img, cx + 2, ty - 12, cx + 14, ty + 0, TEAL)
            sleeve_folds(img, cx + 2, cx + 14, ty - 11, ty - 1, NIGHT, TEAL_B)
            sleeve_cuff(img, cx + 2, cx + 14, ty - 2, TEAL)
            hand(img, cx + 8 + shake, ty - 14, SKIN, fist=True)
            # sword HIGH above head, tip up
            qy_sword_vert(img, cx + 6 + shake, ty - 8, tip_down=False)
            # wide guard stance flare
            rect(img, cx - 14, ty + 18, cx - 6, ty + 26, TEAL)
            rect(img, cx + 8, ty + 18, cx + 16, ty + 26, TEAL)
            if phase == 1:
                for dx, dy, c in [(0, -28, CREAM), (4, -26, GOLD), (2, -24, CREAM),
                                  (6, -30, TEAL_B), (-2, -26, GOLD), (8, -22, CREAM),
                                  (3, -32, GOLD)]:
                    px(img, cx + 6 + shake + dx, ty + dy, c)
        else:
            # phase 2 = dodge side-step — body deep left, sword across
            rect(img, cx - 18, ty + 2, cx - 8, ty + 14, TEAL)
            sleeve_folds(img, cx - 18, cx - 8, ty + 3, ty + 13, NIGHT, TEAL_B)
            hand(img, cx - 18, ty + 12, SKIN)
            rect(img, cx - 4, ty - 4, cx + 8, ty + 8, TEAL)
            hand(img, cx + 4, ty - 2, SKIN, fist=True)
            # blade angled across body as dodge guard
            qy_sword_slash(img, cx + 6, ty + 0, length=18, dy=2, flash=False)
            # deep side lean mass
            rect(img, cx - 18, ty + 16, cx - 8, ty + 28, TEAL)
            robe_folds(img, cx - 18, cx - 8, ty + 17, ty + 27, NIGHT, TEAL_B)

    # silhouette ink edges
    vline(img, cx - 11, ty, ty + 22, INK)
    vline(img, cx + 11, ty, ty + 18, INK)


# ============================================================
# LANGREN
# ============================================================
def lr_head(img, cx, cy):
    # wild hair
    rect(img, cx - 9, cy + 3, cx + 10, cy + 10, INK)
    rect(img, cx - 11, cy + 5, cx + 11, cy + 10, INK)
    for fx, fy in [(-7, 0), (-5, -2), (-2, -1), (2, -3), (5, -1), (8, 0),
                   (10, 2), (-9, 1), (0, -2), (6, 1), (-4, 1)]:
        px(img, cx + fx, cy + fy, INK)
    # fringe
    for fx in (-7, -4, -1, 2, 5, 8):
        px(img, cx + fx, cy + 10, INK)
        px(img, cx + fx + 1, cy + 11, INK)
    # red headband
    rect(img, cx - 11, cy + 7, cx + 12, cy + 11, CINN_B)
    hline(img, cx - 11, cx + 12, cy + 7, CINN)
    hline(img, cx - 11, cx + 12, cy + 10, BLOOD)
    # trailing cloth RIGHT — clear silhouette cue
    rect(img, cx + 11, cy + 9, cx + 20, cy + 13, CINN_B)
    rect(img, cx + 17, cy + 11, cx + 22, cy + 16, CINN)
    px(img, cx + 21, cy + 15, BLOOD)
    px(img, cx + 19, cy + 12, CREAM)
    px(img, cx + 20, cy + 14, CINN_B)
    # face darker
    rect(img, cx - 8, cy + 11, cx + 10, cy + 21, SKIN_D)
    # eyes
    px(img, cx - 2, cy + 15, INK)
    px(img, cx - 1, cy + 15, INK)
    px(img, cx + 3, cy + 15, INK)
    px(img, cx + 4, cy + 15, INK)
    px(img, cx + 5, cy + 15, INK)
    px(img, cx - 2, cy + 13, INK_SOFT)
    px(img, cx + 3, cy + 13, INK)
    # stubble jaw
    hline(img, cx - 5, cx + 8, cy + 19, WOOD)
    hline(img, cx - 4, cx + 7, cy + 20, INK_SOFT)
    px(img, cx + 8, cy + 17, WOOD)
    # neck
    rect(img, cx - 4, cy + 21, cx + 6, cy + 25, SKIN_D)
    vline(img, cx - 11, cy + 5, cy + 18, INK)
    vline(img, cx + 11, cy + 5, cy + 16, INK)


def lr_blade_vert(img, hx, hy, tip_down=True):
    """Thick odachi — 5–6px, blood groove, wrapped grip."""
    # grip
    rect(img, hx, hy - 12, hx + 5, hy - 2, INK_SOFT)
    for yy in range(hy - 11, hy - 2, 2):
        hline(img, hx, hx + 5, yy, FRAME)
    # pommel
    rect(img, hx - 1, hy - 14, hx + 6, hy - 11, CINN_B)
    px(img, hx + 2, hy - 13, CREAM)
    # guard wide
    rect(img, hx - 4, hy - 3, hx + 9, hy + 1, WOOD)
    outline_rect(img, hx - 4, hy - 3, hx + 9, hy + 1, INK)
    px(img, hx + 2, hy - 2, CINN_B)
    px(img, hx + 4, hy - 1, GOLD)
    if tip_down:
        rect(img, hx, hy, hx + 5, hy + 28, INK_SOFT)
        rect(img, hx + 1, hy + 1, hx + 4, hy + 26, MIST)
        vline(img, hx, hy, hy + 28, INK)
        vline(img, hx + 4, hy, hy + 28, FRAME)
        vline(img, hx + 2, hy + 3, hy + 24, CINN_B)  # blood groove
        px(img, hx + 1, hy + 28, INK_SOFT)
        px(img, hx + 2, hy + 28, MIST)
        px(img, hx + 2, hy + 29, CREAM)
        px(img, hx + 3, hy + 28, FRAME)
    else:
        rect(img, hx, hy - 28, hx + 5, hy, INK_SOFT)
        rect(img, hx + 1, hy - 26, hx + 4, hy - 1, MIST)
        vline(img, hx, hy - 28, hy, INK)
        vline(img, hx + 2, hy - 24, hy - 4, CINN_B)
        px(img, hx + 2, hy - 29, CREAM)


def lr_blade_back(img, hx, hy, lean=0):
    """Windup r2: odachi HIGH-BACK behind head."""
    rect(img, hx - 1, hy, hx + 6, hy + 6, INK_SOFT)
    for yy in range(hy + 1, hy + 5, 2):
        hline(img, hx, hx + 5, yy, FRAME)
    rect(img, hx - 5, hy - 3, hx + 10, hy + 2, WOOD)
    outline_rect(img, hx - 5, hy - 3, hx + 10, hy + 2, INK)
    px(img, hx + 2, hy - 1, CINN_B)
    px(img, hx + 5, hy, GOLD)
    for i in range(26):
        x = hx - (i // 2) - lean * 2
        y = hy - 4 - i
        rect(img, x, y, x + 5, y + 3, INK_SOFT)
        px(img, x, y, INK)
        px(img, x + 2, y + 1, MIST)
        if i % 2 == 0:
            px(img, x + 3, y + 1, CINN_B)
        if i % 4 == 0:
            px(img, x - 1, y + 1, FRAME)
    tx = hx - (25 // 2) - lean * 2
    ty = hy - 4 - 25
    px(img, tx + 2, ty - 1, CREAM)
    px(img, tx + 1, ty, MIST)
    px(img, tx + 2, ty - 2, CREAM)


def lr_blade_slash(img, hx, hy, length=22, dy=0, flash=False):
    """Horizontal odachi + arc trail r2."""
    rect(img, hx - 4, hy - 1, hx + 1, hy + 4, INK_SOFT)
    for yy in range(hy, hy + 3, 2):
        hline(img, hx - 3, hx, yy, FRAME)
    rect(img, hx, hy - 4, hx + 5, hy + 6, WOOD)
    outline_rect(img, hx, hy - 4, hx + 5, hy + 6, INK)
    px(img, hx + 2, hy, CINN_B)
    rect(img, hx + 5, hy + dy, hx + 5 + length, hy + 5 + dy, INK_SOFT)
    hline(img, hx + 5, hx + 5 + length, hy + dy, INK)
    hline(img, hx + 5, hx + 5 + length, hy + 4 + dy, FRAME)
    rect(img, hx + 6, hy + 1 + dy, hx + 4 + length, hy + 3 + dy, MIST)
    hline(img, hx + 7, hx + 3 + length, hy + 2 + dy, CINN_B)
    for i in range(0, length - 2, 3):
        px(img, hx + 7 + i, hy - 2 + dy - (i // 8), FRAME)
        px(img, hx + 8 + i, hy - 3 + dy - (i // 8), MIST)
        px(img, hx + 7 + i, hy + 6 + dy + (i // 10), CINN_B)
    tip = hx + 4 + length
    px(img, tip, hy + 2 + dy, CREAM)
    px(img, tip, hy + 1 + dy, MIST)
    px(img, tip - 1, hy - 1 + dy, INK_SOFT)
    px(img, tip + 1, hy + 2 + dy, CREAM)
    if flash:
        for dx, dy2, c in [(-2, -3, GOLD), (0, -2, CREAM), (1, 2, CREAM),
                           (-1, 6, CINN_B), (-3, -4, CINN_B), (2, 0, CREAM),
                           (-4, -5, GOLD), (1, 4, BLOOD), (-2, 7, CREAM)]:
            px(img, tip + dx, hy + dy + dy2, c)


def lr_blade_diag(img, hx, hy):
    rect(img, hx, hy, hx + 5, hy + 5, INK_SOFT)
    rect(img, hx + 4, hy - 2, hx + 10, hy + 4, WOOD)
    outline_rect(img, hx + 4, hy - 2, hx + 10, hy + 4, INK)
    px(img, hx + 6, hy, CINN_B)
    for i in range(18):
        x = hx + 9 + i
        y = hy - 1 + (i // 2)
        rect(img, x, y, x + 4, y + 4, INK_SOFT)
        px(img, x, y, INK)
        px(img, x + 2, y + 1, MIST)
        if i % 2 == 0:
            px(img, x + 3, y + 2, CINN_B)
    px(img, hx + 26, hy + 8, CREAM)
    px(img, hx + 27, hy + 9, CINN_B)


def langren_draw(img, pose):
    breath = pose.get("breath", 0)
    bx = pose.get("bx", 0)
    by = pose.get("by", 0)
    cx = 22 + bx
    cy = 3 + by + breath

    lr_head(img, cx, cy)

    ty = 26 + by + breath
    # broader shoulders
    rect(img, cx - 13, ty, cx + 14, ty + 5, WOOD)
    hline(img, cx - 12, cx + 13, ty, WOOD_L)
    px(img, cx - 13, ty, CINN_B)
    px(img, cx + 13, ty + 1, FRAME)
    # armor chest
    rect(img, cx - 12, ty + 4, cx + 13, ty + 20, INK_SOFT)
    rect(img, cx - 9, ty + 5, cx + 10, ty + 13, WOOD)
    rect(img, cx - 7, ty + 7, cx + 8, ty + 11, WOOD_L)
    for rx, ry in [(-5, 8), (4, 8), (-2, 7), (1, 7), (-5, 10), (4, 10)]:
        px(img, cx + rx, ty + ry, GOLD)
    robe_folds(img, cx - 12, cx + 13, ty + 13, ty + 20, NIGHT, FRAME)
    # belt + red sash
    rect(img, cx - 12, ty + 14, cx + 13, ty + 19, FRAME)
    hline(img, cx - 12, cx + 13, ty + 14, INK)
    hline(img, cx - 12, cx + 13, ty + 18, NIGHT)
    rect(img, cx - 3, ty + 13, cx + 5, ty + 20, CINN_B)
    outline_rect(img, cx - 3, ty + 13, cx + 5, ty + 20, INK)
    px(img, cx, ty + 15, CREAM)
    px(img, cx + 1, ty + 16, CREAM)
    rect(img, cx - 1, ty + 20, cx + 3, ty + 28, CINN)
    px(img, cx, ty + 26, BLOOD)
    px(img, cx + 1, ty + 24, CINN_B)

    lift_l = pose.get("lift_l", 0)
    lift_r = pose.get("lift_r", 0)
    ly = ty + 20
    lx0 = cx - 10 - (4 if lift_l else 0) - (2 if pose.get("stride_l") else 0)
    rect(img, lx0, ly - lift_l, lx0 + 9, ly + 16 - lift_l, INK_SOFT)
    hline(img, lx0 + 1, lx0 + 8, ly - lift_l + 6, NIGHT)
    hline(img, lx0 + 1, lx0 + 8, ly - lift_l + 11, FRAME)
    rx0 = cx + 1 + (4 if lift_r else 0) + (2 if pose.get("stride_r") else 0)
    rect(img, rx0, ly - lift_r, rx0 + 9, ly + 16 - lift_r, INK_SOFT)
    hline(img, rx0 + 1, rx0 + 8, ly - lift_r + 6, NIGHT)
    hline(img, rx0 + 1, rx0 + 8, ly - lift_r + 11, FRAME)
    hem_layers(img, cx - 13, cx + 14, ly + 1, INK_SOFT, NIGHT, FRAME)
    if lift_l:
        px(img, lx0 - 2, ly - lift_l + 1, INK_SOFT)
        px(img, lx0 - 1, ly - lift_l, NIGHT)
    if lift_r:
        px(img, rx0 + 9, ly - lift_r + 1, INK_SOFT)
        px(img, rx0 + 10, ly - lift_r, NIGHT)
    shoe(img, lx0 - 1, ly + 16 - lift_l, wide=True)
    shoe(img, rx0, ly + 16 - lift_r, wide=True)

    kind = pose.get("kind", "idle")

    if kind == "idle":
        rect(img, cx - 17, ty + 3, cx - 11, ty + 15, INK_SOFT)
        rect(img, cx - 18, ty + 13, cx - 12, ty + 19, INK_SOFT)
        sleeve_cuff(img, cx - 18, cx - 12, ty + 15, INK_SOFT, FRAME)
        hand(img, cx - 18, ty + 17, SKIN_D)
        rect(img, cx + 11, ty + 5, cx + 17, ty + 15, INK_SOFT)
        sleeve_cuff(img, cx + 11, cx + 17, ty + 13, INK_SOFT, FRAME)
        hand(img, cx + 13, ty + 13, SKIN_D, fist=True)
        lr_blade_vert(img, cx + 17, ty + 10, tip_down=True)

    elif kind == "walk":
        if lift_l:
            rect(img, cx + 11, ty + 1, cx + 18, ty + 12, INK_SOFT)
            hand(img, cx + 16, ty + 10, SKIN_D)
            rect(img, cx - 17, ty + 7, cx - 11, ty + 17, INK_SOFT)
            hand(img, cx - 18, ty + 15, SKIN_D)
        else:
            rect(img, cx - 19, ty + 1, cx - 11, ty + 12, INK_SOFT)
            hand(img, cx - 19, ty + 10, SKIN_D)
            rect(img, cx + 11, ty + 7, cx + 17, ty + 17, INK_SOFT)
            hand(img, cx + 13, ty + 15, SKIN_D, fist=True)
        lr_blade_vert(img, cx + 17, ty + 12, tip_down=True)

    elif kind == "windup":
        phase = pose.get("phase", 0)
        # r2 heavy coil: arms high-back, jacket flares, weight on rear
        rect(img, cx - 19, ty - 6, cx - 8, ty + 6, INK_SOFT)
        sleeve_folds(img, cx - 19, cx - 8, ty - 5, ty + 5, NIGHT, FRAME)
        rect(img, cx - 21, ty - 2, cx - 13, ty + 6, INK_SOFT)
        hand(img, cx - 21, ty + 2, SKIN_D, fist=True)
        rect(img, cx - 8, ty - 8, cx + 4, ty + 2, INK_SOFT)
        sleeve_folds(img, cx - 8, cx + 4, ty - 7, ty + 1, NIGHT, FRAME)
        hand(img, cx - 10, ty - 6, SKIN_D, fist=True)
        rect(img, cx + 12, ty + 12, cx + 20, ty + 24, INK_SOFT)
        robe_folds(img, cx + 12, cx + 20, ty + 13, ty + 23, NIGHT, FRAME)
        rect(img, cx - 17, ty + 14, cx - 9, ty + 26, INK_SOFT)
        for dx, dy in [(15, 16), (17, 18), (18, 20), (-14, 18), (-16, 21)]:
            px(img, cx + dx, ty + dy, CINN_B if dx > 0 else FRAME)
        lr_blade_back(img, cx - 15, ty - 2, lean=phase + 1)
        rect(img, cx - 17, ly + 4, cx - 3, ly + 16, INK_SOFT)
        hline(img, cx - 16, cx - 4, ly + 8, NIGHT)
        hline(img, cx - 15, cx - 5, ly + 12, FRAME)
        if phase >= 1:
            rect(img, cx + 2, ly - 8, cx + 11, ly + 6, INK_SOFT)
            hline(img, cx + 3, cx + 10, ly - 4, NIGHT)

    elif kind == "strike":
        phase = pose.get("phase", 0)
        if phase == 0:
            rect(img, cx - 14, ty - 4, cx - 4, ty + 8, INK_SOFT)
            sleeve_folds(img, cx - 14, cx - 4, ty - 3, ty + 7, NIGHT, FRAME)
            hand(img, cx - 14, ty + 4, SKIN_D, fist=True)
            rect(img, cx + 6, ty - 6, cx + 16, ty + 6, INK_SOFT)
            hand(img, cx + 13, ty - 2, SKIN_D, fist=True)
            lr_blade_diag(img, cx + 14, ty - 2)
            rect(img, cx - 14, ty + 14, cx - 6, ty + 26, INK_SOFT)
        elif phase == 1:
            # === HIT FRAME — heavy lunge, arm out, blade long ===
            rect(img, cx - 14, ty + 8, cx - 4, ty + 18, INK_SOFT)
            sleeve_folds(img, cx - 14, cx - 4, ty + 9, ty + 17, NIGHT, FRAME)
            hand(img, cx - 14, ty + 16, SKIN_D)
            rect(img, cx + 6, ty + 0, cx + 22, ty + 10, INK_SOFT)
            sleeve_folds(img, cx + 6, cx + 22, ty + 1, ty + 9, NIGHT, FRAME)
            sleeve_cuff(img, cx + 16, cx + 22, ty + 8, INK_SOFT, FRAME)
            hand(img, cx + 20, ty + 2, SKIN_D, fist=True)
            lr_blade_slash(img, cx + 22, ty + 3, length=28, dy=-2, flash=True)
            rect(img, cx + 12, ty + 12, cx + 22, ty + 24, INK_SOFT)
            robe_folds(img, cx + 12, cx + 22, ty + 13, ty + 23, NIGHT, FRAME)
            for i, (dx, dy) in enumerate([(-2, 2), (-4, 0), (-6, 3), (-3, -2)]):
                px(img, cx + 4 + dx, ty + 4 + dy, CINN_B if i % 2 == 0 else CREAM)
        elif phase == 2:
            rect(img, cx - 10, ty + 10, cx - 2, ty + 20, INK_SOFT)
            hand(img, cx - 10, ty + 18, SKIN_D)
            rect(img, cx + 8, ty + 2, cx + 24, ty + 12, INK_SOFT)
            sleeve_folds(img, cx + 8, cx + 24, ty + 3, ty + 11, NIGHT, FRAME)
            hand(img, cx + 22, ty + 4, SKIN_D, fist=True)
            lr_blade_slash(img, cx + 24, ty + 5, length=26, dy=1, flash=True)
            rect(img, cx + 10, ty + 14, cx + 20, ty + 24, INK_SOFT)
        else:
            rect(img, cx - 13, ty + 5, cx - 5, ty + 15, INK_SOFT)
            hand(img, cx - 13, ty + 13, SKIN_D)
            rect(img, cx + 8, ty + 5, cx + 15, ty + 15, INK_SOFT)
            hand(img, cx + 11, ty + 13, SKIN_D, fist=True)
            lr_blade_vert(img, cx + 15, ty + 10, tip_down=True)

    elif kind == "hurt":
        phase = pose.get("phase", 0)
        if phase == 0:
            rect(img, cx + 10, ty - 5, cx + 20, ty + 7, INK_SOFT)
            hand(img, cx + 18, ty - 6, SKIN_D)
            rect(img, cx - 16, ty + 9, cx - 8, ty + 19, INK_SOFT)
            hand(img, cx - 17, ty + 17, SKIN_D)
            lr_blade_vert(img, cx + 6, ty + 14, tip_down=True)
        else:
            rect(img, cx + 11, ty + 5, cx + 22, ty + 15, INK_SOFT)
            hand(img, cx + 20, ty + 13, SKIN_D)
            rect(img, cx - 15, ty + 3, cx - 7, ty + 13, INK_SOFT)
            hand(img, cx - 16, ty + 11, SKIN_D)
            lr_blade_vert(img, cx - 4, ty + 16, tip_down=True)
        for dx, dy, c in [
            (6, 4, CINN_B), (12, 8, BLOOD), (2, 12, CINN_B),
            (16, 6, BLOOD), (8, 14, BLOOD), (14, 2, CINN_B),
            (-2, 10, BLOOD), (18, 10, CINN), (4, 16, BLOOD), (10, 18, BLOOD),
        ]:
            px(img, cx + dx, ty + dy, c)

    elif kind == "parry":
        phase = pose.get("phase", 0)
        shake = pose.get("shake", 0)
        if phase < 2:
            # overhead guard — arms up, blade high above head
            rect(img, cx - 17, ty - 10, cx - 6, ty + 2, INK_SOFT)
            sleeve_folds(img, cx - 17, cx - 6, ty - 9, ty + 1, NIGHT, FRAME)
            hand(img, cx - 10, ty - 12, SKIN_D, fist=True)
            rect(img, cx + 2, ty - 12, cx + 15, ty + 0, INK_SOFT)
            sleeve_folds(img, cx + 2, cx + 15, ty - 11, ty - 1, NIGHT, FRAME)
            hand(img, cx + 9 + shake, ty - 14, SKIN_D, fist=True)
            lr_blade_vert(img, cx + 7 + shake, ty - 8, tip_down=False)
            rect(img, cx - 15, ty + 16, cx - 5, ty + 26, INK_SOFT)
            rect(img, cx + 8, ty + 16, cx + 18, ty + 26, INK_SOFT)
            if phase == 1:
                for dx, dy, c in [(0, -28, CREAM), (4, -26, GOLD), (2, -24, CREAM),
                                  (6, -30, CINN_B), (-2, -26, GOLD), (8, -22, CREAM),
                                  (3, -32, GOLD)]:
                    px(img, cx + 7 + shake + dx, ty + dy, c)
        else:
            # dodge — deep side lean
            rect(img, cx - 19, ty + 2, cx - 8, ty + 14, INK_SOFT)
            sleeve_folds(img, cx - 19, cx - 8, ty + 3, ty + 13, NIGHT, FRAME)
            hand(img, cx - 19, ty + 12, SKIN_D)
            rect(img, cx - 4, ty - 4, cx + 8, ty + 8, INK_SOFT)
            hand(img, cx + 4, ty - 2, SKIN_D, fist=True)
            lr_blade_slash(img, cx + 6, ty + 0, length=18, dy=2, flash=False)
            rect(img, cx - 19, ty + 14, cx - 7, ty + 28, INK_SOFT)
            robe_folds(img, cx - 19, cx - 7, ty + 15, ty + 27, NIGHT, FRAME)

    vline(img, cx - 13, ty, ty + 18, INK)
    vline(img, cx + 13, ty, ty + 16, INK)


# ============================================================
# assembly
# ============================================================
def poses_v09():
    """r2: exaggerated windup/parry/strike offsets vs idle."""
    poses = []
    poses.append({"kind": "idle", "breath": 0, "bx": 0, "by": 0})
    poses.append({"kind": "idle", "breath": 1, "bx": 0, "by": 0})
    poses.append({"kind": "walk", "breath": 0, "lift_l": 12, "stride_l": 1, "bx": -2})
    poses.append({"kind": "walk", "breath": 0, "lift_l": 4, "bx": 0})
    poses.append({"kind": "walk", "breath": 0, "lift_r": 12, "stride_r": 1, "bx": 2})
    poses.append({"kind": "walk", "breath": 1, "lift_r": 4, "bx": 0})
    # windup — deep LEFT lean + slight crouch so high-back sword fits
    poses.append({"kind": "windup", "phase": 0, "breath": 0, "bx": -4, "by": 2, "lift_l": 2})
    poses.append({"kind": "windup", "phase": 1, "breath": 0, "bx": -8, "by": 2, "lift_r": 10})
    poses.append({"kind": "windup", "phase": 2, "breath": 1, "bx": -10, "by": 3, "lift_r": 12})
    # strike — body left; hit frame (phase1=frame10) lunges forward with front lift
    poses.append({"kind": "strike", "phase": 0, "breath": 0, "bx": -6, "by": 0})
    poses.append({"kind": "strike", "phase": 1, "breath": 0, "bx": -4, "by": 0, "lift_r": 10, "stride_r": 1})
    poses.append({"kind": "strike", "phase": 2, "breath": 1, "bx": -2, "by": 0, "lift_l": 6})
    poses.append({"kind": "strike", "phase": 3, "breath": 0, "bx": -4})
    poses.append({"kind": "hurt", "phase": 0, "breath": 0, "bx": -8, "lift_l": 6})
    poses.append({"kind": "hurt", "phase": 1, "breath": 1, "bx": -12, "by": 2, "lift_r": 4})
    # parry — crouch + overhead; dodge deep left
    poses.append({"kind": "parry", "phase": 0, "breath": 0, "shake": 0, "bx": 2, "by": 3, "lift_l": 4, "lift_r": 4})
    poses.append({"kind": "parry", "phase": 1, "breath": 0, "shake": 3, "bx": 0, "by": 3, "lift_l": 5, "lift_r": 5})
    poses.append({"kind": "parry", "phase": 2, "breath": 1, "shake": 0, "bx": -10, "by": 1, "lift_l": 8})
    return poses


DRAWERS = {"qingyi": qingyi_draw, "langren": langren_draw}


def make_sheet(char_id: str) -> Image.Image:
    sheet = Image.new("RGBA", (18 * FS, FS), TRANS)
    drawer = DRAWERS[char_id]
    poses = poses_v09()
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
    text = """# 精靈表 64×64（原生）— 墨點江湖

> 原生像素 · 僅盤內色 · 透明底 · 硬邊無抗鋸齒  
> **唔係** 32 版 nearest 放大。

## v0.9 精修狀態

| 檔 | 尺寸 | 狀態 | 生成腳本 |
|----|------|------|----------|
| `qingyi.png` | **1152×64** | **v0.9 r2 精修**（姿勢差加大／判定幀） | `tools/gen_sprites_64_v09.py` |
| `langren.png` | **1152×64** | **v0.9 r2 精修**（姿勢差加大／判定幀） | `tools/gen_sprites_64_v09.py` |
| `tiezhang.png` | 1152×64 | 待 v0.9（暫留舊版） | `tools/gen_sprites_64.py` |
| `qinshi.png` | 1152×64 | 待 v0.9（暫留舊版） | `tools/gen_sprites_64.py` |
| `xiaoer.png` | 1152×64 | 待 v0.9（暫留舊版） | `tools/gen_sprites_64.py` |
| `guest_sit.png` | 384×64 | 可選／舊版 | `tools/gen_sprites_64.py` |
| `boss_*_combat.png` | 64×64 | 可選／舊版 | `tools/gen_sprites_64.py` |

每角：每幀 **64×64**，橫向 **18** 幀 → `18×64 = 1152`。面向右。戰鬥顯示 ×2 上 960 場。

## 對幀（v0.9 戰鬥狀態機）

| 幀 | 動作 | 說明 |
|----|------|------|
| 0–1 | **idle** | 呼吸微動，剪影穩定 |
| 2–5 | **walk** | 抬腳明顯，四幀循環 |
| 6–8 | **windup** | 讀招：後引／蓄勢（武器後拉、重心後移）— **唔再係 serve 斟茶** |
| 9–12 | **strike** | 起手→判定接觸→穿過→收勢 |
| 13–14 | **hurt** | stagger／後仰 |
| 15–17 | **parry** | 舉武器擋；幀 17 可兼 dodge 側身 |

```js
const FRAME = 64;
const sx = frameIndex * FRAME; // 0..17
ctx.imageSmoothingEnabled = false;
ctx.drawImage(sheet, sx, 0, FRAME, FRAME, dx, dy, FRAME, FRAME);
```

## 角色主色（ART.md）

| 角 | 主色 | 輔色 |
|----|------|------|
| qingyi | `#2A6A6A` teal | `#4A9A9A` teal-bright（劍鋒／袍亮） |
| langren | `#3D3226` 墨褐 | `#C42B2B` 硃紅亮（刀血／巾） |

## 重跑 v0.9（只覆寫 qingyi／langren）

```bash
python3 /workspace/wuxia-inn/tools/gen_sprites_64_v09.py
```

合規報告：`_gen_report_v09.txt`。預覽：`assets/_preview/64_{qingyi,langren}_*_x2.png`。
"""
    (OUT / "README.md").write_text(text, encoding="utf-8")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    PREV.mkdir(parents=True, exist_ok=True)
    report = ["# v0.9 r2 sprite gen report", ""]
    total_oob = 0
    frame_labels = [
        "idle0", "idle1", "walk0", "walk1", "walk2", "walk3",
        "windup0", "windup1", "windup2",
        "strike0", "strike1", "strike2", "strike3",
        "hurt0", "hurt1", "parry0", "parry1", "parry2",
    ]
    key_preview = {"idle": 0, "windup": 7, "strike": 10, "strike_hit": 10, "hurt": 13, "parry": 15, "parry_dodge": 17, "walk": 2}

    for cid in ("qingyi", "langren"):
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

    report.append(f"TOTAL_OOB={total_oob}")
    (OUT / "_gen_report_v09.txt").write_text("\n".join(report) + "\n", encoding="utf-8")
    write_readme()
    print(f"TOTAL_OOB={total_oob}")
    if total_oob != 0:
        raise SystemExit(f"palette oob={total_oob}")
    print("OK")


if __name__ == "__main__":
    main()
