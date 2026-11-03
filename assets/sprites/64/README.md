# 精靈表 64×64（原生）— 墨點江湖

> 原生像素 · 僅盤內色 · 透明底 · 硬邊無抗鋸齒  
> **唔係** 32 版 nearest 放大。

## v0.9 精修狀態

| 檔 | 尺寸 | 狀態 | 生成腳本 |
|----|------|------|----------|
| `qingyi.png` | **1152×64** | **v0.9 r2 精修**（姿勢差加大／判定幀；遊戲 `?v=0.9.1` cache bust） | `tools/gen_sprites_64_v09.py` |
| `langren.png` | **1152×64** | **v0.9 r2 精修**（姿勢差加大／判定幀；遊戲 `?v=0.9.1` cache bust） | `tools/gen_sprites_64_v09.py` |
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
