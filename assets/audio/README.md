# assets/audio/ — 墨點江湖音效資產

> 全部為本專案 **Python 合成自製**（`_work/gen_audio.py`），再經 ffmpeg 轉 **Ogg Vorbis**。  
> **無第三方樣本庫、無版權風險。** 中間 WAV 僅留在 `_work/`，執行期只讀 `sfx/`、`bgm/`。

## 目錄

```
assets/audio/
  sfx/          # 短音效 .ogg（mono）
  bgm/          # 可循環背景音樂 .ogg（mono，約 24–32 秒）
  _work/        # 生成腳本與中間 wav（非執行期依賴）
  README.md
```

## SFX（`sfx/*.ogg`）

| 檔名 | 用途 | 約時長 | 約大小 |
|------|------|--------|--------|
| `door_wood.ogg` | 木門開合 | 0.55s | ~5 KB |
| `footstep.ogg` | 腳步 | 0.18s | ~5 KB |
| `tea_pour.ogg` | 斟茶倒水 | 0.70s | ~7 KB |
| `coin.ogg` | 銀兩 | 0.35s | ~5 KB |
| `sword_slash.ogg` | 刀斬 | 0.32s | ~5 KB |
| `parry.ogg` | 招架 | 0.28s | ~5 KB |
| `hit.ogg` | 受擊 | 0.28s | ~5 KB |
| `guest_sit.ogg` | 客人入座 | 0.40s | ~6 KB |
| `victory.ogg` | 勝利短句 | 0.85s | ~6 KB |
| `defeat.ogg` | 失敗短句 | 0.94s | ~6 KB |
| `ui_click.ogg` | UI 點擊（P1） | 0.08s | ~4 KB |

## BGM（`bgm/*.ogg`，可 loop）

| 檔名 | 用途 | 約時長 | 約大小 |
|------|------|--------|--------|
| `bgm_inn.ogg` | 客棧預設（＝日） | 28s | ~161 KB |
| `bgm_inn_day.ogg` | 客棧日氛圍 | 28s | ~161 KB |
| `bgm_inn_night.ogg` | 客棧夜氛圍 | 32s | ~181 KB |
| `bgm_combat.ogg` | 戰鬥緊張 | 24s | ~95 KB |

## 重新生成

```bash
python3 assets/audio/_work/gen_audio.py
# 再 ffmpeg 轉 ogg（見該目錄註解或 AUDIO.md）
```

播放 API 見專案根目錄 **[AUDIO.md](../../AUDIO.md)** 與 `js/audio.js`（`WuxiaAudio`）。
