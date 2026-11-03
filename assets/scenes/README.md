# 客棧 Hub 分層場景 — 墨點江湖（**v2.0 · 960×540**）

邏輯格：**960×540**。硬邊、盤內色、透明分層（`hub_composed.png` 為預覽合成）。

**正式 v2.0**（墨點場景）：原生生成 960×540（邏輯 480 格整數 ×2，硬邊無 AA），**減雜**——throng 疏一檔、走廊中軸暢通。舊 480 備份：`assets/scenes/_prev_480/`。

## 檔案與 z-order（由底到頂）

| z | 檔案 | 內容 |
|---|------|------|
| 0 | `hub_wall.png` | 牆／門／告示／地圖／旗幌 |
| 1 | `hub_floor.png` | 地板／地毯／硬影 |
| 2 | `hub_furniture.png` | 枱凳／書架／道具（減雜） |
| 3 | `hub_counter.png` | 櫃檯 |
| 4 | （角色／客人精靈） | 優先 `assets/sprites/64/` |
| 5 | `hub_lanterns.png` | 日間燈籠／旗串 |
| 5′ | `hub_lanterns_night.png` | 夜燈 |
| 6 | `hub_fg.png` | 最前景 |
| — | `hub_composed.png` | 合成預覽 |

建議繪製／碰撞順序：`wall → floor → furniture → counter → （角色）→ lanterns → fg`

## 熱點錨點表（960×540）

| 熱點 | 大約位置（x0–x1，y0–y1） | 對應玩法 |
|------|--------------------------|----------|
| 大門 | 12–108，164–300 | 進出／出巡 |
| 告示板 | 216–304，184–280 | 江湖 |
| 書架／藏書 | 216–296，**224**–324 | 藏書 |
| 櫃檯 | 306–674，326–440 | 經營 |
| 地圖架 | 724–816，182–288 | 據點 |
| 俠客席 | 676–820，356–424 | 俠客 |
| 走廊可走帶 | **390–550**，**320–500** | 小二 walk |
| 雅座 A/B/C | 見 `js/stages.js` HOTSPOTS | 小費／加急 |

## 重生

```bash
python3 tools/gen_ink_pixel_assets.py --scenes-only
```

Audit：opaque 像素 `oob=0`（見 `_gen_report.txt`）。
