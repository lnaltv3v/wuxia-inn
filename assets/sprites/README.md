# 俠客棧精靈表 — 墨點江湖對幀說明（v1.2）

> 原生像素 · Pillow 生成 · 僅盤內色 · 透明底 · 硬邊無抗鋸齒  
> 生成腳本：`/workspace/wuxia-inn/tools/gen_ink_pixel_assets.py`（**sprites-only**；Hub 場景改由「墨點場景」負責，唔覆寫 `assets/scenes/`）  
> **v1.2**：同解析度加資訊量——頭／帽／髮型／肩飾剪影差更大；袍領口／袖口／下擺褶 1–2px；腰帶扣／藥囊／劍鞘；walk 抬腳約 **8px**＋衣擺跟動；serve 茶盤／壺／杯分離＋倒茶弧；attack／hurt／parry 姿勢一眼可讀；Boss 威脅剪影加厚；`guest_sit` 扩至 **6** 幀（杯／碗）。

## 檔名與尺寸

| 檔案 | 尺寸 | 說明 |
|------|------|------|
| `qingyi.png` | **576×32** | 青衣劍客 · 18 幀橫向 |
| `tiezhang.png` | **576×32** | 鐵掌醫女 |
| `langren.png` | **576×32** | 浪人刀客 |
| `qinshi.png` | **576×32** | 琴心師太 |
| `xiaoer.png` | **576×32** | 客棧小二（斟茶＋抹枱） |
| `guest_sit.png` | **192×32** | 客人坐姿 ×**6**（衣色／帽型／杯或碗） |
| `boss_heifeng_combat.png` | **32×32** | 黑風寨主戰鬥站姿剪影 |
| `boss_xieyi_combat.png` | **32×32** | 邪醫戰鬥站姿剪影 |

每角精靈表：每幀 **32×32**，橫向 **18** 幀 → 總寬 `18×32 = 576`。

## 統一對幀（0-indexed）

| 幀 | 動作 | 說明 |
|----|------|------|
| 0–1 | **idle** | 呼吸微動（1px 上下） |
| 2–5 | **walk** | 高抬左 → 過渡 → 高抬右 → 過渡；抬腳約 **8px**＋跨步＋衣擺跟動 |
| 6–8 | **serve** | 起盤 → 端穩 → 微傾倒茶（茶盤／壺／杯分離＋倒茶弧）。`qinshi`＝撫琴／持琴 |
| 9–12 | **attack** *或* **wipe** | 俠客：起手 → 揮出 → 擊中（刃尖高光）→ 收勢。**小二見下** |
| 13–14 | **hurt** | 後仰＋血點＋甩臂 |
| 15–17 | **parry** | 舉武器／盤擋身前 → 微震 → 回穩 |

### ⚠ xiaoer 幀位（不變）

| 幀 | xiaoer 動作 |
|----|-------------|
| 6–8 | **serve**＝斟茶 |
| **9–12** | **wipe／抹枱**——**唔係 attack** |

### 程式取幀

```js
const FRAME = 32;
const sx = frameIndex * FRAME; // 0..17
ctx.drawImage(sheet, sx, 0, FRAME, FRAME, dx, dy, FRAME, FRAME);

// guests v1.2：6 幀
const guestIndex = 0..5; // teal / robe-red / ink-soft / violet / jade / wood-hat
ctx.drawImage(guestSit, guestIndex * 32, 0, 32, 32, dx, dy, 32, 32);
```

角色統一 **面向右側**。坐姿客偏右側持杯／碗。

## 角色主色與剪影（v1.2）

| id | 主色 | 輔色 | 剪影重點 |
|----|------|------|------|
| qingyi | `#2A6A6A` | `#4A9A9A` | 高頂髻＋青袍褶＋肩飾＋髖劍鞘 |
| tiezhang | `#A04040` | `#3D8F66` | 雙髻金釵＋紅袍＋藥囊繩 |
| langren | `#3D3226` | `#C42B2B` | 額帶拖尾＋甲肩＋寬刀 |
| qinshi | `#5A4060` | `#F4E6C4` | 高白帽＋長袖＋梵紫／素袍 |
| xiaoer | `#5C4030` | 宣紙圍裙＋硃紅腰帶 | 寬木帽＋圍裙袋＋茶盤／抹布 |
| guest_sit | 六色輪換 | 凳＋杯／碗 | 坐姿穩、手持可辨 |
| boss_heifeng | 墨褐＋血 | 巨刀 | 披髮額帶＋寬肩甲＋大刀 |
| boss_xieyi | 梵紫＋藥綠 | 毒瓶／爪 | 雙髻＋毒瓶＋前伸爪 |

設計語言：無鼻子、無髮絲；眼睛 1×1 墨點；硬邊色塊。**禁止**抄《大俠立志傳》立繪／搬高清／寫實。

## Boss 頭像重用

`assets/heroes/boss_heifeng.png`、`boss_heifeng_64.png`、`boss_xieyi.png`、`boss_xieyi_64.png`  
戰鬥舞台用本目錄 `boss_*_combat.png`。

## 色盤約束

僅准 ART.md 22 色＋角色擴充 4 色（青衫／劍鋒亮／醫袍紅／梵紫）。

## 稽核（生成時）

所有俠客／小二 `size==(576,32)`、`guest_sit==(192,32)`、Boss `32×32`、oob=0、每 32px 欄有可見像素。詳見 `_gen_report.txt`。

重生（只精靈）：`python3 tools/gen_ink_pixel_assets.py`
