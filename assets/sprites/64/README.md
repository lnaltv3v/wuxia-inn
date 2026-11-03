# 精靈表 64×64（原生）— 墨點江湖

> 原生像素 · `tools/gen_sprites_64.py` · 僅盤內色 · 透明底 · 硬邊無抗鋸齒  
> **唔係** 32 版 nearest-neighbor 放大——喺 64 格內加袍褶／武器厚度／茶盤器物；眼睛仍 1–2px 墨點。

## 檔案

| 檔 | 尺寸 | 說明 |
|----|------|------|
| `qingyi.png` | **1152×64** | 青衣劍客 · 18 幀 |
| `tiezhang.png` | **1152×64** | 鐵掌醫女 |
| `langren.png` | **1152×64** | 浪人刀客 |
| `qinshi.png` | **1152×64** | 琴心師太 |
| `xiaoer.png` | **1152×64** | 客棧小二（斟茶＋抹枱） |
| `guest_sit.png` | **384×64** | 客人坐姿 ×6（可選） |
| `boss_heifeng_combat.png` | **64×64** | Boss 戰鬥剪影（可選） |
| `boss_xieyi_combat.png` | **64×64** | Boss 戰鬥剪影（可選） |
| `boss_xueying_combat.png` | **64×64** | Boss 戰鬥剪影（可選） |

每角：每幀 **64×64**，橫向 **18** 幀 → `18×64 = 1152`。

## 對幀（同 32 版）

| 幀 | 動作 | 說明 |
|----|------|------|
| 0–1 | **idle** | 呼吸微動 |
| 2–5 | **walk** | 高抬左 → 過渡 → 高抬右 → 過渡（抬腳約 16px） |
| 6–8 | **serve** | 起盤 → 端穩 → 倒茶／撫琴（qinshi） |
| 9–12 | **attack** *或* **wipe** | 俠客：後引→大弧→擊中→收回；**xiaoer＝抹枱** |
| 13–14 | **hurt** | 兩幀差大 stagger |
| 15–17 | **parry** | 舉武器／盤擋 → 微震 → 回穩 |

```js
const FRAME = 64;
const sx = frameIndex * FRAME; // 0..17
ctx.imageSmoothingEnabled = false;
ctx.drawImage(sheet, sx, 0, FRAME, FRAME, dx, dy, FRAME, FRAME); // Hub 960×540 用 ×1
// 或再整數倍：dx 顯示寬 = FRAME * N
```

## 同 32 版對應

| 32 路徑 | 64 路徑 | 幀對齊 |
|---------|---------|--------|
| `assets/sprites/qingyi.png` (576×32) | `assets/sprites/64/qingyi.png` (1152×64) | 幀 index 相同 |
| …其餘俠客／小二同上 | `64/{id}.png` | 相同 |
| `guest_sit.png` (192×32) | `64/guest_sit.png` (384×64) | guestIndex 0–5 |
| `boss_*_combat.png` (32×32) | `64/boss_*_combat.png` (64×64) | 單幀 |

Hub 已係 **960×540** 時：原生 64 用 **×1**（或再 ×2／×3 整數倍 + `pixelated`）；唔好用非整數縮放。

## 重跑

```bash
python3 /workspace/wuxia-inn/tools/gen_sprites_64.py
```

合規：oob=0、每幀有可見像素、尺寸正確。預覽：`assets/_preview/64_*_x2.png`。
