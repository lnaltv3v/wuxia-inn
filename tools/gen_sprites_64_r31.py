#!/usr/bin/env python3
"""v r3.1 — detail overlays on integrated r3 official sheets (DRAFT *_r31.png).

Reads assets/sprites/64/{qingyi,langren,tiezhang,qinshi}.png (current = r3)
and layers: sword/blade tassels, light armor plates / thicker bracers,
longer forked whisk tips. Does NOT overwrite official PNGs.

Frame map: 0–1 idle | 2–5 walk | 6–8 windup | 9–12 strike | 13–14 hurt | 15–17 parry
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


def poses_r3():
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


# ============================================================
# tassel: hard-edge bead chain (GOLD / CINN / PAPER / CREAM)
# ============================================================
def tassel_down(img, gx, gy, length=9, beads=None):
    """Hang from guard (gx,gy) downward-right — 1px beads + tip fork."""
    if beads is None:
        beads = (GOLD, CINN_B, PAPER_L, CREAM, GOLD, CINN, PAPER_D, CREAM, GOLD)
    for i in range(length):
        x = gx + (i // 3)
        y = gy + 1 + i
        c = beads[i % len(beads)]
        px(img, x, y, c)
        if i % 2 == 0:
            px(img, x + 1, y, INK if i % 4 == 0 else FRAME)
        if i % 3 == 0:
            px(img, x - 1, y, beads[(i + 2) % len(beads)])
    # tip fork 1–2px
    tipx, tipy = gx + (length // 3), gy + length
    px(img, tipx, tipy + 1, CINN_B)
    px(img, tipx - 1, tipy + 2, PAPER_L)
    px(img, tipx + 1, tipy + 2, GOLD)
    px(img, tipx, tipy + 3, CREAM)


def tassel_side(img, gx, gy, length=8, right=True):
    """Horizontal-ish tassel from guard during slash (trailing)."""
    beads = (GOLD, CINN_B, PAPER_L, CREAM, GOLD, CINN, PAPER_D)
    sign = 1 if right else -1
    for i in range(length):
        x = gx - sign * (1 + i)
        y = gy + 2 + (i // 2)
        px(img, x, y, beads[i % len(beads)])
        if i % 2 == 0:
            px(img, x, y + 1, FRAME)
        if i % 3 == 0:
            px(img, x, y - 1, CREAM)
    tipx = gx - sign * (1 + length)
    tipy = gy + 2 + (length // 2)
    px(img, tipx - sign, tipy, CINN_B)
    px(img, tipx - sign, tipy + 1, PAPER_L)
    px(img, tipx - 2 * sign, tipy, GOLD)


def tassel_up(img, gx, gy, length=7):
    """Tassel hanging when blade tip-up (parry high / windup)."""
    beads = (GOLD, CINN, PAPER_L, CREAM, GOLD, CINN_B, PAPER_D)
    for i in range(length):
        x = gx + 3 + (i // 3)
        y = gy + 2 + i
        px(img, x, y, beads[i % len(beads)])
        if i % 2 == 0:
            px(img, x + 1, y, FRAME)
    px(img, gx + 5, gy + length + 2, CINN_B)
    px(img, gx + 4, gy + length + 3, PAPER_L)
    px(img, gx + 6, gy + length + 3, GOLD)


# ============================================================
# light armor plates / thicker bracers
# ============================================================
def shoulder_plate(img, x, y, main=FRAME, rim=GOLD, wide=6):
    rect(img, x, y, x + wide, y + 4, main)
    hline(img, x, x + wide, y, rim)
    hline(img, x, x + wide, y + 3, INK)
    px(img, x + 1, y + 1, CREAM)
    px(img, x + wide - 2, y + 1, LOESS)
    px(img, x + 2, y + 2, INK)


def chest_plate(img, x, y, main=FRAME, rim=GOLD):
    rect(img, x, y, x + 7, y + 5, main)
    outline_rect(img, x, y, x + 7, y + 5, INK)
    hline(img, x + 1, x + 6, y + 1, rim)
    px(img, x + 3, y + 2, CREAM)
    px(img, x + 4, y + 3, LOESS)
    px(img, x + 2, y + 3, INK)


def thick_bracer(img, x0, x1, y0, y1, main=WOOD, rim=GOLD):
    """Thicker forearm guard than r3 bracer."""
    rect(img, x0, y0, x1, y1, main)
    hline(img, x0, x1, y0, rim)
    hline(img, x0, x1, y0 + 1, CREAM if main != BLOOD else CINN_B)
    hline(img, x0, x1, y1 - 1, INK)
    hline(img, x0 + 1, x1 - 1, y0 + 2, FRAME)
    vline(img, (x0 + x1) // 2, y0 + 1, y1 - 1, INK)
    px(img, (x0 + x1) // 2 + 1, y0 + 1, CREAM)
    # rivet
    px(img, x0 + 1, y0 + 2, rim)
    px(img, x1 - 2, y0 + 2, rim)


# ============================================================
# qinshi whisk tip extend + fork
# ============================================================
def _whisk_colors():
    return {PAPER_L[:3], PAPER[:3], PAPER_D[:3], CREAM[:3]}


def _find_whisk_extrema(img, tip_up=True):
    """Find extremal PAPER-family pixels (whisk hair) to grow from."""
    cols = _whisk_colors()
    pts = []
    for y in range(FS):
        for x in range(FS):
            p = img.getpixel((x, y))
            if p[3] and p[:3] in cols:
                pts.append((x, y))
    if not pts:
        return None
    if tip_up:
        min_y = min(y for _, y in pts)
        tip_pts = [(x, y) for x, y in pts if y <= min_y + 2]
    else:
        max_y = max(y for _, y in pts)
        tip_pts = [(x, y) for x, y in pts if y >= max_y - 2]
    return tip_pts


def extend_whisk_tips_vert(img, hx, hy, tip_up=True):
    """Add 4–6px longer forked tips beyond existing hair mass (scan-based)."""
    tips = _find_whisk_extrema(img, tip_up=tip_up)
    if not tips:
        # fallback geometric
        if tip_up:
            tips = [(hx + ox, hy - 24) for ox in (-4, -2, 0, 2, 4)]
        else:
            tips = [(hx + ox, min(FS - 5, hy + 30)) for ox in (-4, -2, 0, 2, 4)]
    for i, (tx, ty) in enumerate(tips):
        if tip_up:
            for d in range(1, 6):
                y = ty - d
                px(img, tx, y, PAPER_L if d % 2 == 0 else PAPER)
                if d >= 3:
                    px(img, tx - 1, y, PAPER_D)  # fork L
                    px(img, tx + 1, y, PAPER_L)  # fork R
                if d == 5:
                    px(img, tx, y - 1, CREAM)
                    if i % 3 == 0:
                        px(img, tx, y - 1, VIOLET)
        else:
            for d in range(1, 6):
                y = ty + d
                px(img, tx, y, PAPER_L if d % 2 == 0 else PAPER)
                if d >= 3:
                    px(img, tx - 1, y, PAPER)
                    px(img, tx + 1, y, PAPER_L)
                if d == 5:
                    px(img, tx, y + 1, CREAM)
                    if i % 3 == 0:
                        px(img, tx, y, VIOLET)


def extend_whisk_tips_slash(img, hx, hy, length=22, dy=0):
    cols = _whisk_colors()
    # find rightmost paper pixels as tip front
    max_x = -1
    tip_ys = []
    for y in range(FS):
        for x in range(FS):
            p = img.getpixel((x, y))
            if p[3] and p[:3] in cols and x >= max_x:
                if x > max_x:
                    max_x = x
                    tip_ys = [y]
                else:
                    tip_ys.append(y)
    if max_x < 0:
        max_x = min(FS - 4, hx + 5 + length)
        tip_ys = [hy + dy, hy + dy + 2, hy + dy + 4]
    for i, ty in enumerate(sorted(set(tip_ys))[:8]):
        for d in range(1, 7):
            x = max_x + d
            px(img, x, ty, PAPER_L if d % 2 == 0 else PAPER)
            if d >= 3:
                px(img, x, ty - 1, PAPER_L)  # fork up
                px(img, x, ty + 1, PAPER)    # fork down
            if d == 6:
                px(img, x + 1, ty, CREAM)
                if i % 2 == 0:
                    px(img, x + 1, ty - 1, VIOLET)


def extend_whisk_tips_back(img, hx, hy, lean=0):
    for i in range(6):
        x = hx - 14 - lean * 2 - (i // 2)
        y = hy - 28 - i
        px(img, x, y, PAPER_L)
        px(img, x + 2, y - 1, CREAM)
        if i % 2 == 0:
            px(img, x - 1, y - 1, PAPER)  # fork
            px(img, x + 1, y - 2, PAPER_L)
        if i % 3 == 0:
            px(img, x, y - 2, VIOLET)


# ============================================================
# per-character weapon anchors (match r3 draw call sites)
# ============================================================
def qy_weapon_anchor(pose):
    breath = pose.get("breath", 0)
    bx = pose.get("bx", 0)
    by = pose.get("by", 0)
    cx = 22 + bx
    ty = 24 + by + breath
    k = pose.get("kind", "idle")
    phase = pose.get("phase", 0)
    shake = pose.get("shake", 0)
    if k in ("idle", "walk"):
        return ("vert_down", cx + 16, ty + 10 if k == "idle" else ty + 12)
    if k == "windup":
        return ("back", cx - 14, ty - 2)
    if k == "strike":
        if phase == 0:
            return ("diag", cx + 14, ty - 2)
        if phase == 1:
            return ("slash", cx + 22, ty + 3)
        if phase == 2:
            return ("slash", cx + 24, ty + 5)
        return ("vert_down", cx + 15, ty + 10)
    if k == "hurt":
        if phase == 0:
            return ("vert_down", cx + 8, ty + 14)
        return ("vert_down", cx - 2, ty + 16)
    if k == "parry":
        if phase == 2:
            return ("slash", cx + 6, ty + 0)
        return ("vert_up", cx + 6 + shake, ty - 8)
    return ("vert_down", cx + 16, ty + 10)


def lr_weapon_anchor(pose):
    breath = pose.get("breath", 0)
    bx = pose.get("bx", 0)
    by = pose.get("by", 0)
    cx = 22 + bx
    ty = 24 + by + breath
    k = pose.get("kind", "idle")
    phase = pose.get("phase", 0)
    shake = pose.get("shake", 0)
    if k in ("idle", "walk"):
        return ("vert_down", cx + 17, ty + 10 if k == "idle" else ty + 12)
    if k == "windup":
        return ("back", cx - 15, ty - 2)
    if k == "strike":
        if phase == 0:
            return ("diag", cx + 14, ty - 2)
        if phase == 1:
            return ("slash", cx + 22, ty + 3)
        if phase == 2:
            return ("slash", cx + 24, ty + 5)
        return ("vert_down", cx + 15, ty + 10)
    if k == "hurt":
        if phase == 0:
            return ("vert_down", cx + 6, ty + 14)
        return ("vert_down", cx - 4, ty + 16)
    if k == "parry":
        if phase == 2:
            return ("slash", cx + 6, ty + 0)
        return ("vert_up", cx + 7 + shake, ty - 8)
    return ("vert_down", cx + 17, ty + 10)


def qs_weapon_anchor(pose):
    breath = pose.get("breath", 0)
    bx = pose.get("bx", 0)
    by = pose.get("by", 0)
    cx = 22 + bx
    ty = 24 + by + breath
    k = pose.get("kind", "idle")
    phase = pose.get("phase", 0)
    shake = pose.get("shake", 0)
    if k in ("idle", "walk"):
        return ("vert_down", cx + 16, ty + 8 if k == "idle" else ty + 10)
    if k == "windup":
        return ("back", cx - 14, ty - 2, phase + 1)
    if k == "strike":
        # from r3 qinshi: phase0 slash16, phase1 longer, etc — approximate
        if phase == 0:
            return ("slash", cx + 14, ty - 2, 16)
        if phase == 1:
            return ("slash", cx + 20, ty + 2, 24)
        if phase == 2:
            return ("slash", cx + 22, ty + 4, 22)
        return ("vert_down", cx + 14, ty + 10)
    if k == "hurt":
        return ("vert_down", cx + 8, ty + 14)
    if k == "parry":
        if phase == 2:
            return ("slash", cx + 6, ty + 0, 14)
        return ("vert_up", cx + 6 + shake, ty - 6)
    return ("vert_down", cx + 16, ty + 8)


def body_xy(pose):
    breath = pose.get("breath", 0)
    bx = pose.get("bx", 0)
    by = pose.get("by", 0)
    return 22 + bx, 24 + by + breath


# ============================================================
# overlays
# ============================================================
def overlay_qingyi(frame, pose):
    mode, hx, hy = qy_weapon_anchor(pose)[:3]
    # tassel from guard
    if mode == "vert_down":
        # guard at hy-3..hy+1 → hang from right of guard
        tassel_down(frame, hx + 6, hy - 1, length=11)
        # second short cord from pommel
        tassel_down(frame, hx - 2, hy - 10, length=6,
                    beads=(GOLD, PAPER_L, CINN_B, CREAM, GOLD, PAPER_D))
    elif mode == "vert_up":
        tassel_up(frame, hx, hy, length=8)
    elif mode == "slash":
        tassel_side(frame, hx, hy, length=9, right=False)  # trail behind slash
    elif mode == "diag":
        tassel_down(frame, hx + 5, hy + 2, length=8)
    elif mode == "back":
        tassel_up(frame, hx, hy + 2, length=7)
    # tiny pommel ring accent
    if mode in ("vert_down", "vert_up"):
        px(frame, hx + 1, hy - 12 if mode == "vert_down" else hy + 2, GOLD)
        px(frame, hx + 2, hy - 13 if mode == "vert_down" else hy + 3, CINN_B)


def overlay_langren(frame, pose):
    mode, hx, hy = lr_weapon_anchor(pose)[:3]
    if mode == "vert_down":
        tassel_down(frame, hx + 7, hy - 1, length=9,
                    beads=(GOLD, CINN, CINN_B, PAPER_L, CREAM, GOLD, CINN_B))
    elif mode == "vert_up":
        tassel_up(frame, hx, hy, length=7)
    elif mode == "slash":
        tassel_side(frame, hx, hy, length=8, right=False)
    elif mode == "diag":
        tassel_down(frame, hx + 6, hy + 2, length=7)
    elif mode == "back":
        tassel_up(frame, hx, hy + 2, length=6)
    # light armor plates shoulder/chest
    cx, ty = body_xy(pose)
    k = pose.get("kind", "idle")
    shoulder_plate(frame, cx - 14, ty + 1, FRAME, GOLD, wide=7)
    shoulder_plate(frame, cx + 7, ty + 1, FRAME, CINN_B, wide=7)
    if k in ("idle", "walk", "parry", "windup", "hurt"):
        chest_plate(frame, cx - 3, ty + 8, FRAME, GOLD)
    # thicker bracers + strap tags
    if k in ("idle", "walk", "windup", "parry", "hurt"):
        thick_bracer(frame, cx - 18, cx - 9, ty + 9, ty + 18, WOOD, GOLD)
        thick_bracer(frame, cx + 11, cx + 20, ty + 9, ty + 18, WOOD, CINN_B)
        rect(frame, cx - 19, ty + 17, cx - 16, ty + 22, FRAME)
        px(frame, cx - 18, ty + 21, GOLD)
        rect(frame, cx + 17, ty + 17, cx + 20, ty + 22, FRAME)
        px(frame, cx + 18, ty + 21, CINN_B)


def overlay_tiezhang(frame, pose):
    cx, ty = body_xy(pose)
    k = pose.get("kind", "idle")
    # medical robe: smaller shoulder plates sticking slightly out
    shoulder_plate(frame, cx - 13, ty + 1, WOOD, GOLD, wide=5)
    shoulder_plate(frame, cx + 8, ty + 1, WOOD, JADE_B, wide=5)
    # thicker medical bracers — extend 1–2px beyond typical sleeve edge
    if k in ("idle", "walk", "windup", "parry", "hurt", "strike"):
        thick_bracer(frame, cx - 18, cx - 9, ty + 9, ty + 18, BLOOD, GOLD)
        thick_bracer(frame, cx + 11, cx + 20, ty + 9, ty + 18, WOOD, JADE_B)
        # hanging strap tags off bracer (new opaque pixels)
        rect(frame, cx - 19, ty + 17, cx - 16, ty + 23, WOOD)
        px(frame, cx - 18, ty + 22, GOLD)
        rect(frame, cx + 17, ty + 17, cx + 20, ty + 23, WOOD_L)
        px(frame, cx + 18, ty + 22, JADE_B)
    # small chest clasp plate
    if k in ("idle", "walk", "parry", "windup"):
        rect(frame, cx - 2, ty + 7, cx + 4, ty + 11, WOOD)
        outline_rect(frame, cx - 2, ty + 7, cx + 4, ty + 11, INK)
        px(frame, cx, ty + 8, GOLD)
        px(frame, cx + 1, ty + 9, JADE_B)


def overlay_qinshi(frame, pose):
    anc = qs_weapon_anchor(pose)
    mode = anc[0]
    hx, hy = anc[1], anc[2]
    if mode == "vert_down":
        extend_whisk_tips_vert(frame, hx, hy, tip_up=False)
    elif mode == "vert_up":
        extend_whisk_tips_vert(frame, hx, hy, tip_up=True)
    elif mode == "slash":
        length = anc[3] if len(anc) > 3 else 22
        extend_whisk_tips_slash(frame, hx, hy, length=length, dy=0)
    elif mode == "back":
        lean = anc[3] if len(anc) > 3 else 1
        extend_whisk_tips_back(frame, hx, hy, lean=lean)


OVERLAYS = {
    "qingyi": overlay_qingyi,
    "langren": overlay_langren,
    "tiezhang": overlay_tiezhang,
    "qinshi": overlay_qinshi,
}


def crop_frame(sheet, i):
    return sheet.crop((i * FS, 0, (i + 1) * FS, FS)).convert("RGBA")


def apply_sheet(cid: str) -> Image.Image:
    src = Image.open(OUT / f"{cid}.png").convert("RGBA")
    assert src.size == (1152, 64), src.size
    out = src.copy()
    poses = poses_r3()
    overlay = OVERLAYS[cid]
    for i, pose in enumerate(poses):
        fr = crop_frame(out, i)
        overlay(fr, pose)
        out.paste(fr, (i * FS, 0))
    return out


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


def make_compare(sheet, cid):
    def paper_x3(fr):
        big = fr.resize((192, 192), Image.Resampling.NEAREST)
        bg = Image.new("RGBA", (192, 192), PAPER)
        bg.paste(big, (0, 0), big)
        return bg
    strip = Image.new("RGBA", (192 * 4 + 12, 192), PAPER_D)
    for i, idx in enumerate([0, 7, 10, 15]):
        strip.paste(paper_x3(crop_frame(sheet, idx)), (i * (192 + 4), 0))
    strip.save(PREV / f"64_{cid}_r31_compare.png")


def write_readme():
    readme = OUT / "README.md"
    text = readme.read_text(encoding="utf-8") if readme.exists() else ""
    if "## r3.1 草稿" not in text:
        note = """
## r3.1 草稿（劍穗／甲片／拂塵加長 · 未接正式檔）

喺已整合嘅 **r3 正式** `qingyi.png` 等之上疊加細節；**唔覆寫** 正式四俠檔。

| 草稿檔 | 加料 |
|--------|------|
| `qingyi_r31.png` | 劍穗（金／硃／宣紙色珠串＋分叉尖） |
| `langren_r31.png` | 刀穗＋肩／胸輕甲片＋加厚護腕 |
| `tiezhang_r31.png` | 肩小片＋醫袍加厚護腕／胸扣（掌法不變） |
| `qinshi_r31.png` | 拂塵尾加長＋1–2px 硬邊分叉 |

- 生成：`tools/gen_sprites_64_r31.py`（讀正式 sheet 再疊）
- 報告：`_gen_report_r31.txt`；預覽：`assets/_preview/64_*_r31_compare.png`

"""
        text = text.rstrip() + "\n" + note
        readme.write_text(text, encoding="utf-8")


def main():
    import hashlib
    OUT.mkdir(parents=True, exist_ok=True)
    PREV.mkdir(parents=True, exist_ok=True)
    report = ["# r3.1 detail overlay draft report", ""]
    total_oob = 0

    official = {}
    for name in (
        "qingyi", "langren", "tiezhang", "qinshi",
        "xiaoer", "guest_sit", "guest_walk",
        "boss_heifeng_combat", "boss_xieyi_combat", "boss_xueying_combat",
        "enemy_charge", "enemy_kite", "enemy_melee",
    ):
        fp = OUT / f"{name}.png"
        if fp.exists():
            official[name] = hashlib.md5(fp.read_bytes()).hexdigest()

    labels = [
        "idle0", "idle1", "walk0", "walk1", "walk2", "walk3",
        "windup0", "windup1", "windup2",
        "strike0", "strike1", "strike2", "strike3",
        "hurt0", "hurt1", "parry0", "parry1", "parry2",
    ]
    added = {
        "qingyi": "sword tassel (GOLD/CINN/PAPER/CREAM beads + tip fork) at guard/pommel",
        "langren": "blade tassel + shoulder/chest hard plates + thicker bracers",
        "tiezhang": "shoulder plates + thicker medical bracers + chest clasp (palm unchanged)",
        "qinshi": "whisk tip +4–6px + 1–2px hard forks (vert/slash/back)",
    }

    for cid in ("qingyi", "langren", "tiezhang", "qinshi"):
        base = Image.open(OUT / f"{cid}.png")
        sheet = apply_sheet(cid)
        assert sheet.size == (1152, 64)
        oob, samples = count_oob(sheet)
        total_oob += oob
        path = OUT / f"{cid}_r31.png"
        sheet.save(path)
        preview_scale(sheet, PREV / f"64_{cid}_r31_x2.png", 2)
        make_compare(sheet, cid)
        for name, idx in [("idle", 0), ("windup", 7), ("strike", 10), ("parry", 15)]:
            preview_scale(crop_frame(sheet, idx), PREV / f"64_{cid}_r31_{name}_x3.png", 3)
        d0 = visible_pixels(sheet, 0) - visible_pixels(base, 0)
        report.append(f"## {cid}_r31")
        report.append(f"path: {path}")
        report.append(f"added: {added[cid]}")
        report.append(f"oob: {oob}  idle0_visible Δ+{d0} ({visible_pixels(base,0)}→{visible_pixels(sheet,0)})")
        if samples:
            report.append(f"oob_samples: {samples}")
        report.append(f"palette_used ({len(colors_used(sheet))}): {', '.join(colors_used(sheet))}")
        for i, lab in enumerate(labels):
            vp = visible_pixels(sheet, i)
            report.append(f"  {i:02d} {lab}: visible={vp}")
        report.append("")
        print(f"{cid}_r31: oob={oob} idleΔ=+{d0}")

    for name, h in official.items():
        now = hashlib.md5((OUT / f"{name}.png").read_bytes()).hexdigest()
        assert now == h, f"FORBIDDEN overwrite of {name}"
        report.append(f"untouched_ok: {name}")

    report.append(f"TOTAL_OOB={total_oob}")
    report.append("""
## weaknesses
- tassel anchors are pose-estimated; may float 1–2px off actual guard on some frames
- armor plates can cover robe folds / pouch edges on tiezhang
- whisk extension may clip frame bottom on idle tip-down
- still no sword tassel physics (static bead chain)
""")
    (OUT / "_gen_report_r31.txt").write_text("\n".join(report) + "\n", encoding="utf-8")
    write_readme()
    print(f"TOTAL_OOB={total_oob}")
    if total_oob != 0:
        raise SystemExit(f"palette oob={total_oob}")
    print("OK")


if __name__ == "__main__":
    main()
