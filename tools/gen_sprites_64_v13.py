#!/usr/bin/env python3
"""v1.3 Ink-Pixel Inn — xiaoer + guest_sit + guest_walk at r2 density.

Does NOT overwrite qingyi / langren / tiezhang / qinshi / scenes / fx.

xiaoer frames: 0–1 idle | 2–5 walk | 6–8 serve | 9–12 wipe | 13–14 hurt | 15–17 parry
guest_sit: 6×64 → 384×64
guest_walk: 6×8×64 → 3072×64  (absIndex = guestIndex*8 + localFrame)
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
# XIAOER — wood-hat waiter: serve tea / wipe table
# ============================================================
def xe_head(img, cx, cy):
    """Wide wood hat + short hair fringe."""
    # hat brim
    rect(img, cx - 14, cy + 4, cx + 15, cy + 10, WOOD)
    rect(img, cx - 12, cy + 2, cx + 13, cy + 6, WOOD_L)
    hline(img, cx - 14, cx + 15, cy + 4, INK)
    hline(img, cx - 12, cx + 13, cy + 9, NIGHT)
    # crown
    rect(img, cx - 8, cy - 2, cx + 9, cy + 5, WOOD)
    rect(img, cx - 6, cy - 4, cx + 7, cy + 1, WOOD_L)
    px(img, cx, cy - 3, GOLD)
    px(img, cx + 2, cy - 2, LOESS)
    # hair under hat
    rect(img, cx - 9, cy + 8, cx + 10, cy + 12, INK)
    # face
    rect(img, cx - 7, cy + 10, cx + 9, cy + 20, SKIN)
    for fx in (-5, -2, 1, 4, 6):
        px(img, cx + fx, cy + 10, INK)
    px(img, cx - 2, cy + 14, INK); px(img, cx - 1, cy + 14, INK)
    px(img, cx + 3, cy + 14, INK); px(img, cx + 4, cy + 14, INK); px(img, cx + 5, cy + 14, INK)
    px(img, cx - 2, cy + 12, INK_SOFT); px(img, cx + 3, cy + 12, INK_SOFT)
    px(img, cx + 7, cy + 16, SKIN_D)
    hline(img, cx - 5, cx + 7, cy + 19, SKIN_D)
    rect(img, cx - 3, cy + 20, cx + 5, cy + 24, SKIN)
    vline(img, cx - 10, cy + 8, cy + 18, INK)
    vline(img, cx + 10, cy + 8, cy + 16, INK)


def xe_tray(img, x, y, pot_dx=0, pour=False, steam=False):
    """Tea tray with separate pot + cups."""
    # tray board
    rect(img, x, y, x + 28, y + 5, WOOD_L)
    hline(img, x, x + 28, y, INK)
    hline(img, x, x + 28, y + 4, WOOD)
    rect(img, x + 1, y + 1, x + 27, y + 3, FRAME)
    # pot
    px0 = x + 4 + pot_dx
    rect(img, px0, y - 10, px0 + 10, y, CINN_B)
    outline_rect(img, px0, y - 10, px0 + 10, y, INK)
    rect(img, px0 + 2, y - 12, px0 + 8, y - 10, GOLD)
    # spout + handle
    px(img, px0 + 10, y - 6, WOOD)
    px(img, px0 + 11, y - 5, WOOD)
    px(img, px0 + 12, y - 4, WOOD)
    px(img, px0 - 2, y - 5, WOOD)
    px(img, px0 - 3, y - 4, WOOD_L)
    # cups (separate silhouettes)
    c1 = x + 16
    rect(img, c1, y - 5, c1 + 5, y, CREAM)
    outline_rect(img, c1, y - 5, c1 + 5, y, INK)
    px(img, c1 + 2, y - 4, PAPER_L)
    c2 = x + 22
    rect(img, c2, y - 5, c2 + 5, y, PAPER_L)
    outline_rect(img, c2, y - 5, c2 + 5, y, INK)
    if steam:
        px(img, px0 + 4, y - 14, MIST)
        px(img, px0 + 6, y - 16, MIST)
        px(img, px0 + 5, y - 15, PAPER)
    if pour:
        # pour arc from spout to cup
        for i, (dx, dy) in enumerate([(12, -2), (13, 0), (14, 2), (15, 3), (16, 4)]):
            px(img, px0 + dx, y + dy, LOESS if i % 2 == 0 else CREAM)
        px(img, c1 + 2, y - 1, LOESS)
        px(img, c1 + 3, y, CREAM)


def xe_rag(img, x, y, wide=10):
    rect(img, x, y, x + wide, y + 6, CREAM)
    outline_rect(img, x, y, x + wide, y + 6, INK)
    rect(img, x + 2, y + 2, x + wide - 2, y + 5, PAPER_L)
    px(img, x + wide // 2, y + 3, MIST)
    px(img, x + 2, y + 1, PAPER)


def xiaoer_draw(img, pose):
    breath = pose.get("breath", 0)
    bx = pose.get("bx", 0)
    by = pose.get("by", 0)
    cx = 22 + bx
    cy = 2 + by + breath
    xe_head(img, cx, cy)

    ty = 24 + by + breath
    # wood tunic shoulders
    rect(img, cx - 11, ty, cx + 12, ty + 5, WOOD)
    hline(img, cx - 10, cx + 11, ty, WOOD_L)
    px(img, cx - 11, ty, GOLD)
    # collar
    rect(img, cx - 4, ty, cx + 6, ty + 5, PAPER_L)
    rect(img, cx - 3, ty + 1, cx + 5, ty + 4, PAPER)
    # paper apron over wood torso
    rect(img, cx - 10, ty + 4, cx + 12, ty + 14, WOOD)
    robe_folds(img, cx - 10, cx + 12, ty + 5, ty + 14, NIGHT, WOOD_L)
    rect(img, cx - 9, ty + 10, cx + 11, ty + 28, PAPER)
    robe_folds(img, cx - 9, cx + 11, ty + 12, ty + 28, PAPER_D, PAPER_L)
    # cinnabar belt
    belt(img, cx - 10, cx + 12, ty + 9, CINN, GOLD, hang=True)
    # apron pocket
    rect(img, cx - 2, ty + 16, cx + 6, ty + 24, PAPER_L)
    outline_rect(img, cx - 2, ty + 16, cx + 6, ty + 24, PAPER_D)
    px(img, cx + 1, ty + 18, MIST)
    px(img, cx + 3, ty + 20, PAPER)

    lift_l = pose.get("lift_l", 0)
    lift_r = pose.get("lift_r", 0)
    ly = ty + 28
    lx0 = cx - 9 - (4 if lift_l else 0) - (2 if pose.get("stride_l") else 0)
    rect(img, lx0, ly - lift_l, lx0 + 8, ly + 12 - lift_l, WOOD)
    hline(img, lx0 + 1, lx0 + 7, ly - lift_l + 5, NIGHT)
    rx0 = cx + 1 + (4 if lift_r else 0) + (2 if pose.get("stride_r") else 0)
    rect(img, rx0, ly - lift_r, rx0 + 8, ly + 12 - lift_r, WOOD)
    hline(img, rx0 + 1, rx0 + 7, ly - lift_r + 5, NIGHT)
    hem_layers(img, cx - 11, cx + 13, ly + 1, PAPER, PAPER_D, PAPER_L)
    if lift_l:
        px(img, lx0 - 2, ly - lift_l + 1, PAPER)
    if lift_r:
        px(img, rx0 + 8, ly - lift_r + 1, PAPER)
    shoe(img, lx0 - 1, ly + 12 - lift_l)
    shoe(img, rx0, ly + 12 - lift_r)

    kind = pose.get("kind", "idle")

    if kind == "idle":
        rect(img, cx - 15, ty + 3, cx - 9, ty + 15, WOOD)
        sleeve_folds(img, cx - 15, cx - 9, ty + 4, ty + 14, NIGHT, WOOD_L)
        sleeve_cuff(img, cx - 15, cx - 9, ty + 13, WOOD)
        hand(img, cx - 16, ty + 15, SKIN)
        # rag in front hand
        rect(img, cx + 10, ty + 5, cx + 16, ty + 15, WOOD)
        sleeve_folds(img, cx + 10, cx + 16, ty + 6, ty + 14, NIGHT, WOOD_L)
        sleeve_cuff(img, cx + 10, cx + 16, ty + 13, WOOD)
        hand(img, cx + 12, ty + 13, SKIN)
        xe_rag(img, cx + 14, ty + 14, wide=10)

    elif kind == "walk":
        if lift_l:
            rect(img, cx + 10, ty + 1, cx + 17, ty + 12, WOOD)
            sleeve_cuff(img, cx + 10, cx + 17, ty + 10, WOOD)
            hand(img, cx + 15, ty + 10, SKIN)
            xe_rag(img, cx + 16, ty + 11, wide=8)
            rect(img, cx - 15, ty + 7, cx - 9, ty + 17, WOOD)
            hand(img, cx - 16, ty + 15, SKIN)
        else:
            rect(img, cx - 17, ty + 1, cx - 9, ty + 12, WOOD)
            sleeve_cuff(img, cx - 17, cx - 9, ty + 10, WOOD)
            hand(img, cx - 17, ty + 10, SKIN)
            rect(img, cx + 10, ty + 7, cx + 16, ty + 17, WOOD)
            hand(img, cx + 12, ty + 15, SKIN)
            xe_rag(img, cx + 14, ty + 16, wide=8)

    elif kind == "serve":
        phase = pose.get("phase", 0)
        # both arms supporting tray — exaggerated vs idle
        if phase == 0:
            # lift tray from low — knees bend cue via by
            rect(img, cx - 16, ty + 6, cx - 4, ty + 18, WOOD)
            sleeve_folds(img, cx - 16, cx - 4, ty + 7, ty + 17, NIGHT, WOOD_L)
            hand(img, cx - 10, ty + 16, SKIN)
            rect(img, cx + 4, ty + 2, cx + 18, ty + 14, WOOD)
            sleeve_folds(img, cx + 4, cx + 18, ty + 3, ty + 13, NIGHT, WOOD_L)
            hand(img, cx + 16, ty + 10, SKIN)
            xe_tray(img, cx + 12, ty + 8, pot_dx=0, pour=False, steam=False)
            rect(img, cx - 16, ty + 18, cx - 6, ty + 30, PAPER)
            robe_folds(img, cx - 16, cx - 6, ty + 19, ty + 29, PAPER_D, PAPER_L)
        elif phase == 1:
            # steady hold high, steam — arms extended
            rect(img, cx - 16, ty - 2, cx - 4, ty + 12, WOOD)
            sleeve_folds(img, cx - 16, cx - 4, ty - 1, ty + 11, NIGHT, WOOD_L)
            hand(img, cx - 8, ty + 6, SKIN)
            rect(img, cx + 6, ty - 8, cx + 22, ty + 6, WOOD)
            sleeve_folds(img, cx + 6, cx + 22, ty - 7, ty + 5, NIGHT, WOOD_L)
            hand(img, cx + 20, ty - 2, SKIN)
            xe_tray(img, cx + 14, ty - 4, pot_dx=0, pour=False, steam=True)
            rect(img, cx + 12, ty + 14, cx + 20, ty + 28, PAPER)
            robe_folds(img, cx + 12, cx + 20, ty + 15, ty + 27, PAPER_D, PAPER_L)
        else:
            # pour — pot tipped far, clear pour arc + deep lean
            rect(img, cx - 18, ty + 4, cx - 4, ty + 16, WOOD)
            sleeve_folds(img, cx - 18, cx - 4, ty + 5, ty + 15, NIGHT, WOOD_L)
            hand(img, cx - 12, ty + 12, SKIN)
            rect(img, cx + 2, ty - 10, cx + 22, ty + 4, WOOD)
            sleeve_folds(img, cx + 2, cx + 22, ty - 9, ty + 3, NIGHT, WOOD_L)
            hand(img, cx + 20, ty - 6, SKIN, fist=True)
            xe_tray(img, cx + 12, ty - 6, pot_dx=6, pour=True, steam=True)
            rect(img, cx + 8, ty + 12, cx + 22, ty + 28, PAPER)
            robe_folds(img, cx + 8, cx + 22, ty + 13, ty + 27, PAPER_D, PAPER_L)
            # forward planted mass
            rect(img, cx - 14, ly + 2, cx - 2, ly + 12, WOOD)

    elif kind == "wipe":
        phase = pose.get("phase", 0)
        # table edge
        hline(img, cx + 4, 62, ty + 28, WOOD_L)
        hline(img, cx + 4, 62, ty + 30, WOOD)
        hline(img, cx + 6, 60, ty + 29, FRAME)
        # back arm brace
        rect(img, cx - 16, ty + 10, cx - 6, ty + 20, WOOD)
        sleeve_folds(img, cx - 16, cx - 6, ty + 11, ty + 19, NIGHT, WOOD_L)
        hand(img, cx - 16, ty + 18, SKIN)
        # wipe arm arc by phase — lean deeper as wipe progresses
        lean = phase * 2
        if phase == 0:
            rect(img, cx + 6, ty + 6, cx + 18, ty + 16, WOOD)
            sleeve_folds(img, cx + 6, cx + 18, ty + 7, ty + 15, NIGHT, WOOD_L)
            hand(img, cx + 16, ty + 14, SKIN)
            xe_rag(img, cx + 14, ty + 16, wide=12)
        elif phase == 1:
            rect(img, cx + 8, ty + 4, cx + 22, ty + 14, WOOD)
            sleeve_folds(img, cx + 8, cx + 22, ty + 5, ty + 13, NIGHT, WOOD_L)
            hand(img, cx + 20, ty + 12, SKIN)
            xe_rag(img, cx + 18, ty + 14, wide=14)
            px(img, cx + 28, ty + 16, MIST)
            px(img, cx + 30, ty + 18, MIST)
        elif phase == 2:
            # farthest reach + deepest lean
            rect(img, cx + 8 - lean, ty + 2, cx + 26, ty + 12, WOOD)
            sleeve_folds(img, cx + 8, cx + 26, ty + 3, ty + 11, NIGHT, WOOD_L)
            hand(img, cx + 24, ty + 10, SKIN)
            xe_rag(img, cx + 22, ty + 12, wide=16)
            for dx in range(0, 12, 3):
                px(img, cx + 30 + dx, ty + 14, MIST)
                px(img, cx + 32 + dx, ty + 16, PAPER)
            rect(img, cx + 10, ty + 16, cx + 20, ty + 26, PAPER)
            robe_folds(img, cx + 10, cx + 20, ty + 17, ty + 25, PAPER_D, PAPER_L)
        else:
            # recover
            rect(img, cx + 6, ty + 5, cx + 18, ty + 15, WOOD)
            sleeve_folds(img, cx + 6, cx + 18, ty + 6, ty + 14, NIGHT, WOOD_L)
            hand(img, cx + 16, ty + 13, SKIN)
            xe_rag(img, cx + 14, ty + 15, wide=12)
            px(img, cx + 26, ty + 17, MIST)

    elif kind == "hurt":
        phase = pose.get("phase", 0)
        if phase == 0:
            rect(img, cx + 10, ty - 4, cx + 18, ty + 8, WOOD)
            hand(img, cx + 16, ty - 5, SKIN)
            rect(img, cx - 15, ty + 8, cx - 7, ty + 18, WOOD)
            hand(img, cx - 16, ty + 16, SKIN)
            xe_rag(img, cx + 4, ty + 18, wide=8)
        else:
            rect(img, cx + 11, ty + 6, cx + 20, ty + 16, WOOD)
            hand(img, cx + 18, ty + 14, SKIN)
            rect(img, cx - 14, ty + 4, cx - 6, ty + 14, WOOD)
            hand(img, cx - 15, ty + 12, SKIN)
        for dx, dy, c in [
            (6, 6, CINN_B), (10, 10, BLOOD), (2, 14, CINN_B),
            (14, 8, BLOOD), (8, 16, BLOOD), (12, 4, CINN_B),
        ]:
            px(img, cx + dx, ty + dy, c)

    elif kind == "parry":
        phase = pose.get("phase", 0)
        shake = pose.get("shake", 0)
        if phase < 2:
            # tray as shield overhead
            rect(img, cx - 14, ty - 8, cx - 4, ty + 4, WOOD)
            sleeve_folds(img, cx - 14, cx - 4, ty - 7, ty + 3, NIGHT, WOOD_L)
            hand(img, cx - 8, ty - 6, SKIN, fist=True)
            rect(img, cx + 2, ty - 10, cx + 14, ty + 2, WOOD)
            sleeve_folds(img, cx + 2, cx + 14, ty - 9, ty + 1, NIGHT, WOOD_L)
            hand(img, cx + 10 + shake, ty - 8, SKIN, fist=True)
            # tray board high
            rect(img, cx - 4 + shake, ty - 16, cx + 22 + shake, ty - 10, WOOD_L)
            outline_rect(img, cx - 4 + shake, ty - 16, cx + 22 + shake, ty - 10, INK)
            rect(img, cx - 2 + shake, ty - 14, cx + 20 + shake, ty - 12, FRAME)
            # pot tipped on tray
            rect(img, cx + 4 + shake, ty - 22, cx + 12 + shake, ty - 16, CINN_B)
            outline_rect(img, cx + 4 + shake, ty - 22, cx + 12 + shake, ty - 16, INK)
            if phase == 1:
                px(img, cx + 22 + shake, ty - 14, CREAM)
                px(img, cx + 24 + shake, ty - 12, GOLD)
            rect(img, cx - 14, ty + 18, cx - 6, ty + 28, PAPER)
            rect(img, cx + 8, ty + 18, cx + 16, ty + 28, PAPER)
        else:
            # dodge left with tray across body
            rect(img, cx - 18, ty + 2, cx - 8, ty + 14, WOOD)
            sleeve_folds(img, cx - 18, cx - 8, ty + 3, ty + 13, NIGHT, WOOD_L)
            hand(img, cx - 18, ty + 12, SKIN)
            rect(img, cx - 4, ty - 2, cx + 10, ty + 10, WOOD)
            hand(img, cx + 6, ty + 0, SKIN, fist=True)
            rect(img, cx - 2, ty - 6, cx + 20, ty + 0, WOOD_L)
            outline_rect(img, cx - 2, ty - 6, cx + 20, ty + 0, INK)
            rect(img, cx - 18, ty + 16, cx - 8, ty + 28, PAPER)
            robe_folds(img, cx - 18, cx - 8, ty + 17, ty + 27, PAPER_D, PAPER_L)

    vline(img, cx - 11, ty, ty + 22, INK)
    vline(img, cx + 11, ty, ty + 18, INK)


def poses_xiaoer():
    poses = []
    poses.append({"kind": "idle", "breath": 0, "bx": 0, "by": 0})
    poses.append({"kind": "idle", "breath": 1, "bx": 0, "by": 0})
    poses.append({"kind": "walk", "breath": 0, "lift_l": 12, "stride_l": 1, "bx": -2})
    poses.append({"kind": "walk", "breath": 0, "lift_l": 4, "bx": 0})
    poses.append({"kind": "walk", "breath": 0, "lift_r": 12, "stride_r": 1, "bx": 2})
    poses.append({"kind": "walk", "breath": 1, "lift_r": 4, "bx": 0})
    # serve 6–8
    poses.append({"kind": "serve", "phase": 0, "breath": 0, "bx": -4, "by": 3, "lift_l": 4})
    poses.append({"kind": "serve", "phase": 1, "breath": 0, "bx": -4, "by": 1})
    poses.append({"kind": "serve", "phase": 2, "breath": 1, "bx": -2, "by": 2, "lift_r": 8, "stride_r": 1})
    # wipe 9–12
    poses.append({"kind": "wipe", "phase": 0, "breath": 0, "bx": -2, "by": 2})
    poses.append({"kind": "wipe", "phase": 1, "breath": 0, "bx": -4, "by": 2, "lift_r": 4})
    poses.append({"kind": "wipe", "phase": 2, "breath": 1, "bx": -6, "by": 3, "lift_r": 8})
    poses.append({"kind": "wipe", "phase": 3, "breath": 0, "bx": -2, "by": 1})
    poses.append({"kind": "hurt", "phase": 0, "breath": 0, "bx": -8, "lift_l": 6})
    poses.append({"kind": "hurt", "phase": 1, "breath": 1, "bx": -12, "by": 2, "lift_r": 4})
    poses.append({"kind": "parry", "phase": 0, "breath": 0, "shake": 0, "bx": 2, "by": 2, "lift_l": 4, "lift_r": 4})
    poses.append({"kind": "parry", "phase": 1, "breath": 0, "shake": 3, "bx": 0, "by": 2, "lift_l": 5, "lift_r": 5})
    poses.append({"kind": "parry", "phase": 2, "breath": 1, "shake": 0, "bx": -10, "by": 1, "lift_l": 8})
    return poses


# ============================================================
# GUEST heads / stool / props
# ============================================================
GUEST_VARIANTS = [
    # robe, belt, hair, face, hat_mode, prop_kind, prop_color
    (TEAL, WOOD_L, INK, SKIN, "topknot", "cup", CREAM),
    (ROBE_R, GOLD, INK, SKIN, "bun", "bowl", PAPER_L),
    (INK_SOFT, FRAME, INK, SKIN_D, "fringe", "cup", CREAM),
    (VIOLET, GOLD, PAPER_L, SKIN, "bald", "cup", PAPER),
    (JADE, WOOD_L, INK, SKIN, "topknot", "bowl", CINN_B),
    (WOOD, CINN, INK, SKIN_D, "hat", "cup", CREAM),
]


def guest_head(img, cx, cy, hair, face, hat):
    if hat == "topknot":
        rect(img, cx - 5, cy - 6, cx + 6, cy + 2, hair)
        rect(img, cx - 3, cy - 10, cx + 4, cy - 4, hair)
        px(img, cx, cy - 8, GOLD)
        px(img, cx + 1, cy - 6, LOESS)
        rect(img, cx - 8, cy + 2, cx + 9, cy + 9, hair)
    elif hat == "bun":
        rect(img, cx - 8, cy + 2, cx + 9, cy + 9, hair)
        rect(img, cx - 12, cy - 2, cx - 4, cy + 6, hair)
        rect(img, cx + 4, cy - 4, cx + 14, cy + 6, hair)
        px(img, cx - 8, cy - 1, GOLD)
        px(img, cx + 10, cy - 2, GOLD)
        px(img, cx + 11, cy, CINN_B)
    elif hat == "fringe":
        rect(img, cx - 9, cy + 1, cx + 10, cy + 9, hair)
        rect(img, cx - 10, cy + 4, cx + 11, cy + 10, hair)
        # headband
        rect(img, cx - 8, cy + 6, cx + 9, cy + 9, CINN_B)
        hline(img, cx - 8, cx + 9, cy + 7, CINN)
        px(img, cx + 9, cy + 8, BLOOD)  # trailing band
        px(img, cx + 10, cy + 9, BLOOD)
        px(img, cx + 11, cy + 10, CINN)
    elif hat == "bald":
        rect(img, cx - 8, cy + 1, cx + 9, cy + 8, PAPER_L)
        rect(img, cx - 6, cy - 2, cx + 7, cy + 2, PAPER)
        hline(img, cx - 8, cx + 8, cy + 2, PAPER_D)
        px(img, cx, cy + 3, GOLD)
        px(img, cx - 1, cy + 4, VIOLET)
        px(img, cx + 1, cy + 4, VIOLET)
        rect(img, cx - 10, cy + 8, cx - 7, cy + 14, PAPER_L)
        rect(img, cx + 8, cy + 8, cx + 11, cy + 14, PAPER_L)
    elif hat == "hat":
        rect(img, cx - 14, cy + 3, cx + 15, cy + 9, WOOD)
        rect(img, cx - 12, cy + 1, cx + 13, cy + 5, WOOD_L)
        hline(img, cx - 14, cx + 15, cy + 3, INK)
        rect(img, cx - 8, cy - 3, cx + 9, cy + 4, WOOD)
        px(img, cx, cy - 2, GOLD)
        rect(img, cx - 9, cy + 8, cx + 10, cy + 11, INK)

    # face shared
    fy = cy + 9 if hat != "hat" else cy + 10
    if hat == "bald":
        fy = cy + 8
    rect(img, cx - 7, fy, cx + 9, fy + 10, face)
    for fx in (-5, -2, 1, 4, 6):
        px(img, cx + fx, fy, INK if hat != "bald" else hair if hair != PAPER_L else INK)
    px(img, cx - 2, fy + 4, INK); px(img, cx - 1, fy + 4, INK)
    px(img, cx + 3, fy + 4, INK); px(img, cx + 4, fy + 4, INK); px(img, cx + 5, fy + 4, INK)
    px(img, cx + 7, fy + 6, SKIN_D if face == SKIN else face)
    hline(img, cx - 5, cx + 7, fy + 9, SKIN_D if face == SKIN else NIGHT)
    rect(img, cx - 3, fy + 10, cx + 5, fy + 14, face)
    vline(img, cx - 10, fy - 2, fy + 8, INK)
    vline(img, cx + 10, fy - 2, fy + 6, INK)


def stool(img, x, y, tall=False):
    """Visible wooden stool with seat + legs + rung."""
    h = 10 if not tall else 12
    rect(img, x, y, x + 28, y + 6, WOOD_L)
    outline_rect(img, x, y, x + 28, y + 6, INK)
    hline(img, x + 2, x + 26, y + 2, WOOD)
    hline(img, x + 3, x + 25, y + 4, FRAME)
    # legs
    rect(img, x + 3, y + 6, x + 7, y + 6 + h, WOOD)
    rect(img, x + 21, y + 6, x + 25, y + 6 + h, WOOD)
    # rung
    hline(img, x + 5, x + 23, y + 6 + h // 2, WOOD_L)
    px(img, x + 4, y + 5 + h, INK)
    px(img, x + 22, y + 5 + h, INK)


def cup_prop(img, x, y, color=CREAM):
    rect(img, x, y, x + 7, y + 8, color)
    outline_rect(img, x, y, x + 7, y + 8, INK)
    px(img, x + 3, y + 2, CREAM if color != CREAM else PAPER_L)
    px(img, x + 2, y - 1, MIST)
    px(img, x + 4, y - 2, MIST)


def bowl_prop(img, x, y, color=PAPER_L):
    rect(img, x, y, x + 12, y + 7, color)
    outline_rect(img, x, y, x + 12, y + 7, INK)
    hline(img, x + 1, x + 11, y + 3, LOESS if color != LOESS else GOLD)
    px(img, x + 5, y + 2, CREAM)
    px(img, x + 7, y + 4, GOLD)


def guest_sit_draw(img, gi):
    robe, belt_c, hair, face, hat, prop_kind, prop_c = GUEST_VARIANTS[gi]
    cx, cy = 26, 2
    # stool first (behind / under)
    stool(img, 14, 42)
    guest_head(img, cx, cy, hair, face, hat)
    ty = 22
    # torso
    rect(img, cx - 11, ty, cx + 13, ty + 18, robe)
    robe_folds(img, cx - 11, cx + 13, ty + 2, ty + 18, NIGHT, GOLD if robe in (TEAL, VIOLET, JADE) else WOOD_L)
    rect(img, cx - 4, ty, cx + 6, ty + 4, PAPER_L)
    rect(img, cx - 3, ty + 1, cx + 5, ty + 3, PAPER)
    # shoulders accent
    rect(img, cx - 12, ty, cx - 8, ty + 6, robe)
    rect(img, cx + 9, ty, cx + 14, ty + 6, robe)
    px(img, cx - 12, ty, GOLD)
    px(img, cx + 13, ty + 1, GOLD)
    belt(img, cx - 11, cx + 13, ty + 10, belt_c, GOLD, hang=True)
    # lap / bent legs
    rect(img, cx - 12, ty + 14, cx + 16, ty + 24, robe)
    robe_folds(img, cx - 12, cx + 16, ty + 15, ty + 24, NIGHT, None)
    rect(img, cx + 2, ty + 18, cx + 18, ty + 26, robe)
    hline(img, cx - 12, cx + 16, ty + 23, NIGHT)
    # dangling feet
    rect(img, cx - 8, 50, cx - 1, 58, INK_SOFT)
    rect(img, cx + 6, 51, cx + 14, 59, INK_SOFT)
    hline(img, cx - 8, cx - 1, 57, INK)
    hline(img, cx + 6, cx + 14, 58, INK)
    # front arm + prop
    rect(img, cx + 8, ty + 4, cx + 18, ty + 12, robe)
    sleeve_folds(img, cx + 8, cx + 18, ty + 5, ty + 11, NIGHT, GOLD)
    hand(img, cx + 16, ty + 8, face)
    if prop_kind == "cup":
        cup_prop(img, cx + 18, ty + 2, prop_c)
    else:
        bowl_prop(img, cx + 16, ty + 4, prop_c)
    # other hand on lap
    rect(img, cx - 16, ty + 10, cx - 8, ty + 18, robe)
    hand(img, cx - 16, ty + 16, face)
    vline(img, cx - 12, ty, ty + 16, INK)
    vline(img, cx + 12, ty, ty + 14, INK)


def guest_walk_draw(img, gi, phase):
    robe, belt_c, hair, face, hat, _pk, _pc = GUEST_VARIANTS[gi]
    if phase in (0, 4):
        lift_l, lift_r, bx, breath = 12, 0, -2, 0
    elif phase in (1, 5):
        lift_l, lift_r, bx, breath = 0, 0, 0, 1
    elif phase == 2:
        lift_l, lift_r, bx, breath = 0, 12, 2, 0
    elif phase == 3:
        lift_l, lift_r, bx, breath = 0, 0, 0, 0
    else:
        lift_l, lift_r, bx, breath = 0, 0, 0, 0

    if phase <= 5:
        cx = 22 + bx
        cy = 2 + breath
        guest_head(img, cx, cy, hair, face, hat)
        ty = 24 + breath
        rect(img, cx - 11, ty, cx + 12, ty + 22, robe)
        robe_folds(img, cx - 11, cx + 12, ty + 2, ty + 22, NIGHT, GOLD if robe in (TEAL, VIOLET, JADE) else WOOD_L)
        rect(img, cx - 4, ty, cx + 6, ty + 4, PAPER_L)
        belt(img, cx - 11, cx + 12, ty + 12, belt_c, GOLD, hang=True)
        # arms
        if lift_l:
            rect(img, cx + 10, ty + 1, cx + 17, ty + 12, robe)
            sleeve_cuff(img, cx + 10, cx + 17, ty + 10, robe)
            hand(img, cx + 15, ty + 10, face)
            rect(img, cx - 15, ty + 7, cx - 9, ty + 17, robe)
            hand(img, cx - 16, ty + 15, face)
        elif lift_r:
            rect(img, cx - 17, ty + 1, cx - 9, ty + 12, robe)
            sleeve_cuff(img, cx - 17, cx - 9, ty + 10, robe)
            hand(img, cx - 17, ty + 10, face)
            rect(img, cx + 10, ty + 7, cx + 16, ty + 17, robe)
            hand(img, cx + 12, ty + 15, face)
        else:
            rect(img, cx - 15, ty + 3, cx - 9, ty + 15, robe)
            sleeve_cuff(img, cx - 15, cx - 9, ty + 13, robe)
            hand(img, cx - 16, ty + 15, face)
            rect(img, cx + 10, ty + 5, cx + 16, ty + 15, robe)
            sleeve_cuff(img, cx + 10, cx + 16, ty + 13, robe)
            hand(img, cx + 12, ty + 13, face)
        if phase == 5:
            # approach: arms tucked
            rect(img, cx + 8, ty + 4, cx + 14, ty + 14, robe)
            px(img, cx + 6, ty + 6, CREAM)
        ly = ty + 22
        lx0 = cx - 9 - (4 if lift_l else 0)
        rect(img, lx0, ly - lift_l, lx0 + 8, ly + 14 - lift_l, robe)
        hline(img, lx0 + 1, lx0 + 7, ly - lift_l + 5, NIGHT)
        rx0 = cx + 1 + (4 if lift_r else 0)
        rect(img, rx0, ly - lift_r, rx0 + 8, ly + 14 - lift_r, robe)
        hline(img, rx0 + 1, rx0 + 7, ly - lift_r + 5, NIGHT)
        hem_layers(img, cx - 11, cx + 13, ly + 1, robe, NIGHT, None)
        shoe(img, lx0 - 1, ly + 14 - lift_l)
        shoe(img, rx0, ly + 14 - lift_r)
        vline(img, cx - 11, ty, ty + 20, INK)
        vline(img, cx + 11, ty, ty + 16, INK)

    elif phase == 6:
        # sit_down bend — stool appears
        stool(img, 14, 44)
        cx, cy = 24, 4
        guest_head(img, cx, cy, hair, face, hat)
        ty = 24
        # bent forward torso
        rect(img, cx - 12, ty, cx + 10, ty + 16, robe)
        robe_folds(img, cx - 12, cx + 10, ty + 2, ty + 16, NIGHT, None)
        rect(img, cx - 4, ty, cx + 5, ty + 4, PAPER_L)
        belt(img, cx - 12, cx + 10, ty + 10, belt_c, GOLD, hang=True)
        # thighs folding
        rect(img, cx - 10, ty + 12, cx + 18, ty + 24, robe)
        rect(img, cx + 2, ty + 16, cx + 20, ty + 26, robe)
        hline(img, cx - 10, cx + 18, ty + 22, NIGHT)
        # arms bracing
        rect(img, cx + 6, ty + 2, cx + 18, ty + 12, robe)
        hand(img, cx + 16, ty + 8, face)
        rect(img, cx - 16, ty + 8, cx - 8, ty + 18, robe)
        hand(img, cx - 16, ty + 16, face)
        # feet
        rect(img, cx - 6, 52, cx + 1, 60, INK_SOFT)
        rect(img, cx + 6, 50, cx + 13, 58, INK_SOFT)
        hline(img, cx - 6, cx + 1, 59, INK)
        hline(img, cx + 6, cx + 13, 57, INK)

    else:
        # sit settled — no cup (cut to guest_sit)
        stool(img, 14, 42)
        cx, cy = 26, 2
        guest_head(img, cx, cy, hair, face, hat)
        ty = 22
        rect(img, cx - 11, ty, cx + 13, ty + 18, robe)
        robe_folds(img, cx - 11, cx + 13, ty + 2, ty + 18, NIGHT, None)
        rect(img, cx - 4, ty, cx + 6, ty + 4, PAPER_L)
        belt(img, cx - 11, cx + 13, ty + 10, belt_c, GOLD, hang=True)
        rect(img, cx - 12, ty + 14, cx + 16, ty + 24, robe)
        rect(img, cx + 2, ty + 18, cx + 18, ty + 26, robe)
        hline(img, cx - 12, cx + 16, ty + 23, NIGHT)
        rect(img, cx - 8, 50, cx - 1, 58, INK_SOFT)
        rect(img, cx + 6, 51, cx + 14, 59, INK_SOFT)
        hline(img, cx - 8, cx - 1, 57, INK)
        hline(img, cx + 6, cx + 14, 58, INK)
        # hands on lap — no prop
        rect(img, cx + 8, ty + 4, cx + 16, ty + 12, robe)
        hand(img, cx + 14, ty + 8, face)
        rect(img, cx - 16, ty + 10, cx - 8, ty + 18, robe)
        hand(img, cx - 16, ty + 16, face)


# ============================================================
# assembly
# ============================================================
def make_xiaoer_sheet() -> Image.Image:
    sheet = Image.new("RGBA", (18 * FS, FS), TRANS)
    poses = poses_xiaoer()
    assert len(poses) == 18
    for i, pose in enumerate(poses):
        fr = new_frame()
        xiaoer_draw(fr, pose)
        sheet.paste(fr, (i * FS, 0), fr)
    return sheet


def make_guest_sit_sheet() -> Image.Image:
    sheet = Image.new("RGBA", (6 * FS, FS), TRANS)
    for gi in range(6):
        fr = new_frame()
        guest_sit_draw(fr, gi)
        sheet.paste(fr, (gi * FS, 0), fr)
    return sheet


def make_guest_walk_sheet() -> Image.Image:
    sheet = Image.new("RGBA", (48 * FS, FS), TRANS)  # 3072×64
    for gi in range(6):
        for phase in range(8):
            fr = new_frame()
            guest_walk_draw(fr, gi, phase)
            abs_i = gi * 8 + phase
            sheet.paste(fr, (abs_i * FS, 0), fr)
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


def visible_pixels(sheet, i, fs=FS):
    x0 = i * fs
    return sum(1 for y in range(fs) for x in range(x0, x0 + fs) if sheet.getpixel((x, y))[3] > 0)


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


def crop_frame(sheet, i, fs=FS):
    return sheet.crop((i * fs, 0, (i + 1) * fs, fs))


def write_readme():
    import re
    readme = OUT / "README.md"
    text = readme.read_text(encoding="utf-8") if readme.exists() else ""

    def set_row(txt, name, size, status, script):
        pat = rf"\| `{re.escape(name)}` \|[^\n]+\n"
        row = f"| `{name}` | **{size}** | **{status}** | `{script}` |\n"
        if re.search(pat, txt):
            return re.sub(pat, row, txt)
        # insert before boss row if missing
        return txt

    text = set_row(text, "xiaoer.png", "1152×64", "v1.3 精修（serve／wipe）", "tools/gen_sprites_64_v13.py")
    text = set_row(text, "guest_sit.png", "384×64", "v1.3 精修（6 色坐姿）", "tools/gen_sprites_64_v13.py")
    if "guest_walk.png" not in text.split("##")[0] and "| `guest_walk.png`" not in text:
        # add row after guest_sit
        text = text.replace(
            "| `guest_sit.png` | **384×64** | **v1.3 精修（6 色坐姿）** | `tools/gen_sprites_64_v13.py` |\n",
            "| `guest_sit.png` | **384×64** | **v1.3 精修（6 色坐姿）** | `tools/gen_sprites_64_v13.py` |\n"
            "| `guest_walk.png` | **3072×64** | **v1.3 新增（6×8 walk／入座）** | `tools/gen_sprites_64_v13.py` |\n",
        )
    else:
        text = set_row(text, "guest_walk.png", "3072×64", "v1.3 新增（6×8 walk／入座）", "tools/gen_sprites_64_v13.py")

    if "## v1.3" not in text:
        note = """
## v1.3 客棧生活（xiaoer／guest）

### xiaoer 專用對幀（唔跟俠客 windup／strike）

| 幀 | 動作 |
|----|------|
| 0–1 | idle |
| 2–5 | walk |
| 6–8 | **serve 斟茶**（起盤→端穩→倒茶；茶盤／壺／杯分離） |
| 9–12 | **wipe 抹枱** |
| 13–14 | hurt |
| 15–17 | parry（托盤擋） |

### guest_walk 64

- 佈局：6 客人 × 8 幀 = 48 幀 → **3072×64**
- `absIndex = guestIndex * 8 + localFrame`；`FRAME = 64`
- localFrame：0–3 walk｜4–5 approach｜6–7 sit_down（幀7坐定無杯 → 切 `guest_sit` 同色加杯）
- 主色／帽對齊 `guest_sit` 0–5

```js
const FRAME = 64;
const sx = (guestIndex * 8 + local) * FRAME;
ctx.drawImage(guestWalk, sx, 0, FRAME, FRAME, dx, dy, FRAME, FRAME);
```

生成：`tools/gen_sprites_64_v13.py` · 報告：`_gen_report_v13.txt`

"""
        text = text.rstrip() + "\n" + note
    # role colors
    if "xiaoer |" not in text and "| xiaoer |" not in text:
        text = text.replace(
            "| qinshi | `#5A4060` violet | `#F4E6C4` paper-light（素袍／拂塵） |\n",
            "| qinshi | `#5A4060` violet | `#F4E6C4` paper-light（素袍／拂塵） |\n"
            "| xiaoer | `#5C4030` wood | 宣紙圍裙＋硃紅腰帶（茶盤／抹布） |\n",
        )
    readme.write_text(text, encoding="utf-8")


def make_xiaoer_compare(sheet):
    def paper_x3(fr):
        big = fr.resize((192, 192), Image.Resampling.NEAREST)
        bg = Image.new("RGBA", (192, 192), PAPER)
        bg.paste(big, (0, 0), big)
        return bg
    strip = Image.new("RGBA", (192 * 4 + 12, 192), PAPER_D)
    for i, idx in enumerate([0, 8, 11, 15]):  # idle / serve-pour / wipe / parry
        strip.paste(paper_x3(crop_frame(sheet, idx)), (i * (192 + 4), 0))
    strip.save(PREV / "64_xiaoer_compare_v13.png")


def main():
    import hashlib
    OUT.mkdir(parents=True, exist_ok=True)
    PREV.mkdir(parents=True, exist_ok=True)
    report = ["# v1.3 sprite gen report (xiaoer + guest_sit + guest_walk)", ""]
    total_oob = 0

    untouched = {}
    for cid in ("qingyi", "langren", "tiezhang", "qinshi"):
        fp = OUT / f"{cid}.png"
        if fp.exists():
            untouched[cid] = hashlib.md5(fp.read_bytes()).hexdigest()

    # ---- xiaoer ----
    xe = make_xiaoer_sheet()
    assert xe.size == (1152, 64)
    oob, samples = count_oob(xe)
    total_oob += oob
    (OUT / "xiaoer.png").write_bytes(b"")  # touch
    xe.save(OUT / "xiaoer.png")
    preview_scale(xe, PREV / "64_xiaoer_x2.png", 2)
    for name, idx in [("idle", 0), ("serve", 8), ("wipe", 11), ("walk", 2), ("hurt", 13), ("parry", 15)]:
        fr = crop_frame(xe, idx)
        preview_scale(fr, PREV / f"64_xiaoer_{name}_x2.png", 2)
        preview_scale(fr, PREV / f"64_xiaoer_{name}_x3.png", 3)
    make_xiaoer_compare(xe)
    report.append("## xiaoer")
    report.append(f"path: {OUT / 'xiaoer.png'}")
    report.append(f"size: {xe.size}")
    report.append(f"oob: {oob}")
    if samples:
        report.append(f"oob_samples: {samples}")
    report.append(f"palette_used ({len(colors_used(xe))}): {', '.join(colors_used(xe))}")
    labels = [
        "idle0", "idle1", "walk0", "walk1", "walk2", "walk3",
        "serve0", "serve1", "serve2",
        "wipe0", "wipe1", "wipe2", "wipe3",
        "hurt0", "hurt1", "parry0", "parry1", "parry2",
    ]
    for i, lab in enumerate(labels):
        vp = visible_pixels(xe, i)
        report.append(f"  {i:02d} {lab}: visible={vp}{' EMPTY!' if vp == 0 else ''}")
    report.append("")
    print(f"xiaoer: {xe.size} oob={oob}")

    # ---- guest_sit ----
    gs = make_guest_sit_sheet()
    assert gs.size == (384, 64)
    oob, samples = count_oob(gs)
    total_oob += oob
    gs.save(OUT / "guest_sit.png")
    preview_scale(gs, PREV / "64_guest_sit_x2.png", 2)
    preview_scale(gs, PREV / "64_guest_sit_x3.png", 3)
    report.append("## guest_sit")
    report.append(f"path: {OUT / 'guest_sit.png'}")
    report.append(f"size: {gs.size}")
    report.append(f"oob: {oob}")
    if samples:
        report.append(f"oob_samples: {samples}")
    for i in range(6):
        report.append(f"  {i}: visible={visible_pixels(gs, i)} hat={GUEST_VARIANTS[i][4]}")
    report.append("")
    print(f"guest_sit: {gs.size} oob={oob}")

    # ---- guest_walk ----
    gw = make_guest_walk_sheet()
    assert gw.size == (3072, 64), gw.size
    oob, samples = count_oob(gw)
    total_oob += oob
    gw.save(OUT / "guest_walk.png")
    # full sheet preview at x1 paper (already large); also x2 would be huge — save compact strip of guest0
    preview_scale(gw, PREV / "64_guest_walk_x1.png", 1)
    # sample strip: guest0 all 8 + guest1 walk0 + sit frames of each
    sample = Image.new("RGBA", (10 * FS, FS), TRANS)
    # guest0 frames 0..7
    for i in range(8):
        sample.paste(crop_frame(gw, i), (i * FS, 0))
    # guest5 walk0 + sit7
    sample.paste(crop_frame(gw, 5 * 8 + 0), (8 * FS, 0))
    sample.paste(crop_frame(gw, 5 * 8 + 7), (9 * FS, 0))
    preview_scale(sample, PREV / "64_guest_walk_x2.png", 2)
    report.append("## guest_walk")
    report.append(f"path: {OUT / 'guest_walk.png'}")
    report.append(f"size: {gw.size}")
    report.append(f"oob: {oob}")
    if samples:
        report.append(f"oob_samples: {samples}")
    report.append("formula: absIndex = guestIndex * 8 + localFrame; FRAME=64")
    empty = []
    for gi in range(6):
        for ph in range(8):
            ai = gi * 8 + ph
            vp = visible_pixels(gw, ai)
            if vp == 0:
                empty.append(ai)
        report.append(f"  guest{gi} ({GUEST_VARIANTS[gi][4]}): walk0={visible_pixels(gw, gi*8)} sit7={visible_pixels(gw, gi*8+7)}")
    if empty:
        report.append(f"EMPTY frames: {empty}")
    report.append("")
    print(f"guest_walk: {gw.size} oob={oob}")

    for cid, h in untouched.items():
        now = hashlib.md5((OUT / f"{cid}.png").read_bytes()).hexdigest()
        assert now == h, f"FORBIDDEN overwrite of {cid}"
        report.append(f"untouched_ok: {cid} md5={h}")

    report.append(f"TOTAL_OOB={total_oob}")
    (OUT / "_gen_report_v13.txt").write_text("\n".join(report) + "\n", encoding="utf-8")
    write_readme()
    print(f"TOTAL_OOB={total_oob}")
    if total_oob != 0:
        raise SystemExit(f"palette oob={total_oob}")
    print("OK")


if __name__ == "__main__":
    main()
