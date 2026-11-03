#!/usr/bin/env python3
"""Native 64×64 Ink-Pixel Inn character spritesheets.

NOT a nearest-neighbor upscale of 32×32 — redrawn at 64 with extra readable
detail (robe folds, weapon thickness, trayware, 1–2px ink eyes), hard-edge,
palette-locked, transparent bg, facing right.

Output: assets/sprites/64/{id}.png — 18 frames × 64 → 1152×64
Optional: guest_sit.png (6×64=384×64), boss_*_combat.png (64×64)

Frame map (same as 32):
  0–1 idle | 2–5 walk | 6–8 windup (舊 serve；Hub xiaoer 暫共用斟茶) | 9–12 strike/attack (xiaoer=wipe) | 13–14 hurt | 15–17 parry
"""
from __future__ import annotations

from pathlib import Path
from PIL import Image

ROOT = Path("/workspace/wuxia-inn")
OUT = ROOT / "assets" / "sprites" / "64"
PREV = ROOT / "assets" / "_preview"
SPRITES32 = ROOT / "assets" / "sprites"

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

FS = 64  # frame size


def new_frame(w=FS, h=FS):
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
              topknot=False, bun=False, bald_cap=False, fringe=False, hat_wood=False,
              double_bun=False, tall_knot=False):
    """¾ head facing right — ink-pixel eyes 1–2px, richer hair/hat at 64."""
    if bald_cap:
        fill_rect(img, cx - 8, cy - 2, cx + 8, cy + 6, PAPER_L)
        fill_rect(img, cx - 10, cy + 2, cx + 10, cy + 6, PAPER_L)
        fill_rect(img, cx - 6, cy - 4, cx + 6, cy, PAPER)
        hline(img, cx - 8, cx + 8, cy - 2, INK)
        hline(img, cx - 7, cx + 7, cy - 1, PAPER_D)
        fill_rect(img, cx - 8, cy + 6, cx + 8, cy + 16, face)
        hline(img, cx - 8, cx + 8, cy + 6, PAPER_D)
    elif hat_wood:
        fill_rect(img, cx - 12, cy, cx + 12, cy + 4, WOOD)
        fill_rect(img, cx - 8, cy - 6, cx + 8, cy, WOOD_L)
        fill_rect(img, cx - 6, cy - 8, cx + 6, cy - 6, WOOD)
        px(img, cx, cy - 10, GOLD)
        px(img, cx - 1, cy - 9, LOESS)
        px(img, cx + 1, cy - 9, LOESS)
        fill_rect(img, cx - 8, cy + 4, cx + 8, cy + 16, face)
        px(img, cx - 8, cy + 4, hair)
        px(img, cx + 7, cy + 4, hair)
        px(img, cx + 8, cy + 6, hair)
        px(img, cx - 9, cy + 5, hair)
    else:
        fill_rect(img, cx - 8, cy, cx + 8, cy + 6, hair)
        fill_rect(img, cx - 10, cy + 2, cx + 10, cy + 6, hair)
        if tall_knot or topknot:
            fill_rect(img, cx - 2, cy - 8, cx + 4, cy, hair)
            fill_rect(img, cx - 4, cy - 4, cx + 6, cy, hair)
            px(img, cx, cy - 10, GOLD)
            px(img, cx + 1, cy - 9, GOLD)
            px(img, cx + 2, cy - 6, GOLD)
            px(img, cx - 1, cy - 6, LOESS)
            px(img, cx + 1, cy - 7, LOESS)
        if double_bun or bun:
            fill_rect(img, cx + 4, cy - 4, cx + 14, cy + 6, hair)
            fill_rect(img, cx + 6, cy - 6, cx + 12, cy - 2, hair)
            px(img, cx + 10, cy - 2, GOLD)
            px(img, cx + 12, cy + 2, CINN_B)
            px(img, cx + 11, cy, LOESS)
        if fringe:
            hline(img, cx - 8, cx + 8, cy + 6, hair)
            px(img, cx - 6, cy + 8, hair)
            px(img, cx - 2, cy + 8, hair)
            px(img, cx + 4, cy + 8, hair)
            px(img, cx + 1, cy + 7, hair)
        fill_rect(img, cx - 8, cy + 6, cx + 8, cy + 16, face)
        if hair_side:
            fill_rect(img, cx - 10, cy + 6, cx - 6, cy + 18, hair_side)
            fill_rect(img, cx + 6, cy + 6, cx + 10, cy + 16, hair_side)
            px(img, cx - 10, cy + 16, hair_side)
            px(img, cx - 9, cy + 17, hair_side)
        else:
            px(img, cx - 8, cy + 6, hair)
            px(img, cx + 7, cy + 6, hair)
    # eyes 1–2px ink + cheek
    px(img, cx - 4, cy + 10, eye)
    px(img, cx - 3, cy + 10, eye)
    px(img, cx + 2, cy + 10, eye)
    px(img, cx + 3, cy + 10, eye)
    px(img, cx + 6, cy + 12, SKIN_D if face in (SKIN, SKIN_D) else face)
    px(img, cx + 5, cy + 13, SKIN_D if face in (SKIN, SKIN_D) else face)
    # hard outline
    top_y = cy if not hat_wood else cy + 4
    hline(img, cx - 8, cx + 8, top_y, INK)
    vline(img, cx - 10, cy + 2, cy + 16, INK)
    vline(img, cx + 8, cy + 2, cy + 16, INK)


def draw_cuff(img, x0, y0, x1, y1, robe, cuff=PAPER_L):
    fill_rect(img, x0, y0, x1, y1, robe)
    hline(img, x0, x1, y1 - 1, cuff)
    hline(img, x0, x1, y1 - 2, cuff)


def draw_hem_sway(img, x0, x1, y, lift_l, lift_r, robe, fold=NIGHT):
    hline(img, x0, x1, y, fold)
    hline(img, x0 + 1, x1 - 1, y + 1, robe)
    hline(img, x0 + 2, x1 - 2, y + 2, fold)
    if lift_l:
        px(img, x0 - 2, y - 2, robe)
        px(img, x0 - 1, y - 3, fold)
        px(img, x0, y - 2, fold)
        px(img, x0 + 1, y - 1, fold)
    if lift_r:
        px(img, x1 + 1, y - 2, robe)
        px(img, x1, y - 3, fold)
        px(img, x1 - 1, y - 2, fold)
        px(img, x1 + 2, y - 1, fold)


def draw_shoulder(img, cx, cy, w, robe, accent=None):
    fill_rect(img, cx - w, cy, cx + w, cy + 4, robe)
    hline(img, cx - w, cx + w, cy + 1, NIGHT)
    if accent:
        px(img, cx - w, cy, accent)
        px(img, cx - w + 1, cy + 1, accent)
        px(img, cx + w - 1, cy, accent)
        px(img, cx + w - 2, cy + 1, accent)


def draw_feet(img, lx, ly, rx, ry, shoe=INK_SOFT, lift_l=0, lift_r=0, stride=0):
    lxo = lx - (4 if lift_l else 0) + (stride if lift_l else -stride // 2)
    rxo = rx + (4 if lift_r else 0) + (stride if lift_r else -stride // 2 if lift_l else 0)
    fill_rect(img, lxo, ly - lift_l, lxo + 10, ly - lift_l + 6, shoe)
    fill_rect(img, rxo, ry - lift_r, rxo + 10, ry - lift_r + 6, shoe)
    hline(img, lxo, lxo + 10, ly - lift_l + 5, INK)
    hline(img, rxo, rxo + 10, ry - lift_r + 5, INK)
    if lift_l >= 8:
        px(img, lxo + 8, ly - lift_l, CREAM if shoe != CREAM else GOLD)
        px(img, lxo + 9, ly - lift_l + 1, shoe)
        px(img, lxo + 10, ly - lift_l + 2, shoe)
    if lift_r >= 8:
        px(img, rxo + 8, ry - lift_r, CREAM if shoe != CREAM else GOLD)
        px(img, rxo + 9, ry - lift_r + 1, shoe)
        px(img, rxo + 10, ry - lift_r + 2, shoe)


def body_shift(pose):
    if pose.get("hurt"):
        return -8 if pose.get("hurt_phase", 0) == 0 else -12
    if pose.get("wipe_phase") is not None:
        return 2 if pose.get("wipe_phase", 0) % 2 else 0
    if pose.get("attack_phase") == 0:
        return -4
    if pose.get("attack_phase") == 1:
        return 2
    if pose.get("attack_phase") == 2:
        return 6
    if pose.get("attack_phase") == 3:
        return 0
    if pose.get("lift_l"):
        return -4
    if pose.get("lift_r"):
        return 4
    return 0


def draw_robe_folds(img, x0, x1, y, c=NIGHT):
    hline(img, x0, x1, y, c)
    hline(img, x0 + 2, x1 - 2, y + 4, c)
    hline(img, x0 + 4, x1 - 4, y + 10, c)
    px(img, x0 + 2, y + 2, c)
    px(img, x1 - 3, y + 2, c)
    px(img, x0 + 3, y + 6, c)
    px(img, x1 - 4, y + 6, c)
    vline(img, (x0 + x1) // 2, y + 1, y + 12, c)


def draw_belt(img, x0, x1, y, main=WOOD_L, buckle=GOLD):
    fill_rect(img, x0, y, x1, y + 4, main)
    mid = (x0 + x1) // 2
    fill_rect(img, mid - 2, y - 2, mid + 4, y + 6, buckle)
    px(img, mid, y + 1, CREAM if buckle != CREAM else LOESS)
    px(img, mid + 1, y + 2, CREAM if buckle != CREAM else LOESS)
    px(img, x0 + 2, y + 2, INK)
    px(img, x1 - 3, y + 2, INK)


def draw_tray(img, bx, ty, yoff, pot_col=CINN_B, cups=True):
    """Tea tray with pot + cups — readable at 64."""
    fill_rect(img, 36 + bx, ty + 2 + yoff, 60 + bx, ty + 6 + yoff, WOOD)
    hline(img, 36 + bx, 60 + bx, ty + 2 + yoff, INK)
    hline(img, 36 + bx, 60 + bx, ty + 6 + yoff, INK_SOFT)
    fill_rect(img, 37 + bx, ty + 3 + yoff, 59 + bx, ty + 5 + yoff, WOOD_L)
    # pot
    fill_rect(img, 38 + bx, ty - 4 + yoff, 46 + bx, ty + 2 + yoff, pot_col)
    fill_rect(img, 40 + bx, ty - 6 + yoff, 44 + bx, ty - 4 + yoff, GOLD)
    px(img, 46 + bx, ty - 2 + yoff, WOOD)  # spout
    px(img, 47 + bx, ty - 1 + yoff, WOOD)
    px(img, 37 + bx, ty - 1 + yoff, WOOD)  # handle
    px(img, 36 + bx, ty + 0 + yoff, WOOD)
    if cups:
        fill_rect(img, 50 + bx, ty - 2 + yoff, 54 + bx, ty + 2 + yoff, CREAM)
        outline_rect(img, 50 + bx, ty - 2 + yoff, 54 + bx, ty + 2 + yoff, INK)
        fill_rect(img, 55 + bx, ty - 2 + yoff, 59 + bx, ty + 2 + yoff, PAPER_L)
        outline_rect(img, 55 + bx, ty - 2 + yoff, 59 + bx, ty + 2 + yoff, INK)


# ---------- characters (native 64) ----------

def qingyi_body(img, ox, oy, pose):
    breath = pose.get("breath", 0) * 2
    bx = ox + body_shift(pose)
    head_y = 2 + breath
    draw_head(img, 26 + bx, head_y + oy, hair=INK, face=SKIN, topknot=True, tall_knot=True)
    fill_rect(img, 22 + bx, 16 + breath + oy, 30 + bx, 20 + breath + oy, SKIN)
    ty = 18 + breath + oy
    # teal robe
    fill_rect(img, 16 + bx, ty, 36 + bx, ty + 24, TEAL)
    draw_shoulder(img, 26 + bx, ty, 12, TEAL, TEAL_B)
    fill_rect(img, 22 + bx, ty, 30 + bx, ty + 4, PAPER_L)  # collar
    fill_rect(img, 18 + bx, ty + 2, 22 + bx, ty + 6, TEAL_B)  # lapel
    fill_rect(img, 30 + bx, ty + 2, 34 + bx, ty + 6, TEAL_B)
    draw_robe_folds(img, 16 + bx, 36 + bx, ty + 8, NIGHT)
    draw_belt(img, 16 + bx, 36 + bx, ty + 14, WOOD_L, GOLD)
    vline(img, 24 + bx, ty + 4, ty + 24, NIGHT)
    vline(img, 25 + bx, ty + 6, ty + 22, TEAL_B)
    # hip sheath
    fill_rect(img, 34 + bx, ty + 16, 40 + bx, ty + 28, TEAL_B)
    outline_rect(img, 34 + bx, ty + 16, 40 + bx, ty + 28, INK)
    px(img, 34 + bx, ty + 14, GOLD)
    px(img, 38 + bx, ty + 26, WOOD)

    lift_l = pose.get("lift_l", 0)
    lift_r = pose.get("lift_r", 0)

    if pose.get("parry"):
        shake = pose.get("shake", 0) * 2
        fill_rect(img, 8 + bx, ty + 2, 18 + bx, ty + 14, TEAL)
        fill_rect(img, 6 + bx, ty - 2, 14 + bx, ty + 6, SKIN)
        fill_rect(img, 32 + bx + shake, ty - 14, 36 + bx + shake, ty + 20, TEAL_B)
        fill_rect(img, 30 + bx + shake, ty - 16, 38 + bx + shake, ty - 10, GOLD)
        fill_rect(img, 32 + bx + shake, ty + 20, 36 + bx + shake, ty + 26, WOOD)
        px(img, 34 + bx + shake, ty - 8, CREAM)
        if shake:
            px(img, 38 + bx, ty - 6, CREAM)
            px(img, 40 + bx, ty - 2, GOLD)
    elif pose.get("tray"):
        phase = pose.get("serve_phase", 1)
        fill_rect(img, 34 + bx, ty + 4, 46 + bx, ty + 10, TEAL)
        fill_rect(img, 42 + bx, ty + 6, 50 + bx, ty + 12, SKIN)
        yoff = -2 if phase == 0 else (2 if phase == 2 else 0)
        draw_tray(img, bx, ty, yoff, TEAL_B)
        if phase == 2:
            px(img, 47 + bx, ty + 0, WOOD)
            px(img, 48 + bx, ty + 2, LOESS)
            px(img, 48 + bx, ty + 4, LOESS)
            px(img, 50 + bx, ty + 6, LOESS)
            px(img, 52 + bx, ty + 4, CREAM)
        fill_rect(img, 36 + bx, ty + 16, 40 + bx, ty + 36, TEAL_B)
        px(img, 36 + bx, ty + 14, GOLD)
    elif pose.get("attack_phase") is not None:
        ap = pose["attack_phase"]
        if ap == 0:
            fill_rect(img, 8 + bx, ty + 2, 20 + bx, ty + 14, TEAL)
            fill_rect(img, 4 + bx, ty + 8, 12 + bx, ty + 16, SKIN)
            fill_rect(img, 2 + bx, ty - 14, 8 + bx, ty + 28, TEAL_B)
            fill_rect(img, 0 + bx, ty - 18, 10 + bx, ty - 12, GOLD)
            px(img, 4 + bx, ty - 10, CREAM)
            px(img, 4 + bx, ty + 26, WOOD)
            fill_rect(img, 30 + bx, ty + 8, 40 + bx, ty + 18, TEAL)
            fill_rect(img, 34 + bx, ty + 14, 42 + bx, ty + 20, SKIN)
        elif ap == 1:
            fill_rect(img, 30 + bx, ty + 0, 48 + bx, ty + 10, TEAL)
            fill_rect(img, 42 + bx, ty + 2, 52 + bx, ty + 10, SKIN)
            fill_rect(img, bx + 36, ty + 2, bx + 44, ty + 8, GOLD)
            fill_rect(img, bx + 42, ty - 4, bx + 64, ty + 2, TEAL_B)
            px(img, bx + 40, ty + 0, WOOD)
            px(img, bx + 62, ty - 6, TEAL_B)
            px(img, bx + 60, ty - 4, CREAM)
            px(img, bx + 58, ty - 2, GOLD)
            fill_rect(img, 2 + bx, ty + 6, 14 + bx, ty + 16, TEAL)
            fill_rect(img, 0 + bx, ty + 12, 8 + bx, ty + 18, SKIN)
        elif ap == 2:
            fill_rect(img, 32 + bx, ty + 2, 52 + bx, ty + 12, TEAL)
            fill_rect(img, 46 + bx, ty + 4, 56 + bx, ty + 12, SKIN)
            fill_rect(img, bx + 40, ty + 0, bx + 48, ty + 6, GOLD)
            fill_rect(img, bx + 46, ty - 2, bx + 64, ty + 4, TEAL_B)
            px(img, bx + 62, ty - 4, CREAM)
            px(img, bx + 60, ty - 2, CREAM)
            px(img, bx + 62, ty + 0, TEAL_B)
            px(img, bx + 58, ty - 4, GOLD)
            px(img, bx + 56, ty - 2, CREAM)
            px(img, bx + 52, ty - 6, TEAL_B)
            fill_rect(img, 4 + bx, ty + 8, 16 + bx, ty + 18, TEAL)
            fill_rect(img, 2 + bx, ty + 14, 10 + bx, ty + 20, SKIN)
        else:
            fill_rect(img, 28 + bx, ty + 4, 42 + bx, ty + 14, TEAL)
            fill_rect(img, 36 + bx, ty + 10, 44 + bx, ty + 16, SKIN)
            fill_rect(img, bx + 36, ty + 2, bx + 42, ty + 28, TEAL_B)
            fill_rect(img, bx + 34, ty + 0, bx + 44, ty + 4, GOLD)
            px(img, bx + 38, ty + 26, WOOD)
            fill_rect(img, 8 + bx, ty + 6, 18 + bx, ty + 16, TEAL)
            fill_rect(img, 6 + bx, ty + 12, 14 + bx, ty + 18, SKIN)
    elif not pose.get("hurt"):
        fill_rect(img, 8 + bx, ty + 4, 18 + bx, ty + 16, TEAL)
        fill_rect(img, 6 + bx, ty + 12, 14 + bx, ty + 18, SKIN)
        draw_cuff(img, 6 + bx, ty + 12, 14 + bx, ty + 18, TEAL, PAPER_L)
        if lift_r:
            fill_rect(img, 32 + bx, ty + 0, 42 + bx, ty + 10, TEAL)
            fill_rect(img, 38 + bx, ty + 6, 46 + bx, ty + 12, SKIN)
        elif lift_l:
            fill_rect(img, 32 + bx, ty + 8, 40 + bx, ty + 20, TEAL)
            fill_rect(img, 36 + bx, ty + 16, 44 + bx, ty + 22, SKIN)
        else:
            fill_rect(img, 32 + bx, ty + 4, 40 + bx, ty + 14, TEAL)
            fill_rect(img, 36 + bx, ty + 10, 42 + bx, ty + 16, SKIN)
        fill_rect(img, 36 + bx, ty + 2, 40 + bx, ty + 32, TEAL_B)
        fill_rect(img, 34 + bx, ty + 28, 42 + bx, ty + 32, WOOD)
        fill_rect(img, 34 + bx, ty, 42 + bx, ty + 4, GOLD)

    ly = ty + 24
    fill_rect(img, 18 + bx - (4 if lift_l else 0), ly - lift_l, 26 + bx - (4 if lift_l else 0), ly + 12 - lift_l, TEAL)
    fill_rect(img, 26 + bx + (4 if lift_r else 0), ly - lift_r, 34 + bx + (4 if lift_r else 0), ly + 12 - lift_r, TEAL)
    if lift_l:
        hline(img, 18 + bx - 4, 26 + bx - 4, ly - lift_l + 4, NIGHT)
    if lift_r:
        hline(img, 26 + bx + 4, 34 + bx + 4, ly - lift_r + 4, NIGHT)
    draw_hem_sway(img, 16 + bx, 36 + bx, ly + 2, lift_l, lift_r, TEAL, NIGHT)
    stride = 6 if (lift_l or lift_r) else 0
    draw_feet(img, 16 + bx, ly + 12, 28 + bx, ly + 12, INK_SOFT, lift_l, lift_r, stride=stride)

    if pose.get("hurt"):
        hp = pose.get("hurt_phase", 0)
        if hp == 0:
            fill_rect(img, 34 + bx, ty - 4, 48 + bx, ty + 6, TEAL)
            fill_rect(img, 44 + bx, ty - 6, 54 + bx, ty + 2, SKIN)
            fill_rect(img, 2 + bx, ty + 10, 14 + bx, ty + 20, TEAL)
            fill_rect(img, 0 + bx, ty + 16, 8 + bx, ty + 22, SKIN)
            for dx, dy, c in [(30, 10, CINN_B), (34, 12, BLOOD), (36, 16, CINN_B),
                              (20, 20, BLOOD), (38, 18, BLOOD), (40, 10, CINN_B), (24, 14, BLOOD)]:
                px(img, dx + bx, dy + oy, c)
        else:
            fill_rect(img, 36 + bx, ty + 8, 50 + bx, ty + 18, TEAL)
            fill_rect(img, 46 + bx, ty + 14, 56 + bx, ty + 22, SKIN)
            fill_rect(img, 4 + bx, ty + 4, 16 + bx, ty + 14, TEAL)
            fill_rect(img, 2 + bx, ty + 10, 10 + bx, ty + 16, SKIN)
            for dx, dy, c in [(28, 8, BLOOD), (32, 14, CINN_B), (18, 24, BLOOD),
                              (36, 22, CINN_B), (42, 16, BLOOD), (22, 18, CINN_B), (40, 26, BLOOD)]:
                px(img, dx + bx, dy + oy, c)


def tiezhang_body(img, ox, oy, pose):
    breath = pose.get("breath", 0) * 2
    bx = ox + body_shift(pose)
    head_y = 2 + breath
    draw_head(img, 26 + bx, head_y + oy, hair=INK, face=SKIN, hair_side=INK, bun=True, double_bun=True)
    fill_rect(img, 22 + bx, head_y + oy, 30 + bx, head_y + 4 + oy, CINN)
    px(img, 32 + bx, head_y + 2 + oy, GOLD)
    px(img, 34 + bx, head_y + 4 + oy, CINN_B)
    fill_rect(img, 22 + bx, 16 + breath + oy, 30 + bx, 20 + breath + oy, SKIN)
    ty = 18 + breath + oy
    fill_rect(img, 16 + bx, ty, 36 + bx, ty + 24, ROBE_R)
    draw_shoulder(img, 26 + bx, ty, 12, ROBE_R, GOLD)
    fill_rect(img, 20 + bx, ty, 32 + bx, ty + 4, PAPER_L)
    fill_rect(img, 18 + bx, ty + 4, 22 + bx, ty + 8, BLOOD)
    draw_robe_folds(img, 16 + bx, 36 + bx, ty + 8, BLOOD)
    draw_belt(img, 16 + bx, 36 + bx, ty + 14, BLOOD, GOLD)
    # medicine pouch
    fill_rect(img, 34 + bx, ty + 12, 46 + bx, ty + 26, JADE_B)
    outline_rect(img, 34 + bx, ty + 12, 46 + bx, ty + 26, INK)
    px(img, 38 + bx, ty + 16, GOLD)
    px(img, 40 + bx, ty + 20, JADE)
    px(img, 42 + bx, ty + 18, JADE)
    px(img, 36 + bx, ty + 10, WOOD)
    px(img, 37 + bx, ty + 10, WOOD)

    lift_l = pose.get("lift_l", 0)
    lift_r = pose.get("lift_r", 0)

    if pose.get("tray"):
        phase = pose.get("serve_phase", 1)
        fill_rect(img, 34 + bx, ty + 4, 46 + bx, ty + 10, ROBE_R)
        fill_rect(img, 42 + bx, ty + 6, 50 + bx, ty + 12, SKIN)
        yoff = -2 if phase == 0 else (2 if phase == 2 else 0)
        draw_tray(img, bx, ty, yoff, JADE_B)
        if phase == 2:
            px(img, 48 + bx, ty + 4, JADE)
            px(img, 50 + bx, ty + 6, JADE_B)
    elif pose.get("parry"):
        shake = pose.get("shake", 0) * 2
        fill_rect(img, 30 + bx, ty - 6, 44 + bx, ty + 8, ROBE_R)
        fill_rect(img, 34 + bx + shake, ty - 12, 50 + bx + shake, ty + 2, SKIN)
        fill_rect(img, 44 + bx + shake, ty - 14, 52 + bx + shake, ty - 6, JADE_B)
        px(img, 48 + bx + shake, ty - 16, CREAM)
        px(img, 50 + bx + shake, ty - 10, JADE)
        if shake:
            px(img, 54 + bx, ty - 12, CREAM)
    elif pose.get("attack_phase") is not None:
        ap = pose["attack_phase"]
        if ap == 0:
            fill_rect(img, 4 + bx, ty - 4, 18 + bx, ty + 10, ROBE_R)
            fill_rect(img, 2 + bx, ty - 2, 10 + bx, ty + 8, SKIN)
            fill_rect(img, 0 + bx, ty - 6, 8 + bx, ty + 0, JADE_B)
            px(img, 2 + bx, ty - 8, CREAM)
            px(img, 4 + bx, ty - 4, JADE)
            fill_rect(img, 30 + bx, ty + 4, 42 + bx, ty + 14, ROBE_R)
            fill_rect(img, 36 + bx, ty + 8, 44 + bx, ty + 16, SKIN)
        elif ap == 1:
            fill_rect(img, 30 + bx, ty - 2, 50 + bx, ty + 10, ROBE_R)
            fill_rect(img, 42 + bx, ty + 0, 58 + bx, ty + 10, SKIN)
            fill_rect(img, 52 + bx, ty - 2, 60 + bx, ty + 4, JADE_B)
            px(img, 56 + bx, ty - 4, JADE)
            fill_rect(img, 2 + bx, ty + 6, 14 + bx, ty + 16, ROBE_R)
            fill_rect(img, 0 + bx, ty + 12, 8 + bx, ty + 18, SKIN)
        elif ap == 2:
            fill_rect(img, 32 + bx, ty + 0, 54 + bx, ty + 12, ROBE_R)
            fill_rect(img, 46 + bx, ty + 2, 62 + bx, ty + 12, SKIN)
            fill_rect(img, 56 + bx, ty - 2, 64, ty + 6, JADE_B)
            px(img, 62, ty - 4, CREAM)
            px(img, 60, ty - 2, CREAM)
            px(img, 62, ty + 2, GOLD)
            px(img, 58, ty - 4, JADE)
            px(img, 56, ty + 0, CREAM)
            px(img, 54, ty - 6, JADE_B)
            fill_rect(img, 4 + bx, ty + 8, 16 + bx, ty + 18, ROBE_R)
            fill_rect(img, 2 + bx, ty + 14, 10 + bx, ty + 20, SKIN)
        else:
            fill_rect(img, 28 + bx, ty + 4, 44 + bx, ty + 14, ROBE_R)
            fill_rect(img, 36 + bx, ty + 8, 46 + bx, ty + 16, SKIN)
            px(img, 42 + bx, ty + 6, JADE_B)
            fill_rect(img, 6 + bx, ty + 6, 16 + bx, ty + 16, ROBE_R)
            fill_rect(img, 4 + bx, ty + 12, 12 + bx, ty + 18, SKIN)
    elif not pose.get("hurt"):
        fill_rect(img, 6 + bx, ty + 4, 16 + bx, ty + 16, ROBE_R)
        fill_rect(img, 4 + bx, ty + 12, 12 + bx, ty + 18, SKIN)
        if lift_r:
            fill_rect(img, 32 + bx, ty + 0, 42 + bx, ty + 10, ROBE_R)
            fill_rect(img, 38 + bx, ty + 6, 44 + bx, ty + 12, SKIN)
        elif lift_l:
            fill_rect(img, 32 + bx, ty + 8, 40 + bx, ty + 18, ROBE_R)
        else:
            fill_rect(img, 30 + bx, ty + 4, 38 + bx, ty + 12, ROBE_R)

    ly = ty + 24
    fill_rect(img, 18 + bx - (4 if lift_l else 0), ly - lift_l, 26 + bx - (4 if lift_l else 0), ly + 12 - lift_l, ROBE_R)
    fill_rect(img, 26 + bx + (4 if lift_r else 0), ly - lift_r, 34 + bx + (4 if lift_r else 0), ly + 12 - lift_r, ROBE_R)
    if lift_l:
        hline(img, 18 + bx - 4, 26 + bx - 4, ly - lift_l + 4, BLOOD)
    if lift_r:
        hline(img, 26 + bx + 4, 34 + bx + 4, ly - lift_r + 4, BLOOD)
    draw_hem_sway(img, 16 + bx, 36 + bx, ly + 2, lift_l, lift_r, ROBE_R, BLOOD)
    draw_feet(img, 16 + bx, ly + 12, 28 + bx, ly + 12, INK_SOFT, lift_l, lift_r,
              stride=6 if (lift_l or lift_r) else 0)
    if pose.get("hurt"):
        hp = pose.get("hurt_phase", 0)
        if hp == 0:
            fill_rect(img, 34 + bx, ty - 4, 50 + bx, ty + 6, ROBE_R)
            fill_rect(img, 44 + bx, ty - 6, 54 + bx, ty + 2, SKIN)
            fill_rect(img, 2 + bx, ty + 10, 14 + bx, ty + 20, ROBE_R)
            for dx, dy, c in [(30, 10, CINN_B), (34, 14, BLOOD), (18, 20, BLOOD),
                              (36, 18, CINN_B), (40, 12, BLOOD), (24, 16, CINN_B)]:
                px(img, dx + bx, dy + oy, c)
        else:
            fill_rect(img, 36 + bx, ty + 8, 52 + bx, ty + 18, ROBE_R)
            fill_rect(img, 46 + bx, ty + 14, 56 + bx, ty + 22, SKIN)
            fill_rect(img, 4 + bx, ty + 4, 16 + bx, ty + 14, ROBE_R)
            for dx, dy, c in [(28, 8, BLOOD), (32, 16, CINN_B), (16, 24, BLOOD),
                              (38, 22, CINN_B), (42, 18, BLOOD), (22, 18, CINN_B)]:
                px(img, dx + bx, dy + oy, c)


def langren_body(img, ox, oy, pose):
    breath = pose.get("breath", 0) * 2
    bx = ox + body_shift(pose)
    head_y = 2 + breath
    draw_head(img, 26 + bx, head_y + oy, hair=INK, face=SKIN_D, fringe=True)
    fill_rect(img, 14 + bx, head_y + 4 + oy, 38 + bx, head_y + 8 + oy, CINN_B)
    fill_rect(img, 36 + bx, head_y + 6 + oy, 44 + bx, head_y + 10 + oy, CINN)
    px(img, 42 + bx, head_y + 10 + oy, BLOOD)
    px(img, 43 + bx, head_y + 11 + oy, BLOOD)
    fill_rect(img, 22 + bx, 16 + breath + oy, 30 + bx, 20 + breath + oy, SKIN_D)
    ty = 18 + breath + oy
    fill_rect(img, 16 + bx, ty, 36 + bx, ty + 24, INK_SOFT)
    draw_shoulder(img, 26 + bx, ty, 14, WOOD, CINN_B)
    fill_rect(img, 18 + bx, ty + 2, 34 + bx, ty + 10, WOOD)
    fill_rect(img, 20 + bx, ty + 4, 32 + bx, ty + 8, WOOD_L)
    px(img, 24 + bx, ty + 6, GOLD)
    px(img, 28 + bx, ty + 6, GOLD)
    draw_robe_folds(img, 16 + bx, 36 + bx, ty + 12, NIGHT)
    draw_belt(img, 16 + bx, 36 + bx, ty + 16, FRAME, CINN_B)

    lift_l = pose.get("lift_l", 0)
    lift_r = pose.get("lift_r", 0)

    if pose.get("tray"):
        phase = pose.get("serve_phase", 1)
        fill_rect(img, 34 + bx, ty + 4, 46 + bx, ty + 10, INK_SOFT)
        fill_rect(img, 42 + bx, ty + 6, 50 + bx, ty + 12, SKIN_D)
        yoff = -2 if phase == 0 else (2 if phase == 2 else 0)
        draw_tray(img, bx, ty, yoff, CREAM)
        fill_rect(img, 8 + bx, ty + 6, 14 + bx, ty + 34, INK)
        px(img, 10 + bx, ty + 4, CINN_B)
    elif pose.get("parry"):
        shake = pose.get("shake", 0) * 2
        fill_rect(img, 28 + bx, ty - 6, 38 + bx, ty + 8, INK_SOFT)
        fill_rect(img, 32 + bx + shake, ty - 16, 44 + bx + shake, ty + 20, INK_SOFT)
        fill_rect(img, 34 + bx + shake, ty - 14, 42 + bx + shake, ty + 16, MIST)
        fill_rect(img, 32 + bx + shake, ty + 20, 44 + bx + shake, ty + 26, WOOD)
        px(img, 36 + bx + shake, ty - 18, CINN_B)
        if shake:
            px(img, 46 + bx, ty - 10, CREAM)
            px(img, 48 + bx, ty - 6, GOLD)
    elif pose.get("attack_phase") is not None:
        ap = pose["attack_phase"]
        if ap == 0:
            fill_rect(img, 8 + bx, ty + 2, 20 + bx, ty + 14, INK_SOFT)
            fill_rect(img, 4 + bx, ty + 8, 12 + bx, ty + 16, SKIN_D)
            fill_rect(img, 0 + bx, ty - 16, 8 + bx, ty + 26, INK_SOFT)
            fill_rect(img, 2 + bx, ty - 14, 6 + bx, ty + 22, MIST)
            fill_rect(img, 0 + bx, ty + 26, 8 + bx, ty + 32, WOOD)
            px(img, 2 + bx, ty - 18, CINN_B)
            px(img, 4 + bx, ty - 12, CREAM)
            fill_rect(img, 30 + bx, ty + 8, 40 + bx, ty + 18, INK_SOFT)
            fill_rect(img, 34 + bx, ty + 14, 42 + bx, ty + 20, SKIN_D)
        elif ap == 1:
            fill_rect(img, 30 + bx, ty + 0, 48 + bx, ty + 10, INK_SOFT)
            fill_rect(img, 40 + bx, ty + 2, 50 + bx, ty + 10, SKIN_D)
            fill_rect(img, 36 + bx, ty - 2, 44 + bx, ty + 6, WOOD)
            fill_rect(img, 40 + bx, ty - 6, 64, ty + 2, INK_SOFT)
            fill_rect(img, 42 + bx, ty - 4, 62, ty + 0, MIST)
            px(img, 62, ty - 8, INK_SOFT)
            px(img, 60, ty - 6, CREAM)
            px(img, 58, ty - 4, CINN_B)
            fill_rect(img, 2 + bx, ty + 6, 14 + bx, ty + 16, INK_SOFT)
            fill_rect(img, 0 + bx, ty + 12, 8 + bx, ty + 18, SKIN_D)
        elif ap == 2:
            fill_rect(img, 32 + bx, ty + 2, 50 + bx, ty + 12, INK_SOFT)
            fill_rect(img, 44 + bx, ty + 4, 54 + bx, ty + 12, SKIN_D)
            fill_rect(img, 38 + bx, ty + 0, 46 + bx, ty + 6, WOOD)
            fill_rect(img, 42 + bx, ty - 2, 64, ty + 6, INK_SOFT)
            fill_rect(img, 44 + bx, ty + 0, 62, ty + 4, CINN_B)
            px(img, 62, ty - 4, CREAM)
            px(img, 60, ty - 2, CREAM)
            px(img, 62, ty + 2, GOLD)
            px(img, 58, ty - 4, CINN)
            px(img, 56, ty - 2, CREAM)
            px(img, 54, ty - 6, CINN_B)
            fill_rect(img, 4 + bx, ty + 8, 16 + bx, ty + 18, INK_SOFT)
            fill_rect(img, 2 + bx, ty + 14, 10 + bx, ty + 20, SKIN_D)
        else:
            fill_rect(img, 28 + bx, ty + 4, 42 + bx, ty + 14, INK_SOFT)
            fill_rect(img, 36 + bx, ty + 4, 44 + bx, ty + 32, INK_SOFT)
            fill_rect(img, 38 + bx, ty + 6, 42 + bx, ty + 28, MIST)
            fill_rect(img, 36 + bx, ty + 30, 44 + bx, ty + 34, WOOD)
            px(img, 38 + bx, ty + 2, CINN_B)
            fill_rect(img, 6 + bx, ty + 6, 16 + bx, ty + 16, INK_SOFT)
            fill_rect(img, 4 + bx, ty + 12, 12 + bx, ty + 18, SKIN_D)
    elif not pose.get("hurt"):
        fill_rect(img, 6 + bx, ty + 4, 16 + bx, ty + 16, INK_SOFT)
        fill_rect(img, 4 + bx, ty + 12, 12 + bx, ty + 18, SKIN_D)
        fill_rect(img, 36 + bx, ty + 2, 44 + bx, ty + 32, INK_SOFT)
        fill_rect(img, 38 + bx, ty + 4, 42 + bx, ty + 28, MIST)
        fill_rect(img, 36 + bx, ty + 32, 44 + bx, ty + 36, WOOD)
        px(img, 38 + bx, ty, CINN_B)
        if lift_r:
            fill_rect(img, 32 + bx, ty + 0, 40 + bx, ty + 10, INK_SOFT)
        elif lift_l:
            fill_rect(img, 32 + bx, ty + 8, 38 + bx, ty + 18, INK_SOFT)

    ly = ty + 24
    fill_rect(img, 18 + bx - (4 if lift_l else 0), ly - lift_l, 26 + bx - (4 if lift_l else 0), ly + 12 - lift_l, INK_SOFT)
    fill_rect(img, 26 + bx + (4 if lift_r else 0), ly - lift_r, 34 + bx + (4 if lift_r else 0), ly + 12 - lift_r, INK_SOFT)
    draw_hem_sway(img, 16 + bx, 36 + bx, ly + 2, lift_l, lift_r, INK_SOFT, NIGHT)
    draw_feet(img, 16 + bx, ly + 12, 28 + bx, ly + 12, INK, lift_l, lift_r,
              stride=6 if (lift_l or lift_r) else 0)
    if pose.get("hurt"):
        hp = pose.get("hurt_phase", 0)
        if hp == 0:
            fill_rect(img, 34 + bx, ty - 6, 50 + bx, ty + 4, INK_SOFT)
            fill_rect(img, 44 + bx, ty - 8, 54 + bx, ty + 0, SKIN_D)
            fill_rect(img, 2 + bx, ty + 10, 14 + bx, ty + 20, INK_SOFT)
            for dx, dy, c in [(28, 8, CINN_B), (32, 12, BLOOD), (22, 22, BLOOD),
                              (38, 16, CINN_B), (40, 10, BLOOD), (24, 14, CINN_B)]:
                px(img, dx + bx, dy + oy, c)
        else:
            fill_rect(img, 36 + bx, ty + 8, 52 + bx, ty + 18, INK_SOFT)
            fill_rect(img, 46 + bx, ty + 14, 56 + bx, ty + 22, SKIN_D)
            fill_rect(img, 4 + bx, ty + 4, 16 + bx, ty + 14, INK_SOFT)
            for dx, dy, c in [(26, 6, BLOOD), (30, 14, CINN_B), (20, 26, BLOOD),
                              (36, 20, CINN_B), (42, 16, BLOOD), (22, 18, CINN), (40, 24, BLOOD)]:
                px(img, dx + bx, dy + oy, c)


def qinshi_body(img, ox, oy, pose):
    breath = pose.get("breath", 0) * 2
    bx = ox + body_shift(pose)
    head_y = 2 + breath
    draw_head(img, 26 + bx, head_y + oy, hair=PAPER_L, face=SKIN, hair_side=PAPER_L, bald_cap=True)
    px(img, 24 + bx, head_y + 8 + oy, VIOLET)
    px(img, 26 + bx, head_y + 8 + oy, VIOLET)
    px(img, 28 + bx, head_y + 8 + oy, GOLD)
    px(img, 22 + bx, head_y + 10 + oy, VIOLET)
    fill_rect(img, 22 + bx, 16 + breath + oy, 30 + bx, 20 + breath + oy, SKIN)
    ty = 18 + breath + oy
    fill_rect(img, 16 + bx, ty, 36 + bx, ty + 12, VIOLET)
    draw_shoulder(img, 26 + bx, ty, 12, VIOLET, GOLD)
    fill_rect(img, 14 + bx, ty + 12, 38 + bx, ty + 26, PAPER_L)
    fill_rect(img, 20 + bx, ty, 32 + bx, ty + 4, PAPER_L)
    draw_robe_folds(img, 14 + bx, 38 + bx, ty + 16, PAPER_D)
    draw_belt(img, 16 + bx, 36 + bx, ty + 10, GOLD, CREAM)
    fill_rect(img, 10 + bx, ty + 4, 16 + bx, ty + 24, VIOLET)
    fill_rect(img, 10 + bx, ty + 20, 16 + bx, ty + 24, PAPER_L)

    lift_l = pose.get("lift_l", 0)
    lift_r = pose.get("lift_r", 0)

    if pose.get("tray") or pose.get("hold"):
        phase = pose.get("serve_phase", 1)
        fill_rect(img, 32 + bx, ty + 6, 44 + bx, ty + 14, VIOLET)
        fill_rect(img, 40 + bx, ty + 8, 48 + bx, ty + 14, SKIN)
        yoff = -2 if phase == 0 else (2 if phase == 2 else 0)
        # guqin
        fill_rect(img, 32 + bx, ty + 4 + yoff, 62 + bx, ty + 10 + yoff, WOOD)
        hline(img, 34 + bx, 60 + bx, ty + 6 + yoff, WOOD_L)
        px(img, 36 + bx, ty + 4 + yoff, GOLD)
        px(img, 58 + bx, ty + 4 + yoff, GOLD)
        hline(img, 36 + bx, 58 + bx, ty + 6 + yoff, INK)
        hline(img, 36 + bx, 58 + bx, ty + 8 + yoff, INK_SOFT)
        if phase == 2:
            px(img, 48 + bx, ty + 2, CREAM)
            px(img, 50 + bx, ty + 2, SKIN)
    elif pose.get("parry"):
        shake = pose.get("shake", 0) * 2
        fill_rect(img, 28 + bx, ty - 4, 38 + bx, ty + 8, VIOLET)
        fill_rect(img, 32 + bx + shake, ty - 16, 36 + bx + shake, ty + 16, WOOD)
        fill_rect(img, 28 + bx + shake, ty - 20, 40 + bx + shake, ty - 10, PAPER_L)
        px(img, 30 + bx + shake, ty - 18, CREAM)
        px(img, 38 + bx + shake, ty - 18, CREAM)
        if shake:
            px(img, 42 + bx, ty - 14, GOLD)
            px(img, 44 + bx, ty - 10, CREAM)
    elif pose.get("attack_phase") is not None:
        ap = pose["attack_phase"]
        if ap == 0:
            fill_rect(img, 8 + bx, ty + 2, 20 + bx, ty + 14, VIOLET)
            fill_rect(img, 4 + bx, ty + 8, 12 + bx, ty + 16, SKIN)
            fill_rect(img, 2 + bx, ty - 10, 8 + bx, ty + 26, WOOD)
            fill_rect(img, 0 + bx, ty - 20, 10 + bx, ty - 10, PAPER_L)
            vline(img, 4 + bx, ty - 20, ty - 8, CREAM)
            px(img, 2 + bx, ty - 18, CREAM)
            px(img, 6 + bx, ty - 16, CREAM)
            px(img, 4 + bx, ty - 8, GOLD)
            fill_rect(img, 30 + bx, ty + 8, 40 + bx, ty + 18, VIOLET)
            fill_rect(img, 34 + bx, ty + 14, 42 + bx, ty + 20, SKIN)
        elif ap == 1:
            fill_rect(img, 30 + bx, ty + 0, 48 + bx, ty + 10, VIOLET)
            fill_rect(img, 40 + bx, ty + 2, 50 + bx, ty + 10, SKIN)
            fill_rect(img, 38 + bx, ty - 4, 64, ty + 2, WOOD)
            fill_rect(img, 54, ty - 8, 64, ty - 2, PAPER_L)
            px(img, 62, ty - 10, CREAM)
            px(img, 60, ty - 6, CREAM)
            px(img, 56, ty - 4, GOLD)
            fill_rect(img, 2 + bx, ty + 6, 14 + bx, ty + 16, VIOLET)
            fill_rect(img, 0 + bx, ty + 12, 8 + bx, ty + 18, SKIN)
        elif ap == 2:
            fill_rect(img, 32 + bx, ty + 2, 50 + bx, ty + 12, VIOLET)
            fill_rect(img, 44 + bx, ty + 4, 54 + bx, ty + 12, SKIN)
            fill_rect(img, 40 + bx, ty - 2, 64, ty + 4, WOOD)
            fill_rect(img, 56, ty - 6, 64, ty + 0, PAPER_L)
            px(img, 62, ty - 8, CREAM)
            px(img, 60, ty - 4, CREAM)
            px(img, 62, ty + 0, GOLD)
            px(img, 58, ty - 6, GOLD)
            px(img, 56, ty - 2, CREAM)
            px(img, 54, ty - 8, PAPER_L)
            fill_rect(img, 4 + bx, ty + 8, 16 + bx, ty + 18, VIOLET)
            fill_rect(img, 2 + bx, ty + 14, 10 + bx, ty + 20, SKIN)
        else:
            fill_rect(img, 28 + bx, ty + 4, 42 + bx, ty + 14, VIOLET)
            fill_rect(img, 34 + bx, ty + 4, 40 + bx, ty + 28, WOOD)
            hline(img, 34 + bx, 40 + bx, ty + 8, WOOD_L)
            px(img, 36 + bx, ty + 4, GOLD)
            fill_rect(img, 6 + bx, ty + 6, 16 + bx, ty + 16, VIOLET)
            fill_rect(img, 4 + bx, ty + 12, 12 + bx, ty + 18, SKIN)
    elif not pose.get("hurt"):
        fill_rect(img, 6 + bx, ty + 4, 16 + bx, ty + 16, VIOLET)
        fill_rect(img, 4 + bx, ty + 12, 12 + bx, ty + 18, SKIN)
        fill_rect(img, 36 + bx, ty + 8, 42 + bx, ty + 30, WOOD)
        hline(img, 36 + bx, 42 + bx, ty + 12, WOOD_L)
        px(img, 38 + bx, ty + 8, GOLD)
        if lift_r:
            fill_rect(img, 32 + bx, ty + 0, 40 + bx, ty + 10, VIOLET)
        elif lift_l:
            fill_rect(img, 32 + bx, ty + 8, 38 + bx, ty + 18, VIOLET)

    ly = ty + 26
    fill_rect(img, 18 + bx - (4 if lift_l else 0), ly - lift_l, 26 + bx - (4 if lift_l else 0), ly + 10 - lift_l, PAPER_L)
    fill_rect(img, 26 + bx + (4 if lift_r else 0), ly - lift_r, 34 + bx + (4 if lift_r else 0), ly + 10 - lift_r, PAPER_L)
    draw_hem_sway(img, 14 + bx, 38 + bx, ly + 2, lift_l, lift_r, PAPER_L, PAPER_D)
    draw_feet(img, 16 + bx, ly + 10, 28 + bx, ly + 10, INK_SOFT, lift_l, lift_r,
              stride=6 if (lift_l or lift_r) else 0)
    if pose.get("hurt"):
        hp = pose.get("hurt_phase", 0)
        if hp == 0:
            fill_rect(img, 34 + bx, ty - 4, 50 + bx, ty + 6, VIOLET)
            fill_rect(img, 44 + bx, ty - 6, 54 + bx, ty + 2, SKIN)
            fill_rect(img, 2 + bx, ty + 10, 14 + bx, ty + 20, VIOLET)
            for dx, dy, c in [(30, 10, CINN_B), (34, 14, BLOOD), (20, 20, BLOOD),
                              (36, 18, CINN_B), (40, 12, BLOOD), (24, 16, CINN_B)]:
                px(img, dx + bx, dy + oy, c)
        else:
            fill_rect(img, 36 + bx, ty + 8, 52 + bx, ty + 18, VIOLET)
            fill_rect(img, 46 + bx, ty + 14, 56 + bx, ty + 22, SKIN)
            fill_rect(img, 4 + bx, ty + 4, 16 + bx, ty + 14, VIOLET)
            for dx, dy, c in [(28, 8, BLOOD), (32, 16, CINN_B), (18, 24, BLOOD),
                              (38, 22, CINN_B), (42, 18, BLOOD), (22, 18, CINN)]:
                px(img, dx + bx, dy + oy, c)


def xiaoer_body(img, ox, oy, pose):
    breath = pose.get("breath", 0) * 2
    bx = ox + body_shift(pose)
    head_y = 2 + breath
    draw_head(img, 26 + bx, head_y + oy, hair=INK, face=SKIN, hat_wood=True)
    fill_rect(img, 22 + bx, 16 + breath + oy, 30 + bx, 20 + breath + oy, SKIN)
    ty = 18 + breath + oy
    fill_rect(img, 16 + bx, ty, 36 + bx, ty + 22, WOOD)
    draw_shoulder(img, 26 + bx, ty, 10, WOOD, WOOD_L)
    fill_rect(img, 18 + bx, ty + 8, 34 + bx, ty + 26, PAPER)
    fill_rect(img, 20 + bx, ty + 10, 32 + bx, ty + 24, PAPER_L)
    draw_robe_folds(img, 18 + bx, 34 + bx, ty + 14, PAPER_D)
    draw_belt(img, 16 + bx, 36 + bx, ty + 6, CINN, GOLD)
    px(img, 18 + bx, ty + 8, CINN)
    px(img, 32 + bx, ty + 8, CINN)
    fill_rect(img, 24 + bx, ty + 16, 30 + bx, ty + 22, PAPER)
    outline_rect(img, 24 + bx, ty + 16, 30 + bx, ty + 22, PAPER_D)

    lift_l = pose.get("lift_l", 0)
    lift_r = pose.get("lift_r", 0)

    if pose.get("tray") or (pose.get("serve_phase") is not None and pose.get("wipe_phase") is None
                            and pose.get("attack_phase") is None and not pose.get("parry")
                            and not pose.get("hurt")):
        sp = pose.get("serve_phase", 1)
        yoff = -4 if sp == 0 else (0 if sp == 1 else 2)
        arm_ext = 2 if sp >= 1 else 0
        fill_rect(img, 32 + bx + arm_ext, ty + 4, 44 + bx + arm_ext, ty + 12, WOOD)
        fill_rect(img, 40 + bx + arm_ext, ty + 6, 48 + bx + arm_ext, ty + 12, SKIN)
        fill_rect(img, 34 + bx + arm_ext, ty + yoff, 62 + bx + arm_ext, ty + 4 + yoff, WOOD_L)
        hline(img, 34 + bx + arm_ext, 62 + bx + arm_ext, ty + yoff, INK)
        hline(img, 34 + bx + arm_ext, 62 + bx + arm_ext, ty + 4 + yoff, WOOD)
        pot_x = 38 + bx + arm_ext + (2 if sp == 2 else 0)
        fill_rect(img, pot_x, ty - 8 + yoff, pot_x + 10, ty + yoff, CINN_B)
        fill_rect(img, pot_x + 2, ty - 10 + yoff, pot_x + 8, ty - 8 + yoff, GOLD)
        px(img, pot_x + 10, ty - 6 + yoff, WOOD)
        px(img, pot_x + 11, ty - 4 + yoff, WOOD)
        px(img, pot_x - 2, ty - 4 + yoff, WOOD)
        fill_rect(img, 52 + bx + arm_ext, ty - 4 + yoff, 56 + bx + arm_ext, ty + yoff, CREAM)
        outline_rect(img, 52 + bx + arm_ext, ty - 4 + yoff, 56 + bx + arm_ext, ty + yoff, INK)
        fill_rect(img, 58 + bx + arm_ext, ty - 4 + yoff, 62 + bx + arm_ext, ty + yoff, PAPER_L)
        if sp == 1:
            px(img, pot_x + 4, ty - 12 + yoff, MIST)
            px(img, pot_x + 6, ty - 14 + yoff, MIST)
        if sp == 2:
            px(img, pot_x + 10, ty + 0, WOOD)
            px(img, pot_x + 12, ty + 2, LOESS)
            px(img, pot_x + 12, ty + 4, LOESS)
            px(img, pot_x + 14, ty + 6, LOESS)
            px(img, 54 + bx + arm_ext, ty + 2, LOESS)
            px(img, 54 + bx + arm_ext, ty + 0, CREAM)
    elif pose.get("wipe_phase") is not None:
        wp = pose["wipe_phase"]
        fill_rect(img, 6 + bx, ty + 14, 18 + bx, ty + 20, WOOD)
        fill_rect(img, 4 + bx, ty + 18, 12 + bx, ty + 22, SKIN)
        hline(img, 24 + bx, 62, ty + 24, WOOD_L)
        hline(img, 24 + bx, 62, ty + 26, WOOD)
        fill_rect(img, 32 + bx, ty + 4, 44 + bx, ty + 12, WOOD)
        fill_rect(img, 40 + bx, ty + 6, 48 + bx, ty + 12, SKIN)
        if wp == 0:
            fill_rect(img, 36 + bx, ty + 14, 48 + bx, ty + 20, CREAM)
            fill_rect(img, 38 + bx, ty + 20, 44 + bx, ty + 26, PAPER_L)
            hline(img, 36 + bx, 48 + bx, ty + 14, INK)
            px(img, 40 + bx, ty + 22, MIST)
            px(img, 46 + bx, ty + 16, PAPER)
        elif wp == 1:
            fill_rect(img, 40 + bx, ty + 12, 56 + bx, ty + 18, CREAM)
            fill_rect(img, 44 + bx, ty + 18, 52 + bx, ty + 24, PAPER_L)
            hline(img, 40 + bx, 56 + bx, ty + 12, INK)
            px(img, 48 + bx, ty + 14, MIST)
            px(img, 52 + bx, ty + 16, MIST)
            px(img, 54 + bx, ty + 20, PAPER)
        elif wp == 2:
            fill_rect(img, 44 + bx, ty + 10, 62 + bx, ty + 16, CREAM)
            fill_rect(img, 50 + bx, ty + 16, 60 + bx, ty + 24, PAPER_L)
            hline(img, 44 + bx, 62 + bx, ty + 10, INK)
            px(img, 56 + bx, ty + 12, MIST)
            px(img, 52 + bx, ty + 14, MIST)
            px(img, 58 + bx, ty + 18, MIST)
            px(img, 60 + bx, ty + 22, PAPER)
        else:
            fill_rect(img, 34 + bx, ty + 12, 46 + bx, ty + 18, CREAM)
            fill_rect(img, 36 + bx, ty + 18, 42 + bx, ty + 26, PAPER_L)
            hline(img, 34 + bx, 46 + bx, ty + 12, INK)
            px(img, 38 + bx, ty + 22, MIST)
            px(img, 44 + bx, ty + 14, PAPER)
    elif pose.get("parry"):
        shake = pose.get("shake", 0) * 2
        fill_rect(img, 28 + bx, ty - 4, 40 + bx, ty + 6, WOOD)
        fill_rect(img, 30 + bx + shake, ty - 14, 48 + bx + shake, ty - 4, PAPER_L)
        hline(img, 30 + bx + shake, 48 + bx + shake, ty - 14, INK)
        fill_rect(img, 32 + bx + shake, ty - 12, 46 + bx + shake, ty - 6, WOOD_L)
        if shake:
            px(img, 50 + bx, ty - 10, CREAM)
    elif pose.get("hurt"):
        fill_rect(img, 36 + bx, ty + 2, 48 + bx, ty + 10, WOOD)
        fill_rect(img, 44 + bx, ty + 4, 52 + bx, ty + 10, SKIN)
        px(img, 30 + bx, 12 + oy, BLOOD)
        px(img, 22 + bx, 18 + oy, CINN)
        px(img, 36 + bx, 20 + oy, BLOOD)
    else:
        fill_rect(img, 6 + bx, ty + 4, 16 + bx, ty + 16, WOOD)
        fill_rect(img, 4 + bx, ty + 12, 12 + bx, ty + 18, SKIN)
        fill_rect(img, 32 + bx, ty + 4, 40 + bx, ty + 14, WOOD)
        fill_rect(img, 34 + bx, ty + 14, 44 + bx, ty + 20, PAPER_L)
        if lift_r:
            fill_rect(img, 32 + bx, ty + 0, 42 + bx, ty + 10, WOOD)
            fill_rect(img, 38 + bx, ty + 6, 46 + bx, ty + 12, SKIN)
        elif lift_l:
            fill_rect(img, 32 + bx, ty + 8, 40 + bx, ty + 20, WOOD)

    if not pose.get("hurt"):
        ly = ty + 26
        fill_rect(img, 18 + bx - (4 if lift_l else 0), ly - lift_l,
                  26 + bx - (4 if lift_l else 0), ly + 10 - lift_l, INK_SOFT)
        fill_rect(img, 26 + bx + (4 if lift_r else 0), ly - lift_r,
                  34 + bx + (4 if lift_r else 0), ly + 10 - lift_r, INK_SOFT)
        draw_feet(img, 16 + bx, ly + 10, 28 + bx, ly + 10, INK, lift_l, lift_r,
                  stride=4 if (lift_l or lift_r) else 0)
    else:
        ly = ty + 26
        fill_rect(img, 16 + bx, ly, 24 + bx, ly + 10, INK_SOFT)
        fill_rect(img, 26 + bx, ly + 2, 34 + bx, ly + 10, INK_SOFT)
        draw_feet(img, 14 + bx, ly + 10, 26 + bx, ly + 10, INK, 2, 0, stride=0)


def poses_for_character(kind):
    poses = []
    poses.append({"breath": 0})
    poses.append({"breath": 1})
    poses.append({"lift_l": 16, "breath": 0})
    poses.append({"lift_l": 6, "breath": 0})
    poses.append({"lift_r": 16, "breath": 0})
    poses.append({"lift_r": 6, "breath": 1})
    if kind == "qinshi":
        # frames 6–8：v0.9 語意 = windup（腳本變數名仍 serve_phase，僅佔位／預覽用，唔當最終美術）
        poses.append({"hold": True, "serve_phase": 0, "breath": 0})
        poses.append({"hold": True, "serve_phase": 1, "breath": 1})
        poses.append({"hold": True, "serve_phase": 2, "breath": 0})
    else:
        poses.append({"tray": True, "serve_phase": 0, "breath": 0})
        poses.append({"tray": True, "serve_phase": 1, "breath": 0})
        poses.append({"tray": True, "serve_phase": 2, "breath": 1})
    if kind == "xiaoer":
        for wp in range(4):
            poses.append({"wipe_phase": wp, "breath": 0 if wp < 2 else 1})
    else:
        for ap in range(4):
            poses.append({"attack_phase": ap, "breath": 0 if ap < 2 else 1})
    poses.append({"hurt": True, "hurt_phase": 0, "breath": 0, "lift_l": 8})
    poses.append({"hurt": True, "hurt_phase": 1, "breath": 1, "lift_r": 6})
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
    sheet = Image.new("RGBA", (18 * FS, FS), TRANS)
    drawer = DRAWERS[char_id]
    poses = poses_for_character(char_id)
    assert len(poses) == 18, f"{char_id} pose count {len(poses)}"
    for i, pose in enumerate(poses):
        frame = new_frame()
        drawer(frame, 0, 0, pose)
        sheet.paste(frame, (i * FS, 0), frame)
    return sheet


def make_guest_sit64() -> Image.Image:
    """6 seated guests, 64×64 each → 384×64."""
    variants = [
        (TEAL, WOOD_L, INK, SKIN, False),
        (ROBE_R, BLOOD, INK, SKIN, False),
        (INK_SOFT, FRAME, INK, SKIN_D, True),  # fringe
        (VIOLET, GOLD, PAPER_L, SKIN, False),
        (JADE, JADE_B, INK, SKIN, False),
        (WOOD, CINN, INK, SKIN, False),  # wood-hat style via hat
    ]
    sheet = Image.new("RGBA", (6 * FS, FS), TRANS)
    for i, (robe, belt, hair, face, fringe) in enumerate(variants):
        img = new_frame()
        hat = (i == 5)
        draw_head(img, 28, 4, hair=hair, face=face, fringe=fringe, hat_wood=hat,
                  bald_cap=(i == 3))
        # seated torso
        fill_rect(img, 18, 20, 40, 40, robe)
        draw_shoulder(img, 29, 20, 11, robe, belt)
        draw_belt(img, 18, 40, 32, belt, GOLD)
        # legs tucked (sit)
        fill_rect(img, 16, 38, 30, 50, robe)
        fill_rect(img, 30, 40, 44, 52, robe)
        hline(img, 16, 44, 48, NIGHT)
        # table edge + cup/bowl
        hline(img, 40, 62, 36, WOOD_L)
        hline(img, 40, 62, 38, WOOD)
        if i % 2 == 0:
            fill_rect(img, 48, 28, 54, 36, CREAM)
            outline_rect(img, 48, 28, 54, 36, INK)
        else:
            fill_rect(img, 46, 30, 56, 38, PAPER_L)
            outline_rect(img, 46, 30, 56, 38, INK)
            fill_rect(img, 48, 32, 54, 36, LOESS)
        # arm on table
        fill_rect(img, 36, 28, 46, 34, robe)
        fill_rect(img, 42, 30, 50, 36, face)
        sheet.paste(img, (i * FS, 0), img)
    return sheet


def make_boss_combat64(which: str) -> Image.Image:
    img = new_frame(64, 64)
    if which == "heifeng":
        draw_head(img, 20, 2, hair=INK, face=SKIN_D, fringe=True)
        fill_rect(img, 10, 2, 32, 10, INK)
        px(img, 14, 0, INK)
        px(img, 24, 0, INK)
        fill_rect(img, 12, 6, 30, 10, CINN_B)
        fill_rect(img, 16, 16, 26, 20, SKIN_D)
        fill_rect(img, 8, 18, 36, 44, INK_SOFT)
        draw_shoulder(img, 22, 18, 16, WOOD, CINN_B)
        fill_rect(img, 12, 22, 32, 32, NIGHT)
        fill_rect(img, 14, 24, 30, 30, WOOD)
        px(img, 20, 26, GOLD)
        px(img, 24, 26, GOLD)
        fill_rect(img, 10, 32, 34, 36, FRAME)
        px(img, 22, 34, CINN_B)
        fill_rect(img, 12, 44, 22, 56, INK_SOFT)
        fill_rect(img, 22, 44, 32, 56, INK_SOFT)
        draw_feet(img, 10, 56, 24, 56, INK)
        fill_rect(img, 36, 4, 52, 56, INK)
        fill_rect(img, 38, 6, 50, 52, MIST)
        fill_rect(img, 40, 8, 48, 48, CINN_B)
        fill_rect(img, 36, 52, 52, 60, WOOD)
        px(img, 42, 2, CINN_B)
        px(img, 44, 4, CREAM)
        fill_rect(img, 30, 20, 38, 30, INK_SOFT)
        px(img, 34, 18, GOLD)
    elif which == "xieyi":
        draw_head(img, 24, 2, hair=INK, face=SKIN, bun=True, double_bun=True)
        fill_rect(img, 20, 2, 28, 6, VIOLET)
        px(img, 30, 4, GOLD)
        fill_rect(img, 20, 16, 28, 20, SKIN)
        fill_rect(img, 14, 18, 36, 42, ROBE_R)
        draw_shoulder(img, 25, 18, 12, ROBE_R, GOLD)
        draw_belt(img, 14, 36, 30, BLOOD, GOLD)
        fill_rect(img, 34, 24, 46, 40, JADE_B)  # vial
        outline_rect(img, 34, 24, 46, 40, INK)
        px(img, 38, 28, GOLD)
        px(img, 40, 32, JADE)
        fill_rect(img, 16, 42, 24, 54, ROBE_R)
        fill_rect(img, 26, 42, 34, 54, ROBE_R)
        draw_feet(img, 14, 54, 26, 54, INK_SOFT)
        # clawed hand forward
        fill_rect(img, 40, 16, 54, 28, SKIN)
        px(img, 54, 14, INK)
        px(img, 56, 16, INK)
        px(img, 54, 18, INK)
        px(img, 52, 12, INK)
    else:  # xueying
        draw_head(img, 24, 2, hair=INK, face=SKIN_D, fringe=True)
        fill_rect(img, 14, 6, 34, 10, BLOOD)
        fill_rect(img, 20, 16, 28, 20, SKIN_D)
        fill_rect(img, 14, 18, 36, 42, NIGHT)
        draw_shoulder(img, 25, 18, 12, INK_SOFT, CINN_B)
        draw_belt(img, 14, 36, 30, CINN, GOLD)
        fill_rect(img, 16, 42, 24, 54, NIGHT)
        fill_rect(img, 26, 42, 34, 54, NIGHT)
        draw_feet(img, 14, 54, 26, 54, INK)
        # twin daggers
        fill_rect(img, 38, 10, 42, 40, MIST)
        fill_rect(img, 44, 14, 48, 44, MIST)
        px(img, 40, 8, CREAM)
        px(img, 46, 12, CREAM)
        fill_rect(img, 36, 38, 44, 44, WOOD)
        fill_rect(img, 42, 42, 50, 48, WOOD)
    return img


def count_oob(img: Image.Image) -> int:
    n = 0
    for y in range(img.height):
        for x in range(img.width):
            p = img.getpixel((x, y))
            if p[3] == 0:
                continue
            if p[:3] not in PALETTE_SET:
                n += 1
    return n


def frame_has_pixels(sheet: Image.Image, i: int, fw=FS) -> bool:
    x0 = i * fw
    for y in range(sheet.height):
        for x in range(x0, x0 + fw):
            if sheet.getpixel((x, y))[3] > 0:
                return True
    return False


def preview_x2(src: Image.Image, path: Path):
    big = src.resize((src.width * 2, src.height * 2), Image.Resampling.NEAREST)
    big.save(path)
    return path


def write_readme64():
    text = """# 精靈表 64×64（原生）— 墨點江湖

> 原生像素 · `tools/gen_sprites_64.py` · 僅盤內色 · 透明底 · 硬邊無抗鋸齒  
> **唔係** 32 版 nearest-neighbor 放大——喺 64 格內加袍褶／武器厚度／茶盤器物；眼睛仍 1–2px 墨點。

## 檔案

| 檔 | 尺寸 | 說明 |
|----|------|------|
| `qingyi.png` | **1152×64** | 青衣劍客 · 18 幀 |
| `tiezhang.png` | **1152×64** | 鐵掌醫女 |
| `langren.png` | **1152×64** | 浪人刀客 |
| `qinshi.png` | **1152×64** | 琴心師太 |
| `xiaoer.png` | **1152×64** | 客棧小二（斟茶＋抹枱） |
| `guest_sit.png` | **384×64** | 客人坐姿 ×6（可選） |
| `boss_heifeng_combat.png` | **64×64** | Boss 戰鬥剪影（可選） |
| `boss_xieyi_combat.png` | **64×64** | Boss 戰鬥剪影（可選） |
| `boss_xueying_combat.png` | **64×64** | Boss 戰鬥剪影（可選） |

每角：每幀 **64×64**，橫向 **18** 幀 → `18×64 = 1152`。

## 對幀（同 32 版）

| 幀 | 動作 | 說明 |
|----|------|------|
| 0–1 | **idle** | 呼吸微動 |
| 2–5 | **walk** | 高抬左 → 過渡 → 高抬右 → 過渡（抬腳約 16px） |
| 6–8 | **windup** | 讀招蓄勢（舊 serve 位；xiaoer Hub 暫共用斟茶） |
| 9–12 | **strike**／**attack** *或* **wipe** | 俠客出招；**xiaoer＝抹枱** |
| 13–14 | **hurt** | 兩幀差大 stagger |
| 15–17 | **parry** | 舉武器／盤擋 → 微震 → 回穩 |

```js
const FRAME = 64;
const sx = frameIndex * FRAME; // 0..17
ctx.imageSmoothingEnabled = false;
ctx.drawImage(sheet, sx, 0, FRAME, FRAME, dx, dy, FRAME, FRAME); // Hub 960×540 用 ×1
// 或再整數倍：dx 顯示寬 = FRAME * N
```

## 同 32 版對應

| 32 路徑 | 64 路徑 | 幀對齊 |
|---------|---------|--------|
| `assets/sprites/qingyi.png` (576×32) | `assets/sprites/64/qingyi.png` (1152×64) | 幀 index 相同 |
| …其餘俠客／小二同上 | `64/{id}.png` | 相同 |
| `guest_sit.png` (192×32) | `64/guest_sit.png` (384×64) | guestIndex 0–5 |
| `boss_*_combat.png` (32×32) | `64/boss_*_combat.png` (64×64) | 單幀 |

Hub 已係 **960×540** 時：原生 64 用 **×1**（或再 ×2／×3 整數倍 + `pixelated`）；唔好用非整數縮放。

## 重跑

```bash
python3 /workspace/wuxia-inn/tools/gen_sprites_64.py
```

合規：oob=0、每幀有可見像素、尺寸正確。預覽：`assets/_preview/64_*_x2.png`。
"""
    (OUT / "README.md").write_text(text, encoding="utf-8")


def patch_main_readme():
    path = SPRITES32 / "README.md"
    text = path.read_text(encoding="utf-8")
    marker = "## 原生 64×64"
    section = """
## 原生 64×64（Hub 960×540）

目錄：[`64/`](./64/) · 生成：`tools/gen_sprites_64.py`  
每角 **1152×64**（18×64），對幀同本文件 32 版。**原生重繪**（袍褶／武器厚度／茶盤），唔係 NN 放大。  
Hub 顯示建議：`image-rendering: pixelated`，×1 或整數倍。詳見 [`64/README.md`](./64/README.md)。

"""
    if marker in text:
        # replace from marker to next ## or end — simple: find and splice
        i = text.index(marker)
        j = text.find("\n## ", i + 3)
        if j < 0:
            text = text[:i] + section
        else:
            text = text[:i] + section + text[j + 1:]
    else:
        text = text.rstrip() + "\n" + section
    path.write_text(text, encoding="utf-8")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    PREV.mkdir(parents=True, exist_ok=True)
    report = []
    total_oob = 0

    for cid in DRAWERS:
        sheet = make_spritesheet(cid)
        assert sheet.size == (1152, 64), sheet.size
        oob = count_oob(sheet)
        total_oob += oob
        empty = [i for i in range(18) if not frame_has_pixels(sheet, i)]
        path = OUT / f"{cid}.png"
        sheet.save(path)
        preview_x2(sheet, PREV / f"64_{cid}_x2.png")
        # also single-frame idle preview crop
        idle = sheet.crop((0, 0, FS, FS))
        preview_x2(idle, PREV / f"64_{cid}_idle_x2.png")
        line = f"{cid}: {path} size={sheet.size} oob={oob} empty_frames={empty}"
        report.append(line)
        print(line)

    # optional same batch
    gs = make_guest_sit64()
    assert gs.size == (384, 64)
    oob = count_oob(gs)
    total_oob += oob
    gs.save(OUT / "guest_sit.png")
    preview_x2(gs, PREV / "64_guest_sit_x2.png")
    report.append(f"guest_sit: size={gs.size} oob={oob}")
    print(report[-1])

    for boss in ("heifeng", "xieyi", "xueying"):
        b = make_boss_combat64(boss)
        assert b.size == (64, 64)
        oob = count_oob(b)
        total_oob += oob
        bp = OUT / f"boss_{boss}_combat.png"
        b.save(bp)
        preview_x2(b, PREV / f"64_boss_{boss}_x2.png")
        report.append(f"boss_{boss}: size={b.size} oob={oob}")
        print(report[-1])

    write_readme64()
    patch_main_readme()
    (OUT / "_gen_report.txt").write_text(
        "\n".join(report) + f"\nTOTAL_OOB={total_oob}\n", encoding="utf-8"
    )
    print(f"TOTAL_OOB={total_oob}")
    if total_oob != 0:
        raise SystemExit(f"palette oob={total_oob}")
    print("OK")


if __name__ == "__main__":
    main()
