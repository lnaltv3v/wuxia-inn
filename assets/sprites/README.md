# 俠客棧精靈表 — 墨點江湖對幀說明（v1.1）

> 原生像素 · Pillow 生成 · 僅盤內色 · 透明底 · 硬邊無抗鋸齒  
> 生成腳本：`/workspace/wuxia-inn/tools/gen_ink_pixel_assets.py`  
> **v1.1**：袍褶／腰帶／髮型剪影加密度；walk 抬腳更高＋跨步；serve 茶盤／壺／杯分離；attack 弧更大；hurt／parry 一眼可辨；**xiaoer 9–12 = 抹枱 wipe**；新增 `guest_sit.png`。

## 檔名與尺寸

| 檔案 | 尺寸 | 說明 |
|------|------|------|
| `qingyi.png` | **576×32** | 青衣劍客 · 18 幀橫向 |
| `tiezhang.png` | **576×32** | 鐵掌醫女 |
| `langren.png` | **576×32** | 浪人刀客 |
| `qinshi.png` | **576×32** | 琴心師太 |
| `xiaoer.png` | **576×32** | 客棧小二（斟茶＋抹枱） |
| `guest_sit.png` | **128×32** | 客人坐姿靜幀 ×4（不同衣色） |
| `boss_heifeng_combat.png` | **32×32** | 黑風寨主戰鬥站姿剪影 |
| `boss_xieyi_combat.png` | **32×32** | 邪醫戰鬥站姿剪影 |

每角精靈表：每幀 **32×32**，橫向 **18** 幀 → 總寬 `18×32 = 576`。

## 統一對幀（0-indexed）

| 幀 | 動作 | 說明 |
|----|------|------|
| 0–1 | **idle** | 呼吸微動（1px 上下） |
| 2–5 | **walk** | 高抬左 → 過渡 → 高抬右 → 過渡；抬腳約 **7px**＋跨步，臂擺可辨 |
| 6–8 | **serve** | 斟茶／端盤：起盤 → 端穩 → 微傾倒茶；茶盤／壺／杯分離清楚。`qinshi` 同幀位＝撫琴／持琴 |
| 9–12 | **attack** *或* **wipe** | 俠客：起手（武器後引）→ 揮出 → 擊中（刃尖高光）→ 收勢。**小二見下** |
| 13–14 | **hurt** | 後仰＋血點＋甩臂；姿勢同 parry 一眼可辨 |
| 15–17 | **parry** | 舉武器／盤擋身前 → 微震 → 回穩 |

### ⚠ xiaoer 幀位特殊說明（v1.1）

| 幀 | xiaoer 動作 |
|----|-------------|
| 6–8 | **serve**＝斟茶（茶盤＋硃紅壺＋杯，可倒茶） |
| **9–12** | **wipe／抹枱**（抹布橫掃：起手 → 中掃 → 遠掃 → 收勢／左手撑枱）——**唔係 attack** |

接入時：小二生活循環用 `9–12` 做抹枱；唔好當戰鬥攻擊播。

### 程式取幀

```js
const FRAME = 32;
const sx = frameIndex * FRAME; // 0..17
ctx.drawImage(sheet, sx, 0, FRAME, FRAME, dx, dy, FRAME, FRAME);

// guests
const guestIndex = 0..3; // teal / robe-red / ink-soft / violet
ctx.drawImage(guestSit, guestIndex * 32, 0, 32, 32, dx, dy, 32, 32);
```

角色統一 **面向右側**（走路／戰鬥一致），武器在身右。坐姿客亦偏右側持杯。

## 角色主色（盤內）

| id | 主色 | 輔色 | 剪影（v1.1） |
|----|------|------|------|
| qingyi | 青衫 `#2A6A6A` | 劍 `#4A9A9A` | 頂髻＋青袍褶＋直劍 |
| tiezhang | 醫袍紅 `#A04040` | 藥綠 `#3D8F66` | 髮髻金釵＋紅袍＋藥囊 |
| langren | 褐甲 `#3D3226` | 刀血 `#C42B2B` | 額帶＋胸甲＋寬刀 |
| qinshi | 梵紫 `#5A4060` | 素袍 `#F4E6C4` | 白帽＋紫／素袍＋琴／拂塵 |
| xiaoer | 木褐 `#5C4030` | 宣紙圍裙＋硃紅腰帶 | 木帽＋圍裙＋茶盤／抹布 |
| guest_sit | 四色輪換 | 凳＋持杯 | 坐姿四分三 |

設計語言：無鼻子、無髮絲；眼睛 1×1 墨點；硬邊色塊；外框可用墨黑 1px。

## Boss 頭像重用

`assets/heroes/boss_heifeng.png`、`boss_heifeng_64.png`、`boss_xieyi.png`、`boss_xieyi_64.png`  
色盤稽核合規（oob=0）。戰鬥舞台用本目錄 `boss_*_combat.png`。

## 色盤約束

僅准 ART.md 22 色＋角色擴充 4 色（青衫／劍鋒亮／醫袍紅／梵紫）。  
禁止寫實、柔邊、盤外 hex、抗鋸齒半透明、抄《大俠立志傳》資產。

## 稽核（生成時）

所有精靈表 `size==(576,32)`（guest_sit 為 `128×32`）、oob=0、每 32px 欄有可見像素。詳見 `_gen_report.txt`。
