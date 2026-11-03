# 美術資源 — 墨點江湖（Ink-Pixel Inn）

權威規範：**[/ART.md](../ART.md)**。不合規素材勿放入執行路徑。

## 俠客頭像（合規後）
| 路徑 | 對應 | 規格 |
|------|------|------|
| `heroes/qingyi.png` | 青衣劍客 | 32×32 或 64×64、盤內色、透明底、硬邊 |
| `heroes/tiezhang.png` | 鐵掌醫女 | 同上 |
| `heroes/langren.png` | 浪人刀客 | 同上 |
| `heroes/qinshi.png` | 琴心師太 | 同上 |

目前目錄為空：遊戲用 `js/game.js` 內 **SVG 像素剪影**。  
高清舊稿在 `heroes/_legacy/`，執行期不讀取。

合規 PNG 放入後，將 `USE_COMPLIANT_PORTRAITS` 改為 `true`。

## UI
| 路徑 | 用途 |
|------|------|
| `ui/` | 合規 UI 點陣（可選） |
| `ui/_legacy/inn-banner.png` | 舊寫實感 banner（已停用；場景為 SVG） |
