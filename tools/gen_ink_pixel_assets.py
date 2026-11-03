#!/usr/bin/env python3
"""Generate Ink-Pixel Inn assets: Ink-Pixel palette-locked hard-edge sprites/scenes.

Sprites 32×32; Hub scenes native 960×540 (v2.0, hard edge, palette-locked, no AA).
Sprites owned by 墨點美術; Hub scenes by 墨點場景.
Native 64×64 sheets: tools/gen_sprites_64.py → assets/sprites/64/ (do not NN-upscale 32).
Use --scenes-only to regenerate assets/scenes/ + hub previews without touching sprites.
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
              topknot=False, bun=False, bald_cap=False, fringe=False, hat_wood=False,
              double_bun=False, tall_knot=False):
    """3/4 head facing right — v1.2 silhouette variants (hat/hair/knot readable at a glance)."""
    if bald_cap:
        # nun/monk: taller white cap silhouette + forehead band
        fill_rect(img, cx - 4, cy - 1, cx + 4, cy + 3, PAPER_L)
        fill_rect(img, cx - 5, cy + 1, cx + 5, cy + 3, PAPER_L)
        fill_rect(img, cx - 3, cy - 2, cx + 3, cy, PAPER)
        hline(img, cx - 4, cx + 4, cy - 1, INK)
        fill_rect(img, cx - 4, cy + 3, cx + 4, cy + 8, face)
        hline(img, cx - 4, cx + 4, cy + 3, PAPER_D)
    elif hat_wood:
        # waiter hat: wider brim + taller crown + gold bead
        fill_rect(img, cx - 6, cy, cx + 6, cy + 2, WOOD)
        fill_rect(img, cx - 4, cy - 3, cx + 4, cy, WOOD_L)
        fill_rect(img, cx - 3, cy - 4, cx + 3, cy - 3, WOOD)
        px(img, cx, cy - 5, GOLD)
        px(img, cx - 1, cy - 4, LOESS)
        fill_rect(img, cx - 4, cy + 2, cx + 4, cy + 8, face)
        px(img, cx - 4, cy + 2, hair)
        px(img, cx + 3, cy + 2, hair)
        px(img, cx + 4, cy + 3, hair)
    else:
        fill_rect(img, cx - 4, cy, cx + 4, cy + 3, hair)
        fill_rect(img, cx - 5, cy + 1, cx + 5, cy + 3, hair)
        if tall_knot or topknot:
            # taller topknot + pin — sword hero silhouette
            fill_rect(img, cx - 1, cy - 4, cx + 2, cy, hair)
            fill_rect(img, cx - 2, cy - 2, cx + 3, cy, hair)
            px(img, cx, cy - 5, GOLD)
            px(img, cx + 1, cy - 3, GOLD)
            px(img, cx - 1, cy - 3, LOESS)
        if double_bun or bun:
            # side bun + hairpin (medic silhouette)
            fill_rect(img, cx + 2, cy - 2, cx + 7, cy + 3, hair)
            fill_rect(img, cx + 3, cy - 3, cx + 6, cy - 1, hair)
            px(img, cx + 5, cy - 1, GOLD)
            px(img, cx + 6, cy + 1, CINN_B if bun or double_bun else GOLD)
        if fringe:
            # heavy fringe + headband-ready (blade rogue)
            hline(img, cx - 4, cx + 4, cy + 3, hair)
            px(img, cx - 3, cy + 4, hair)
            px(img, cx - 1, cy + 4, hair)
            px(img, cx + 2, cy + 4, hair)
        fill_rect(img, cx - 4, cy + 3, cx + 4, cy + 8, face)
        if hair_side:
            fill_rect(img, cx - 5, cy + 3, cx - 3, cy + 9, hair_side)
            fill_rect(img, cx + 3, cy + 3, cx + 5, cy + 8, hair_side)
            px(img, cx - 5, cy + 8, hair_side)
        else:
            px(img, cx - 4, cy + 3, hair)
            px(img, cx + 3, cy + 3, hair)
    # eyes 1×1 + cheek shade
    px(img, cx - 2, cy + 5, eye)
    px(img, cx + 1, cy + 5, eye)
    px(img, cx + 3, cy + 6, SKIN_D if face in (SKIN, SKIN_D) else face)
    hline(img, cx - 4, cx + 4, cy if not hat_wood else cy + 2, INK)
    vline(img, cx - 5, cy + 1, cy + 8, INK)
    vline(img, cx + 4, cy + 1, cy + 8, INK)


def draw_cuff(img, x0, y0, x1, y1, robe, cuff=PAPER_L):
    """1px sleeve cuff layer at wrist end."""
    fill_rect(img, x0, y0, x1, y1, robe)
    hline(img, x0, x1, y1 - 1, cuff)


def draw_hem_sway(img, x0, x1, y, lift_l, lift_r, robe, fold=NIGHT):
    """Lower robe hem that follows walk — 1–2px fold layers."""
    # base hem
    hline(img, x0, x1, y, fold)
    hline(img, x0 + 1, x1 - 1, y + 1, robe)
    if lift_l:
        # left hem rises / swings back
        px(img, x0 - 1, y - 1, robe)
        px(img, x0, y - 2, fold)
        px(img, x0 + 1, y - 1, fold)
    if lift_r:
        px(img, x1, y - 1, robe)
        px(img, x1 - 1, y - 2, fold)
        px(img, x1 + 1, y - 1, fold)


def draw_shoulder(img, cx, cy, w, robe, accent=None):
    """Shoulder pad / ornament — silhouette differencer."""
    fill_rect(img, cx - w, cy, cx + w, cy + 2, robe)
    if accent:
        px(img, cx - w, cy, accent)
        px(img, cx + w - 1, cy, accent)


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
    """v1.2.1: attack lean (wind-up ↔ impact) + two-phase hurt; keep weapons on-canvas."""
    if pose.get("hurt"):
        # phase0 reel-back; phase1 deeper stagger — readable at slow combat
        return -4 if pose.get("hurt_phase", 0) == 0 else -6
    if pose.get("wipe_phase") is not None:
        return 1 if pose.get("wipe_phase", 0) % 2 else 0
    if pose.get("attack_phase") == 0:
        return -2  # wind-up lean back (weapon stays in 32px)
    if pose.get("attack_phase") == 1:
        return 1   # swing mid
    if pose.get("attack_phase") == 2:
        return 3   # impact lean forward
    if pose.get("attack_phase") == 3:
        return 0   # recover
    if pose.get("lift_l"):
        return -2
    if pose.get("lift_r"):
        return 2
    return 0


def draw_robe_folds(img, x0, x1, y, c=NIGHT):
    """2-layer fold: waist crease + lower drape."""
    hline(img, x0, x1, y, c)
    hline(img, x0 + 1, x1 - 1, y + 2, c)
    hline(img, x0 + 2, x1 - 2, y + 5, c)
    px(img, x0 + 1, y + 1, c)
    px(img, x1 - 2, y + 1, c)


def draw_belt(img, x0, x1, y, main=WOOD_L, buckle=GOLD):
    fill_rect(img, x0, y, x1, y + 2, main)
    mid = (x0 + x1) // 2
    # square buckle + studs
    fill_rect(img, mid - 1, y - 1, mid + 2, y + 3, buckle)
    px(img, mid, y, CREAM if buckle != CREAM else LOESS)
    px(img, x0 + 1, y + 1, INK)
    px(img, x1 - 2, y + 1, INK)


# ---------- characters ----------

def qingyi_body(img, ox, oy, pose):
    breath = pose.get("breath", 0)
    bx = ox + body_shift(pose)
    head_y = 1 + breath
    draw_head(img, 13 + bx, head_y + oy, hair=INK, face=SKIN, topknot=True, tall_knot=True)
    fill_rect(img, 11 + bx, 8 + breath + oy, 15 + bx, 10 + breath + oy, SKIN)
    ty = 9 + breath + oy
    # teal robe + collar + shoulder + folds + sash + sheath
    fill_rect(img, 8 + bx, ty, 18 + bx, ty + 12, TEAL)
    draw_shoulder(img, 13 + bx, ty, 6, TEAL, TEAL_B)
    fill_rect(img, 11 + bx, ty, 15 + bx, ty + 2, PAPER_L)
    fill_rect(img, 9 + bx, ty + 1, 11 + bx, ty + 3, TEAL_B)  # lapel
    fill_rect(img, 15 + bx, ty + 1, 17 + bx, ty + 3, TEAL_B)
    draw_robe_folds(img, 8 + bx, 18 + bx, ty + 4, NIGHT)
    draw_belt(img, 8 + bx, 18 + bx, ty + 7, WOOD_L, GOLD)
    vline(img, 12 + bx, ty + 2, ty + 12, NIGHT)  # front slit
    # hip sheath (idle readable)
    fill_rect(img, 17 + bx, ty + 8, 20 + bx, ty + 14, TEAL_B)
    px(img, 17 + bx, ty + 7, GOLD)
    px(img, 19 + bx, ty + 13, WOOD)

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
            # pour arc: spout → stream → cup
            px(img, 23 + bx, ty + 0, WOOD)
            px(img, 24 + bx, ty + 1, LOESS)
            px(img, 24 + bx, ty + 2, LOESS)
            px(img, 25 + bx, ty + 3, LOESS)
            px(img, 26 + bx, ty + 2, CREAM)
        # sheathed sword on hip
        fill_rect(img, 18 + bx, ty + 8, 20 + bx, ty + 18, TEAL_B)
        px(img, 18 + bx, ty + 7, GOLD)
    elif pose.get("attack_phase") is not None:
        ap = pose["attack_phase"]
        if ap == 0:  # wind-up: sword vertical left of body, tip high (on-canvas)
            fill_rect(img, 4 + bx, ty + 1, 10 + bx, ty + 7, TEAL)
            fill_rect(img, 2 + bx, ty + 4, 6 + bx, ty + 8, SKIN)
            # blade vertical left, tip up — clear wind-up silhouette
            fill_rect(img, 1 + bx, ty - 7, 4 + bx, ty + 14, TEAL_B)
            fill_rect(img, 0 + bx, ty - 9, 5 + bx, ty - 6, GOLD)
            px(img, 2 + bx, ty - 5, CREAM)
            px(img, 2 + bx, ty + 13, WOOD)
            # free arm tucked back-right
            fill_rect(img, 15 + bx, ty + 4, 20 + bx, ty + 9, TEAL)
            fill_rect(img, 17 + bx, ty + 7, 21 + bx, ty + 10, SKIN)
        elif ap == 1:  # big arc swing out (diagonal tip rising)
            fill_rect(img, 15 + bx, ty + 0, 24 + bx, ty + 5, TEAL)
            fill_rect(img, 21 + bx, ty + 1, 26 + bx, ty + 5, SKIN)
            # long blade arc: hilt mid → tip far right-up
            fill_rect(img, bx + 18, ty + 1, bx + 22, ty + 4, GOLD)
            fill_rect(img, bx + 21, ty - 2, bx + 32, ty + 1, TEAL_B)
            px(img, bx + 20, ty + 0, WOOD)
            px(img, bx + 31, ty - 3, TEAL_B)
            px(img, bx + 30, ty - 2, CREAM)
            px(img, bx + 29, ty - 1, GOLD)
            # left arm counterbalance back
            fill_rect(img, 1 + bx, ty + 3, 7 + bx, ty + 8, TEAL)
            fill_rect(img, 0 + bx, ty + 6, 4 + bx, ty + 9, SKIN)
        elif ap == 2:  # impact: tip thrust + 1px cream highlight cluster
            fill_rect(img, 16 + bx, ty + 1, 26 + bx, ty + 6, TEAL)
            fill_rect(img, 23 + bx, ty + 2, 28 + bx, ty + 6, SKIN)
            fill_rect(img, bx + 20, ty + 0, bx + 24, ty + 3, GOLD)
            fill_rect(img, bx + 23, ty - 1, bx + 32, ty + 2, TEAL_B)
            # tip flash (palette cream / teal-bright / gold)
            px(img, bx + 31, ty - 2, CREAM)
            px(img, bx + 30, ty - 1, CREAM)
            px(img, bx + 31, ty + 0, TEAL_B)
            px(img, bx + 29, ty - 2, GOLD)
            px(img, bx + 28, ty - 1, CREAM)
            # trailing afterimage speck
            px(img, bx + 26, ty - 3, TEAL_B)
            fill_rect(img, 2 + bx, ty + 4, 8 + bx, ty + 9, TEAL)
            fill_rect(img, 1 + bx, ty + 7, 5 + bx, ty + 10, SKIN)
        else:  # recover: blade returns toward hip, slight forward settle
            fill_rect(img, 14 + bx, ty + 2, 21 + bx, ty + 7, TEAL)
            fill_rect(img, 18 + bx, ty + 5, 22 + bx, ty + 8, SKIN)
            fill_rect(img, bx + 18, ty + 1, bx + 21, ty + 14, TEAL_B)
            fill_rect(img, bx + 17, ty + 0, bx + 22, ty + 2, GOLD)
            px(img, bx + 19, ty + 13, WOOD)
            fill_rect(img, 4 + bx, ty + 3, 9 + bx, ty + 8, TEAL)
            fill_rect(img, 3 + bx, ty + 6, 7 + bx, ty + 9, SKIN)
    elif not pose.get("hurt"):
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
    draw_hem_sway(img, 8 + bx, 18 + bx, ly + 1, lift_l, lift_r, TEAL, NIGHT)
    stride = 3 if (lift_l or lift_r) else 0
    draw_feet(img, 8 + bx, ly + 6, 14 + bx, ly + 6, INK_SOFT, lift_l, lift_r, stride=stride)

    if pose.get("hurt"):
        hp = pose.get("hurt_phase", 0)
        if hp == 0:
            # reel: arm flung high-right, blood spray chest/face
            fill_rect(img, 17 + bx, ty - 2, 24 + bx, ty + 3, TEAL)
            fill_rect(img, 22 + bx, ty - 3, 27 + bx, ty + 1, SKIN)
            fill_rect(img, 1 + bx, ty + 5, 7 + bx, ty + 10, TEAL)
            fill_rect(img, 0 + bx, ty + 8, 4 + bx, ty + 11, SKIN)
            px(img, 15 + bx, 5 + oy, CINN_B)
            px(img, 17 + bx, 6 + oy, BLOOD)
            px(img, 18 + bx, 8 + oy, CINN_B)
            px(img, 10 + bx, 10 + oy, BLOOD)
            px(img, 19 + bx, 9 + oy, BLOOD)
            px(img, 20 + bx, 5 + oy, CINN_B)
            px(img, 12 + bx, 7 + oy, BLOOD)
        else:
            # deeper stagger: arm flung down-out, different blood arc
            fill_rect(img, 18 + bx, ty + 4, 25 + bx, ty + 9, TEAL)
            fill_rect(img, 23 + bx, ty + 7, 28 + bx, ty + 11, SKIN)
            fill_rect(img, 2 + bx, ty + 2, 8 + bx, ty + 7, TEAL)
            fill_rect(img, 1 + bx, ty + 5, 5 + bx, ty + 8, SKIN)
            px(img, 14 + bx, 4 + oy, BLOOD)
            px(img, 16 + bx, 7 + oy, CINN_B)
            px(img, 9 + bx, 12 + oy, BLOOD)
            px(img, 18 + bx, 11 + oy, CINN_B)
            px(img, 21 + bx, 8 + oy, BLOOD)
            px(img, 11 + bx, 9 + oy, CINN_B)
            px(img, 20 + bx, 13 + oy, BLOOD)


def tiezhang_body(img, ox, oy, pose):
    breath = pose.get("breath", 0)
    bx = ox + body_shift(pose)
    head_y = 1 + breath
    draw_head(img, 13 + bx, head_y + oy, hair=INK, face=SKIN, hair_side=INK, bun=True, double_bun=True)
    fill_rect(img, 11 + bx, head_y + oy, 15 + bx, head_y + 2 + oy, CINN)  # hairpin band
    px(img, 16 + bx, head_y + 1 + oy, GOLD)
    px(img, 17 + bx, head_y + 2 + oy, CINN_B)
    fill_rect(img, 11 + bx, 8 + breath + oy, 15 + bx, 10 + breath + oy, SKIN)
    ty = 9 + breath + oy
    fill_rect(img, 8 + bx, ty, 18 + bx, ty + 12, ROBE_R)
    draw_shoulder(img, 13 + bx, ty, 6, ROBE_R, GOLD)
    fill_rect(img, 10 + bx, ty, 16 + bx, ty + 2, PAPER_L)
    fill_rect(img, 9 + bx, ty + 2, 11 + bx, ty + 4, BLOOD)  # collar trim
    draw_robe_folds(img, 8 + bx, 18 + bx, ty + 4, BLOOD)
    draw_belt(img, 8 + bx, 18 + bx, ty + 7, BLOOD, GOLD)
    # medicine pouch (bigger + cord + leaf mark)
    fill_rect(img, 17 + bx, ty + 6, 23 + bx, ty + 13, JADE_B)
    outline_rect(img, 17 + bx, ty + 6, 23 + bx, ty + 13, INK)
    px(img, 19 + bx, ty + 8, GOLD)
    px(img, 20 + bx, ty + 10, JADE)
    px(img, 21 + bx, ty + 9, JADE)
    px(img, 18 + bx, ty + 5, WOOD)  # cord

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
        if ap == 0:  # charge: rear palm high-back + jade glow (readable wind-up)
            fill_rect(img, 2 + bx, ty - 2, 9 + bx, ty + 5, ROBE_R)
            fill_rect(img, 1 + bx, ty - 1, 5 + bx, ty + 4, SKIN)
            fill_rect(img, 0 + bx, ty - 3, 4 + bx, ty + 0, JADE_B)
            px(img, 1 + bx, ty - 4, CREAM)
            px(img, 2 + bx, ty - 2, JADE)
            px(img, 0 + bx, ty - 1, JADE_B)
            # front arm chambered
            fill_rect(img, 15 + bx, ty + 2, 21 + bx, ty + 7, ROBE_R)
            fill_rect(img, 18 + bx, ty + 4, 22 + bx, ty + 8, SKIN)
        elif ap == 1:  # thrust mid — palm extending
            fill_rect(img, 15 + bx, ty - 1, 25 + bx, ty + 5, ROBE_R)
            fill_rect(img, 21 + bx, ty + 0, 29 + bx, ty + 5, SKIN)
            fill_rect(img, 26 + bx, ty - 1, 30 + bx, ty + 2, JADE_B)
            px(img, 28 + bx, ty - 2, JADE)
            fill_rect(img, 1 + bx, ty + 3, 7 + bx, ty + 8, ROBE_R)
            fill_rect(img, 0 + bx, ty + 6, 4 + bx, ty + 9, SKIN)
        elif ap == 2:  # impact: palm blast + hard 1px highlights
            fill_rect(img, 16 + bx, ty + 0, 27 + bx, ty + 6, ROBE_R)
            fill_rect(img, 23 + bx, ty + 1, 31 + bx, ty + 6, SKIN)
            fill_rect(img, 28 + bx, ty - 1, 32 + bx, ty + 3, JADE_B)
            px(img, 31, ty - 2, CREAM)
            px(img, 30, ty - 1, CREAM)
            px(img, 31, ty + 1, GOLD)
            px(img, 29, ty - 2, JADE)
            px(img, 28, ty + 0, CREAM)
            px(img, 27, ty - 3, JADE_B)
            fill_rect(img, 2 + bx, ty + 4, 8 + bx, ty + 9, ROBE_R)
            fill_rect(img, 1 + bx, ty + 7, 5 + bx, ty + 10, SKIN)
        else:  # recover settle
            fill_rect(img, 14 + bx, ty + 2, 22 + bx, ty + 7, ROBE_R)
            fill_rect(img, 18 + bx, ty + 4, 23 + bx, ty + 8, SKIN)
            px(img, 21 + bx, ty + 3, JADE_B)
            fill_rect(img, 3 + bx, ty + 3, 8 + bx, ty + 8, ROBE_R)
            fill_rect(img, 2 + bx, ty + 6, 6 + bx, ty + 9, SKIN)
    elif not pose.get("hurt"):
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
    draw_hem_sway(img, 8 + bx, 18 + bx, ly + 1, lift_l, lift_r, ROBE_R, BLOOD)
    draw_feet(img, 8 + bx, ly + 6, 14 + bx, ly + 6, INK_SOFT, lift_l, lift_r,
              stride=3 if (lift_l or lift_r) else 0)
    if pose.get("hurt"):
        hp = pose.get("hurt_phase", 0)
        if hp == 0:
            fill_rect(img, 17 + bx, ty - 2, 25 + bx, ty + 3, ROBE_R)
            fill_rect(img, 22 + bx, ty - 3, 27 + bx, ty + 1, SKIN)
            fill_rect(img, 1 + bx, ty + 5, 7 + bx, ty + 10, ROBE_R)
            px(img, 15 + bx, 5 + oy, CINN_B)
            px(img, 17 + bx, 7 + oy, BLOOD)
            px(img, 9 + bx, 10 + oy, BLOOD)
            px(img, 18 + bx, 9 + oy, CINN_B)
            px(img, 20 + bx, 6 + oy, BLOOD)
            px(img, 12 + bx, 8 + oy, CINN_B)
        else:
            fill_rect(img, 18 + bx, ty + 4, 26 + bx, ty + 9, ROBE_R)
            fill_rect(img, 23 + bx, ty + 7, 28 + bx, ty + 11, SKIN)
            fill_rect(img, 2 + bx, ty + 2, 8 + bx, ty + 7, ROBE_R)
            px(img, 14 + bx, 4 + oy, BLOOD)
            px(img, 16 + bx, 8 + oy, CINN_B)
            px(img, 8 + bx, 12 + oy, BLOOD)
            px(img, 19 + bx, 11 + oy, CINN_B)
            px(img, 21 + bx, 9 + oy, BLOOD)
            px(img, 11 + bx, 9 + oy, CINN_B)


def langren_body(img, ox, oy, pose):
    breath = pose.get("breath", 0)
    bx = ox + body_shift(pose)
    head_y = 1 + breath
    draw_head(img, 13 + bx, head_y + oy, hair=INK, face=SKIN_D, fringe=True)
    # wider blood headband + trailing end
    fill_rect(img, 7 + bx, head_y + 2 + oy, 19 + bx, head_y + 4 + oy, CINN_B)
    fill_rect(img, 18 + bx, head_y + 3 + oy, 22 + bx, head_y + 5 + oy, CINN)
    px(img, 21 + bx, head_y + 5 + oy, BLOOD)
    fill_rect(img, 11 + bx, 8 + breath + oy, 15 + bx, 10 + breath + oy, SKIN_D)
    ty = 9 + breath + oy
    fill_rect(img, 8 + bx, ty, 18 + bx, ty + 12, INK_SOFT)
    draw_shoulder(img, 13 + bx, ty, 7, WOOD, CINN_B)  # armored shoulders
    fill_rect(img, 9 + bx, ty + 1, 17 + bx, ty + 5, WOOD)  # chest plate
    fill_rect(img, 10 + bx, ty + 2, 16 + bx, ty + 4, WOOD_L)
    px(img, 12 + bx, ty + 3, GOLD)  # plate stud
    px(img, 14 + bx, ty + 3, GOLD)
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
        if ap == 0:  # dao raised high left of body — thick blade on-canvas
            fill_rect(img, 4 + bx, ty + 1, 10 + bx, ty + 7, INK_SOFT)
            fill_rect(img, 2 + bx, ty + 4, 6 + bx, ty + 8, SKIN_D)
            # tall rear dao left
            fill_rect(img, 0 + bx, ty - 8, 4 + bx, ty + 13, INK_SOFT)
            fill_rect(img, 1 + bx, ty - 7, 3 + bx, ty + 11, MIST)
            fill_rect(img, 0 + bx, ty + 13, 4 + bx, ty + 16, WOOD)
            px(img, 1 + bx, ty - 9, CINN_B)
            px(img, 2 + bx, ty - 6, CREAM)
            fill_rect(img, 15 + bx, ty + 4, 20 + bx, ty + 9, INK_SOFT)
            fill_rect(img, 17 + bx, ty + 7, 21 + bx, ty + 10, SKIN_D)
        elif ap == 1:  # wide horizontal cleave arc
            fill_rect(img, 15 + bx, ty + 0, 24 + bx, ty + 5, INK_SOFT)
            fill_rect(img, 20 + bx, ty + 1, 25 + bx, ty + 5, SKIN_D)
            fill_rect(img, 18 + bx, ty - 1, 22 + bx, ty + 3, WOOD)
            fill_rect(img, 20 + bx, ty - 3, 32, ty + 1, INK_SOFT)
            fill_rect(img, 21 + bx, ty - 2, 31, ty + 0, MIST)
            px(img, 31, ty - 4, INK_SOFT)
            px(img, 30, ty - 3, CREAM)
            px(img, 29, ty - 2, CINN_B)
            fill_rect(img, 1 + bx, ty + 3, 7 + bx, ty + 8, INK_SOFT)
            fill_rect(img, 0 + bx, ty + 6, 4 + bx, ty + 9, SKIN_D)
        elif ap == 2:  # impact: blood-edge flash on tip
            fill_rect(img, 16 + bx, ty + 1, 25 + bx, ty + 6, INK_SOFT)
            fill_rect(img, 22 + bx, ty + 2, 27 + bx, ty + 6, SKIN_D)
            fill_rect(img, 19 + bx, ty + 0, 23 + bx, ty + 3, WOOD)
            fill_rect(img, 21 + bx, ty - 1, 32, ty + 3, INK_SOFT)
            fill_rect(img, 22 + bx, ty + 0, 31, ty + 2, CINN_B)
            px(img, 31, ty - 2, CREAM)
            px(img, 30, ty - 1, CREAM)
            px(img, 31, ty + 1, GOLD)
            px(img, 29, ty - 2, CINN)
            px(img, 28, ty - 1, CREAM)
            px(img, 27, ty - 3, CINN_B)
            fill_rect(img, 2 + bx, ty + 4, 8 + bx, ty + 9, INK_SOFT)
            fill_rect(img, 1 + bx, ty + 7, 5 + bx, ty + 10, SKIN_D)
        else:  # recover: dao returns toward hip
            fill_rect(img, 14 + bx, ty + 2, 21 + bx, ty + 7, INK_SOFT)
            fill_rect(img, 18 + bx, ty + 2, 22 + bx, ty + 16, INK_SOFT)
            fill_rect(img, 19 + bx, ty + 3, 21 + bx, ty + 14, MIST)
            fill_rect(img, 18 + bx, ty + 15, 22 + bx, ty + 17, WOOD)
            px(img, 19 + bx, ty + 1, CINN_B)
            fill_rect(img, 3 + bx, ty + 3, 8 + bx, ty + 8, INK_SOFT)
            fill_rect(img, 2 + bx, ty + 6, 6 + bx, ty + 9, SKIN_D)
    elif not pose.get("hurt"):
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
    draw_hem_sway(img, 8 + bx, 18 + bx, ly + 1, lift_l, lift_r, INK_SOFT, NIGHT)
    draw_feet(img, 8 + bx, ly + 6, 14 + bx, ly + 6, INK, lift_l, lift_r,
              stride=3 if (lift_l or lift_r) else 0)
    if pose.get("hurt"):
        hp = pose.get("hurt_phase", 0)
        if hp == 0:
            fill_rect(img, 17 + bx, ty - 3, 25 + bx, ty + 2, INK_SOFT)
            fill_rect(img, 22 + bx, ty - 4, 27 + bx, ty + 0, SKIN_D)
            fill_rect(img, 1 + bx, ty + 5, 7 + bx, ty + 10, INK_SOFT)
            px(img, 14 + bx, 4 + oy, CINN_B)
            px(img, 16 + bx, 6 + oy, BLOOD)
            px(img, 11 + bx, 11 + oy, BLOOD)
            px(img, 19 + bx, 8 + oy, CINN_B)
            px(img, 20 + bx, 5 + oy, BLOOD)
            px(img, 12 + bx, 7 + oy, CINN_B)
        else:
            fill_rect(img, 18 + bx, ty + 4, 26 + bx, ty + 9, INK_SOFT)
            fill_rect(img, 23 + bx, ty + 7, 28 + bx, ty + 11, SKIN_D)
            fill_rect(img, 2 + bx, ty + 2, 8 + bx, ty + 7, INK_SOFT)
            px(img, 13 + bx, 3 + oy, BLOOD)
            px(img, 15 + bx, 7 + oy, CINN_B)
            px(img, 10 + bx, 13 + oy, BLOOD)
            px(img, 18 + bx, 10 + oy, CINN_B)
            px(img, 21 + bx, 8 + oy, BLOOD)
            px(img, 11 + bx, 9 + oy, CINN)
            px(img, 20 + bx, 12 + oy, BLOOD)


def qinshi_body(img, ox, oy, pose):
    breath = pose.get("breath", 0)
    bx = ox + body_shift(pose)
    head_y = 1 + breath
    draw_head(img, 13 + bx, head_y + oy, hair=PAPER_L, face=SKIN, hair_side=PAPER_L, bald_cap=True)
    # violet forehead jewel row
    px(img, 12 + bx, head_y + 4 + oy, VIOLET)
    px(img, 13 + bx, head_y + 4 + oy, VIOLET)
    px(img, 14 + bx, head_y + 4 + oy, GOLD)
    px(img, 11 + bx, head_y + 5 + oy, VIOLET)
    fill_rect(img, 11 + bx, 8 + breath + oy, 15 + bx, 10 + breath + oy, SKIN)
    ty = 9 + breath + oy
    fill_rect(img, 8 + bx, ty, 18 + bx, ty + 6, VIOLET)
    draw_shoulder(img, 13 + bx, ty, 6, VIOLET, GOLD)
    fill_rect(img, 7 + bx, ty + 6, 19 + bx, ty + 13, PAPER_L)
    fill_rect(img, 10 + bx, ty, 16 + bx, ty + 2, PAPER_L)
    draw_robe_folds(img, 7 + bx, 19 + bx, ty + 8, PAPER_D)
    draw_belt(img, 8 + bx, 18 + bx, ty + 5, GOLD, CREAM)
    # long sleeve drape — nun silhouette
    fill_rect(img, 5 + bx, ty + 2, 8 + bx, ty + 12, VIOLET)
    fill_rect(img, 5 + bx, ty + 10, 8 + bx, ty + 12, PAPER_L)  # cuff

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
        if ap == 0:  # staff vertical left + paper tuft on tip (not tray-like)
            fill_rect(img, 4 + bx, ty + 1, 10 + bx, ty + 7, VIOLET)
            fill_rect(img, 2 + bx, ty + 4, 6 + bx, ty + 8, SKIN)
            fill_rect(img, 1 + bx, ty - 5, 4 + bx, ty + 13, WOOD)
            # tuft = vertical fluff on tip (taller than wide)
            fill_rect(img, 0 + bx, ty - 10, 5 + bx, ty - 5, PAPER_L)
            vline(img, 2 + bx, ty - 10, ty - 4, CREAM)
            px(img, 1 + bx, ty - 9, CREAM)
            px(img, 3 + bx, ty - 8, CREAM)
            px(img, 2 + bx, ty - 4, GOLD)
            fill_rect(img, 15 + bx, ty + 4, 20 + bx, ty + 9, VIOLET)
            fill_rect(img, 17 + bx, ty + 7, 21 + bx, ty + 10, SKIN)
        elif ap == 1:  # horizontal whisk sweep arc
            fill_rect(img, 15 + bx, ty + 0, 24 + bx, ty + 5, VIOLET)
            fill_rect(img, 20 + bx, ty + 1, 25 + bx, ty + 5, SKIN)
            fill_rect(img, 19 + bx, ty - 2, 32, ty + 1, WOOD)
            fill_rect(img, 27, ty - 4, 32, ty - 1, PAPER_L)
            px(img, 31, ty - 5, CREAM)
            px(img, 30, ty - 3, CREAM)
            px(img, 28, ty - 2, GOLD)
            fill_rect(img, 1 + bx, ty + 3, 7 + bx, ty + 8, VIOLET)
            fill_rect(img, 0 + bx, ty + 6, 4 + bx, ty + 9, SKIN)
        elif ap == 2:  # impact tip sparkle
            fill_rect(img, 16 + bx, ty + 1, 25 + bx, ty + 6, VIOLET)
            fill_rect(img, 22 + bx, ty + 2, 27 + bx, ty + 6, SKIN)
            fill_rect(img, 20 + bx, ty - 1, 32, ty + 2, WOOD)
            fill_rect(img, 28, ty - 3, 32, ty + 0, PAPER_L)
            px(img, 31, ty - 4, CREAM)
            px(img, 30, ty - 2, CREAM)
            px(img, 31, ty + 0, GOLD)
            px(img, 29, ty - 3, GOLD)
            px(img, 28, ty - 1, CREAM)
            px(img, 27, ty - 4, PAPER_L)
            fill_rect(img, 2 + bx, ty + 4, 8 + bx, ty + 9, VIOLET)
            fill_rect(img, 1 + bx, ty + 7, 5 + bx, ty + 10, SKIN)
        else:  # recover staff to side
            fill_rect(img, 14 + bx, ty + 2, 21 + bx, ty + 7, VIOLET)
            fill_rect(img, 17 + bx, ty + 2, 20 + bx, ty + 14, WOOD)
            hline(img, 17 + bx, 20 + bx, ty + 4, WOOD_L)
            px(img, 18 + bx, ty + 2, GOLD)
            fill_rect(img, 3 + bx, ty + 3, 8 + bx, ty + 8, VIOLET)
            fill_rect(img, 2 + bx, ty + 6, 6 + bx, ty + 9, SKIN)
    elif not pose.get("hurt"):
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
    draw_hem_sway(img, 7 + bx, 19 + bx, ly + 1, lift_l, lift_r, PAPER_L, PAPER_D)
    draw_feet(img, 8 + bx, ly + 5, 14 + bx, ly + 5, INK_SOFT, lift_l, lift_r,
              stride=3 if (lift_l or lift_r) else 0)
    if pose.get("hurt"):
        hp = pose.get("hurt_phase", 0)
        if hp == 0:
            fill_rect(img, 17 + bx, ty - 2, 25 + bx, ty + 3, VIOLET)
            fill_rect(img, 22 + bx, ty - 3, 27 + bx, ty + 1, SKIN)
            fill_rect(img, 1 + bx, ty + 5, 7 + bx, ty + 10, VIOLET)
            px(img, 15 + bx, 5 + oy, CINN_B)
            px(img, 17 + bx, 7 + oy, BLOOD)
            px(img, 10 + bx, 10 + oy, BLOOD)
            px(img, 18 + bx, 9 + oy, CINN_B)
            px(img, 20 + bx, 6 + oy, BLOOD)
            px(img, 12 + bx, 8 + oy, CINN_B)
        else:
            fill_rect(img, 18 + bx, ty + 4, 26 + bx, ty + 9, VIOLET)
            fill_rect(img, 23 + bx, ty + 7, 28 + bx, ty + 11, SKIN)
            fill_rect(img, 2 + bx, ty + 2, 8 + bx, ty + 7, VIOLET)
            px(img, 14 + bx, 4 + oy, BLOOD)
            px(img, 16 + bx, 8 + oy, CINN_B)
            px(img, 9 + bx, 12 + oy, BLOOD)
            px(img, 19 + bx, 11 + oy, CINN_B)
            px(img, 21 + bx, 9 + oy, BLOOD)
            px(img, 11 + bx, 9 + oy, CINN)


def xiaoer_body(img, ox, oy, pose):
    breath = pose.get("breath", 0)
    bx = ox + body_shift(pose)
    head_y = 1 + breath
    draw_head(img, 13 + bx, head_y + oy, hair=INK, face=SKIN, hat_wood=True)
    fill_rect(img, 11 + bx, 8 + breath + oy, 15 + bx, 10 + breath + oy, SKIN)
    ty = 9 + breath + oy
    # brown tunic + paper apron + cinnabar sash — denser apron folds
    fill_rect(img, 8 + bx, ty, 18 + bx, ty + 11, WOOD)
    draw_shoulder(img, 13 + bx, ty, 5, WOOD, WOOD_L)
    fill_rect(img, 9 + bx, ty + 4, 17 + bx, ty + 13, PAPER)
    fill_rect(img, 10 + bx, ty + 5, 16 + bx, ty + 12, PAPER_L)
    draw_robe_folds(img, 9 + bx, 17 + bx, ty + 7, PAPER_D)
    draw_belt(img, 8 + bx, 18 + bx, ty + 3, CINN, GOLD)
    # apron strings + pocket patch
    px(img, 9 + bx, ty + 4, CINN)
    px(img, 16 + bx, ty + 4, CINN)
    fill_rect(img, 12 + bx, ty + 8, 15 + bx, ty + 11, PAPER)
    outline_rect(img, 12 + bx, ty + 8, 15 + bx, ty + 11, PAPER_D)

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
            # pour arc into cup
            px(img, pot_x + 5, ty + 0, WOOD)
            px(img, pot_x + 6, ty + 1, LOESS)
            px(img, pot_x + 6, ty + 2, LOESS)
            px(img, pot_x + 7, ty + 3, LOESS)
            px(img, 27 + bx + arm_ext, ty + 1, LOESS)
            px(img, 27 + bx + arm_ext, ty + 0, CREAM)
    elif pose.get("wipe_phase") is not None:
        wp = pose["wipe_phase"]
        # lean over implied table: left hand brace + rag in right (not a tray)
        fill_rect(img, 3 + bx, ty + 7, 9 + bx, ty + 10, WOOD)
        fill_rect(img, 2 + bx, ty + 9, 6 + bx, ty + 11, SKIN)
        # table edge hint under wipe (wood plank strip)
        hline(img, 12 + bx, 31, ty + 12, WOOD_L)
        hline(img, 12 + bx, 31, ty + 13, WOOD)
        fill_rect(img, 16 + bx, ty + 2, 22 + bx, ty + 6, WOOD)
        fill_rect(img, 20 + bx, ty + 3, 24 + bx, ty + 6, SKIN)
        # rag: hanging flaps + damp MIST — silhouette ≠ tray/teapot
        if wp == 0:  # gather rag near body
            fill_rect(img, 18 + bx, ty + 7, 24 + bx, ty + 10, CREAM)
            fill_rect(img, 19 + bx, ty + 10, 22 + bx, ty + 13, PAPER_L)  # hang down
            hline(img, 18 + bx, 24 + bx, ty + 7, INK)
            px(img, 20 + bx, ty + 11, MIST)
            px(img, 23 + bx, ty + 8, PAPER)
        elif wp == 1:  # sweep mid
            fill_rect(img, 20 + bx, ty + 6, 28 + bx, ty + 9, CREAM)
            fill_rect(img, 22 + bx, ty + 9, 26 + bx, ty + 12, PAPER_L)
            hline(img, 20 + bx, 28 + bx, ty + 6, INK)
            px(img, 24 + bx, ty + 7, MIST)
            px(img, 26 + bx, ty + 8, MIST)
            px(img, 27 + bx, ty + 10, PAPER)
            px(img, 21 + bx, ty + 8, CREAM)
        elif wp == 2:  # far sweep
            fill_rect(img, 22 + bx, ty + 5, 31 + bx, ty + 8, CREAM)
            fill_rect(img, 25 + bx, ty + 8, 30 + bx, ty + 12, PAPER_L)
            hline(img, 22 + bx, 31 + bx, ty + 5, INK)
            px(img, 28 + bx, ty + 6, MIST)
            px(img, 26 + bx, ty + 7, MIST)
            px(img, 29 + bx, ty + 9, MIST)
            px(img, 30 + bx, ty + 11, PAPER)
            px(img, 24 + bx, ty + 6, CREAM)
        else:  # recover / shake rag
            fill_rect(img, 17 + bx, ty + 6, 23 + bx, ty + 9, CREAM)
            fill_rect(img, 18 + bx, ty + 9, 21 + bx, ty + 13, PAPER_L)
            hline(img, 17 + bx, 23 + bx, ty + 6, INK)
            px(img, 19 + bx, ty + 11, MIST)
            px(img, 22 + bx, ty + 7, PAPER)
            px(img, 20 + bx, ty + 8, CREAM)
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
    # walk: v1.2 higher lifts (8) + mid residual — hem sway reads
    poses.append({"lift_l": 8, "breath": 0})
    poses.append({"lift_l": 3, "breath": 0})
    poses.append({"lift_r": 8, "breath": 0})
    poses.append({"lift_r": 3, "breath": 1})
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
    # hurt 13–14: two strongly different reels (v1.2.1)
    poses.append({"hurt": True, "hurt_phase": 0, "breath": 0, "lift_l": 4})
    poses.append({"hurt": True, "hurt_phase": 1, "breath": 1, "lift_r": 3})
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
    """v1.2: broader shoulders, bigger weapon arcs, threat-readable silhouettes."""
    img = new_frame(32, 32)
    if which == "heifeng":
        # Black Wind chief: spiked hair, huge dao, plated chest
        draw_head(img, 10, 1, hair=INK, face=SKIN_D, fringe=True)
        fill_rect(img, 5, 1, 16, 5, INK)  # wild mane
        px(img, 7, 0, INK)
        px(img, 12, 0, INK)
        fill_rect(img, 6, 3, 15, 5, CINN_B)  # blood band
        fill_rect(img, 8, 8, 13, 10, SKIN_D)
        # broad torso + spaulders
        fill_rect(img, 4, 9, 18, 22, INK_SOFT)
        draw_shoulder(img, 11, 9, 8, WOOD, CINN_B)
        fill_rect(img, 6, 11, 16, 16, NIGHT)
        fill_rect(img, 7, 12, 15, 15, WOOD)
        px(img, 10, 13, GOLD)
        px(img, 12, 13, GOLD)
        fill_rect(img, 5, 16, 17, 18, FRAME)
        px(img, 11, 17, CINN_B)
        fill_rect(img, 6, 22, 11, 28, INK_SOFT)
        fill_rect(img, 11, 22, 16, 28, INK_SOFT)
        draw_feet(img, 5, 28, 12, 28, INK)
        # massive blade silhouette (right)
        fill_rect(img, 18, 2, 26, 28, INK)
        fill_rect(img, 19, 3, 25, 26, MIST)
        fill_rect(img, 20, 4, 24, 24, CINN_B)
        fill_rect(img, 18, 26, 26, 30, WOOD)
        px(img, 21, 1, CINN_B)
        px(img, 22, 2, CREAM)
        fill_rect(img, 15, 10, 19, 15, INK_SOFT)  # grip arm
        px(img, 17, 9, GOLD)
    else:
        # Evil medic: violet bun, toxin vial, clawed hand
        draw_head(img, 10, 1, hair=VIOLET, face=SKIN_D, hair_side=VIOLET, bun=True, double_bun=True)
        fill_rect(img, 8, 8, 13, 10, SKIN_D)
        fill_rect(img, 4, 9, 18, 22, VIOLET)
        draw_shoulder(img, 11, 9, 7, VIOLET, JADE_B)
        fill_rect(img, 6, 11, 16, 19, JADE)
        fill_rect(img, 7, 12, 15, 18, JADE_B)
        # toxin vial on belt
        fill_rect(img, 16, 14, 22, 22, ROBE_R)
        outline_rect(img, 16, 14, 22, 22, INK)
        fill_rect(img, 17, 15, 21, 20, JADE_B)
        px(img, 18, 13, GOLD)
        px(img, 19, 17, CINN)
        px(img, 19, 19, CINN_B)
        fill_rect(img, 5, 17, 17, 19, GOLD)
        fill_rect(img, 6, 22, 11, 28, VIOLET)
        fill_rect(img, 11, 22, 16, 28, VIOLET)
        draw_feet(img, 5, 28, 12, 28, INK_SOFT)
        # clawed reaching hand (threat)
        fill_rect(img, 18, 8, 28, 14, SKIN_D)
        px(img, 28, 7, JADE_B)
        px(img, 29, 8, JADE)
        px(img, 30, 9, CINN_B)
        px(img, 27, 6, CREAM)
        px(img, 29, 10, CINN)
    return img


def make_guest_sit() -> Image.Image:
    """6 seated guests, 32×32 each — v1.2 stabler sit, cup/bowl, clearer robe colors."""
    sheet = Image.new("RGBA", (192, 32), TRANS)
    variants = [
        # (robe, belt, hair, face, prop, prop_kind, hat_mode)
        (TEAL, WOOD_L, INK, SKIN, CREAM, "cup", "topknot"),
        (ROBE_R, GOLD, INK, SKIN, PAPER_L, "bowl", "bun"),
        (INK_SOFT, FRAME, INK, SKIN_D, CREAM, "cup", "fringe"),
        (VIOLET, GOLD, PAPER_L, SKIN, PAPER, "cup", "bald"),
        (JADE, WOOD_L, INK, SKIN, CINN_B, "bowl", "topknot"),
        (WOOD, CINN, INK, SKIN_D, CREAM, "cup", "hat"),
    ]
    for i, (robe, belt, hair, face, prop, kind, hat) in enumerate(variants):
        img = new_frame(32, 32)
        # denser stool with rung
        fill_rect(img, 7, 23, 23, 28, WOOD_L)
        outline_rect(img, 7, 23, 23, 28, INK)
        hline(img, 9, 21, 25, WOOD)
        fill_rect(img, 9, 28, 12, 32, WOOD)
        fill_rect(img, 18, 28, 21, 32, WOOD)
        px(img, 10, 31, INK)
        px(img, 19, 31, INK)
        # head variants
        kw = {}
        if hat == "topknot":
            kw = dict(topknot=True, tall_knot=True)
        elif hat == "bun":
            kw = dict(bun=True, double_bun=True, hair_side=hair)
        elif hat == "fringe":
            kw = dict(fringe=True)
        elif hat == "bald":
            kw = dict(bald_cap=True, hair_side=PAPER_L)
        elif hat == "hat":
            kw = dict(hat_wood=True)
        draw_head(img, 14, 3, hair=hair, face=face, **kw)
        if hat == "bald":
            px(img, 13, 7, VIOLET)
        if hat == "fringe":
            fill_rect(img, 9, 5, 19, 7, CINN_B)
        fill_rect(img, 12, 10, 16, 12, face)
        # seated torso — lower, wider lap for stability
        fill_rect(img, 8, 11, 21, 22, robe)
        fill_rect(img, 11, 11, 17, 13, PAPER_L)
        draw_robe_folds(img, 8, 21, 14, NIGHT if robe not in (PAPER_L, PAPER) else PAPER_D)
        draw_belt(img, 8, 21, 16, belt, GOLD)
        draw_shoulder(img, 14, 11, 6, robe, GOLD if i % 2 else None)
        # lap / bent legs
        fill_rect(img, 9, 19, 23, 25, robe)
        fill_rect(img, 17, 21, 25, 26, robe)
        hline(img, 9, 23, 24, NIGHT)
        # feet dangling clearer
        fill_rect(img, 10, 25, 15, 29, INK_SOFT)
        fill_rect(img, 18, 26, 24, 30, INK_SOFT)
        hline(img, 10, 15, 28, INK)
        hline(img, 18, 24, 29, INK)
        # arm holding cup or bowl
        fill_rect(img, 17, 13, 24, 17, robe)
        fill_rect(img, 22, 14, 26, 17, face)
        if kind == "cup":
            fill_rect(img, 24, 11, 29, 16, prop)
            outline_rect(img, 24, 11, 29, 16, INK)
            px(img, 26, 12, CREAM if prop != CREAM else PAPER_L)
            if i % 2 == 0:
                px(img, 26, 10, MIST)
                px(img, 27, 9, MIST)
        else:
            # bowl wider
            fill_rect(img, 23, 12, 31, 17, prop)
            outline_rect(img, 23, 12, 31, 17, INK)
            hline(img, 24, 30, 14, LOESS if prop != LOESS else GOLD)
            px(img, 26, 13, CREAM)
        # other hand on lap
        fill_rect(img, 6, 16, 10, 19, robe)
        fill_rect(img, 5, 17, 8, 20, face)
        sheet.paste(img, (i * 32, 0), img)
    return sheet


def _guest_hat_kwargs(hat: str, hair):
    if hat == "topknot":
        return dict(topknot=True, tall_knot=True)
    if hat == "bun":
        return dict(bun=True, double_bun=True, hair_side=hair)
    if hat == "fringe":
        return dict(fringe=True)
    if hat == "bald":
        return dict(bald_cap=True, hair_side=PAPER_L)
    if hat == "hat":
        return dict(hat_wood=True)
    return {}


def draw_guest_walk_frame(robe, belt, hair, face, hat, phase: int) -> Image.Image:
    """One 32×32 guest frame facing right.

    phase 0–3: walk (L lift, mid, R lift, mid)
    phase 4–5: approach (slowed walk / micro pause)
    phase 6: sit_down bend
    phase 7: sit settled (near guest_sit pose, no stool prop — stool is scene)
    """
    img = new_frame(32, 32)
    kw = _guest_hat_kwargs(hat, hair)

    # walk / approach parameters
    if phase in (0, 4):
        lift_l, lift_r, stride, breath = 6, 0, 2, 0
    elif phase in (1, 5):
        lift_l, lift_r, stride, breath = 0, 0, 0, 1
    elif phase == 2:
        lift_l, lift_r, stride, breath = 0, 6, 2, 0
    elif phase == 3:
        lift_l, lift_r, stride, breath = 0, 0, 0, 0
    else:
        lift_l, lift_r, stride, breath = 0, 0, 0, 0

    bx = 0
    if phase in (0, 4):
        bx = -1
    elif phase == 2:
        bx = 1
    elif phase == 6:
        bx = 0
    elif phase == 7:
        bx = 0

    if phase <= 5:
        # —— standing / walking ——
        head_y = 1 + breath
        draw_head(img, 13 + bx, head_y, hair=hair, face=face, **kw)
        if hat == "bald":
            px(img, 12, 7, VIOLET)
        if hat == "fringe":
            fill_rect(img, 8, 5, 18, 7, CINN_B)
        fill_rect(img, 11 + bx, 8 + breath, 15 + bx, 10 + breath, face)
        # torso
        ty = 9 + breath
        fill_rect(img, 8 + bx, ty, 19 + bx, ty + 12, robe)
        fill_rect(img, 10 + bx, ty + 1, 16 + bx, ty + 3, PAPER_L)
        draw_shoulder(img, 13 + bx, ty, 6, robe, GOLD)
        draw_robe_folds(img, 8 + bx, 19 + bx, ty + 5, NIGHT)
        draw_belt(img, 8 + bx, 19 + bx, ty + 7, belt, GOLD)
        # swinging arms
        if lift_l:
            fill_rect(img, 4 + bx, ty + 2, 9 + bx, ty + 8, robe)
            fill_rect(img, 3 + bx, ty + 7, 7 + bx, ty + 10, face)
            fill_rect(img, 17 + bx, ty + 1, 22 + bx, ty + 6, robe)
            fill_rect(img, 20 + bx, ty + 5, 24 + bx, ty + 8, face)
        elif lift_r:
            fill_rect(img, 17 + bx, ty + 2, 23 + bx, ty + 8, robe)
            fill_rect(img, 21 + bx, ty + 7, 25 + bx, ty + 10, face)
            fill_rect(img, 5 + bx, ty + 1, 10 + bx, ty + 6, robe)
            fill_rect(img, 4 + bx, ty + 5, 8 + bx, ty + 8, face)
        else:
            fill_rect(img, 5 + bx, ty + 2, 9 + bx, ty + 9, robe)
            fill_rect(img, 4 + bx, ty + 8, 8 + bx, ty + 11, face)
            fill_rect(img, 17 + bx, ty + 2, 22 + bx, ty + 9, robe)
            fill_rect(img, 20 + bx, ty + 8, 24 + bx, ty + 11, face)
        # legs + hem
        ly = ty + 12
        fill_rect(img, 9 + bx - (2 if lift_l else 0), ly - lift_l, 13 + bx - (2 if lift_l else 0), ly + 6 - lift_l, robe)
        fill_rect(img, 13 + bx + (2 if lift_r else 0), ly - lift_r, 17 + bx + (2 if lift_r else 0), ly + 6 - lift_r, robe)
        draw_hem_sway(img, 8 + bx, 19 + bx, ly + 1, lift_l, lift_r, robe, NIGHT)
        draw_feet(img, 8 + bx, 28, 14 + bx, 28, INK_SOFT, lift_l=lift_l, lift_r=lift_r, stride=stride)
        # approach pause: slightly tucked arms / slower silhouette cue
        if phase == 5:
            fill_rect(img, 16 + bx, ty + 3, 20 + bx, ty + 8, robe)
            px(img, 14 + bx, ty + 4, CREAM)

    elif phase == 6:
        # —— sit_down bend：彎腰下坐 ——
        draw_head(img, 14, 4, hair=hair, face=face, **kw)
        if hat == "bald":
            px(img, 13, 8, VIOLET)
        if hat == "fringe":
            fill_rect(img, 9, 6, 19, 8, CINN_B)
        fill_rect(img, 12, 11, 16, 13, face)
        # stool appearing under
        fill_rect(img, 7, 24, 23, 28, WOOD_L)
        outline_rect(img, 7, 24, 23, 28, INK)
        fill_rect(img, 9, 28, 12, 32, WOOD)
        fill_rect(img, 18, 28, 21, 32, WOOD)
        # bent torso leaning forward
        fill_rect(img, 7, 12, 20, 22, robe)
        fill_rect(img, 10, 12, 16, 14, PAPER_L)
        draw_belt(img, 7, 20, 17, belt, GOLD)
        draw_shoulder(img, 13, 12, 5, robe, GOLD)
        # thighs folding onto stool
        fill_rect(img, 8, 18, 24, 25, robe)
        fill_rect(img, 16, 20, 26, 26, robe)
        hline(img, 8, 24, 24, NIGHT)
        # arms reaching down / bracing
        fill_rect(img, 18, 13, 26, 17, robe)
        fill_rect(img, 24, 15, 28, 18, face)
        fill_rect(img, 5, 15, 10, 19, robe)
        fill_rect(img, 4, 17, 8, 20, face)
        # feet still nearly standing then tuck
        fill_rect(img, 10, 26, 15, 30, INK_SOFT)
        fill_rect(img, 17, 25, 22, 29, INK_SOFT)
        hline(img, 10, 15, 29, INK)
        hline(img, 17, 22, 28, INK)

    else:
        # —— sit settled：接近 guest_sit（無杯，方便切換到 guest_sit）——
        fill_rect(img, 7, 23, 23, 28, WOOD_L)
        outline_rect(img, 7, 23, 23, 28, INK)
        hline(img, 9, 21, 25, WOOD)
        fill_rect(img, 9, 28, 12, 32, WOOD)
        fill_rect(img, 18, 28, 21, 32, WOOD)
        px(img, 10, 31, INK)
        px(img, 19, 31, INK)
        draw_head(img, 14, 3, hair=hair, face=face, **kw)
        if hat == "bald":
            px(img, 13, 7, VIOLET)
        if hat == "fringe":
            fill_rect(img, 9, 5, 19, 7, CINN_B)
        fill_rect(img, 12, 10, 16, 12, face)
        fill_rect(img, 8, 11, 21, 22, robe)
        fill_rect(img, 11, 11, 17, 13, PAPER_L)
        draw_robe_folds(img, 8, 21, 14, NIGHT)
        draw_belt(img, 8, 21, 16, belt, GOLD)
        draw_shoulder(img, 14, 11, 6, robe, GOLD)
        fill_rect(img, 9, 19, 23, 25, robe)
        fill_rect(img, 17, 21, 25, 26, robe)
        hline(img, 9, 23, 24, NIGHT)
        fill_rect(img, 10, 25, 15, 29, INK_SOFT)
        fill_rect(img, 18, 26, 24, 30, INK_SOFT)
        hline(img, 10, 15, 28, INK)
        hline(img, 18, 24, 29, INK)
        # hands on lap (no cup — cut to guest_sit for prop)
        fill_rect(img, 17, 13, 23, 17, robe)
        fill_rect(img, 21, 14, 25, 17, face)
        fill_rect(img, 6, 16, 10, 19, robe)
        fill_rect(img, 5, 17, 8, 20, face)

    return img


def make_guest_walk() -> Image.Image:
    """6 guests × 8 frames = 1536×32 — walk / approach / sit_down.

    Guest order matches guest_sit 0–5:
      teal / robe-red / ink-soft / violet / jade / wood-hat.
    Per guest local frames:
      0–3 walk, 4–5 approach, 6 sit_down bend, 7 sit settled (no cup).
    Absolute index = guest * 8 + local.
    """
    sheet = Image.new("RGBA", (1536, 32), TRANS)
    variants = [
        # (robe, belt, hair, face, hat) — align guest_sit 0–5
        (TEAL, WOOD_L, INK, SKIN, "topknot"),
        (ROBE_R, GOLD, INK, SKIN, "bun"),
        (INK_SOFT, FRAME, INK, SKIN_D, "fringe"),
        (VIOLET, GOLD, PAPER_L, SKIN, "bald"),
        (JADE, WOOD_L, INK, SKIN, "topknot"),   # guestIndex 4 = jade
        (WOOD, CINN, INK, SKIN_D, "hat"),       # guestIndex 5 = wood-hat
    ]
    for gi, (robe, belt, hair, face, hat) in enumerate(variants):
        for phase in range(8):
            fr = draw_guest_walk_frame(robe, belt, hair, face, hat, phase)
            sheet.paste(fr, ((gi * 8 + phase) * 32, 0), fr)
    return sheet


# ---------- Hub ----------

def draw_wood_floor(img, y0, y1):
    W = img.width
    fill_rect(img, 0, y0, W, y1, WOOD)
    row_h = 7
    for y in range(y0, y1, row_h):
        hline(img, 0, W, y, INK_SOFT)
        hline(img, 0, W, y + row_h - 1, NIGHT)
        off = 0 if ((y - y0) // row_h) % 2 == 0 else 10
        for x in range(off, W, 20):
            vline(img, x, y, min(y + row_h, y1), NIGHT)
            # plank seam nails / grain
            if x + 3 < W:
                px(img, x + 3, y + 2, WOOD_L)
            if x + 8 < W:
                px(img, x + 8, y + 4, FRAME)
            if x + 14 < W and (x + y) % 5 == 0:
                px(img, x + 14, y + 3, INK_SOFT)


def draw_table(img, tx, ty, tw=40, th=18, fancy=False, dishes="full"):
    fill_rect(img, tx, ty, tx + tw, ty + 8, WOOD_L)
    outline_rect(img, tx, ty, tx + tw, ty + 8, INK)
    hline(img, tx + 2, tx + tw - 2, ty + 3, WOOD)
    hline(img, tx + 4, tx + tw - 4, ty + 5, FRAME)
    fill_rect(img, tx + 2, ty + 8, tx + tw - 2, ty + th, WOOD)
    fill_rect(img, tx + 2, ty + 8, tx + 6, ty + th, WOOD)
    fill_rect(img, tx + tw - 6, ty + 8, tx + tw - 2, ty + th, WOOD)
    vline(img, tx + 2, ty + 8, ty + th, INK)
    vline(img, tx + tw - 3, ty + 8, ty + th, INK)
    hline(img, tx + 2, tx + tw - 2, ty + th - 1, INK)
    # chopsticks + dishes denser
    if dishes in ("full", "bowl", "cup"):
        # chopsticks
        hline(img, tx + 3, tx + 11, ty + 1, INK)
        hline(img, tx + 3, tx + 11, ty + 2, INK_SOFT)
    if dishes in ("full", "bowl"):
        fill_rect(img, tx + 4, ty + 3, tx + 11, ty + 7, CREAM)
        outline_rect(img, tx + 4, ty + 3, tx + 11, ty + 7, INK)
        px(img, tx + 6, ty + 4, LOESS)
        px(img, tx + 8, ty + 5, GOLD)
    if dishes in ("full", "cup"):
        fill_rect(img, tx + 13, ty + 2, tx + 18, ty + 7, CINN_B)
        outline_rect(img, tx + 13, ty + 2, tx + 18, ty + 7, INK)
        px(img, tx + 15, ty + 3, CREAM)
    if dishes == "full" and tw >= 36:
        # wine pot
        fill_rect(img, tx + 20, ty + 0, tx + 30, ty + 7, WOOD)
        fill_rect(img, tx + 22, ty + 1, tx + 28, ty + 6, CINN)
        px(img, tx + 24, ty - 1 if ty > 0 else ty, GOLD)
        px(img, tx + 29, ty + 3, WOOD)  # spout
        # cup pair
        fill_rect(img, tx + 31, ty + 2, tx + 35, ty + 7, PAPER_L)
        outline_rect(img, tx + 31, ty + 2, tx + 35, ty + 7, INK)
        if tw >= 42:
            fill_rect(img, tx + 36, ty + 3, tx + 40, ty + 7, CREAM)
            outline_rect(img, tx + 36, ty + 3, tx + 40, ty + 7, INK)
    if fancy:
        fill_rect(img, tx + 7, ty + 1, tx + 12, ty + 3, JADE_B)
        px(img, tx + 18, ty + 3, LOESS)
        px(img, tx + 19, ty + 4, GOLD)
        px(img, tx + 9, ty + 2, CREAM)


def draw_floor_jar(img, jx, jy, col=JADE):
    """Wine jar sitting on floor — life density prop."""
    fill_rect(img, jx, jy, jx + 10, jy + 14, col)
    fill_rect(img, jx + 1, jy + 1, jx + 9, jy + 12, JADE_B if col == JADE else CINN_B)
    fill_rect(img, jx + 2, jy - 3, jx + 8, jy, GOLD)
    px(img, jx + 4, jy + 4, CREAM)
    outline_rect(img, jx, jy, jx + 10, jy + 14, INK)


def draw_stool(img, sx, sy):
    fill_rect(img, sx, sy, sx + 12, sy + 5, WOOD_L)
    outline_rect(img, sx, sy, sx + 12, sy + 5, INK)
    hline(img, sx + 1, sx + 11, sy + 2, WOOD)
    fill_rect(img, sx + 2, sy + 5, sx + 5, sy + 13, WOOD)
    fill_rect(img, sx + 7, sy + 5, sx + 10, sy + 13, WOOD)
    px(img, sx + 3, sy + 12, INK)
    px(img, sx + 8, sy + 12, INK)


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



def draw_notice_board(img, x, y, w=42, h=46):
    """Wall notice board — cinnabar frame + stacked paper notices (江湖熱點)."""
    fill_rect(img, x, y, x + w, y + h, CINN)
    outline_rect(img, x, y, x + w, y + h, INK)
    fill_rect(img, x + 2, y + 2, x + w - 2, y + h - 2, WOOD)
    # header bar
    fill_rect(img, x + 2, y + 2, x + w - 2, y + 8, CINN_B)
    hline(img, x + 3, x + w - 3, y + 4, GOLD)
    for gx in (x + 8, x + w // 2, x + w - 10):
        px(img, gx, y + 5, PAPER_L)
    # stacked notices
    notices = [
        (x + 4, y + 10, 16, 14, PAPER_L, CINN),
        (x + 22, y + 10, 16, 12, PAPER, BLOOD),
        (x + 4, y + 26, 18, 16, PAPER_D, INK_SOFT),
        (x + 24, y + 24, 14, 18, PAPER_L, JADE),
    ]
    for nx, ny, nw, nh, paper, accent in notices:
        fill_rect(img, nx, ny, nx + nw, ny + nh, paper)
        outline_rect(img, nx, ny, nx + nw, ny + nh, INK)
        for ly in range(ny + 2, ny + nh - 2, 3):
            hline(img, nx + 2, nx + nw - 2, ly, INK_SOFT)
        px(img, nx + nw - 3, ny + 2, accent)
        px(img, nx + 2, ny + 2, accent)


def draw_map_rack(img, x, y, w=44, h=52):
    """Hanging map / route board — far mountains + path blocks (據點熱點)."""
    fill_rect(img, x, y, x + w, y + h, WOOD_L)
    outline_rect(img, x, y, x + w, y + h, INK)
    fill_rect(img, x + 2, y + 2, x + w - 2, y + h - 2, PAPER)
    # sky band
    fill_rect(img, x + 3, y + 3, x + w - 3, y + 16, SKY)
    # mountains
    fill_rect(img, x + 4, y + 12, x + 18, y + 28, MTN)
    fill_rect(img, x + 14, y + 8, x + 30, y + 28, JADE)
    fill_rect(img, x + 26, y + 14, x + 40, y + 28, MTN)
    px(img, x + 20, y + 10, MIST)
    # path / route blocks
    for i, (px0, py0) in enumerate([(x + 8, y + 32), (x + 16, y + 36), (x + 24, y + 34), (x + 32, y + 38)]):
        fill_rect(img, px0, py0, px0 + 6, py0 + 4, LOESS if i % 2 == 0 else GOLD)
        outline_rect(img, px0, py0, px0 + 6, py0 + 4, INK)
    # route line
    hline(img, x + 10, x + 36, y + 42, WOOD)
    px(img, x + 12, y + 42, CINN_B)
    px(img, x + 22, y + 42, CINN)
    px(img, x + 34, y + 42, CINN_B)
    # seal
    px(img, x + w - 6, y + h - 6, CINN)
    px(img, x + w - 5, y + h - 5, CINN_B)
    # top hang pegs
    fill_rect(img, x + 6, y - 3, x + 10, y + 1, INK_SOFT)
    fill_rect(img, x + w - 10, y - 3, x + w - 6, y + 1, INK_SOFT)
    px(img, x + 7, y - 4, GOLD)
    px(img, x + w - 9, y - 4, GOLD)


def draw_bookshelf(img, x, y, w=38, h=48):
    """Multi-shelf books — spine color blocks (藏書熱點)."""
    fill_rect(img, x, y, x + w, y + h, WOOD)
    outline_rect(img, x, y, x + w, y + h, INK)
    fill_rect(img, x + 1, y + 1, x + w - 1, y + 4, WOOD_L)
    shelves = [y + 5, y + 18, y + 31, y + 42]
    spine_sets = [
        (CINN, CINN_B, BLOOD, ROBE_R, VIOLET, TEAL),
        (JADE, JADE_B, TEAL, TEAL_B, MTN, WOOD_L),
        (GOLD, LOESS, PAPER_D, FRAME, INK_SOFT, CINN),
        (VIOLET, BLOOD, TEAL, JADE, ROBE_R, CINN_B),
    ]
    for si, sy in enumerate(shelves[:-1]):
        hline(img, x + 2, x + w - 2, shelves[si + 1] - 1, INK_SOFT)
        colors = spine_sets[si % len(spine_sets)]
        bx = x + 3
        for i, col in enumerate(colors):
            bw = 4 if i % 3 else 5
            if bx + bw >= x + w - 2:
                break
            fill_rect(img, bx, sy, bx + bw, shelves[si + 1] - 2, col)
            px(img, bx + 1, sy + 2, PAPER_L if col != PAPER_D else CREAM)
            bx += bw + 1
    # top ornament
    px(img, x + w // 2, y + 2, GOLD)


def draw_door_threshold(img, x0, x1, y):
    """Door sill on floor — clickable entrance feel."""
    fill_rect(img, x0, y, x1, y + 4, WOOD_L)
    outline_rect(img, x0, y, x1, y + 4, INK)
    hline(img, x0 + 2, x1 - 2, y + 1, GOLD)
    for tx in range(x0 + 4, x1 - 4, 6):
        px(img, tx, y + 2, LOESS)


def draw_hero_seat_marker(img, x, y, w=70, h=22):
    """席区 carpet under hero table — readable seat zone, not corridor."""
    fill_rect(img, x, y, x + w, y + h, TEAL)
    outline_rect(img, x, y, x + w, y + h, INK)
    fill_rect(img, x + 2, y + 2, x + w - 2, y + h - 2, TEAL_B)
    # abstract 「席」block motif (not copied glyph art)
    cx, cy = x + w // 2, y + h // 2
    fill_rect(img, cx - 6, cy - 5, cx + 6, cy - 3, GOLD)
    fill_rect(img, cx - 1, cy - 5, cx + 1, cy + 5, GOLD)
    fill_rect(img, cx - 5, cy + 1, cx + 5, cy + 3, LOESS)
    for i in range(x + 5, x + w - 5, 8):
        px(img, i, y + 3, PAPER_L)
        px(img, i, y + h - 4, PAPER_L)


def draw_hard_shadow(img, x, y, w, h, ox=3, oy=2, col=NIGHT):
    """Opaque hard-offset footprint shadow — no alpha, no blur (ART.md)."""
    fill_rect(img, x + ox, y + oy, x + w + ox, y + h + oy, col)


def draw_pennant_string(img, x0, y0, x1, n=14, colors=None, drop=8):
    """Triangular pennant string (旗串) along a near-horizontal rope."""
    if colors is None:
        colors = [CINN, JADE, GOLD, PAPER_L, TEAL, CINN_B, BLOOD, LOESS]
    if x1 < x0:
        x0, x1 = x1, x0
    hline(img, x0, x1, y0, INK_SOFT)
    hline(img, x0, x1, y0 + 1, FRAME)
    span = max(1, x1 - x0)
    for i in range(n):
        cx = x0 + (i * span) // max(1, n - 1) if n > 1 else x0
        col = colors[i % len(colors)]
        for dy in range(drop):
            ww = max(1, 5 - dy // 2)
            fill_rect(img, cx - ww // 2, y0 + 2 + dy, cx - ww // 2 + ww, y0 + 3 + dy, col)
        px(img, cx, y0 + 1 + drop, INK)


def draw_banner(img, x, y, w=12, h=36, cloth=PAPER_L, accent=CINN, pole=True):
    """Vertical hanging cloth banner (豎旗／布幌)."""
    if pole:
        vline(img, x + w // 2, y - 8, y, INK_SOFT)
        fill_rect(img, x - 1, y - 2, x + w + 1, y + 1, WOOD_L)
        outline_rect(img, x - 1, y - 2, x + w + 1, y + 1, INK)
    fill_rect(img, x, y, x + w, y + h, cloth)
    outline_rect(img, x, y, x + w, y + h, INK)
    fill_rect(img, x + 1, y + 1, x + w - 1, y + 4, accent)
    for sy in range(y + 7, y + h - 5, 5):
        hline(img, x + 2, x + w - 2, sy, INK_SOFT)
        if ((sy - y) // 5) % 2 == 0:
            fill_rect(img, x + 3, sy + 1, x + w - 3, sy + 3, accent if accent != cloth else INK)
    for fx in range(x + 1, x + w - 1, 3):
        vline(img, fx, y + h, y + h + 3, cloth)
    px(img, x + w // 2, y + 2, GOLD)


def draw_hanging_cloth(img, x, y, w=22, h=14, cloth=CINN):
    """Short shop cloth 布幌 under beam."""
    fill_rect(img, x, y, x + w, y + 3, WOOD_L)
    outline_rect(img, x, y, x + w, y + 3, INK)
    fill_rect(img, x + 1, y + 3, x + w - 1, y + h, cloth)
    outline_rect(img, x + 1, y + 3, x + w - 1, y + h, INK)
    px(img, x + w // 2, y + 6, GOLD)
    px(img, x + w // 2 - 1, y + 8, LOESS)
    for fx in range(x + 2, x + w - 2, 4):
        vline(img, fx, y + h, y + h + 3, cloth)


def draw_crate(img, x, y, w=16, h=12):
    """Wooden crate / box prop."""
    fill_rect(img, x, y, x + w, y + h, WOOD)
    outline_rect(img, x, y, x + w, y + h, INK)
    hline(img, x + 1, x + w - 1, y + h // 2, INK_SOFT)
    vline(img, x + w // 2, y + 1, y + h - 1, FRAME)
    px(img, x + 2, y + 2, WOOD_L)
    px(img, x + w - 3, y + h - 3, NIGHT)


def draw_basket(img, x, y, w=14, h=10, fill=JADE_B):
    """Woven basket with peeking contents."""
    fill_rect(img, x, y + 2, x + w, y + h, LOESS)
    outline_rect(img, x, y + 2, x + w, y + h, INK)
    fill_rect(img, x + 1, y, x + w - 1, y + 4, fill)
    for i in range(x + 2, x + w - 2, 3):
        vline(img, i, y + 3, y + h - 1, WOOD)
    px(img, x + w // 2, y + 1, CREAM)


def draw_scroll_stack(img, x, y, n=3):
    """Stacked scrolls / books on floor or shelf foot."""
    for i in range(n):
        paper = PAPER if i % 2 == 0 else PAPER_L
        fill_rect(img, x + i, y - i * 3, x + 14 + i, y + 4 - i * 3, paper)
        outline_rect(img, x + i, y - i * 3, x + 14 + i, y + 4 - i * 3, INK)
        px(img, x + 12 + i, y - i * 3 + 1, CINN)
        hline(img, x + 2 + i, x + 10 + i, y - i * 3 + 2, INK_SOFT)


def draw_stall_cloth(img, tx, ty, tw, cloth=MIST):
    """Tattered cloth drape over table edge (攤布感)."""
    fill_rect(img, tx + 2, ty + 6, tx + tw - 2, ty + 14, cloth)
    outline_rect(img, tx + 2, ty + 6, tx + tw - 2, ty + 14, INK)
    for fx in range(tx + 3, tx + tw - 3, 5):
        vline(img, fx, ty + 14, ty + 17, cloth)
    px(img, tx + tw // 2, ty + 9, PAPER_D)


def draw_cloth_bag(img, x, y, w=12, h=10, cloth=PAPER_D):
    """Tied cloth bundle / 布包 on floor."""
    fill_rect(img, x, y + 2, x + w, y + h, cloth)
    outline_rect(img, x, y + 2, x + w, y + h, INK)
    fill_rect(img, x + 2, y, x + w - 2, y + 4, cloth)
    px(img, x + w // 2, y, INK_SOFT)  # knot
    px(img, x + w // 2 - 1, y + 1, GOLD)
    px(img, x + 2, y + h - 2, NIGHT)


def draw_produce_basket(img, x, y, w=16, h=11, fills=None):
    """Basket with multi-color produce blocks (蔬果籃)."""
    if fills is None:
        fills = [JADE_B, LOESS, CINN_B, PAPER_L]
    fill_rect(img, x, y + 3, x + w, y + h, WOOD_L)
    outline_rect(img, x, y + 3, x + w, y + h, INK)
    for i in range(x + 2, x + w - 2, 3):
        vline(img, i, y + 4, y + h - 1, WOOD)
    # peeking produce
    for i, col in enumerate(fills[:4]):
        px0 = x + 2 + i * 3
        if px0 + 3 >= x + w:
            break
        fill_rect(img, px0, y, px0 + 3, y + 5, col)
        px(img, px0 + 1, y + 1, CREAM if col != CREAM else PAPER_L)


def draw_small_pot(img, x, y, col=FRAME):
    """Tiny ceramic pot / 陶壺 (smaller than floor jar)."""
    fill_rect(img, x, y, x + 7, y + 9, col)
    fill_rect(img, x + 1, y + 1, x + 6, y + 8, WOOD if col == FRAME else CINN_B)
    fill_rect(img, x + 2, y - 2, x + 5, y, GOLD)
    outline_rect(img, x, y, x + 7, y + 9, INK)
    px(img, x + 3, y + 3, CREAM)


def draw_lantern(img, lx, ly, hanging=True, night=False):
    if hanging:
        vline(img, lx + 4, ly - 10, ly, INK)
        hline(img, lx + 2, lx + 7, ly - 10, INK)
        px(img, lx + 4, ly - 11, FRAME)
    fill_rect(img, lx, ly, lx + 9, ly + 12, CINN)
    fill_rect(img, lx + 1, ly + 1, lx + 8, ly + 11, CINN_B)
    fill_rect(img, lx, ly, lx + 9, ly + 2, GOLD)
    fill_rect(img, lx, ly + 10, lx + 9, ly + 12, GOLD)
    # flame
    px(img, lx + 4, ly + 5, CREAM)
    px(img, lx + 3, ly + 6, PAPER_L)
    px(img, lx + 5, ly + 6, LOESS)
    if night:
        # larger flame core + extra cream / cinnabar bright cells
        px(img, lx + 4, ly + 4, CREAM)
        px(img, lx + 3, ly + 5, CREAM)
        px(img, lx + 5, ly + 5, CREAM)
        px(img, lx + 4, ly + 6, PAPER_L)
        px(img, lx + 2, ly + 6, CINN_B)
        px(img, lx + 6, ly + 6, CINN_B)
        px(img, lx + 4, ly + 7, LOESS)
        # hard-block night "glow" halo (opaque night ink / wood, NOT soft alpha)
        for ox, oy in [(-2, 4), (-1, 3), (9, 4), (10, 3), (3, -1), (5, -1),
                       (-2, 8), (9, 8), (1, 13), (7, 13)]:
            px(img, lx + ox, ly + oy, NIGHT)
        for ox, oy in [(-1, 4), (9, 4), (4, -1), (2, 13), (6, 13)]:
            px(img, lx + ox, ly + oy, INK_SOFT)
    # tassels longer
    vline(img, lx + 2, ly + 12, ly + 18, GOLD)
    vline(img, lx + 6, ly + 12, ly + 18, GOLD)
    px(img, lx + 2, ly + 18, LOESS)
    px(img, lx + 6, ly + 18, LOESS)


def make_hub_layers():
    """Hub v2.0 — native 960×540 (draw logical 480×270 then NEAREST ×2).
    Throng ~halved; hotspot breathing room; corridor mid clear (logical x 195–275 → 390–550).
    """
    # Draw at logical base, then integer-scale to native output size.
    BW, BH = 480, 270
    OW, OH = 960, 540
    layers_base = {}

    # ----- FLOOR -----
    floor = Image.new("RGBA", (BW, BH), TRANS)
    draw_wood_floor(floor, 148, 270)
    for y in range(158, 248):
        for x in range(70, 410):
            if (x + y * 3) % 11 == 0:
                r, g, b, a = floor.getpixel((x, y))
                if a and (r, g, b) == WOOD[:3]:
                    floor.putpixel((x, y), WOOD_L)
    # guest rugs — fewer, leave breathing gaps near hotspots
    draw_hard_shadow(floor, 78, 210, 58, 18, ox=2, oy=2, col=INK_SOFT)
    draw_rug(floor, 78, 210, 58, 18)
    draw_hard_shadow(floor, 300, 210, 52, 18, ox=2, oy=2, col=INK_SOFT)
    draw_rug(floor, 300, 210, 52, 18)
    # 俠客席 carpet
    draw_hard_shadow(floor, 338, 188, 72, 24, ox=3, oy=2, col=NIGHT)
    draw_hero_seat_marker(floor, 338, 188, 72, 24)
    # door threshold
    draw_hard_shadow(floor, 8, 146, 46, 4, ox=2, oy=1, col=NIGHT)
    draw_door_threshold(floor, 8, 54, 146)
    # counter hard shadow footprint
    draw_hard_shadow(floor, 155, 210, 180, 12, ox=4, oy=3, col=NIGHT)
    draw_hard_shadow(floor, 157, 200, 176, 8, ox=3, oy=2, col=INK_SOFT)
    # central corridor walk-band logical x≈195–275 keep light / clear
    for y in range(160, 268):
        for x in range(195, 276):
            if (x + y) % 7 == 0:
                r, g, b, a = floor.getpixel((x, y))
                if a and (r, g, b) in (WOOD[:3], WOOD_L[:3], INK_SOFT[:3], NIGHT[:3]):
                    floor.putpixel((x, y), WOOD_L)
    for y in range(155, 270, 3):
        px(floor, 194, y, FRAME)
        px(floor, 276, y, FRAME)
    layers_base["hub_floor.png"] = floor

    # ----- WALL -----
    wall = Image.new("RGBA", (BW, BH), TRANS)
    fill_rect(wall, 0, 0, BW, 68, SKY)
    for i, (mx, mh) in enumerate([(0, 40), (40, 55), (90, 35), (130, 50), (180, 42),
                                   (230, 58), (280, 38), (320, 52), (370, 44), (420, 50)]):
        fill_rect(wall, mx, 68 - mh, mx + 55, 68, MTN)
        if i % 2 == 0:
            fill_rect(wall, mx + 10, 68 - mh + 8, mx + 40, 68, JADE)
        if i % 3 == 0:
            px(wall, mx + 20, 68 - mh + 4, MIST)
    hline(wall, 0, BW, 68, MIST)
    fill_rect(wall, 0, 68, BW, 148, NIGHT)
    fill_rect(wall, 0, 88, BW, 148, WOOD)
    # wall panels — skip landmark slots + leave breathing
    for x in range(0, BW, 36):
        if 100 <= x <= 144:  # notice + bookshelf zone
            continue
        if 360 <= x <= 396:  # map rack
            continue
        if x < 54:  # door
            continue
        vline(wall, x, 88, 148, INK_SOFT)
        fill_rect(wall, x + 3, 92, x + 33, 140, FRAME)
        fill_rect(wall, x + 5, 94, x + 31, 138, WOOD)
        slot = (x // 36) % 3
        if slot == 1:
            fill_rect(wall, x + 8, 100, x + 28, 128, SKY)
            outline_rect(wall, x + 8, 100, x + 28, 128, INK)
            hline(wall, x + 8, x + 28, 109, GOLD)
            hline(wall, x + 8, x + 28, 118, GOLD)
            vline(wall, x + 14, 100, 128, GOLD)
            vline(wall, x + 22, 100, 128, GOLD)
            fill_rect(wall, x + 9, 119, x + 27, 128, MTN)
            hline(wall, x + 7, x + 29, 128, WOOD_L)
        elif slot == 0:
            fill_rect(wall, x + 10, 98, x + 26, 134, PAPER)
            outline_rect(wall, x + 10, 98, x + 26, 134, INK)
            fill_rect(wall, x + 10, 98, x + 26, 101, WOOD_L)
            fill_rect(wall, x + 10, 131, x + 26, 134, WOOD_L)
            for sy in range(106, 128, 3):
                hline(wall, x + 13, x + 23, sy, INK_SOFT)
            fill_rect(wall, x + 14, 114, x + 22, 126, MTN)
            px(wall, x + 18, 120, CINN)
            px(wall, x + 19, 121, CINN_B)
        else:
            fill_rect(wall, x + 10, 102, x + 26, 130, PAPER_D)
            outline_rect(wall, x + 10, 102, x + 26, 130, GOLD)
            for sy in (108, 116, 124):
                vline(wall, x + 15, sy, sy + 5, INK)
                vline(wall, x + 20, sy, sy + 5, INK_SOFT)
    # beam / lintel
    fill_rect(wall, 0, 142, BW, 150, INK_SOFT)
    hline(wall, 0, BW, 142, GOLD)
    hline(wall, 0, BW, 144, LOESS)
    for bx in range(20, BW, 48):
        fill_rect(wall, bx, 138, bx + 10, 142, WOOD_L)
    # ===== 大門 =====
    fill_rect(wall, 6, 96, 52, 148, NIGHT)
    fill_rect(wall, 10, 100, 48, 148, WOOD_L)
    outline_rect(wall, 10, 100, 48, 148, INK)
    vline(wall, 29, 100, 148, INK)
    for dy in (108, 118, 128, 138):
        hline(wall, 14, 26, dy, WOOD)
        hline(wall, 32, 44, dy, WOOD)
        px(wall, 20, dy + 2, GOLD)
        px(wall, 38, dy + 2, GOLD)
    fill_rect(wall, 22, 124, 28, 132, GOLD)
    outline_rect(wall, 22, 124, 28, 132, INK)
    px(wall, 24, 127, LOESS)
    fill_rect(wall, 32, 124, 38, 132, GOLD)
    outline_rect(wall, 32, 124, 38, 132, INK)
    px(wall, 34, 127, LOESS)
    fill_rect(wall, 6, 82, 54, 98, CINN)
    outline_rect(wall, 6, 82, 54, 98, GOLD)
    hline(wall, 8, 52, 84, LOESS)
    for px0 in (14, 22, 30, 38, 46):
        vline(wall, px0, 86, 96, PAPER_L)
        px(wall, px0, 88, CREAM)
        px(wall, px0 + 1, 92, PAPER)
    fill_rect(wall, 56, 100, 66, 140, PAPER)
    outline_rect(wall, 56, 100, 66, 140, INK)
    for sy in range(106, 136, 5):
        hline(wall, 58, 64, sy, INK_SOFT)
    fill_rect(wall, 0, 100, 6, 140, PAPER_D)
    for sy in range(106, 136, 5):
        hline(wall, 1, 5, sy, INK_SOFT)
    # ===== 告示板 / 地圖架 =====
    draw_notice_board(wall, 108, 92, 44, 48)
    draw_map_rack(wall, 362, 94, 46, 50)
    for bx in range(12, BW, 40):
        fill_rect(wall, bx, 136, bx + 8, 142, WOOD_L)
        px(wall, bx + 3, 138, GOLD)
    # 豎旗／布幌 — keep but not packed (v2.0 減雜)
    draw_banner(wall, 70, 100, 11, 34, cloth=PAPER_L, accent=CINN)
    draw_banner(wall, 196, 96, 10, 40, cloth=CREAM, accent=TEAL)
    draw_banner(wall, 280, 98, 11, 36, cloth=PAPER_L, accent=BLOOD)
    draw_banner(wall, 412, 96, 11, 38, cloth=PAPER, accent=VIOLET)
    draw_hanging_cloth(wall, 78, 128, 24, 16, cloth=CINN)
    draw_hanging_cloth(wall, 248, 124, 22, 15, cloth=TEAL)
    draw_hanging_cloth(wall, 430, 128, 22, 16, cloth=BLOOD)
    layers_base["hub_wall.png"] = wall

    # ----- COUNTER -----
    counter = Image.new("RGBA", (BW, BH), TRANS)
    cx, cy, cw, ch = 155, 165, 180, 55
    draw_hard_shadow(counter, cx + 2, cy + 12, cw - 4, ch - 10, ox=4, oy=3, col=NIGHT)
    fill_rect(counter, cx - 2, cy - 2, cx + cw + 2, cy + 14, FRAME)
    fill_rect(counter, cx, cy, cx + cw, cy + 12, WOOD_L)
    outline_rect(counter, cx, cy, cx + cw, cy + 12, INK)
    hline(counter, cx + 4, cx + cw - 4, cy + 5, WOOD)
    hline(counter, cx + 8, cx + cw - 8, cy + 8, FRAME)
    for tx in range(cx + 10, cx + cw - 8, 18):
        px(counter, tx, cy + 1, GOLD)
        px(counter, tx + 1, cy + 1, LOESS)
    fill_rect(counter, cx + 2, cy + 12, cx + cw - 2, cy + ch, WOOD)
    for px0 in range(cx + 8, cx + cw - 8, 26):
        fill_rect(counter, px0, cy + 16, px0 + 20, cy + ch - 4, FRAME)
        fill_rect(counter, px0 + 2, cy + 18, px0 + 18, cy + ch - 6, WOOD)
        px(counter, px0 + 9, cy + 28, GOLD)
        hline(counter, px0 + 3, px0 + 17, cy + 22, INK_SOFT)
    fill_rect(counter, cx + 6, cy + 0, cx + 28, cy + 11, PAPER)
    fill_rect(counter, cx + 28, cy + 0, cx + 48, cy + 11, PAPER_L)
    outline_rect(counter, cx + 6, cy + 0, cx + 48, cy + 11, INK)
    fill_rect(counter, cx + 26, cy + 0, cx + 30, cy + 11, BLOOD)
    for ly in (2, 4, 6, 8):
        hline(counter, cx + 8, cx + 24, cy + ly, INK_SOFT)
        hline(counter, cx + 32, cx + 46, cy + ly, INK_SOFT)
    px(counter, cx + 42, cy + 3, CINN)
    px(counter, cx + 43, cy + 4, CINN_B)
    fill_rect(counter, cx + 48, cy - 10, cx + 68, cy + 8, CINN)
    fill_rect(counter, cx + 50, cy - 8, cx + 66, cy + 6, CINN_B)
    fill_rect(counter, cx + 68, cy - 3, cx + 76, cy + 2, WOOD)
    fill_rect(counter, cx + 44, cy - 2, cx + 48, cy + 3, WOOD)
    fill_rect(counter, cx + 54, cy - 12, cx + 64, cy - 10, GOLD)
    px(counter, cx + 58, cy - 6, CREAM)
    for cup_x in (80, 92, 104):
        fill_rect(counter, cx + cup_x, cy + 1, cx + cup_x + 8, cy + 9,
                  CREAM if cup_x != 92 else PAPER_L)
        outline_rect(counter, cx + cup_x, cy + 1, cx + cup_x + 8, cy + 9, INK)
    fill_rect(counter, cx + 120, cy + 0, cx + 162, cy + 11, WOOD)
    outline_rect(counter, cx + 120, cy + 0, cx + 162, cy + 11, INK)
    hline(counter, cx + 122, cx + 160, cy + 5, INK_SOFT)
    for bx in range(cx + 124, cx + 160, 5):
        vline(counter, bx, cy + 1, cy + 10, FRAME)
        px(counter, bx - 1, cy + 2, CINN_B)
        px(counter, bx - 1, cy + 3, CINN)
        px(counter, bx - 1, cy + 7, GOLD)
        px(counter, bx - 1, cy + 8, LOESS)
    fill_rect(counter, cx + 162, cy + 1, cx + 176, cy + 10, GOLD)
    fill_rect(counter, cx + 164, cy - 2, cx + 174, cy + 2, LOESS)
    px(counter, cx + 166, cy + 3, WOOD_L)
    px(counter, cx + 170, cy + 4, WOOD_L)
    px(counter, cx + 168, cy + 6, CREAM)
    fill_rect(counter, cx + 150, cy + 3, cx + 160, cy + 10, GOLD)
    px(counter, cx + 154, cy + 5, LOESS)
    fill_rect(counter, cx + 4, cy - 16, cx + 18, cy + 2, JADE)
    fill_rect(counter, cx + 6, cy - 14, cx + 16, cy, JADE_B)
    fill_rect(counter, cx + 7, cy - 18, cx + 15, cy - 16, GOLD)
    px(counter, cx + 10, cy - 10, CREAM)
    fill_rect(counter, cx + 22, cy - 6, cx + 30, cy + 2, INK_SOFT)
    vline(counter, cx + 24, cy - 10, cy - 4, INK)
    vline(counter, cx + 27, cy - 9, cy - 4, WOOD)
    fill_rect(counter, cx + 32, cy + 2, cx + 42, cy + 9, NIGHT)
    outline_rect(counter, cx + 32, cy + 2, cx + 42, cy + 9, INK)
    px(counter, cx + 36, cy + 4, MIST)
    # keep one basket + scroll on counter (readable, not throng)
    draw_basket(counter, cx + 108, cy - 8, 12, 9, fill=LOESS)
    draw_scroll_stack(counter, cx + 70, cy - 2, n=2)
    layers_base["hub_counter.png"] = counter

    # ----- FURNITURE (breathing room; throng ~halved; clear hotspots + corridor) -----
    furn = Image.new("RGBA", (BW, BH), TRANS)
    tables = [
        (40, 175, 50, 18, True, "full"),
        (48, 220, 46, 18, False, "full"),
        (100, 190, 44, 16, True, "full"),
        (290, 175, 52, 18, True, "full"),
        (320, 220, 46, 18, False, "full"),
        # 俠客席貴桌
        (348, 178, 54, 18, True, "full"),
        (400, 220, 44, 16, True, "full"),
        (55, 248, 40, 14, False, "cup"),
        (350, 248, 42, 16, False, "full"),
        (430, 185, 40, 16, True, "full"),
    ]
    for t in tables:
        tx, ty, tw, th = t[0], t[1], t[2], t[3]
        draw_hard_shadow(furn, tx + 2, ty + 8, tw - 4, th - 6, ox=3, oy=2, col=NIGHT)
        draw_table(furn, *t)
    draw_stall_cloth(furn, 48, 220, 46, cloth=MIST)
    draw_stall_cloth(furn, 320, 220, 46, cloth=PAPER_D)
    stools = [
        (30, 190), (86, 190), (36, 236), (90, 236),
        (90, 205), (140, 205),
        (45, 260), (90, 260),
        (280, 192), (338, 192), (310, 236), (362, 236),
        # hero seat stools (clear around seat carpet)
        (340, 196), (400, 196),
        (340, 254), (420, 254),
        (420, 200), (60, 205),
    ]
    for s in stools:
        sx, sy = s
        draw_hard_shadow(furn, sx, sy + 5, 12, 8, ox=2, oy=2, col=NIGHT)
        draw_stool(furn, *s)
    # floor jars — away from door / counter / corridor / map / seat clutter
    for jx, jy, col in [
        (30, 205, JADE), (30, 240, CINN),
        (460, 235, JADE), (460, 255, CINN),
        (70, 180, TEAL), (445, 215, VIOLET),
        (18, 255, JADE_B),
    ]:
        draw_hard_shadow(furn, jx, jy + 4, 10, 10, ox=2, oy=2, col=NIGHT)
        draw_floor_jar(furn, jx, jy, col)
    # wine shelf
    draw_hard_shadow(furn, 48, 130, 57, 26, ox=3, oy=2, col=NIGHT)
    fill_rect(furn, 48, 118, 105, 156, WOOD)
    outline_rect(furn, 48, 118, 105, 156, INK)
    hline(furn, 50, 103, 130, INK_SOFT)
    hline(furn, 50, 103, 142, INK_SOFT)
    for row, y0 in ((0, 120), (1, 132), (2, 144)):
        for i, col in enumerate((CINN, CINN_B, JADE, ROBE_R, VIOLET, TEAL)):
            jx = 52 + i * 9
            fill_rect(furn, jx, y0, jx + 7, y0 + 9, col)
            px(furn, jx + 2, y0 - 1, GOLD)
            if row == 0:
                px(furn, jx + 3, y0 + 3, CREAM)
    # ===== 書架 =====
    draw_hard_shadow(furn, 108, 130, 40, 32, ox=3, oy=2, col=NIGHT)
    draw_bookshelf(furn, 108, 112, 40, 50)
    # weapon rack
    draw_hard_shadow(furn, 448, 130, 28, 34, ox=3, oy=2, col=NIGHT)
    fill_rect(furn, 448, 120, 476, 164, WOOD)
    outline_rect(furn, 448, 120, 476, 164, INK)
    vline(furn, 454, 124, 160, TEAL_B)
    vline(furn, 460, 126, 160, INK_SOFT)
    vline(furn, 466, 124, 160, MIST)
    vline(furn, 472, 128, 158, WOOD_L)
    px(furn, 454, 122, GOLD)
    px(furn, 460, 124, CINN_B)
    px(furn, 466, 122, GOLD)
    # folding screen
    draw_hard_shadow(furn, 416, 120, 30, 46, ox=3, oy=2, col=NIGHT)
    fill_rect(furn, 416, 108, 446, 166, PAPER_D)
    outline_rect(furn, 416, 108, 446, 166, INK)
    vline(furn, 431, 108, 166, WOOD)
    for sy in range(116, 160, 5):
        hline(furn, 419, 429, sy, MIST)
        hline(furn, 433, 443, sy, MIST)
    fill_rect(furn, 420, 126, 429, 152, MTN)
    fill_rect(furn, 434, 130, 443, 154, JADE)
    px(furn, 424, 140, SKY)
    px(furn, 438, 138, CINN)
    # stove
    draw_hard_shadow(furn, 150, 156, 33, 14, ox=2, oy=2, col=NIGHT)
    fill_rect(furn, 150, 146, 183, 170, INK_SOFT)
    fill_rect(furn, 154, 150, 179, 166, NIGHT)
    px(furn, 161, 154, CINN_B)
    px(furn, 165, 156, GOLD)
    px(furn, 167, 158, CREAM)
    px(furn, 163, 160, LOESS)
    fill_rect(furn, 157, 144, 176, 149, FRAME)
    fill_rect(furn, 160, 140, 174, 148, INK_SOFT)
    fill_rect(furn, 162, 141, 172, 146, MIST)
    px(furn, 166, 142, CREAM)
    # side cabinet
    draw_hard_shadow(furn, 455, 210, 23, 38, ox=3, oy=2, col=NIGHT)
    fill_rect(furn, 455, 198, 478, 248, WOOD)
    outline_rect(furn, 455, 198, 478, 248, INK)
    hline(furn, 457, 476, 218, INK_SOFT)
    hline(furn, 457, 476, 232, INK_SOFT)
    px(furn, 466, 208, GOLD)
    px(furn, 466, 224, GOLD)
    px(furn, 466, 240, GOLD)
    # broom near door (not blocking)
    fill_rect(furn, 68, 210, 72, 236, WOOD_L)
    px(furn, 70, 208, INK_SOFT)
    fill_rect(furn, 66, 236, 76, 242, FRAME)
    # ===== throng ~half — wall feet / table gaps ONLY; no corridor edges; clear hotspots =====
    for cx0, cy0, cw0, ch0 in [
        (18, 218, 16, 12), (18, 236, 14, 10),
        (440, 248, 18, 12), (72, 248, 14, 10),
        (8, 252, 16, 11), (420, 230, 14, 10),
        (50, 188, 13, 10), (330, 255, 16, 11),
    ]:
        draw_hard_shadow(furn, cx0, cy0 + 2, cw0, ch0 - 2, ox=2, oy=2, col=NIGHT)
        draw_crate(furn, cx0, cy0, cw0, ch0)
    for bx0, by0, fill in [
        (40, 200, JADE_B), (120, 235, LOESS), (300, 200, JADE),
        (380, 248, CINN_B), (430, 235, JADE_B), (100, 250, TEAL_B),
        (22, 185, JADE), (310, 240, JADE),
    ]:
        draw_hard_shadow(furn, bx0, by0 + 3, 14, 7, ox=2, oy=2, col=NIGHT)
        draw_basket(furn, bx0, by0, 14, 10, fill=fill)
    for px0, py0, fills in [
        (35, 245, [JADE_B, LOESS, CINN_B, PAPER_L]),
        (125, 250, [LOESS, JADE, CINN_B, CREAM]),
        (305, 255, [JADE_B, TEAL_B, LOESS, PAPER]),
        (70, 260, [JADE, LOESS, CINN_B]),
    ]:
        draw_hard_shadow(furn, px0, py0 + 4, 16, 7, ox=2, oy=2, col=NIGHT)
        draw_produce_basket(furn, px0, py0, 16, 11, fills=fills)
    for gx, gy, cloth in [
        (28, 225, PAPER_D), (95, 250, MIST),
        (285, 235, PAPER_D), (370, 250, FRAME), (445, 255, PAPER_D),
        (320, 190, PAPER),
    ]:
        draw_hard_shadow(furn, gx, gy + 3, 12, 7, ox=2, oy=2, col=NIGHT)
        draw_cloth_bag(furn, gx, gy, 12, 10, cloth=cloth)
    for qx, qy, col in [
        (45, 210, FRAME), (80, 245, WOOD), (115, 245, FRAME),
        (335, 240, FRAME), (405, 250, FRAME),
        (460, 225, WOOD), (20, 200, FRAME), (100, 260, WOOD),
    ]:
        draw_hard_shadow(furn, qx, qy + 3, 7, 6, ox=2, oy=1, col=NIGHT)
        draw_small_pot(furn, qx, qy, col=col)
    for sx, sy, n in [
        (88, 170, 3), (330, 168, 3), (420, 168, 2),
        (60, 245, 2), (400, 255, 2),
        (25, 170, 3), (100, 235, 2),
        (350, 255, 2),
    ]:
        draw_scroll_stack(furn, sx, sy, n=n)
    for hx, hy, col in [(45, 160, GOLD), (295, 160, LOESS), (355, 170, GOLD),
                        (110, 160, GOLD), (70, 165, LOESS)]:
        vline(furn, hx, hy, hy + 8, INK_SOFT)
        fill_rect(furn, hx - 2, hy + 8, hx + 3, hy + 14, col)
        px(furn, hx, hy + 10, CREAM)
    layers_base["hub_furniture.png"] = furn

    # ----- LANTERNS + 旗串 (keep, not packed) -----
    lan = Image.new("RGBA", (BW, BH), TRANS)
    draw_pennant_string(lan, 20, 74, 160, n=12, drop=9,
                        colors=[CINN, JADE, GOLD, PAPER_L, TEAL, CINN_B])
    draw_pennant_string(lan, 170, 68, 310, n=14, drop=8,
                        colors=[JADE, CINN, LOESS, TEAL, PAPER, BLOOD])
    draw_pennant_string(lan, 320, 72, 470, n=12, drop=9,
                        colors=[CINN_B, TEAL, GOLD, PAPER_L, VIOLET, JADE])
    lanterns = [
        (55, 82), (95, 76), (140, 72), (185, 70), (230, 68),
        (275, 70), (320, 72), (365, 76), (410, 80), (450, 84),
        (75, 98), (250, 88), (340, 92), (430, 98),
        (30, 100), (470, 100),
        (200, 84), (100, 70), (400, 70),
    ]
    floor_lamps = (148, 250, 328, 360)
    for lx, ly in lanterns:
        draw_lantern(lan, lx, ly, hanging=True, night=False)
    for lx in floor_lamps:
        draw_hard_shadow(lan, lx - 1, 168, 6, 6, ox=2, oy=2, col=NIGHT)
        fill_rect(lan, lx, 150, lx + 4, 172, WOOD)
        draw_lantern(lan, lx - 2, 140, hanging=False, night=False)
    layers_base["hub_lanterns.png"] = lan

    lan_n = Image.new("RGBA", (BW, BH), TRANS)
    draw_pennant_string(lan_n, 20, 74, 160, n=12, drop=9,
                        colors=[CINN, JADE, GOLD, PAPER_L, TEAL, CINN_B])
    draw_pennant_string(lan_n, 170, 68, 310, n=14, drop=8,
                        colors=[JADE, CINN, LOESS, TEAL, PAPER, BLOOD])
    draw_pennant_string(lan_n, 320, 72, 470, n=12, drop=9,
                        colors=[CINN_B, TEAL, GOLD, PAPER_L, VIOLET, JADE])
    for lx, ly in lanterns:
        draw_lantern(lan_n, lx, ly, hanging=True, night=True)
    for lx in floor_lamps:
        draw_hard_shadow(lan_n, lx - 1, 168, 6, 6, ox=2, oy=2, col=NIGHT)
        fill_rect(lan_n, lx, 150, lx + 4, 172, WOOD)
        draw_lantern(lan_n, lx - 2, 140, hanging=False, night=True)
    layers_base["hub_lanterns_night.png"] = lan_n

    # ----- FOREGROUND (lighter throng) -----
    fg = Image.new("RGBA", (BW, BH), TRANS)
    draw_hard_shadow(fg, 8, 258, 48, 10, ox=2, oy=2, col=NIGHT)
    draw_table(fg, 8, 252, 52, 16, fancy=False, dishes="cup")
    draw_hard_shadow(fg, 380, 258, 48, 10, ox=2, oy=2, col=NIGHT)
    draw_table(fg, 380, 252, 50, 16, fancy=True, dishes="full")
    for sx, sy in [(20, 262), (55, 262), (400, 262), (445, 262)]:
        draw_hard_shadow(fg, sx, sy + 3, 12, 6, ox=2, oy=1, col=NIGHT)
        draw_stool(fg, sx, sy)
    fill_rect(fg, 460, 200, 480, 270, PAPER_D)
    outline_rect(fg, 460, 200, 480, 270, INK)
    vline(fg, 470, 200, 270, WOOD)
    for sy in range(210, 265, 6):
        hline(fg, 462, 468, sy, MIST)
        hline(fg, 472, 478, sy, MIST)
    fill_rect(fg, 463, 220, 468, 250, MTN)
    fill_rect(fg, 473, 225, 478, 255, JADE)
    for lx, ly in [(40, 230), (440, 228)]:
        fill_rect(fg, lx, ly, lx + 9, ly + 10, CINN_B)
        fill_rect(fg, lx, ly, lx + 9, ly + 2, GOLD)
        fill_rect(fg, lx, ly + 8, lx + 9, ly + 10, GOLD)
        px(fg, lx + 4, ly + 4, CREAM)
        vline(fg, lx + 2, ly + 10, ly + 18, GOLD)
        vline(fg, lx + 6, ly + 10, ly + 18, GOLD)
        px(fg, lx + 2, ly + 18, LOESS)
        px(fg, lx + 6, ly + 18, LOESS)
    draw_basket(fg, 12, 245, 14, 10, fill=JADE_B)
    draw_crate(fg, 150, 258, 16, 12)
    draw_produce_basket(fg, 330, 255, 16, 11, fills=[LOESS, JADE_B, CINN_B])
    fill_rect(fg, 0, 240, 6, 270, WOOD)
    fill_rect(fg, 0, 255, 10, 268, FRAME)
    layers_base["hub_fg.png"] = fg

    composed = Image.new("RGBA", (BW, BH), NIGHT)
    for key in ["hub_wall.png", "hub_floor.png", "hub_furniture.png", "hub_counter.png",
                "hub_lanterns.png", "hub_fg.png"]:
        composed.alpha_composite(layers_base[key])
    layers_base["hub_composed.png"] = composed

    # Native 960×540 via nearest-neighbor integer scale (hard edge, no AA)
    layers = {}
    for name, im in layers_base.items():
        layers[name] = im.resize((OW, OH), Image.NEAREST)
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


def write_previews(sprites_only=False):
    PREVIEW.mkdir(parents=True, exist_ok=True)
    # full sheet x4 for key characters
    for cid in ["qingyi", "xiaoer", "tiezhang", "langren", "qinshi"]:
        sheet = Image.open(SPRITES / f"{cid}.png")
        big = sheet.resize((sheet.width * 4, sheet.height * 4), Image.NEAREST)
        big.save(PREVIEW / f"{cid}_x4.png")
        labels = {
            0: "idle", 2: "walk", 6: "serve", 7: "serve1", 8: "serve2",
            9: "attack", 10: "attack1", 11: "attack2", 12: "attack3",
            13: "hurt", 14: "hurt1", 15: "parry", 16: "parry1",
        }
        if cid == "xiaoer":
            labels[9] = "wipe0"
            labels[10] = "wipe1"
            labels[11] = "wipe2"
            labels[12] = "wipe3"
        for fi, lab in labels.items():
            frame = sheet.crop((fi * 32, 0, fi * 32 + 32, 32))
            frame.resize((128, 128), Image.NEAREST).save(PREVIEW / f"{cid}_{lab}.png")
    for bid in ["heifeng", "xieyi"]:
        b = Image.open(SPRITES / f"boss_{bid}_combat.png")
        b.resize((128, 128), Image.NEAREST).save(PREVIEW / f"boss_{bid}_combat_x4.png")
    guests = Image.open(SPRITES / "guest_sit.png")
    guests.resize((guests.width * 4, guests.height * 4), Image.NEAREST).save(PREVIEW / "guest_sit_x4.png")
    gwalk = Image.open(SPRITES / "guest_walk.png")
    gwalk.resize((gwalk.width * 4, gwalk.height * 4), Image.NEAREST).save(PREVIEW / "guest_walk_x4.png")
    if not sprites_only:
        hub = Image.open(SCENES / "hub_composed.png")
        hub.resize((hub.width * 2, hub.height * 2), Image.NEAREST).save(PREVIEW / "hub_composed_x2.png")
        hub.resize((hub.width * 2, hub.height * 2), Image.NEAREST).save(PREVIEW / "hub_read.png")


def write_scenes_only():
    """Regenerate Hub layers only — owned by 墨點場景. Does not touch sprites."""
    SCENES.mkdir(parents=True, exist_ok=True)
    PREVIEW.mkdir(parents=True, exist_ok=True)
    report = ["# Ink-Pixel Inn Hub scenes report v2.0 (960×540)", ""]
    layers = make_hub_layers()
    for name, im in layers.items():
        assert im.size == (960, 540), f"{name} size {im.size}"
        opaque, oob, cols = audit(im, name)
        out = SCENES / name
        im.save(out)
        line = f"SCENE {name}: size={im.size} opaque={opaque} oob={oob} oob_cols={cols} bytes={out.stat().st_size}"
        report.append(line)
        print(line)
        if oob:
            raise SystemExit(f"OOB colors in {name}: {cols}")
    hub = layers["hub_composed.png"]
    # readable preview: native 960 + optional ×2 for inspect
    hub.save(PREVIEW / "hub_composed_x2.png")  # already 960; keep filename for pipeline
    hub.resize((hub.width * 2, hub.height * 2), Image.NEAREST).save(PREVIEW / "hub_read.png")
    report.append("PREVIEWS: hub_composed_x2.png (=960 native) hub_read.png (1920×1080) refreshed")
    report.append("")
    report.append("## z-order（由底到頂）")
    report.append("wall → floor → furniture → counter → （角色）→ lanterns → fg")
    report.append("夜間：lanterns 換成 hub_lanterns_night.png")
    report.append("")
    report.append("## 熱點錨點（960×540 = 邏輯×2）")
    report.append("大門 12–108,164–300｜告示 216–304,184–280｜書架 216–296,224–324")
    report.append("櫃檯 306–674,326–440｜地圖 724–816,182–288｜俠客席 676–820,356–424")
    report.append("走廊中軸 390–550,320–500（暢通，無 throng）")
    report.append("")
    report.append("## 重生")
    report.append("python3 tools/gen_ink_pixel_assets.py --scenes-only")
    print("PREVIEWS: hub_composed_x2.png hub_read.png refreshed")
    (SCENES / "_gen_report.txt").write_text("\n".join(report) + "\n", encoding="utf-8")
    print("DONE v2.0 scenes-only")





def main(scenes_only=False):
    if scenes_only:
        write_scenes_only()
        return
    SPRITES.mkdir(parents=True, exist_ok=True)
    SCENES.mkdir(parents=True, exist_ok=True)
    report = ["# Ink-Pixel Inn asset gen report v1.2.1 attack/hurt clarity", ""]
    for cid in ["qingyi", "tiezhang", "langren", "qinshi", "xiaoer"]:
        sheet = make_spritesheet(cid)
        spath = SPRITES / f"{cid}.png"
        sheet.save(spath)
        opaque, oob, cols, empty = verify_spritesheet(sheet, cid)
        line = f"SPRITE {cid}: size={sheet.size} opaque={opaque} oob={oob} empty_frames={empty} oob_cols={cols}"
        report.append(line)
        print(line)
        if oob:
            raise SystemExit(f"OOB colors in {cid}: {cols}")
    for bid in ["heifeng", "xieyi"]:
        im = make_boss_combat(bid)
        spath = SPRITES / f"boss_{bid}_combat.png"
        im.save(spath)
        opaque, oob, cols = audit(im, spath.name)
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
    gwalk = make_guest_walk()
    gwpath = SPRITES / "guest_walk.png"
    gwalk.save(gwpath)
    opaque, oob, cols = audit(gwalk, "guest_walk")
    empty = []
    for i in range(48):  # 6 guests × 8 frames
        col_opaque = 0
        for y in range(32):
            for x in range(i * 32, i * 32 + 32):
                if gwalk.getpixel((x, y))[3] > 0:
                    col_opaque += 1
        if col_opaque < 20:
            empty.append(i)
    line = f"GUEST walk: size={gwalk.size} opaque={opaque} oob={oob} empty_frames={empty} oob_cols={cols}"
    report.append(line)
    print(line)
    if oob:
        raise SystemExit(f"OOB in guest_walk: {cols}")
    if empty:
        raise SystemExit(f"Empty frames in guest_walk: {empty}")
    # Hub/scenes owned by 墨點場景 — default path does NOT overwrite assets/scenes/
    report.append("SCENES: skipped (owned by 墨點場景; use --scenes-only)")
    print("SCENES: skipped (assets/scenes/ untouched; use --scenes-only)")
    write_previews(sprites_only=True)
    report.append("PREVIEWS: sprite previews refreshed under assets/_preview/")
    (SPRITES / "_gen_report.txt").write_text("\n".join(report) + "\n", encoding="utf-8")
    print("DONE sprites-only (scenes untouched)")


if __name__ == "__main__":
    import sys
    main(scenes_only=("--scenes-only" in sys.argv))
