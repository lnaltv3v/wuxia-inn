#!/usr/bin/env python3
"""Generate Ink-Pixel Inn combat VFX sheets (palette-locked, hard-edge).

Outputs under assets/sprites/fx/:
  slash.png       6×32  knife/sword arc
  spark.png       5×32  hit sparks
  parry_flash.png 4×32  parry flash
  hit_ring.png    3×32  optional hit ring
Also writes assets/_preview/fx_*.png (×4) and fx/README.md.
"""
from __future__ import annotations

from pathlib import Path
from PIL import Image

ROOT = Path("/workspace/wuxia-inn")
FX = ROOT / "assets" / "sprites" / "fx"
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
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            px(img, x, y, c)


def plot_points(img, pts, c):
    for x, y in pts:
        px(img, x, y, c)


def bresenham(x0, y0, x1, y1):
    pts = []
    dx = abs(x1 - x0)
    dy = -abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx + dy
    x, y = x0, y0
    while True:
        pts.append((x, y))
        if x == x1 and y == y1:
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x += sx
        if e2 <= dx:
            err += dx
            y += sy
    return pts


def thick_line(img, x0, y0, x1, y1, colors, width=1):
    """Draw hard line; colors[0]=core, optional outer rings."""
    base = bresenham(x0, y0, x1, y1)
    for i, c in enumerate(reversed(colors)):
        w = width + (len(colors) - 1 - i)
        for bx, by in base:
            for oy in range(-w + 1, w):
                for ox in range(-w + 1, w):
                    if abs(ox) + abs(oy) <= w:
                        px(img, bx + ox, by + oy, c)
    # redraw core last so it sits on top
    for bx, by in base:
        px(img, bx, by, colors[0])


def arc_points(cx, cy, r, a0, a1, steps=24):
    """Approx quarter/third arc with integer points (degrees)."""
    import math
    pts = []
    for i in range(steps + 1):
        t = a0 + (a1 - a0) * i / steps
        rad = math.radians(t)
        x = int(round(cx + r * math.cos(rad)))
        y = int(round(cy + r * math.sin(rad)))
        pts.append((x, y))
    # unique consecutive
    out = []
    for p in pts:
        if not out or out[-1] != p:
            out.append(p)
    return out


def draw_arc(img, cx, cy, r, a0, a1, colors, thickness=1, steps=28):
    pts = arc_points(cx, cy, r, a0, a1, steps)
    for i in range(len(pts) - 1):
        x0, y0 = pts[i]
        x1, y1 = pts[i + 1]
        thick_line(img, x0, y0, x1, y1, colors, width=thickness)


# ---------- slash: 6 frames, 32×32 ----------
def slash_frame(i: int) -> Image.Image:
    """0 start arc → 1 stretch → 2 peak bright → 3 hold → 4 fade → 5 shreds.
    Pivot lower-left; sweep NE as readable blade crescent (hard edge).
    """
    img = new_frame()
    # Horizontal-ish crescent: center below mid so arc bows upward across frame
    cx, cy = 8, 22
    if i == 0:
        # short seed from mid-left upward
        draw_arc(img, cx, cy, 9, -70, -20, [GOLD, TEAL], thickness=1, steps=14)
        plot_points(img, [(14, 12), (15, 11)], CREAM)
        px(img, 10, 16, TEAL_B)
    elif i == 1:
        draw_arc(img, cx, cy, 13, -80, 5, [TEAL_B, GOLD], thickness=1, steps=22)
        draw_arc(img, cx, cy, 12, -75, 0, [CREAM], thickness=0, steps=18)
        plot_points(img, [(20, 8), (21, 7), (22, 8)], CREAM)
        px(img, 21, 8, GOLD)
    elif i == 2:
        # peak: long bright crescent + slight ink under for contrast
        draw_arc(img, cx, cy, 16, -85, 15, [INK_SOFT], thickness=1, steps=28)
        draw_arc(img, cx, cy, 16, -85, 15, [CREAM, GOLD, TEAL_B], thickness=1, steps=28)
        draw_arc(img, cx, cy, 15, -80, 10, [CREAM], thickness=0, steps=24)
        # tip flare
        plot_points(img, [(26, 10), (27, 9), (28, 10), (27, 11)], CREAM)
        px(img, 27, 10, GOLD)
        plot_points(img, [(28, 9), (29, 10)], CINN_B)
        # trailing shreds near hilt
        for p in [(5, 18), (6, 16), (7, 15), (4, 20)]:
            px(img, p[0], p[1], JADE_B)
    elif i == 3:
        draw_arc(img, cx, cy, 17, -90, 20, [GOLD, TEAL_B], thickness=1, steps=30)
        draw_arc(img, cx, cy, 16, -85, 15, [CREAM], thickness=0, steps=26)
        draw_arc(img, cx + 1, cy - 2, 13, -70, 5, [JADE_B], thickness=0, steps=16)
        plot_points(img, [(28, 12), (29, 13)], GOLD)
        px(img, 30, 12, CINN)
    elif i == 4:
        segs = [
            ((5, 18), (10, 12), GOLD),
            ((12, 10), (17, 7), TEAL_B),
            ((19, 6), (24, 8), CREAM),
            ((25, 10), (28, 14), GOLD),
            ((8, 16), (13, 11), JADE_B),
        ]
        for (a, b, c) in segs:
            thick_line(img, a[0], a[1], b[0], b[1], [c], width=1)
        plot_points(img, [(11, 14), (16, 8), (22, 7), (27, 13)], PAPER_L)
    else:
        motes = [
            (6, 17, GOLD), (9, 13, TEAL_B), (13, 9, CREAM),
            (17, 7, GOLD), (21, 8, JADE_B), (24, 12, TEAL),
            (27, 15, GOLD), (8, 19, CINN), (15, 11, PAPER_L),
            (22, 14, GOLD), (11, 16, TEAL_B), (25, 10, CINN_B),
        ]
        for x, y, c in motes:
            px(img, x, y, c)
    return img




# ---------- spark: 5 frames ----------
def spark_frame(i: int) -> Image.Image:
    img = new_frame()
    cx, cy = 15, 15
    if i == 0:
        # impact core
        fill_rect(img, cx - 1, cy - 1, cx + 1, cy + 1, CREAM)
        px(img, cx, cy, CREAM)
        for dx, dy in [(-2, 0), (2, 0), (0, -2), (0, 2)]:
            px(img, cx + dx, cy + dy, GOLD)
        px(img, cx - 1, cy - 2, CINN_B)
        px(img, cx + 2, cy - 1, CINN_B)
    elif i == 1:
        fill_rect(img, cx - 1, cy - 1, cx + 1, cy + 1, GOLD)
        px(img, cx, cy, CREAM)
        rays = [
            (-3, -2, CREAM), (-4, -3, GOLD),
            (3, -2, CREAM), (4, -4, GOLD),
            (-3, 2, TEAL_B), (-4, 3, JADE_B),
            (3, 3, CINN_B), (4, 4, CINN),
            (0, -4, CREAM), (0, 4, GOLD),
            (-5, 0, GOLD), (5, 1, TEAL_B),
        ]
        for dx, dy, c in rays:
            px(img, cx + dx, cy + dy, c)
    elif i == 2:
        # scatter pixels
        dots = [
            (8, 10, CREAM), (7, 8, GOLD), (6, 11, CINN_B),
            (22, 9, CREAM), (24, 7, GOLD), (25, 11, TEAL_B),
            (9, 20, GOLD), (7, 22, CINN), (11, 23, JADE_B),
            (23, 21, CREAM), (25, 23, GOLD), (21, 24, CINN_B),
            (15, 6, CREAM), (16, 5, GOLD),
            (14, 25, TEAL_B), (17, 26, GOLD),
            (4, 15, GOLD), (28, 16, CREAM),
            (15, 15, PAPER_L), (16, 16, GOLD),
        ]
        for x, y, c in dots:
            px(img, x, y, c)
    elif i == 3:
        dots = [
            (5, 7, GOLD), (4, 9, CINN),
            (26, 6, GOLD), (27, 8, TEAL),
            (5, 24, CINN_B), (7, 26, GOLD),
            (26, 24, GOLD), (28, 26, CINN),
            (15, 3, CREAM), (16, 28, GOLD),
            (2, 15, TEAL_B), (29, 14, GOLD),
            (12, 12, PAPER_D), (19, 18, LOESS),
        ]
        for x, y, c in dots:
            px(img, x, y, c)
    else:
        # sparse fade (fully opaque palette pixels, then gone next)
        for x, y, c in [
            (3, 6, GOLD), (28, 5, CINN), (4, 27, TEAL),
            (27, 27, GOLD), (15, 2, LOESS), (16, 29, FRAME),
        ]:
            px(img, x, y, c)
    return img


# ---------- parry_flash: 4 frames ----------
def parry_frame(i: int) -> Image.Image:
    img = new_frame()
    cx, cy = 15, 15
    if i == 0:
        # hard cross + short radiate
        thick_line(img, cx - 8, cy, cx + 8, cy, [CREAM, GOLD], width=1)
        thick_line(img, cx, cy - 8, cx, cy + 8, [CREAM, GOLD], width=1)
        # diagonal short arms
        thick_line(img, cx - 5, cy - 5, cx + 5, cy + 5, [GOLD], width=1)
        thick_line(img, cx - 5, cy + 5, cx + 5, cy - 5, [GOLD], width=1)
        # cinnabar rim tips
        for dx, dy in [(-9, 0), (9, 0), (0, -9), (0, 9)]:
            px(img, cx + dx, cy + dy, CINN_B)
        fill_rect(img, cx - 1, cy - 1, cx + 1, cy + 1, CREAM)
    elif i == 1:
        thick_line(img, cx - 6, cy, cx + 6, cy, [CREAM, GOLD], width=1)
        thick_line(img, cx, cy - 6, cx, cy + 6, [CREAM, GOLD], width=1)
        thick_line(img, cx - 4, cy - 4, cx + 4, cy + 4, [PAPER_L], width=1)
        thick_line(img, cx - 4, cy + 4, cx + 4, cy - 4, [PAPER_L], width=1)
        for dx, dy in [(-7, 0), (7, 0), (0, -7), (0, 7)]:
            px(img, cx + dx, cy + dy, CINN)
        px(img, cx, cy, CREAM)
    elif i == 2:
        # shrink
        thick_line(img, cx - 3, cy, cx + 3, cy, [GOLD, CREAM], width=1)
        thick_line(img, cx, cy - 3, cx, cy + 3, [GOLD, CREAM], width=1)
        plot_points(img, [
            (cx - 2, cy - 2), (cx + 2, cy + 2),
            (cx - 2, cy + 2), (cx + 2, cy - 2),
        ], PAPER_L)
        px(img, cx, cy, CREAM)
        for dx, dy in [(-4, 0), (4, 0), (0, -4), (0, 4)]:
            px(img, cx + dx, cy + dy, CINN_B)
    else:
        # extinguish — tiny cross
        px(img, cx, cy, CREAM)
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            px(img, cx + dx, cy + dy, GOLD)
        for dx, dy in [(-2, 0), (2, 0), (0, -2), (0, 2)]:
            px(img, cx + dx, cy + dy, CINN)
    return img


# ---------- hit_ring: 3 frames (optional) ----------
def hit_ring_frame(i: int) -> Image.Image:
    img = new_frame()
    cx, cy = 15, 15
    if i == 0:
        r = 5
        cols = [CREAM, GOLD]
    elif i == 1:
        r = 9
        cols = [GOLD, CINN_B]
    else:
        r = 13
        cols = [CINN, INK_SOFT]
    # diamond-ish hard ring via 4 arcs / octagon points
    import math
    pts = []
    for deg in range(0, 360, 10):
        rad = math.radians(deg)
        x = int(round(cx + r * math.cos(rad)))
        y = int(round(cy + r * math.sin(rad)))
        pts.append((x, y))
    for p in pts:
        px(img, p[0], p[1], cols[0])
    # inner ring offset for thickness on early frames
    if i < 2:
        for deg in range(0, 360, 12):
            rad = math.radians(deg)
            x = int(round(cx + (r - 1) * math.cos(rad)))
            y = int(round(cy + (r - 1) * math.sin(rad)))
            px(img, x, y, cols[1] if len(cols) > 1 else cols[0])
    if i == 0:
        fill_rect(img, cx - 1, cy - 1, cx + 1, cy + 1, CREAM)
    return img


def sheet_from_frames(frames):
    w = 32 * len(frames)
    sheet = Image.new("RGBA", (w, 32), TRANS)
    for i, fr in enumerate(frames):
        sheet.paste(fr, (i * 32, 0))
    return sheet


def audit(img: Image.Image, name: str) -> int:
    oob = 0
    for y in range(img.height):
        for x in range(img.width):
            r, g, b, a = img.getpixel((x, y))
            if a == 0:
                continue
            if a != 255:
                oob += 1  # no semi-transparent
                continue
            if (r, g, b) not in PALETTE_SET:
                oob += 1
    return oob


def preview_strip(sheet: Image.Image, scale=4) -> Image.Image:
    return sheet.resize((sheet.width * scale, sheet.height * scale), Image.NEAREST)


def write_readme():
    text = """# 戰鬥 VFX 精靈（墨點江湖）

自製硬邊點陣，僅盤內色、透明底、每幀 **32×32**。禁止柔邊光暈／半透明灰。

## 檔案

| 檔案 | 尺寸 | 幀數 | 建議 fps | 綁定 |
|------|------|------|----------|------|
| `slash.png` | 192×32 | 6 | 12–14 | 跟英雄 `attack` **擊中幀**（通常 attack 第 2–3 幀）疊加於武器前方 |
| `spark.png` | 160×32 | 5 | 14–16 | 跟 `hurt`／受擊瞬間，中心對齊命中點 |
| `parry_flash.png` | 128×32 | 4 | 12–14 | 跟 `parry` 成功幀，中心對齊武器／身體中線 |
| `hit_ring.png` | 96×32 | 3 | 10–12 | 可選；受擊圈，跟 hurt 同幀或延後 1 tick |

## 對幀（0-index）

### slash.png — 刀光／劍弧
| 幀 | 內容 |
|----|------|
| 0 | 起弧（短金／青綠） |
| 1 | 拉長 |
| 2 | **最亮**（cream 芯 + 金箔／劍鋒 + 硃紅尖） |
| 3 | 滿弧維持 |
| 4 | 斷弧消散 |
| 5 | 碎點收束 |

播放建議：單次 one-shot，唔 loop；可喺幀 2 觸發 SFX 刀斬。

### spark.png — 打擊火花
| 幀 | 內容 |
|----|------|
| 0 | 撞擊亮核 |
| 1 | 十字／放射硬點 |
| 2 | 四散像素 |
| 3 | 外散淡出 |
| 4 | 殘點 |

### parry_flash.png — 招架閃
| 幀 | 內容 |
|----|------|
| 0 | 大十字 + 短放射（cream／金箔，硃紅尖） |
| 1 | 縮一檔 |
| 2 | 再縮 |
| 3 | 滅 |

### hit_ring.png — 受擊圈（可選）
| 幀 | 內容 |
|----|------|
| 0 | 小亮圈 |
| 1 | 擴張金／硃 |
| 2 | 大圈淡墨邊 |

## 色盤
僅用 ART.md 墨點江湖盤（含角色擴充 teal／robe／violet）。生成腳本：`tools/gen_combat_fx.py`。

## 預覽
`assets/_preview/fx_slash.png`、`fx_spark.png`、`fx_parry_flash.png`、`fx_hit_ring.png`（×4 nearest）。
"""
    (FX / "README.md").write_text(text, encoding="utf-8")


def main():
    FX.mkdir(parents=True, exist_ok=True)
    PREVIEW.mkdir(parents=True, exist_ok=True)

    specs = [
        ("slash.png", [slash_frame(i) for i in range(6)]),
        ("spark.png", [spark_frame(i) for i in range(5)]),
        ("parry_flash.png", [parry_frame(i) for i in range(4)]),
        ("hit_ring.png", [hit_ring_frame(i) for i in range(3)]),
    ]

    report = []
    total_oob = 0
    for name, frames in specs:
        sheet = sheet_from_frames(frames)
        oob = audit(sheet, name)
        total_oob += oob
        out = FX / name
        sheet.save(out)
        prev = preview_strip(sheet, 4)
        prev_name = "fx_" + name
        prev.save(PREVIEW / prev_name)
        report.append(f"{name}: {sheet.size[0]}x{sheet.size[1]} frames={len(frames)} oob={oob} -> {out}")

    write_readme()
    report_path = FX / "_gen_report.txt"
    report_path.write_text(
        "\n".join(report) + f"\nTOTAL_OOB={total_oob}\n", encoding="utf-8"
    )
    print("\n".join(report))
    print(f"TOTAL_OOB={total_oob}")
    return total_oob


if __name__ == "__main__":
    raise SystemExit(main())
