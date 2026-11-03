# 資產說明

## heroes/
合規墨點江湖頭像（原生 32×32，另附 `_64.png` 顯示用變體）：
- `qingyi.png` / `tiezhang.png` / `langren.png` / `qinshi.png`
- `boss_heifeng.png` / `boss_xieyi.png`

`USE_COMPLIANT_PORTRAITS = true`（`js/game.js`）時優先載入上述 PNG；失敗回退 SVG 剪影。

## _legacy/
封存不合規高清稿。**遊戲執行期不讀取。**
