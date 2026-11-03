# 俠客棧 Changelog

## v1.6.0 — 2026-11-03
### QoL
- 日誌頁：**存檔 JSON 匯出／匯入**（文字框＋複製到剪貼簿；匯入會 `migrate` 並覆蓋目前進度，先彈確認）
- **新遊戲／重置**改為**兩次確認**，避免誤觸清空

### 效能
- Hub／戰鬥舞台：`requestAnimationFrame` 用 **loopGen 世代鎖**，唔會重複疊 loop
- 頁面隱藏（`visibilitychange`）→ **pause** Hub／Combat rAF、戰鬥 `setInterval`、以及經營 tick
- 重新顯示或 remount 時會安全重啟單一 loop

### 無障礙
- 主要快捷／分頁按鈕補 `aria-label`
- 全域 **`:focus-visible`** 金框（滑鼠 click 唔強制粗 outline；Tab 可見）
- 戰鬥 canvas `tabindex="0"`；Esc 返回既有邏輯保留

### 內容
- 客棧奇客互動短景：**蒙面人**、**說書人**（三選一，銀／望／好感）
- 輕量 tip／meet 文案：蒙面茶錢、說書拍扇

### 其他
- 版本號／頁腳／DESIGN／ART 對齊 **1.6.0**
- 音效仍暫緩；戰鬥減震維持唔加重

## v1.5.0
- 雙人羈絆事件（劍與藥／刀劍邀月）＋短暫戰意 buff
- 琴心等招募條件進度條＋抵達短景
- 日誌圖鑑摘要（勝仗／已遇／羈絆）
- Boss／敵人短表跟 `combatState` 播幀 0–3（唔再永遠 idle）

## v1.4.0
- 成就擴充＋領獎；戰後結算卡；波次／銀望平衡
- `guest_walk` 正式 3072×64；敵人／Boss 短表 256×64 接入
