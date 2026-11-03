# 精靈表 64×64（原生）— 墨點江湖

> 原生像素 · 僅盤內色 · 透明底 · 硬邊無抗鋸齒  
> **唔係** 32 版 nearest 放大。

## v0.9 精修狀態

| 檔 | 尺寸 | 狀態 | 生成腳本 |
|----|------|------|----------|
| `qingyi.png` | **1152×64** | **v0.9 r2 精修**（姿勢差加大／判定幀；遊戲 `?v=0.9.1` cache bust） | `tools/gen_sprites_64_v09.py` |
| `langren.png` | **1152×64** | **v0.9 r2 精修**（姿勢差加大／判定幀；遊戲 `?v=0.9.1` cache bust） | `tools/gen_sprites_64_v09.py` |
| `tiezhang.png` | **1152×64** | **v1.1→v1.2 正式精修（震掌／藥囊）** | `tools/gen_sprites_64_v11.py` |
| `qinshi.png` | **1152×64** | **v1.1→v1.2 正式精修（拂塵／梵紫）** | `tools/gen_sprites_64_v11.py` |
| `xiaoer.png` | **1152×64** | **v1.3 精修（serve／wipe）** | `tools/gen_sprites_64_v13.py` |
| `guest_sit.png` | **384×64** | **v1.3 精修（6 色坐姿）** | `tools/gen_sprites_64_v13.py` |
| `guest_walk.png` | **3072×64** | **v1.3 新增（6×8 walk／入座）** | `tools/gen_sprites_64_v13.py` |
| `boss_*_combat.png` | **256×64** | **v1.4 精修（4 幀 idle／windup／strike／hurt）** | `tools/gen_sprites_64_v14.py` |
| `enemy_charge.png` | **256×64** | **v1.4 新增（衝鋒 4 幀）** | `tools/gen_sprites_64_v14.py` |
| `enemy_kite.png` | **256×64** | **v1.4 新增（拉距 4 幀）** | `tools/gen_sprites_64_v14.py` |
| `enemy_melee.png` | **256×64** | **v1.4 新增（近戰 4 幀）** | `tools/gen_sprites_64_v14.py` |

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
| tiezhang | `#A04040` robe-red | `#3D8F66` jade-bright（藥囊／震掌） |
| qinshi | `#5A4060` violet | `#F4E6C4` paper-light（素袍／拂塵） |
| xiaoer | `#5C4030` wood | 宣紙圍裙＋硃紅腰帶（茶盤／抹布） |

## 重跑 v0.9（只覆寫 qingyi／langren）

```bash
python3 /workspace/wuxia-inn/tools/gen_sprites_64_v09.py
```

合規報告：`_gen_report_v09.txt`。預覽：`assets/_preview/64_{qingyi,langren}_*_x2.png`。

## v1.1 鐵掌／琴師

- `tiezhang`：醫袍紅＋藥綠囊；攻擊＝蓄掌／震掌（無劍）
- `qinshi`：梵紫＋素袍；道具＝拂塵；攻擊＝橫掃
- 姿勢誇張對齊 v0.9 r2；生成：`tools/gen_sprites_64_v11.py`
- 報告：`_gen_report_v11.txt`

## 重跑 v1.1（只覆寫 tiezhang／qinshi）

```bash
python3 /workspace/wuxia-inn/tools/gen_sprites_64_v11.py
```

合規報告：`_gen_report_v11.txt`。預覽：`assets/_preview/64_{tiezhang,qinshi}_*_x2.png`、`64_*_compare_v11.png`。

## v1.2.0 正式交付

墨點美術正式交 `tiezhang`／`qinshi` 精修（覆寫 PNG），連同 `tools/gen_sprites_64_v11.py`、`_gen_report_v11.txt`、compare／preview 一併入庫。**唔覆寫** `qingyi`／`langren`。

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

