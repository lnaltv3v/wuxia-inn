# 俠客棧音效規範 — 墨點江湖（Ink-Pixel Inn · Audio）

> 版本：v0.5.2 · 聽覺對齊「墨點江湖」視覺：**短、乾、少尾音、無現代電子感**。  
> 全部資產 **自製合成**，禁止第三方樣本庫／不明來源下載。

## 美學一句話
宣紙上的木與鐵——客棧是木門、腳步、茶水、銀兩；戰場是刀斬、招架、受擊；勝負各一句五聲短調。BGM 用慢／快五聲音階循環，像遠房有人撥琴，唔係合成器 Pad。

## 聽覺原則
| 原則 | 說明 |
|------|------|
| 短而乾 | SFX 多 < 0.8s；少殘響；木／金屬瞬態為主 |
| 少尾音 | 避免長 reverb、合唱、現代 EDM 側鏈 |
| 五聲而非西洋和聲堆疊 | 勝利／失敗短句、BGM 旋律用五聲音階感 |
| 小檔案 | mono · 22.05 kHz 中間稿 · 最終 **Ogg Vorbis** |
| 可循環 BGM | 頭尾淡入淡出，20–40 秒一段 |
| 無版權風險 | 僅 `assets/audio/_work/gen_audio.py` 合成 |

## 檔案結構
```
assets/audio/
  sfx/*.ogg          # 短音效
  bgm/*.ogg          # 循環 BGM
  _work/             # 生成腳本＋中間 wav（非執行期）
  README.md
js/audio.js          # 全域 WuxiaAudio
AUDIO.md             # 本文件
```

## 資產清單

### P0 — 必備（本輪已交付）
| id | 路徑 | 用途 | 觸發時機（建議） | 格式 | 時長 | loop |
|----|------|------|------------------|------|------|------|
| `door_wood` | `sfx/door_wood.ogg` | 木門開合 | Hub 客人 enter／leave 過門；點大門熱點 | ogg | ~0.55s | 否 |
| `footstep` | `sfx/footstep.ogg` | 腳步 | enter／leave 移動中節拍（每 2–3 幀一步） | ogg | ~0.18s | 否 |
| `tea_pour` | `sfx/tea_pour.ogg` | 斟茶 | Hub `serve` 階段開始 | ogg | ~0.70s | 否 |
| `coin` | `sfx/coin.ogg` | 銀兩 | Hub `pay`；小費；頂欄銀兩跳動 | ogg | ~0.35s | 否 |
| `sword_slash` | `sfx/sword_slash.ogg` | 刀斬 | 戰鬥 `hit`／`skill` 出手 | ogg | ~0.32s | 否 |
| `parry` | `sfx/parry.ogg` | 招架 | 戰鬥 `parry` | ogg | ~0.28s | 否 |
| `hit` | `sfx/hit.ogg` | 受擊 | 戰鬥命中落地（`hit`／`skill` 受方） | ogg | ~0.28s | 否 |
| `guest_sit` | `sfx/guest_sit.ogg` | 入座 | 客人到位／雅座入座 | ogg | ~0.40s | 否 |
| `victory` | `sfx/victory.ogg` | 勝利短句 | 戰鬥勝利結算 | ogg | ~0.85s | 否 |
| `defeat` | `sfx/defeat.ogg` | 失敗短句 | 戰鬥失敗結算 | ogg | ~0.94s | 否 |
| `bgm_inn` | `bgm/bgm_inn.ogg` | 客棧 BGM | Hub 常駐（預設＝日） | ogg | ~28s | **是** |
| `bgm_combat` | `bgm/bgm_combat.ogg` | 戰鬥 BGM | 進入 Combat Overlay | ogg | ~24s | **是** |

### P0 延伸（已交付）
| id | 路徑 | 用途 | 觸發 |
|----|------|------|------|
| `bgm_inn_day` | `bgm/bgm_inn_day.ogg` | 日氛圍 | Hub 白天色溫 |
| `bgm_inn_night` | `bgm/bgm_inn_night.ogg` | 夜氛圍 | Hub 夜晚／燈火色溫 |

### P1 — 可選（已附檔，掛接可後做）
| id | 路徑 | 用途 |
|----|------|------|
| `ui_click` | `sfx/ui_click.ogg` | 快捷鈕／Sheet 按鈕 |

## Web Audio 用法（`WuxiaAudio`）

瀏覽器需 **用戶手勢** 先 unlock：

```js
// 首次點擊／觸控（建議綁 document 一次）
document.addEventListener('pointerdown', () => WuxiaAudio.unlock(), { once: true });
```

| API | 說明 |
|-----|------|
| `WuxiaAudio.unlock()` | `AudioContext.resume()`；可重入 |
| `WuxiaAudio.play(id, opts?)` | 播 SFX；`opts: { volume?, playbackRate? }` |
| `WuxiaAudio.setMuted(bool)` | 總靜音（含 BGM） |
| `WuxiaAudio.setMasterVolume(0..1)` | 主音量 |
| `WuxiaAudio.setBgm(id\|null)` | 切換／停止循環 BGM（同曲不重啟） |
| `WuxiaAudio.stopBgm()` | 停 BGM |
| `WuxiaAudio.preload()` | 預載 ogg；失敗則合成後備就緒 |
| `WuxiaAudio.ready` | Promise：預載完成 |
| `WuxiaAudio.ACTION_MAP` | 戰鬥 kind → 音效 id 建議表 |
| `WuxiaAudio.HUB_MAP` | Hub phase → 音效建議 |

- 優先 `fetch`＋`decodeAudioData` 讀 `assets/audio/.../*.ogg`  
- 檔案缺失／解碼失敗 → **同 id 的 oscillator／noise 合成後備**（不依賴外部庫）  
- 本模組 **唔改** 玩法數值；掛接由開發主理人接

## 建議掛接點

### Hub（`stages.js` Inn 狀態機 `idle→enter→serve→pay→leave`）
| 時機 | 呼叫建議 |
|------|----------|
| 進入 Hub／日間 | `setBgm('bgm_inn_day')` 或 `'bgm_inn'` |
| 夜色溫切換 | `setBgm('bgm_inn_night')` |
| `enter` 開始 | `play('door_wood')`；移動中偶發 `play('footstep')` |
| 到位 | `play('guest_sit')` |
| `serve` 開始 | `play('tea_pour')` |
| `pay` | `play('coin')` |
| `leave` 過門 | `play('door_wood')` |

### 戰鬥（`game.js` `beginBattle` → `onAction` → `WuxiaStages.Combat.playAction`）
| `evt.kind` | 建議 |
|------------|------|
| 開戰 | `setBgm('bgm_combat')` |
| `hit`／`skill` | `play('sword_slash')` 後短延遲 `play('hit')`；或只播 `ACTION_MAP` |
| `parry` | `play('parry')` |
| `miss` | （可靜音或極輕 `ui_click`） |
| `heal`／`shield` | （P1：可另加 bell，暫略） |
| `ko` | 可加重 `hit` |
| 勝利／失敗 | `play('victory'|'defeat')`；結束後 `setBgm('bgm_inn')` |

### 最小掛接示例（給開發主理人，約 5–8 行）

```js
// 1) 首次手勢
document.addEventListener('pointerdown', () => WuxiaAudio.unlock(), { once: true });
WuxiaAudio.preload();

// 2) Hub 常駐
WuxiaAudio.setBgm('bgm_inn');

// 3) 接客 phase 變化時（stages Inn 回呼／現有 caption 旁）
if (phase === 'serve') WuxiaAudio.play('tea_pour');
if (phase === 'pay') WuxiaAudio.play('coin');

// 4) 戰鬥 onAction
const ids = WuxiaAudio.ACTION_MAP[evt.kind];
(ids || []).forEach((id) => WuxiaAudio.play(id));

// 5) 勝負
WuxiaAudio.play(won ? 'victory' : 'defeat');
WuxiaAudio.setBgm(won ? 'bgm_inn' : 'bgm_inn');
```

## 掛接狀態（v0.5.2）
- `index.html`：`js/audio.js` 於 `game.js` 之前  
- `game.js`：pointerdown unlock、戰鬥 BGM／onAction／勝負、Hub 日夜 BGM、UI 輕量 click  
- `stages.js`：Hub phase → `HUB_MAP`；接客腳步偶發；`isNight`／`setAmbientChange`  

## 與 ART／DESIGN 關係
- 視覺規範：**[ART.md](./ART.md)**  
- 系統／舞台：**[DESIGN.md](./DESIGN.md)**（路線圖「音效／音樂」→ 初版見本文件＋`js/audio.js`）  
- 資產明細：`assets/audio/README.md`

## 禁止事項
1. 引入商業／不明授權樣本、AI 音樂站下載不明授權檔  
2. 長尾電子 Pad、鼓組樣本包、語音素材庫  
3. 大改 `game.js`／`stages.js`／`combat.js` 玩法邏輯只為播音（應用薄呼叫）  
4. 未 unlock 就依賴自動播 BGM（需手勢後）
