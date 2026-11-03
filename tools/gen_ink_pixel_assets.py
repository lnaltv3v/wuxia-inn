#!/usr/bin/env python3
"""Generate Ink-Pixel Inn assets v1.1: denser sprites + hub + guests + wipe frames.

Re-runnable. Overwrites formal paths under assets/sprites/ and assets/scenes/.
Palette-locked hard-edge pixel art only (no AA, no OOB colors).
"""
from __future__ import annotations

from pathlib import Path
from PIL import Image

ROOT = Path("/workspace/wuxia-inn")
SPRITES = ROOT / "assets" / "sprites"
SCENES = ROOT / "assets" / "scenes"
PREVIEW = ROOT / "assets" / "_preview"

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


def new_frame(w=32, h=32):
    return Image.new("RGBA", (w, h), TRANS)


def px(img, x, y, c):
    if 0 <= x < img.width and 0 <= y < img.height and c[3] > 0:
        img.putpixel((x, y), c)


def fill_rect(img, x0, y0, x1, y1, c):
    for y in range(y0, y1):
        for x in range(x0, x1):
            px(img, x, y, c)


def hline(img, x0, x1, y, c):
    for x in range(x0, x1):
        px(img, x, y, c)


def vline(img, x, y0, y1, c):
    for y in range(y0, y1):
        px(img, x, y, c)


def outline_rect(img, x0, y0, x1, y1, c):
    hline(img, x0, x1, y0, c)
    hline(img, x0, x1, y1 - 1, c)
    vline(img, x0, y0, y1, c)
    vline(img, x1 - 1, y0, y1, c)


def draw_head(img, cx, cy, hair=INK, face=SKIN, eye=INK, hair_side=None,
              topknot=False, bun=False, bald_cap=False, fringe=False, hat_wood=False):
    """3/4 head facing right — silhouette variants for v1.1 readability."""
    if bald_cap:
        fill_rect(img, cx - 4, cy, cx + 4, cy + 3, PAPER_L)
        fill_rect(img, cx - 5, cy + 1, cx + 5, cy + 3, PAPER_L)
        fill_rect(img, cx - 4, cy + 3, cx + 4, cy + 8, face)
        hline(img, cx - 4, cx + 4, cy, INK)
    elif hat_wood:
        fill_rect(img, cx - 5, cy - 1, cx + 5, cy + 2, WOOD)
        fill_rect(img, cx - 4, cy - 2, cx + 4, cy, WOOD_L)
        px(img, cx, cy - 3, GOLD)
        fill_rect(img, cx - 4, cy + 2, cx + 4, cy + 8, face)
        px(img, cx - 4, cy + 2, hair)
        px(img, cx + 3, cy + 2, hair)
    else:
        fill_rect(img, cx - 4, cy, cx + 4, cy + 3, hair)
        fill_rect(img, cx - 5, cy + 1, cx + 5, cy + 3, hair)
        if topknot:
            fill_rect(img, cx - 1, cy - 3, cx + 2, cy, hair)
            px(img, cx, cy - 4, GOLD)
            px(img, cx + 1, cy - 2, GOLD)
        if bun:
            fill_rect(img, cx + 2, cy - 1, cx + 6, cy + 3, hair)
            px(img, cx + 5, cy, GOLD)
        if fringe:
            hline(img, cx - 3, cx + 3, cy + 3, hair)
            px(img, cx - 2, cy + 4, hair)
            px(img, cx + 1, cy + 4, hair)
        fill_rect(img, cx - 4, cy + 3, cx + 4, cy + 8, face)
        if hair_side:
            fill_rect(img, cx - 5, cy + 3, cx - 3, cy + 8, hair_side)
            fill_rect(img, cx + 3, cy + 3, cx + 5, cy + 7, hair_side)
        else:
            px(img, cx - 4, cy + 3, hair)
            px(img, cx + 3, cy + 3, hair)
    # eyes
    px(img, cx - 2, cy + 5, eye)
    px(img, cx + 1, cy + 5, eye)
    px(img, cx + 3, cy + 6, SKIN_D if face in (SKIN, SKIN_D) else face)
    hline(img, cx - 4, cx + 4, cy if not hat_wood else cy + 2, INK)
    vline(img, cx - 5, cy + 1, cy + 8, INK)
    vline(img, cx + 4, cy + 1, cy + 8, INK)


def draw_feet(img, lx, ly, rx, ry, shoe=INK_SOFT, lift_l=0, lift_r=0, stride=0):
    """Shoes with stronger stride / lift for v1.1 walk readability."""
    lxo = lx - (2 if lift_l else 0) + (stride if lift_l else -stride // 2)
    rxo = rx + (2 if lift_r else 0) + (stride if lift_r else -stride // 2 if lift_l else 0)
    fill_rect(img, lxo, ly - lift_l, lxo + 5, ly - lift_l + 3, shoe)
    fill_rect(img, rxo, ry - lift_r, rxo + 5, ry - lift_r + 3, shoe)
    hline(img, lxo, lxo + 5, ly - lift_l + 2, INK)
    hline(img, rxo, rxo + 5, ry - lift_r + 2, INK)
    if lift_l >= 4:
        px(img, lxo + 4, ly - lift_l, CREAM if shoe != CREAM else GOLD)
        px(img, lxo + 5, ly - lift_l + 1, shoe)
    if lift_r >= 4:
        px(img, rxo + 4, ry - lift_r, CREAM if shoe != CREAM else GOLD)
        px(img, rxo + 5, ry - lift_r + 1, shoe)


def body_shift(pose):
    if pose.get("hurt"):
        return -4
    if pose.get("wipe_phase") is not None:
        return 1 if pose.get("wipe_phase", 0) % 2 else 0
    if pose.get("attack_phase") == 0:
        return -3
    if pose.get("attack_phase") in (1, 2):
        return 3
    if pose.get("attack_phase") == 3:
        return 1
    if pose.get("lift_l"):
        return -2
    if pose.get("lift_r"):
        return 2
    return 0


def draw_robe_folds(img, x0, x1, y, c=NIGHT):
    hline(img, x0, x1, y, c)
    hline(img, x0 + 1, x1 - 1, y + 3, c)


def draw_belt(img, x0, x1, y, main=WOOD_L, buckle=GOLD):
    fill_rect(img, x0, y, x1, y + 2, main)
    px(img, (x0 + x1) // 2, y, buckle)


# ---------- characters ----------

def qingyi_body(img, ox, oy, pose):
    breath = pose.get("breath", 0)
    bx = ox + body_shift(pose)
    head_y = 1 + breath
    draw_head(img, 13 + bx, head_y + oy, hair=INK, face=SKIN, topknot=True)
    fill_rect(img, 11 + bx, 8 + breath + oy, 15 + bx, 10 + breath + oy, SKIN)
    ty = 9 + breath + oy
    # teal robe + collar + folds + sash
    fill_rect(img, 8 + bx, ty, 18 + bx, ty + 12, TEAL)
    fill_rect(img, 11 + bx, ty, 15 + bx, ty + 2, PAPER_L)
    fill_rect(img, 9 + bx, ty + 1, 11 + bx, ty + 3, TEAL_B)  # lapel
    draw_robe_folds(img, 8 + bx, 18 + bx, ty + 4, NIGHT)
    draw_belt(img, 8 + bx, 18 + bx, ty + 7, WOOD_L, GOLD)
    vline(img, 12 + bx, ty + 2, ty + 12, NIGHT)  # front slit hint

    lift_l = pose.get("lift_l", 0)
    lift_r = pose.get("lift_r", 0)

    if pose.get("parry"):
        shake = pose.get("shake", 0)
        fill_rect(img, 4 + bx, ty + 1, 9 + bx, ty + 7, TEAL)
        fill_rect(img, 3 + bx, ty - 1, 7 + bx, ty + 3, SKIN)
        # sword vertical guard in front
        fill_rect(img, 16 + bx + shake, ty - 7, 18 + bx + shake, ty + 10, TEAL_B)
        fill_rect(img, 15 + bx + shake, ty - 8, 19 + bx + shake, ty - 5, GOLD)
        fill_rect(img, 16 + bx + shake, ty + 10, 18 + bx + shake, ty + 13, WOOD)
        px(img, 17 + bx + shake, ty - 4, CREAM)
        if shake:
            px(img, 19 + bx, ty - 3, CREAM)
            px(img, 20 + bx, ty - 1, GOLD)
    elif pose.get("tray"):
        phase = pose.get("serve_phase", 1)
        fill_rect(img, 17 + bx, ty + 2, 23 + bx, ty + 5, TEAL)
        fill_rect(img, 21 + bx, ty + 3, 25 + bx, ty + 6, SKIN)
        ty_off = -1 if phase == 0 else (1 if phase == 2 else 0)
        # tray
        fill_rect(img, 18 + bx, ty + 1 + ty_off, 30 + bx, ty + 3 + ty_off, WOOD)
        hline(img, 18 + bx, 30 + bx, ty + 1 + ty_off, INK)
        hline(img, 18 + bx, 30 + bx, ty + 3 + ty_off, INK_SOFT)
        # pot
        fill_rect(img, 19 + bx, ty - 2 + ty_off, 23 + bx, ty + 1 + ty_off, CINN_B)
        fill_rect(img, 20 + bx, ty - 3 + ty_off, 22 + bx, ty - 2 + ty_off, GOLD)
        px(img, 23 + bx, ty - 1 + ty_off, WOOD)
        # cups
        fill_rect(img, 25 + bx, ty - 1 + ty_off, 27 + bx, ty + 1 + ty_off, CREAM)
        outline_rect(img, 25 + bx, ty - 1 + ty_off, 27 + bx, ty + 1 + ty_off, INK)
        fill_rect(img, 28 + bx, ty - 1 + ty_off, 30 + bx, ty + 1 + ty_off, PAPER_L)
        if phase == 2:
            px(img, 23 + bx, ty + 2, LOESS)
            px(img, 24 + bx, ty + 3, LOESS)
        # sheathed sword on hip
        fill_rect(img, 18 + bx, ty + 8, 20 + bx, ty + 18, TEAL_B)
        px(img, 18 + bx, ty + 7, GOLD)
    elif pose.get("attack_phase") is not None:
        ap = pose["attack_phase"]
        if ap == 0:  # wind-up: sword pulled far back
            fill_rect(img, 1 + bx, ty + 2, 8 + bx, ty + 7, TEAL)
            fill_rect(img, 0 + bx, ty + 5, 4 + bx, ty + 8, SKIN)
            fill_rect(img, bx - 1, ty + 0, bx + 2, ty + 18, TEAL_B)
            fill_rect(img, bx - 1, ty - 1, bx + 3, ty + 1, GOLD)
            px(img, bx, ty + 17, WOOD)
        elif ap == 1:  # swing out long
            fill_rect(img, 16 + bx, ty + 1, 23 + bx, ty + 5, TEAL)
            fill_rect(img, 21 + bx, ty + 2, 25 + bx, ty + 5, SKIN)
            fill_rect(img, bx + 19, ty - 1, bx + 32, ty + 1, TEAL_B)
            fill_rect(img, bx + 18, ty - 1, bx + 21, ty + 2, GOLD)
            px(img, bx + 31, ty - 1, CREAM)
            px(img, bx + 30, ty - 2, GOLD)
        elif ap == 2:  # impact tip high
            fill_rect(img, 17 + bx, ty + 2, 25 + bx, ty + 6, TEAL)
            fill_rect(img, 23 + bx, ty + 3, 27 + bx, ty + 6, SKIN)
            fill_rect(img, bx + 22, ty + 0, bx + 32, ty + 2, TEAL_B)
            fill_rect(img, bx + 21, ty - 1, bx + 24, ty + 3, GOLD)
            px(img, bx + 31, ty - 1, CREAM)
            px(img, bx + 30, ty, CREAM)
            px(img, bx + 29, ty - 2, GOLD)
        else:  # recover
            fill_rect(img, 15 + bx, ty + 3, 21 + bx, ty + 8, TEAL)
            fill_rect(img, 18 + bx, ty + 6, 22 + bx, ty + 9, SKIN)
            fill_rect(img, bx + 19, ty + 2, bx + 21, ty + 15, TEAL_B)
            fill_rect(img, bx + 18, ty + 1, bx + 22, ty + 3, GOLD)
    else:
        # idle / walk arms
        fill_rect(img, 4 + bx, ty + 2, 9 + bx, ty + 8, TEAL)
        fill_rect(img, 3 + bx, ty + 6, 7 + bx, ty + 9, SKIN)
        if lift_r:
            fill_rect(img, 16 + bx, ty + 0, 21 + bx, ty + 5, TEAL)
            fill_rect(img, 19 + bx, ty + 3, 23 + bx, ty + 6, SKIN)
        elif lift_l:
            fill_rect(img, 16 + bx, ty + 4, 20 + bx, ty + 10, TEAL)
            fill_rect(img, 18 + bx, ty + 8, 22 + bx, ty + 11, SKIN)
        else:
            fill_rect(img, 16 + bx, ty + 2, 20 + bx, ty + 7, TEAL)
            fill_rect(img, 18 + bx, ty + 5, 21 + bx, ty + 8, SKIN)
        fill_rect(img, 18 + bx, ty + 1, 20 + bx, ty + 16, TEAL_B)
        fill_rect(img, 17 + bx, ty + 14, 21 + bx, ty + 16, WOOD)
        fill_rect(img, 17 + bx, ty, 21 + bx, ty + 2, GOLD)

    ly = ty + 12
    fill_rect(img, 9 + bx - (2 if lift_l else 0), ly - lift_l, 13 + bx - (2 if lift_l else 0), ly + 6 - lift_l, TEAL)
    fill_rect(img, 13 + bx + (2 if lift_r else 0), ly - lift_r, 17 + bx + (2 if lift_r else 0), ly + 6 - lift_r, TEAL)
    if lift_l:
        hline(img, 9 + bx - 2, 13 + bx - 2, ly - lift_l + 2, NIGHT)
    if lift_r:
        hline(img, 13 + bx + 2, 17 + bx + 2, ly - lift_r + 2, NIGHT)
    stride = 2 if (lift_l or lift_r) else 0
    draw_feet(img, 8 + bx, ly + 6, 14 + bx, ly + 6, INK_SOFT, lift_l, lift_r, stride=stride)

    if pose.get("hurt"):
        # reeling: arm flung, blood spray
        fill_rect(img, 18 + bx, ty + 1, 24 + bx, ty + 5, TEAL)
        fill_rect(img, 22 + bx, ty + 2, 26 + bx, ty + 5, SKIN)
        px(img, 16 + bx, 6 + oy, BLOOD)
        px(img, 18 + bx, 8 + oy, CINN)
        px(img, 10 + bx, 11 + oy, BLOOD)
        px(img, 19 + bx, 10 + oy, BLOOD)


def tiezhang_body(img, ox, oy, pose):
    breath = pose.get("breath", 0)
    bx = ox + body_shift(pose)
    head_y = 1 + breath
    draw_head(img, 13 + bx, head_y + oy, hair=INK, face=SKIN, hair_side=INK, bun=True)
    fill_rect(img, 11 + bx, head_y + oy, 15 + bx, head_y + 2 + oy, CINN)  # hairpin band
    px(img, 16 + bx, head_y + 1 + oy, GOLD)
    fill_rect(img, 11 + bx, 8 + breath + oy, 15 + bx, 10 + breath + oy, SKIN)
    ty = 9 + breath + oy
    fill_rect(img, 8 + bx, ty, 18 + bx, ty + 12, ROBE_R)
    fill_rect(img, 10 + bx, ty, 16 + bx, ty + 2, PAPER_L)
    draw_robe_folds(img, 8 + bx, 18 + bx, ty + 4, BLOOD)
    draw_belt(img, 8 + bx, 18 + bx, ty + 7, BLOOD, GOLD)
    # medicine pouch
    fill_rect(img, 17 + bx, ty + 6, 22 + bx, ty + 12, JADE_B)
    outline_rect(img, 17 + bx, ty + 6, 22 + bx, ty + 12, INK)
    px(img, 19 + bx, ty + 8, GOLD)
    px(img, 20 + bx, ty + 10, JADE)

    lift_l = pose.get("lift_l", 0)
    lift_r = pose.get("lift_r", 0)

    if pose.get("tray"):
        phase = pose.get("serve_phase", 1)
        fill_rect(img, 17 + bx, ty + 2, 23 + bx, ty + 5, ROBE_R)
        fill_rect(img, 21 + bx, ty + 3, 25 + bx, ty + 6, SKIN)
        ty_off = -1 if phase == 0 else (1 if phase == 2 else 0)
        fill_rect(img, 18 + bx, ty + 1 + ty_off, 30 + bx, ty + 3 + ty_off, WOOD)
        hline(img, 18 + bx, 30 + bx, ty + 1 + ty_off, INK)
        fill_rect(img, 20 + bx, ty - 2 + ty_off, 24 + bx, ty + 1 + ty_off, JADE_B)
        fill_rect(img, 21 + bx, ty - 3 + ty_off, 23 + bx, ty - 2 + ty_off, GOLD)
        fill_rect(img, 26 + bx, ty - 1 + ty_off, 28 + bx, ty + 1 + ty_off, CREAM)
        outline_rect(img, 26 + bx, ty - 1 + ty_off, 28 + bx, ty + 1 + ty_off, INK)
        if phase == 2:
            px(img, 24 + bx, ty + 2, JADE)
            px(img, 25 + bx, ty + 3, JADE_B)
    elif pose.get("parry"):
        shake = pose.get("shake", 0)
        fill_rect(img, 15 + bx, ty - 3, 22 + bx, ty + 4, ROBE_R)
        fill_rect(img, 17 + bx + shake, ty - 6, 25 + bx + shake, ty + 1, SKIN)
        # glowing palm
        fill_rect(img, 22 + bx + shake, ty - 7, 26 + bx + shake, ty - 3, JADE_B)
        px(img, 24 + bx + shake, ty - 8, CREAM)
        px(img, 25 + bx + shake, ty - 5, JADE)
        if shake:
            px(img, 27 + bx, ty - 6, CREAM)
    elif pose.get("attack_phase") is not None:
        ap = pose["attack_phase"]
        if ap == 0:
            fill_rect(img, 1 + bx, ty + 1, 8 + bx, ty + 6, ROBE_R)
            fill_rect(img, 0 + bx, ty + 3, 4 + bx, ty + 7, SKIN)
            px(img, 1 + bx, ty + 2, JADE_B)
        elif ap == 1:
            fill_rect(img, 16 + bx, ty + 0, 24 + bx, ty + 5, ROBE_R)
            fill_rect(img, 21 + bx, ty + 1, 28 + bx, ty + 5, SKIN)
            px(img, 27 + bx, ty, JADE_B)
        elif ap == 2:
            fill_rect(img, 17 + bx, ty + 1, 26 + bx, ty + 6, ROBE_R)
            fill_rect(img, 23 + bx, ty + 2, 31 + bx, ty + 6, SKIN)
            px(img, 29 + bx, ty + 1, JADE_B)
            px(img, 30 + bx, ty + 3, GOLD)
            px(img, 31 + bx, ty + 2, CREAM)
            px(img, 28 + bx, ty, CREAM)
        else:
            fill_rect(img, 15 + bx, ty + 3, 22 + bx, ty + 8, ROBE_R)
            fill_rect(img, 18 + bx, ty + 5, 23 + bx, ty + 9, SKIN)
    else:
        fill_rect(img, 3 + bx, ty + 2, 8 + bx, ty + 8, ROBE_R)
        fill_rect(img, 2 + bx, ty + 6, 6 + bx, ty + 9, SKIN)
        if lift_r:
            fill_rect(img, 16 + bx, ty + 0, 21 + bx, ty + 5, ROBE_R)
            fill_rect(img, 19 + bx, ty + 3, 22 + bx, ty + 6, SKIN)
        elif lift_l:
            fill_rect(img, 16 + bx, ty + 4, 20 + bx, ty + 9, ROBE_R)
        else:
            fill_rect(img, 15 + bx, ty + 2, 19 + bx, ty + 6, ROBE_R)

    ly = ty + 12
    fill_rect(img, 9 + bx - (2 if lift_l else 0), ly - lift_l, 13 + bx - (2 if lift_l else 0), ly + 6 - lift_l, ROBE_R)
    fill_rect(img, 13 + bx + (2 if lift_r else 0), ly - lift_r, 17 + bx + (2 if lift_r else 0), ly + 6 - lift_r, ROBE_R)
    if lift_l:
        hline(img, 9 + bx - 2, 13 + bx - 2, ly - lift_l + 2, BLOOD)
    if lift_r:
        hline(img, 13 + bx + 2, 17 + bx + 2, ly - lift_r + 2, BLOOD)
    draw_feet(img, 8 + bx, ly + 6, 14 + bx, ly + 6, INK_SOFT, lift_l, lift_r,
              stride=2 if (lift_l or lift_r) else 0)
    if pose.get("hurt"):
        fill_rect(img, 18 + bx, ty + 1, 24 + bx, ty + 5, ROBE_R)
        px(img, 15 + bx, 6 + oy, BLOOD)
        px(img, 9 + bx, 10 + oy, CINN)
        px(img, 17 + bx, 9 + oy, BLOOD)


def langren_body(img, ox, oy, pose):
    breath = pose.get("breath", 0)
    bx = ox + body_shift(pose)
    head_y = 1 + breath
    draw_head(img, 13 + bx, head_y + oy, hair=INK, face=SKIN_D, fringe=True)
    # headband
    fill_rect(img, 8 + bx, head_y + 2 + oy, 18 + bx, head_y + 4 + oy, CINN_B)
    px(img, 18 + bx, head_y + 3 + oy, CINN)
    fill_rect(img, 11 + bx, 8 + breath + oy, 15 + bx, 10 + breath + oy, SKIN_D)
    ty = 9 + breath + oy
    fill_rect(img, 8 + bx, ty, 18 + bx, ty + 12, INK_SOFT)
    fill_rect(img, 9 + bx, ty + 1, 17 + bx, ty + 5, WOOD)  # chest plate
    fill_rect(img, 10 + bx, ty + 2, 16 + bx, ty + 4, WOOD_L)
    draw_robe_folds(img, 8 + bx, 18 + bx, ty + 6, NIGHT)
    draw_belt(img, 8 + bx, 18 + bx, ty + 8, FRAME, CINN_B)

    lift_l = pose.get("lift_l", 0)
    lift_r = pose.get("lift_r", 0)

    if pose.get("tray"):
        phase = pose.get("serve_phase", 1)
        fill_rect(img, 17 + bx, ty + 2, 23 + bx, ty + 5, INK_SOFT)
        fill_rect(img, 21 + bx, ty + 3, 25 + bx, ty + 6, SKIN_D)
        ty_off = -1 if phase == 0 else (1 if phase == 2 else 0)
        fill_rect(img, 18 + bx, ty + 1 + ty_off, 30 + bx, ty + 3 + ty_off, WOOD)
        hline(img, 18 + bx, 30 + bx, ty + 1 + ty_off, INK)
        fill_rect(img, 20 + bx, ty - 2 + ty_off, 23 + bx, ty + 1 + ty_off, CREAM)
        fill_rect(img, 25 + bx, ty - 1 + ty_off, 28 + bx, ty + 1 + ty_off, CINN)
        # blade on back/hip
        fill_rect(img, 4 + bx, ty + 3, 7 + bx, ty + 17, INK)
        px(img, 5 + bx, ty + 2, CINN_B)
    elif pose.get("parry"):
        shake = pose.get("shake", 0)
        fill_rect(img, 14 + bx, ty - 3, 19 + bx, ty + 4, INK_SOFT)
        fill_rect(img, 16 + bx + shake, ty - 8, 22 + bx + shake, ty + 10, INK_SOFT)
        fill_rect(img, 17 + bx + shake, ty - 7, 21 + bx + shake, ty + 8, MIST)
        fill_rect(img, 16 + bx + shake, ty + 10, 22 + bx + shake, ty + 13, WOOD)
        px(img, 18 + bx + shake, ty - 9, CINN_B)
        if shake:
            px(img, 23 + bx, ty - 5, CREAM)
            px(img, 24 + bx, ty - 3, GOLD)
    elif pose.get("attack_phase") is not None:
        ap = pose["attack_phase"]
        if ap == 0:
            fill_rect(img, 1 + bx, ty + 2, 8 + bx, ty + 7, INK_SOFT)
            fill_rect(img, bx - 1, ty + 0, bx + 3, ty + 17, INK_SOFT)
            fill_rect(img, bx + 0, ty + 1, bx + 2, ty + 15, MIST)
            fill_rect(img, bx - 1, ty + 17, bx + 3, ty + 19, WOOD)
            px(img, bx, ty - 1, CINN_B)
        elif ap == 1:
            fill_rect(img, 16 + bx, ty + 1, 23 + bx, ty + 5, INK_SOFT)
            fill_rect(img, 19 + bx, ty - 1, 32, ty + 2, INK_SOFT)
            fill_rect(img, 20 + bx, ty + 0, 31, ty + 1, MIST)
            fill_rect(img, 18 + bx, ty - 1, 21 + bx, ty + 3, WOOD)
            px(img, 31, ty - 1, CREAM)
        elif ap == 2:
            fill_rect(img, 17 + bx, ty + 2, 24 + bx, ty + 6, INK_SOFT)
            fill_rect(img, 20 + bx, ty + 0, 32, ty + 3, INK_SOFT)
            fill_rect(img, 21 + bx, ty + 1, 31, ty + 2, CINN_B)
            px(img, 30, ty - 1, CREAM)
            px(img, 31, ty, GOLD)
            px(img, 29, ty - 1, CINN)
        else:
            fill_rect(img, 15 + bx, ty + 3, 21 + bx, ty + 8, INK_SOFT)
            fill_rect(img, 18 + bx, ty + 3, 21 + bx, ty + 17, INK_SOFT)
            fill_rect(img, 19 + bx, ty + 4, 20 + bx, ty + 15, MIST)
    else:
        fill_rect(img, 3 + bx, ty + 2, 8 + bx, ty + 8, INK_SOFT)
        fill_rect(img, 2 + bx, ty + 6, 6 + bx, ty + 9, SKIN_D)
        fill_rect(img, 18 + bx, ty + 1, 22 + bx, ty + 16, INK_SOFT)
        fill_rect(img, 19 + bx, ty + 2, 21 + bx, ty + 14, MIST)
        fill_rect(img, 18 + bx, ty + 16, 22 + bx, ty + 18, WOOD)
        px(img, 19 + bx, ty, CINN_B)
        if lift_r:
            fill_rect(img, 16 + bx, ty + 0, 20 + bx, ty + 5, INK_SOFT)
        elif lift_l:
            fill_rect(img, 16 + bx, ty + 4, 19 + bx, ty + 9, INK_SOFT)

    ly = ty + 12
    fill_rect(img, 9 + bx - (2 if lift_l else 0), ly - lift_l, 13 + bx - (2 if lift_l else 0), ly + 6 - lift_l, INK_SOFT)
    fill_rect(img, 13 + bx + (2 if lift_r else 0), ly - lift_r, 17 + bx + (2 if lift_r else 0), ly + 6 - lift_r, INK_SOFT)
    draw_feet(img, 8 + bx, ly + 6, 14 + bx, ly + 6, INK, lift_l, lift_r,
              stride=2 if (lift_l or lift_r) else 0)
    if pose.get("hurt"):
        fill_rect(img, 18 + bx, ty + 0, 24 + bx, ty + 4, INK_SOFT)
        px(img, 14 + bx, 5 + oy, BLOOD)
        px(img, 16 + bx, 7 + oy, CINN_B)
        px(img, 11 + bx, 12 + oy, BLOOD)
        px(img, 19 + bx, 9 + oy, BLOOD)


def qinshi_body(img, ox, oy, pose):
    breath = pose.get("breath", 0)
    bx = ox + body_shift(pose)
    head_y = 1 + breath
    draw_head(img, 13 + bx, head_y + oy, hair=PAPER_L, face=SKIN, hair_side=PAPER_L, bald_cap=True)
    # violet forehead jewel
    px(img, 12 + bx, head_y + 4 + oy, VIOLET)
    px(img, 13 + bx, head_y + 4 + oy, VIOLET)
    px(img, 14 + bx, head_y + 4 + oy, GOLD)
    fill_rect(img, 11 + bx, 8 + breath + oy, 15 + bx, 10 + breath + oy, SKIN)
    ty = 9 + breath + oy
    fill_rect(img, 8 + bx, ty, 18 + bx, ty + 6, VIOLET)
    fill_rect(img, 7 + bx, ty + 6, 19 + bx, ty + 13, PAPER_L)
    fill_rect(img, 10 + bx, ty, 16 + bx, ty + 2, PAPER_L)
    draw_robe_folds(img, 7 + bx, 19 + bx, ty + 8, PAPER_D)
    draw_belt(img, 8 + bx, 18 + bx, ty + 5, GOLD, CREAM)
    # long sleeve drape idle hint
    fill_rect(img, 6 + bx, ty + 3, 8 + bx, ty + 10, VIOLET)

    lift_l = pose.get("lift_l", 0)
    lift_r = pose.get("lift_r", 0)

    if pose.get("tray") or pose.get("hold"):
        phase = pose.get("serve_phase", 1)
        fill_rect(img, 16 + bx, ty + 3, 22 + bx, ty + 7, VIOLET)
        fill_rect(img, 20 + bx, ty + 4, 24 + bx, ty + 7, SKIN)
        yoff = -1 if phase == 0 else (1 if phase == 2 else 0)
        # guqin body
        fill_rect(img, 16 + bx, ty + 2 + yoff, 31 + bx, ty + 5 + yoff, WOOD)
        hline(img, 17 + bx, 30 + bx, ty + 3 + yoff, WOOD_L)
        px(img, 18 + bx, ty + 2 + yoff, GOLD)
        px(img, 29 + bx, ty + 2 + yoff, GOLD)
        hline(img, 18 + bx, 29 + bx, ty + 3 + yoff, INK)
        hline(img, 18 + bx, 29 + bx, ty + 4 + yoff, INK_SOFT)
        if phase == 2:
            px(img, 24 + bx, ty + 1, CREAM)
            px(img, 25 + bx, ty + 1, SKIN)
    elif pose.get("parry"):
        shake = pose.get("shake", 0)
        fill_rect(img, 14 + bx, ty - 2, 19 + bx, ty + 4, VIOLET)
        # fly-whisk / dust staff vertical
        fill_rect(img, 16 + bx + shake, ty - 8, 18 + bx + shake, ty + 8, WOOD)
        fill_rect(img, 14 + bx + shake, ty - 10, 20 + bx + shake, ty - 5, PAPER_L)
        px(img, 15 + bx + shake, ty - 9, CREAM)
        px(img, 19 + bx + shake, ty - 9, CREAM)
        if shake:
            px(img, 21 + bx, ty - 7, GOLD)
            px(img, 22 + bx, ty - 5, CREAM)
    elif pose.get("attack_phase") is not None:
        ap = pose["attack_phase"]
        if ap == 0:
            fill_rect(img, 1 + bx, ty + 2, 8 + bx, ty + 7, VIOLET)
            fill_rect(img, 0 + bx, ty + 0, 4 + bx, ty + 15, WOOD)
            fill_rect(img, bx - 1, ty - 1, bx + 5, ty + 1, PAPER_L)
        elif ap == 1:
            fill_rect(img, 16 + bx, ty + 1, 23 + bx, ty + 5, VIOLET)
            fill_rect(img, 19 + bx, ty - 1, 32, ty + 1, WOOD)
            fill_rect(img, 28, ty - 2, 32, ty, PAPER_L)
            px(img, 31, ty - 2, CREAM)
        elif ap == 2:
            fill_rect(img, 17 + bx, ty + 2, 24 + bx, ty + 6, VIOLET)
            fill_rect(img, 20 + bx, ty + 0, 32, ty + 2, WOOD)
            px(img, 30, ty - 1, GOLD)
            px(img, 31, ty, CREAM)
            px(img, 29, ty - 2, CREAM)
        else:
            fill_rect(img, 15 + bx, ty + 3, 21 + bx, ty + 8, VIOLET)
            fill_rect(img, 17 + bx, ty + 3, 20 + bx, ty + 15, WOOD)
    else:
        fill_rect(img, 3 + bx, ty + 2, 8 + bx, ty + 8, VIOLET)
        fill_rect(img, 2 + bx, ty + 6, 6 + bx, ty + 9, SKIN)
        fill_rect(img, 18 + bx, ty + 4, 21 + bx, ty + 15, WOOD)
        hline(img, 18 + bx, 21 + bx, ty + 6, WOOD_L)
        px(img, 19 + bx, ty + 4, GOLD)
        if lift_r:
            fill_rect(img, 16 + bx, ty + 0, 20 + bx, ty + 5, VIOLET)
        elif lift_l:
            fill_rect(img, 16 + bx, ty + 4, 19 + bx, ty + 9, VIOLET)

    ly = ty + 13
    fill_rect(img, 9 + bx - (2 if lift_l else 0), ly - lift_l, 13 + bx - (2 if lift_l else 0), ly + 5 - lift_l, PAPER_L)
    fill_rect(img, 13 + bx + (2 if lift_r else 0), ly - lift_r, 17 + bx + (2 if lift_r else 0), ly + 5 - lift_r, PAPER_L)
    draw_feet(img, 8 + bx, ly + 5, 14 + bx, ly + 5, INK_SOFT, lift_l, lift_r,
              stride=2 if (lift_l or lift_r) else 0)
    if pose.get("hurt"):
        fill_rect(img, 18 + bx, ty + 1, 24 + bx, ty + 5, VIOLET)
        px(img, 15 + bx, 6 + oy, BLOOD)
        px(img, 10 + bx, 10 + oy, CINN)
        px(img, 18 + bx, 9 + oy, BLOOD)


def xiaoer_body(img, ox, oy, pose):
    breath = pose.get("breath", 0)
    bx = ox + body_shift(pose)
    head_y = 1 + breath
    draw_head(img, 13 + bx, head_y + oy, hair=INK, face=SKIN, hat_wood=True)
    fill_rect(img, 11 + bx, 8 + breath + oy, 15 + bx, 10 + breath + oy, SKIN)
    ty = 9 + breath + oy
    # brown tunic + paper apron + cinnabar sash
    fill_rect(img, 8 + bx, ty, 18 + bx, ty + 11, WOOD)
    fill_rect(img, 9 + bx, ty + 4, 17 + bx, ty + 13, PAPER)
    fill_rect(img, 10 + bx, ty + 5, 16 + bx, ty + 12, PAPER_L)
    draw_robe_folds(img, 9 + bx, 17 + bx, ty + 7, PAPER_D)
    draw_belt(img, 8 + bx, 18 + bx, ty + 3, CINN, GOLD)
    # apron strings
    px(img, 9 + bx, ty + 4, CINN)
    px(img, 16 + bx, ty + 4, CINN)

    lift_l = pose.get("lift_l", 0)
    lift_r = pose.get("lift_r", 0)

    if pose.get("tray") or (pose.get("serve_phase") is not None and pose.get("wipe_phase") is None
                            and pose.get("attack_phase") is None and not pose.get("parry")
                            and not pose.get("hurt")):
        sp = pose.get("serve_phase", 1)
        yoff = -2 if sp == 0 else (0 if sp == 1 else 1)
        arm_ext = 1 if sp >= 1 else 0
        fill_rect(img, 16 + bx + arm_ext, ty + 2, 22 + bx + arm_ext, ty + 6, WOOD)
        fill_rect(img, 20 + bx + arm_ext, ty + 3, 24 + bx + arm_ext, ty + 6, SKIN)
        # tray board
        fill_rect(img, 17 + bx + arm_ext, ty + yoff, 31 + bx + arm_ext, ty + 2 + yoff, WOOD_L)
        hline(img, 17 + bx + arm_ext, 31 + bx + arm_ext, ty + yoff, INK)
        hline(img, 17 + bx + arm_ext, 31 + bx + arm_ext, ty + 2 + yoff, WOOD)
        # teapot separate
        pot_x = 19 + bx + arm_ext + (1 if sp == 2 else 0)
        fill_rect(img, pot_x, ty - 4 + yoff, pot_x + 5, ty + yoff, CINN_B)
        fill_rect(img, pot_x + 1, ty - 5 + yoff, pot_x + 4, ty - 4 + yoff, GOLD)
        px(img, pot_x + 5, ty - 3 + yoff, WOOD)  # spout
        px(img, pot_x - 1, ty - 2 + yoff, WOOD)  # handle
        # cups separate from pot
        fill_rect(img, 26 + bx + arm_ext, ty - 2 + yoff, 28 + bx + arm_ext, ty + yoff, CREAM)
        outline_rect(img, 26 + bx + arm_ext, ty - 2 + yoff, 28 + bx + arm_ext, ty + yoff, INK)
        fill_rect(img, 29 + bx + arm_ext, ty - 2 + yoff, 31 + bx + arm_ext, ty + yoff, PAPER_L)
        if sp == 1:
            px(img, pot_x + 2, ty - 6 + yoff, MIST)
            px(img, pot_x + 3, ty - 7 + yoff, MIST)
        if sp == 2:
            px(img, pot_x + 6, ty + 1, LOESS)
            px(img, pot_x + 6, ty + 2, LOESS)
            px(img, 27 + bx + arm_ext, ty + 1, LOESS)
    elif pose.get("wipe_phase") is not None:
        wp = pose["wipe_phase"]
        # wipe cloth in right hand, sweeping across table height
        fill_rect(img, 16 + bx, ty + 2, 22 + bx, ty + 6, WOOD)
        fill_rect(img, 20 + bx, ty + 3, 24 + bx, ty + 6, SKIN)
        # cloth position arcs: reach → sweep mid → far → recover
        if wp == 0:
            fill_rect(img, 15 + bx, ty + 8, 22 + bx, ty + 11, PAPER_L)
            hline(img, 15 + bx, 22 + bx, ty + 8, INK)
            px(img, 16 + bx, ty + 9, CREAM)
        elif wp == 1:
            fill_rect(img, 18 + bx, ty + 7, 27 + bx, ty + 10, PAPER_L)
            hline(img, 18 + bx, 27 + bx, ty + 7, INK)
            px(img, 24 + bx, ty + 8, CREAM)
            px(img, 20 + bx, ty + 9, MIST)  # damp streak
        elif wp == 2:
            fill_rect(img, 20 + bx, ty + 6, 31 + bx, ty + 9, PAPER_L)
            hline(img, 20 + bx, 31 + bx, ty + 6, INK)
            px(img, 28 + bx, ty + 7, CREAM)
            px(img, 25 + bx, ty + 8, MIST)
            px(img, 22 + bx, ty + 8, MIST)
        else:
            fill_rect(img, 16 + bx, ty + 8, 23 + bx, ty + 11, PAPER_L)
            hline(img, 16 + bx, 23 + bx, ty + 8, INK)
            # left hand brace on table
            fill_rect(img, 4 + bx, ty + 6, 9 + bx, ty + 9, WOOD)
            fill_rect(img, 3 + bx, ty + 8, 7 + bx, ty + 10, SKIN)
    elif pose.get("parry"):
        shake = pose.get("shake", 0)
        # raise tray as shield
        fill_rect(img, 14 + bx, ty - 2, 20 + bx, ty + 3, WOOD)
        fill_rect(img, 15 + bx + shake, ty - 7, 24 + bx + shake, ty - 2, PAPER_L)
        hline(img, 15 + bx + shake, 24 + bx + shake, ty - 7, INK)
        fill_rect(img, 16 + bx + shake, ty - 6, 23 + bx + shake, ty - 3, WOOD_L)
        if shake:
            px(img, 25 + bx, ty - 5, CREAM)
    elif pose.get("hurt"):
        fill_rect(img, 18 + bx, ty + 1, 24 + bx, ty + 5, WOOD)
        fill_rect(img, 22 + bx, ty + 2, 26 + bx, ty + 5, SKIN)
        px(img, 15 + bx, 6 + oy, BLOOD)
        px(img, 11 + bx, 9 + oy, CINN)
        px(img, 18 + bx, 10 + oy, BLOOD)
    else:
        fill_rect(img, 3 + bx, ty + 2, 8 + bx, ty + 8, WOOD)
        fill_rect(img, 2 + bx, ty + 6, 6 + bx, ty + 9, SKIN)
        fill_rect(img, 16 + bx, ty + 2, 20 + bx, ty + 7, WOOD)
        fill_rect(img, 17 + bx, ty + 7, 22 + bx, ty + 10, PAPER_L)  # hanging towel
        if lift_r:
            fill_rect(img, 16 + bx, ty + 0, 21 + bx, ty + 5, WOOD)
            fill_rect(img, 19 + bx, ty + 3, 23 + bx, ty + 6, SKIN)
        elif lift_l:
            fill_rect(img, 16 + bx, ty + 4, 20 + bx, ty + 10, WOOD)

    if not pose.get("hurt"):
        ly = ty + 13
        fill_rect(img, 9 + bx - (2 if lift_l else 0), ly - lift_l,
                  13 + bx - (2 if lift_l else 0), ly + 5 - lift_l, INK_SOFT)
        fill_rect(img, 13 + bx + (2 if lift_r else 0), ly - lift_r,
                  17 + bx + (2 if lift_r else 0), ly + 5 - lift_r, INK_SOFT)
        draw_feet(img, 8 + bx, ly + 5, 14 + bx, ly + 5, INK, lift_l, lift_r,
                  stride=2 if (lift_l or lift_r) else 0)
    else:
        ly = ty + 13
        fill_rect(img, 8 + bx, ly, 12 + bx, ly + 5, INK_SOFT)
        fill_rect(img, 13 + bx, ly + 1, 17 + bx, ly + 5, INK_SOFT)
        draw_feet(img, 7 + bx, ly + 5, 13 + bx, ly + 5, INK, 1, 0, stride=0)


def poses_for_character(kind):
    poses = []
    poses.append({"breath": 0})
    poses.append({"breath": 1})
    # walk: higher lifts (6–7), clearer mid stance
    poses.append({"lift_l": 7, "breath": 0})
    poses.append({"lift_l": 2, "breath": 0})  # passing mid with residual
    poses.append({"lift_r": 7, "breath": 0})
    poses.append({"lift_r": 2, "breath": 1})
    # serve 6–8
    if kind == "qinshi":
        poses.append({"hold": True, "serve_phase": 0, "breath": 0})
        poses.append({"hold": True, "serve_phase": 1, "breath": 1})
        poses.append({"hold": True, "serve_phase": 2, "breath": 0})
    else:
        poses.append({"tray": True, "serve_phase": 0, "breath": 0})
        poses.append({"tray": True, "serve_phase": 1, "breath": 0})
        poses.append({"tray": True, "serve_phase": 2, "breath": 1})
    # 9–12 attack OR xiaoer wipe
    if kind == "xiaoer":
        for wp in range(4):
            poses.append({"wipe_phase": wp, "breath": 0 if wp < 2 else 1})
    else:
        for ap in range(4):
            poses.append({"attack_phase": ap, "breath": 0 if ap < 2 else 1})
    poses.append({"hurt": True, "breath": 0, "lift_l": 3})
    poses.append({"hurt": True, "breath": 1})
    poses.append({"parry": True, "breath": 0, "shake": 0})
    poses.append({"parry": True, "breath": 0, "shake": 1})
    poses.append({"parry": True, "breath": 1, "shake": 0})
    return poses


DRAWERS = {
    "qingyi": qingyi_body,
    "tiezhang": tiezhang_body,
    "langren": langren_body,
    "qinshi": qinshi_body,
    "xiaoer": xiaoer_body,
}


def make_spritesheet(char_id: str) -> Image.Image:
    sheet = Image.new("RGBA", (576, 32), TRANS)
    drawer = DRAWERS[char_id]
    poses = poses_for_character(char_id)
    assert len(poses) == 18, f"{char_id} pose count {len(poses)}"
    for i, pose in enumerate(poses):
        frame = new_frame()
        drawer(frame, 0, 0, pose)
        sheet.paste(frame, (i * 32, 0), frame)
    return sheet


def make_boss_combat(which: str) -> Image.Image:
    img = new_frame(32, 32)
    if which == "heifeng":
        draw_head(img, 11, 1, hair=INK, face=SKIN_D, fringe=True)
        fill_rect(img, 6, 2, 16, 5, INK)
        fill_rect(img, 9, 8, 13, 10, SKIN_D)
        fill_rect(img, 6, 9, 16, 21, INK_SOFT)
        fill_rect(img, 7, 10, 15, 14, NIGHT)
        fill_rect(img, 6, 15, 16, 17, FRAME)
        px(img, 11, 16, CINN_B)
        fill_rect(img, 7, 21, 11, 27, INK_SOFT)
        fill_rect(img, 11, 21, 15, 27, INK_SOFT)
        draw_feet(img, 6, 27, 12, 27, INK)
        fill_rect(img, 17, 4, 23, 25, INK)
        fill_rect(img, 18, 5, 22, 23, MIST)
        fill_rect(img, 17, 25, 23, 28, WOOD)
        fill_rect(img, 19, 6, 21, 21, CINN_B)
        px(img, 19, 3, CINN_B)
        fill_rect(img, 15, 9, 18, 13, INK)
        px(img, 17, 8, GOLD)
    else:
        draw_head(img, 11, 2, hair=VIOLET, face=SKIN_D, hair_side=VIOLET, bun=True)
        fill_rect(img, 9, 9, 13, 11, SKIN_D)
        fill_rect(img, 6, 10, 16, 21, VIOLET)
        fill_rect(img, 7, 11, 15, 18, JADE)
        fill_rect(img, 8, 12, 14, 17, JADE_B)
        fill_rect(img, 16, 11, 23, 19, ROBE_R)
        outline_rect(img, 16, 11, 23, 19, INK)
        fill_rect(img, 17, 12, 22, 17, JADE_B)
        px(img, 18, 10, GOLD)
        px(img, 19, 18, JADE_B)
        px(img, 19, 19, JADE)
        px(img, 20, 20, CINN)
        fill_rect(img, 7, 21, 11, 27, VIOLET)
        fill_rect(img, 11, 21, 15, 27, VIOLET)
        draw_feet(img, 6, 27, 12, 27, INK_SOFT)
        fill_rect(img, 15, 17, 21, 21, SKIN_D)
        px(img, 21, 16, JADE_B)
        px(img, 22, 17, JADE)
        px(img, 23, 18, CINN_B)
    return img


def make_guest_sit() -> Image.Image:
    """4 seated guests, 32×32 each, side/3-quarter, transparent — for hub life."""
    sheet = Image.new("RGBA", (128, 32), TRANS)
    variants = [
        # (robe, belt, hair, face, cup)
        (TEAL, WOOD_L, INK, SKIN, CREAM),
        (ROBE_R, GOLD, INK, SKIN, PAPER_L),
        (INK_SOFT, FRAME, INK, SKIN_D, CREAM),
        (VIOLET, GOLD, PAPER_L, SKIN, PAPER),
    ]
    for i, (robe, belt, hair, face, cup) in enumerate(variants):
        img = new_frame(32, 32)
        # stool under
        fill_rect(img, 8, 24, 22, 28, WOOD_L)
        outline_rect(img, 8, 24, 22, 28, INK)
        fill_rect(img, 10, 28, 13, 32, WOOD)
        fill_rect(img, 17, 28, 20, 32, WOOD)
        # seated torso (lower center of mass)
        draw_head(img, 14, 4, hair=hair, face=face,
                  hair_side=hair if hair != PAPER_L else PAPER_L,
                  bald_cap=(hair == PAPER_L))
        if hair == PAPER_L:
            px(img, 13, 8, VIOLET)
        fill_rect(img, 12, 11, 16, 13, face)
        fill_rect(img, 9, 12, 20, 22, robe)
        fill_rect(img, 12, 12, 16, 14, PAPER_L)
        draw_belt(img, 9, 20, 17, belt, GOLD)
        # lap / bent legs forward-right
        fill_rect(img, 10, 20, 22, 25, robe)
        fill_rect(img, 18, 22, 24, 26, robe)
        # feet dangling
        fill_rect(img, 11, 25, 15, 28, INK_SOFT)
        fill_rect(img, 18, 26, 23, 29, INK_SOFT)
        # arm on table holding cup
        fill_rect(img, 18, 14, 24, 18, robe)
        fill_rect(img, 22, 15, 26, 18, face)
        fill_rect(img, 24, 13, 28, 17, cup)
        outline_rect(img, 24, 13, 28, 17, INK)
        if i % 2 == 0:
            px(img, 26, 12, MIST)  # steam
        sheet.paste(img, (i * 32, 0), img)
    return sheet


# ---------- Hub ----------

def draw_wood_floor(img, y0, y1):
    fill_rect(img, 0, y0, 480, y1, WOOD)
    row_h = 7
    for y in range(y0, y1, row_h):
        hline(img, 0, 480, y, INK_SOFT)
        hline(img, 0, 480, y + row_h - 1, NIGHT)
        off = 0 if ((y - y0) // row_h) % 2 == 0 else 10
        for x in range(off, 480, 20):
            vline(img, x, y, min(y + row_h, y1), NIGHT)
            # plank seam nails / grain
            if x + 3 < 480:
                px(img, x + 3, y + 2, WOOD_L)
            if x + 8 < 480:
                px(img, x + 8, y + 4, FRAME)
            if x + 14 < 480 and (x + y) % 5 == 0:
                px(img, x + 14, y + 3, INK_SOFT)


def draw_table(img, tx, ty, tw=40, th=18, fancy=False, dishes="full"):
    fill_rect(img, tx, ty, tx + tw, ty + 8, WOOD_L)
    outline_rect(img, tx, ty, tx + tw, ty + 8, INK)
    hline(img, tx + 2, tx + tw - 2, ty + 3, WOOD)
    hline(img, tx + 4, tx + tw - 4, ty + 5, FRAME)
    fill_rect(img, tx + 2, ty + 8, tx + tw - 2, ty + th, WOOD)
    # thicker legs
    fill_rect(img, tx + 2, ty + 8, tx + 6, ty + th, WOOD)
    fill_rect(img, tx + tw - 6, ty + 8, tx + tw - 2, ty + th, WOOD)
    vline(img, tx + 2, ty + 8, ty + th, INK)
    vline(img, tx + tw - 3, ty + 8, ty + th, INK)
    hline(img, tx + 2, tx + tw - 2, ty + th - 1, INK)
    # dishes
    if dishes in ("full", "bowl"):
        fill_rect(img, tx + 4, ty + 2, tx + 10, ty + 6, CREAM)
        outline_rect(img, tx + 4, ty + 2, tx + 10, ty + 6, INK)
        px(img, tx + 6, ty + 3, LOESS)
    if dishes in ("full", "cup"):
        fill_rect(img, tx + 12, ty + 2, tx + 17, ty + 6, CINN_B)
        outline_rect(img, tx + 12, ty + 2, tx + 17, ty + 6, INK)
    if dishes == "full" and tw >= 36:
        fill_rect(img, tx + 20, ty + 1, tx + 30, ty + 6, WOOD)
        fill_rect(img, tx + 22, ty + 2, tx + 28, ty + 5, CINN)
        px(img, tx + 24, ty + 0, GOLD)
        fill_rect(img, tx + 31, ty + 2, tx + 35, ty + 6, PAPER_L)
        outline_rect(img, tx + 31, ty + 2, tx + 35, ty + 6, INK)
    if fancy:
        fill_rect(img, tx + 7, ty + 1, tx + 11, ty + 3, JADE_B)
        px(img, tx + 18, ty + 3, LOESS)
        px(img, tx + 19, ty + 4, GOLD)


def draw_stool(img, sx, sy):
    fill_rect(img, sx, sy, sx + 12, sy + 5, WOOD_L)
    outline_rect(img, sx, sy, sx + 12, sy + 5, INK)
    hline(img, sx + 1, sx + 11, sy + 2, WOOD)
    fill_rect(img, sx + 2, sy + 5, sx + 5, sy + 13, WOOD)
    fill_rect(img, sx + 7, sy + 5, sx + 10, sy + 13, WOOD)
    px(img, sx + 3, sy + 12, INK)
    px(img, sx + 8, sy + 12, INK)


def draw_lantern(img, lx, ly, hanging=True):
    if hanging:
        vline(img, lx + 4, ly - 10, ly, INK)
        hline(img, lx + 2, lx + 7, ly - 10, INK)
        px(img, lx + 4, ly - 11, FRAME)
    fill_rect(img, lx, ly, lx + 9, ly + 12, CINN)
    fill_rect(img, lx + 1, ly + 1, lx + 8, ly + 11, CINN_B)
    fill_rect(img, lx, ly, lx + 9, ly + 2, GOLD)
    fill_rect(img, lx, ly + 10, lx + 9, ly + 12, GOLD)
    # 1px flame white highlight
    px(img, lx + 4, ly + 5, CREAM)
    px(img, lx + 3, ly + 6, PAPER_L)
    px(img, lx + 5, ly + 6, LOESS)
    # tassels longer
    vline(img, lx + 2, ly + 12, ly + 18, GOLD)
    vline(img, lx + 6, ly + 12, ly + 18, GOLD)
    px(img, lx + 2, ly + 18, LOESS)
    px(img, lx + 6, ly + 18, LOESS)


def draw_rug(img, x, y, w, h):
    fill_rect(img, x, y, x + w, y + h, CINN)
    outline_rect(img, x, y, x + w, y + h, INK)
    fill_rect(img, x + 2, y + 2, x + w - 2, y + h - 2, BLOOD)
    # denser pattern blocks
    for i in range(x + 4, x + w - 4, 5):
        px(img, i, y + h // 2, GOLD)
        px(img, i + 1, y + h // 2 - 1, LOESS)
        px(img, i, y + 3, PAPER_L)
        px(img, i, y + h - 4, PAPER_L)
    # corner ornaments
    px(img, x + 3, y + 3, GOLD)
    px(img, x + w - 4, y + 3, GOLD)
    px(img, x + 3, y + h - 4, GOLD)
    px(img, x + w - 4, y + h - 4, GOLD)


def make_hub_layers():
    W, H = 480, 270
    layers = {}

    floor = Image.new("RGBA", (W, H), TRANS)
    draw_wood_floor(floor, 148, 270)
    for y in range(158, 248):
        for x in range(70, 410):
            if (x + y * 3) % 11 == 0:
                r, g, b, a = floor.getpixel((x, y))
                if a and (r, g, b) == WOOD[:3]:
                    floor.putpixel((x, y), WOOD_L)
    draw_rug(floor, 95, 208, 56, 16)
    draw_rug(floor, 310, 212, 52, 14)
    draw_rug(floor, 200, 248, 40, 10)
    layers["hub_floor.png"] = floor

    wall = Image.new("RGBA", (W, H), TRANS)
    fill_rect(wall, 0, 0, W, 68, SKY)
    for i, (mx, mh) in enumerate([(0, 40), (40, 55), (90, 35), (130, 50), (180, 42),
                                   (230, 58), (280, 38), (320, 52), (370, 44), (420, 50)]):
        fill_rect(wall, mx, 68 - mh, mx + 55, 68, MTN)
        if i % 2 == 0:
            fill_rect(wall, mx + 10, 68 - mh + 8, mx + 40, 68, JADE)
        if i % 3 == 0:
            px(wall, mx + 20, 68 - mh + 4, MIST)
    hline(wall, 0, W, 68, MIST)
    fill_rect(wall, 0, 68, W, 148, NIGHT)
    fill_rect(wall, 0, 88, W, 148, WOOD)
    # denser wall panels: windows + scrolls + door lintel detail
    for x in range(0, W, 36):
        vline(wall, x, 88, 148, INK_SOFT)
        fill_rect(wall, x + 3, 92, x + 33, 140, FRAME)
        fill_rect(wall, x + 5, 94, x + 31, 138, WOOD)
        slot = (x // 36) % 3
        if slot == 1:
            # lattice window denser
            fill_rect(wall, x + 8, 100, x + 28, 128, SKY)
            outline_rect(wall, x + 8, 100, x + 28, 128, INK)
            hline(wall, x + 8, x + 28, 109, GOLD)
            hline(wall, x + 8, x + 28, 118, GOLD)
            vline(wall, x + 14, 100, 128, GOLD)
            vline(wall, x + 22, 100, 128, GOLD)
            fill_rect(wall, x + 9, 119, x + 27, 128, MTN)
            # window sill
            hline(wall, x + 7, x + 29, 128, WOOD_L)
        elif slot == 0:
            # scroll painting
            fill_rect(wall, x + 10, 98, x + 26, 134, PAPER)
            outline_rect(wall, x + 10, 98, x + 26, 134, INK)
            fill_rect(wall, x + 10, 98, x + 26, 101, WOOD_L)
            fill_rect(wall, x + 10, 131, x + 26, 134, WOOD_L)
            for sy in range(106, 128, 3):
                hline(wall, x + 13, x + 23, sy, INK_SOFT)
            # mountain ink blotch
            fill_rect(wall, x + 14, 114, x + 22, 126, MTN)
            px(wall, x + 18, 120, CINN)  # seal
            px(wall, x + 19, 121, CINN_B)
        else:
            # plaque / couplet board
            fill_rect(wall, x + 10, 102, x + 26, 130, PAPER_D)
            outline_rect(wall, x + 10, 102, x + 26, 130, GOLD)
            for sy in (108, 116, 124):
                vline(wall, x + 15, sy, sy + 5, INK)
                vline(wall, x + 20, sy, sy + 5, INK_SOFT)
    # beam / lintel
    fill_rect(wall, 0, 142, W, 150, INK_SOFT)
    hline(wall, 0, W, 142, GOLD)
    hline(wall, 0, W, 144, LOESS)
    for bx in range(20, W, 48):
        fill_rect(wall, bx, 138, bx + 10, 142, WOOD_L)  # bracket
    # door left with denser panels
    fill_rect(wall, 6, 96, 52, 148, NIGHT)
    fill_rect(wall, 10, 100, 48, 148, WOOD_L)
    outline_rect(wall, 10, 100, 48, 148, INK)
    vline(wall, 29, 100, 148, INK)
    for dy in (108, 118, 128, 138):
        hline(wall, 14, 26, dy, WOOD)
        hline(wall, 32, 44, dy, WOOD)
        px(wall, 20, dy + 2, GOLD)
        px(wall, 38, dy + 2, GOLD)
    # door plaque
    fill_rect(wall, 8, 86, 50, 98, CINN)
    outline_rect(wall, 8, 86, 50, 98, GOLD)
    for px0 in (16, 24, 32, 40):
        vline(wall, px0, 88, 96, PAPER_L)
    layers["hub_wall.png"] = wall

    counter = Image.new("RGBA", (W, H), TRANS)
    cx, cy, cw, ch = 155, 165, 180, 55
    fill_rect(counter, cx, cy, cx + cw, cy + 12, WOOD_L)
    outline_rect(counter, cx, cy, cx + cw, cy + 12, INK)
    hline(counter, cx + 4, cx + cw - 4, cy + 5, WOOD)
    hline(counter, cx + 8, cx + cw - 8, cy + 8, FRAME)
    fill_rect(counter, cx + 2, cy + 12, cx + cw - 2, cy + ch, WOOD)
    for px0 in range(cx + 8, cx + cw - 8, 26):
        fill_rect(counter, px0, cy + 16, px0 + 20, cy + ch - 4, FRAME)
        fill_rect(counter, px0 + 2, cy + 18, px0 + 18, cy + ch - 6, WOOD)
        px(counter, px0 + 9, cy + 28, GOLD)
        hline(counter, px0 + 3, px0 + 17, cy + 22, INK_SOFT)
    # ledger book (readable)
    fill_rect(counter, cx + 8, cy + 1, cx + 40, cy + 11, PAPER)
    outline_rect(counter, cx + 8, cy + 1, cx + 40, cy + 11, INK)
    fill_rect(counter, cx + 8, cy + 1, cx + 12, cy + 11, BLOOD)  # binding
    for ly in (3, 5, 7, 9):
        hline(counter, cx + 14, cx + 36, cy + ly, INK_SOFT)
    px(counter, cx + 34, cy + 4, CINN)  # seal stamp
    # teapot set clearer
    fill_rect(counter, cx + 48, cy - 10, cx + 68, cy + 8, CINN)
    fill_rect(counter, cx + 50, cy - 8, cx + 66, cy + 6, CINN_B)
    fill_rect(counter, cx + 68, cy - 3, cx + 76, cy + 2, WOOD)  # spout
    fill_rect(counter, cx + 44, cy - 2, cx + 48, cy + 3, WOOD)  # handle
    fill_rect(counter, cx + 54, cy - 12, cx + 64, cy - 10, GOLD)
    px(counter, cx + 58, cy - 6, CREAM)  # highlight
    for cup_x in (80, 92, 104):
        fill_rect(counter, cx + cup_x, cy + 1, cx + cup_x + 8, cy + 9, CREAM if cup_x != 92 else PAPER_L)
        outline_rect(counter, cx + cup_x, cy + 1, cx + cup_x + 8, cy + 9, INK)
    # abacus denser beads
    fill_rect(counter, cx + 120, cy + 0, cx + 162, cy + 11, WOOD)
    outline_rect(counter, cx + 120, cy + 0, cx + 162, cy + 11, INK)
    hline(counter, cx + 122, cx + 160, cy + 5, INK_SOFT)
    for bx in range(cx + 124, cx + 160, 5):
        vline(counter, bx, cy + 1, cy + 10, FRAME)
        px(counter, bx - 1, cy + 2, CINN_B)
        px(counter, bx - 1, cy + 3, CINN)
        px(counter, bx - 1, cy + 7, GOLD)
        px(counter, bx - 1, cy + 8, LOESS)
    # coins pile
    fill_rect(counter, cx + 164, cy + 2, cx + 176, cy + 10, GOLD)
    px(counter, cx + 166, cy + 3, LOESS)
    px(counter, cx + 170, cy + 4, LOESS)
    px(counter, cx + 168, cy + 6, WOOD_L)
    # wine jar on counter corner
    fill_rect(counter, cx + 4, cy - 16, cx + 18, cy + 2, JADE)
    fill_rect(counter, cx + 6, cy - 14, cx + 16, cy, JADE_B)
    fill_rect(counter, cx + 7, cy - 18, cx + 15, cy - 16, GOLD)
    px(counter, cx + 10, cy - 10, CREAM)
    # brush pot
    fill_rect(counter, cx + 22, cy - 6, cx + 30, cy + 2, INK_SOFT)
    vline(counter, cx + 24, cy - 10, cy - 4, INK)
    vline(counter, cx + 27, cy - 9, cy - 4, WOOD)
    layers["hub_counter.png"] = counter

    furn = Image.new("RGBA", (W, H), TRANS)
    tables = [
        (48, 170, 48, 18, True, "full"),
        (58, 216, 44, 18, False, "full"),
        (110, 188, 42, 16, True, "full"),
        (290, 172, 52, 18, True, "full"),
        (330, 218, 44, 18, False, "full"),
        (395, 165, 48, 18, True, "full"),
        (240, 226, 40, 16, False, "cup"),
        (200, 238, 38, 16, False, "bowl"),
        (150, 230, 36, 16, False, "full"),
        (420, 210, 40, 16, True, "full"),
        (70, 245, 36, 14, False, "cup"),
        (360, 245, 38, 14, False, "bowl"),
    ]
    for t in tables:
        draw_table(furn, *t)
    stools = [
        (38, 186), (92, 186), (42, 232), (100, 232),
        (100, 204), (148, 204),
        (280, 190), (338, 190), (320, 234), (372, 234),
        (385, 180), (440, 180), (230, 241), (278, 241),
        (190, 250), (228, 250), (140, 244), (175, 244),
        (410, 198), (450, 198), (405, 224), (448, 224),
        (55, 258), (100, 258), (350, 258), (390, 258),
        (250, 210), (270, 210),
    ]
    for s in stools:
        draw_stool(furn, *s)
    # wine shelf denser jars
    fill_rect(furn, 50, 122, 100, 154, WOOD)
    outline_rect(furn, 50, 122, 100, 154, INK)
    hline(furn, 52, 98, 132, INK_SOFT)
    hline(furn, 52, 98, 142, INK_SOFT)
    for jx, col in ((54, CINN), (64, CINN_B), (74, JADE), (84, ROBE_R), (92, VIOLET)):
        fill_rect(furn, jx, 124, jx + 8, 131, col)
        fill_rect(furn, jx + 1, 134, jx + 7, 141, col)
        fill_rect(furn, jx + 1, 144, jx + 7, 152, col)
        px(furn, jx + 3, 123, GOLD)
        px(furn, jx + 3, 133, GOLD)
        px(furn, jx + 3, 143, GOLD)
    # weapon rack
    fill_rect(furn, 448, 126, 472, 162, WOOD)
    outline_rect(furn, 448, 126, 472, 162, INK)
    vline(furn, 454, 130, 158, TEAL_B)
    vline(furn, 460, 132, 158, INK_SOFT)
    vline(furn, 466, 130, 158, MIST)
    px(furn, 454, 128, GOLD)
    px(furn, 460, 130, CINN_B)
    # folding screen denser
    fill_rect(furn, 418, 112, 446, 164, PAPER_D)
    outline_rect(furn, 418, 112, 446, 164, INK)
    vline(furn, 432, 112, 164, WOOD)
    for sy in range(120, 158, 6):
        hline(furn, 421, 430, sy, MIST)
        hline(furn, 434, 443, sy, MIST)
    fill_rect(furn, 422, 128, 430, 150, MTN)
    fill_rect(furn, 435, 132, 443, 152, JADE)
    px(furn, 426, 140, SKY)
    # stove / hearth
    fill_rect(furn, 128, 148, 154, 168, INK_SOFT)
    fill_rect(furn, 132, 152, 150, 164, NIGHT)
    px(furn, 138, 156, CINN_B)
    px(furn, 142, 158, GOLD)
    px(furn, 140, 160, CREAM)
    fill_rect(furn, 134, 146, 148, 150, FRAME)  # pot rim
    # side cabinet near right
    fill_rect(furn, 455, 200, 478, 245, WOOD)
    outline_rect(furn, 455, 200, 478, 245, INK)
    hline(furn, 457, 476, 220, INK_SOFT)
    px(furn, 466, 210, GOLD)
    px(furn, 466, 230, GOLD)
    layers["hub_furniture.png"] = furn

    lan = Image.new("RGBA", (W, H), TRANS)
    lanterns = [
        (70, 84), (140, 78), (220, 74), (300, 78), (380, 84), (440, 88),
        (100, 96), (180, 90), (260, 88), (340, 90), (410, 96),
        (50, 100), (470, 100),
    ]
    for lx, ly in lanterns:
        draw_lantern(lan, lx, ly, hanging=True)
    for lx in (148, 250, 328):
        fill_rect(lan, lx, 150, lx + 4, 172, WOOD)
        draw_lantern(lan, lx - 2, 140, hanging=False)
    layers["hub_lanterns.png"] = lan

    composed = Image.new("RGBA", (W, H), NIGHT)
    for key in ["hub_wall.png", "hub_floor.png", "hub_furniture.png", "hub_counter.png", "hub_lanterns.png"]:
        composed.alpha_composite(layers[key])
    layers["hub_composed.png"] = composed
    return layers


def audit(img: Image.Image, name: str):
    oob = 0
    opaque = 0
    oob_colors = {}
    for y in range(img.height):
        for x in range(img.width):
            r, g, b, a = img.getpixel((x, y))
            if a == 0:
                continue
            opaque += 1
            if (r, g, b) not in PALETTE_SET:
                oob += 1
                oob_colors[(r, g, b)] = oob_colors.get((r, g, b), 0) + 1
    return opaque, oob, oob_colors


def verify_spritesheet(img: Image.Image, name: str):
    assert img.size == (576, 32), f"{name} size {img.size}"
    opaque, oob, cols = audit(img, name)
    empty_cols = []
    for i in range(18):
        col_opaque = 0
        for y in range(32):
            for x in range(i * 32, i * 32 + 32):
                if img.getpixel((x, y))[3] > 0:
                    col_opaque += 1
        if col_opaque < 20:
            empty_cols.append(i)
    return opaque, oob, cols, empty_cols


def write_previews():
    PREVIEW.mkdir(parents=True, exist_ok=True)
    # full sheet x4 for key characters
    for cid in ["qingyi", "xiaoer", "tiezhang", "langren", "qinshi"]:
        src = Image.open(SPRITES / f"{cid}.png")
        big = src.resize((src.width * 4, src.height * 4), Image.NEAREST)
        big.save(PREVIEW / f"{cid}_x4.png")
        # sample frames
        labels = {
            0: "idle", 2: "walk", 6: "serve", 7: "serve1", 8: "serve2",
            9: "attack", 13: "hurt", 15: "parry", 16: "parry1",
        }
        if cid == "xiaoer":
            labels[9] = "wipe0"
            labels[10] = "wipe1"
            labels[11] = "wipe2"
            labels[12] = "wipe3"
        for fi, lab in labels.items():
            frame = src.crop((fi * 32, 0, fi * 32 + 32, 32))
            frame.resize((128, 128), Image.NEAREST).save(PREVIEW / f"{cid}_{lab}.png")
    hub = Image.open(SCENES / "hub_composed.png")
    hub.resize((hub.width * 2, hub.height * 2), Image.NEAREST).save(PREVIEW / "hub_composed_x2.png")
    hub.resize((hub.width * 2, hub.height * 2), Image.NEAREST).save(PREVIEW / "hub_read.png")
    for bid in ["heifeng", "xieyi"]:
        b = Image.open(SPRITES / f"boss_{bid}_combat.png")
        b.resize((128, 128), Image.NEAREST).save(PREVIEW / f"boss_{bid}_combat_x4.png")
    guests = Image.open(SPRITES / "guest_sit.png")
    guests.resize((guests.width * 4, guests.height * 4), Image.NEAREST).save(PREVIEW / "guest_sit_x4.png")


def main():
    SPRITES.mkdir(parents=True, exist_ok=True)
    SCENES.mkdir(parents=True, exist_ok=True)
    report = ["# Ink-Pixel Inn asset gen report v1.1", ""]
    for cid in ["qingyi", "tiezhang", "langren", "qinshi", "xiaoer"]:
        sheet = make_spritesheet(cid)
        path = SPRITES / f"{cid}.png"
        sheet.save(path)
        opaque, oob, cols, empty = verify_spritesheet(sheet, cid)
        line = f"SPRITE {cid}: size={sheet.size} opaque={opaque} oob={oob} empty_frames={empty} oob_cols={cols}"
        report.append(line)
        print(line)
        if oob:
            raise SystemExit(f"OOB colors in {cid}: {cols}")
    for bid in ["heifeng", "xieyi"]:
        im = make_boss_combat(bid)
        path = SPRITES / f"boss_{bid}_combat.png"
        im.save(path)
        opaque, oob, cols = audit(im, path.name)
        line = f"BOSS {bid}: size={im.size} opaque={opaque} oob={oob} oob_cols={cols}"
        report.append(line)
        print(line)
        if oob:
            raise SystemExit(f"OOB in boss {bid}: {cols}")
    guests = make_guest_sit()
    gpath = SPRITES / "guest_sit.png"
    guests.save(gpath)
    opaque, oob, cols = audit(guests, "guest_sit")
    line = f"GUEST sit: size={guests.size} opaque={opaque} oob={oob} oob_cols={cols}"
    report.append(line)
    print(line)
    if oob:
        raise SystemExit(f"OOB in guest_sit: {cols}")
    layers = make_hub_layers()
    for name, im in layers.items():
        path = SCENES / name
        im.save(path)
        opaque, oob, cols = audit(im, name)
        line = f"SCENE {name}: size={im.size} opaque={opaque} oob={oob} oob_cols={list(cols.keys())[:5]}"
        report.append(line)
        print(line)
        if oob:
            raise SystemExit(f"OOB in {name}: {cols}")
    write_previews()
    report.append("PREVIEWS: refreshed under assets/_preview/")
    (SPRITES / "_gen_report.txt").write_text("\n".join(report) + "\n", encoding="utf-8")
    print("DONE v1.1")


if __name__ == "__main__":
    main()
