# 場景圖層

## Hub（v2.1 生活感 · 960×540）
`hub_wall`／`hub_floor`／`hub_furniture`／`hub_counter`／`hub_props`／`hub_lanterns`／`hub_lanterns_night`／`hub_fg`

z-order：wall → floor → furniture → counter → **props** →（角色）→ lanterns → fg  
夜間：lanterns 換成 `hub_lanterns_night.png`（焰心 cream／硃紅亮＋硬色塊光斑；日間燈保持可辨差異）

可選層：
- `hub_props.png` — 酒罈、抹布、牆飾／紙角、掛帚、毛巾、茶托（走廊中軸與熱點核心已清帶）
- 前緣抹布／凳邊毛巾併入 `hub_fg.png`（唔另開 props_fg，結構清爽）

熱點錨點（960×540）：大門 12–108,164–300｜告示 216–304,184–280｜書架 216–296,224–324｜櫃檯 306–674,326–440｜地圖 724–816,182–288｜俠客席 676–820,356–424  
走廊中軸 390–550,320–500 暢通。

預覽：`assets/_preview/hub_composed_x2.png`、`hub_read.png`、`hub_composed_night.png`  
舊版備份：`assets/scenes/_prev_hub_v20/`  
重生：`python3 tools/gen_ink_pixel_assets.py --scenes-only`（一併出 props／加強夜燈；唔動 sprites／battle_*）

## 戰鬥場（v0.8.4 精修 · 墨點場景 · 960×540）
| 檔 | 層 |
|----|----|
| `battle_sky.png` | 青空／硬邊雲塊／金箔日輪（下半 alpha0） |
| `battle_mid.png` | 遠山層次／遠樹／霧帶硬色塊（透明底） |
| `battle_ground.png` | 黄土擂台／木亮沿／碎石裂縫／左右暗區／中央站位墊 |
| `battle_props.png` | 左右木樁＋硃紅旗／燈柱（焰心 cream）／繩旗串／側邊罈石；**中央戰鬥區留空** |

z-order：`battle_sky` → `battle_mid` → `battle_ground` → `battle_props` →（角色）

站位留白（960×540）：中央墊約 `300–660, 336–440`（對齊 `FIELD.yBase≈325`）；props 唔入此帶。

預覽：`assets/_preview/battle_composed.png`、`battle_composed_x2.png`  
舊版備份：`assets/scenes/_prev_battle_v083/`  
重生：`python3 tools/gen_ink_pixel_assets.py --battle-only`

硬邊盤內色；可整層替換。見 `ART.md` 品質驗收清單（腳本色塊 ≠ 完工，本版為精修交付）。
