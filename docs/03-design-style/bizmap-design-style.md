# BizMap Design Style v1 — System Specification

> 品牌視覺與 UI 設計規範，適用於 bizmap.tw 全站。
> 隸屬 Kairos Engine 設計體系，與 ecosystem-routing.md 一致。

---

## 1. 設計原則

| 原則 | 說明 |
|------|------|
| **資訊優先** | 商家資料是核心，視覺裝飾最低限度 |
| **深色低干擾** | 深色背景讓商家內容突出，閱讀疲勞最低 |
| **Glass 質感** | 通透、輕盈、現代感的毛玻璃卡片 |
| **金色為信號** | 金黃色只在關鍵行動點與品牌元素使用 |
| **效能優先** | 無重圖片、無大動畫、無第三方 UI lib |

---

## 2. 品牌色彩

### 主色盤

```
Ink (bg-primary)    #0c0c0e  — 最深底色，用於 body/nav/footer
Slate (bg-secondary) #1e2330 — 次要底色，用於 section 區隔
Gold (accent)        #c8a84b — 品牌色，CTA / 標題強調 / hover 狀態
```

### 色階系統

| Token | Hex | 用途 |
|-------|-----|------|
| `ink-950` | `#0c0c0e` | Body background |
| `ink-900` | `#353536` | 次要表面 |
| `slate-950` | `#1e2330` | Section 交替底色 |
| `slate-900` | `#282b36` | 卡片邊框 |
| `gold-400` | `#c8a84b` | 品牌金 — 按鈕 / logo / hover |
| `gold-300` | `#e9c76b` | 金高光 — 特殊狀態 |
| `gold-50` | `#fdf8ed` | 金背景光暈 |

### 功能色

| Token | Hex | 用途 |
|-------|-----|------|
| `glass-dark` | `rgba(255,255,255,0.04)` | 莫內卡片底色 |
| `glass-border` | `rgba(255,255,255,0.08)` | 卡片邊框 |
| `glass-hover` | `rgba(255,255,255,0.12)` | 卡片 hover |
| `text-primary` | `#ffffff` | 主文字 |
| `text-secondary` | `rgba(255,255,255,0.4)` | 次要說明文字 |
| `text-tertiary` | `rgba(255,255,255,0.25)` | 淡文字 / placeholder |

---

## 3. 字體系統

| 角色 | 字體 | Fallback |
|------|------|----------|
| 英文數位 | Inter (300–900) | sans-serif |
| 繁體中文 | Noto Sans TC (300–900) | sans-serif |
| 程式碼/數字 | JetBrains Mono (400–600) | ui-monospace |

### 階層

| Element | Size | Weight | Letter-spacing |
|---------|------|--------|----------------|
| H1 Hero | `text-5xl md:text-7xl` | Bold (700) | `tracking-tight` |
| H2 Section | `text-3xl md:text-4xl` | Bold (700) | `tracking-tight` |
| 類別名稱 | `text-sm` | Semibold (600) | normal |
| 說明文字 | `text-xs` | Normal (400) | normal |
| 標籤/標章 | `text-[11px]` | Monospace, Uppercase | `tracking-wider` |
| 品牌標誌 | `text-lg` | Bold (700) | normal |

---

## 4. 佈局系統

### 網格

- **全域 max-width**: `max-w-6xl` (72rem / 1152px)
- **導覽列**: `fixed top-4 left-1/2 -translate-x-1/2 z-50`, 半透明毛玻璃
- **Section 間距**: `py-24` (96px) / `py-28` (112px)
- **內容 padding**: `px-6` (24px)

### 元件

| 元件 | 規格 |
|------|------|
| Navbar | 固定頂部，glass-card 背景 `rgba(12,12,14,0.85)`，h-14 (56px) |
| Hero | 最低 `min-h-[85vh]`，漸層背景 + 網格 overlay + radial glow |
| 搜尋列 | H: 56px，圓角 `rounded-card` (12px)，內左 icon + 搜尋按鈕 |
| 特徵卡片 | Bento grid (2col/md:4col)，glass-card-dark，`p-6`，hover 微上移 |
| 統計區 | 四欄 grid，`-mt-12` 疊在 hero 上，glass-card 浮動效果 |
| 分類網格 | 2col/md:4col，gap-5，每格 `p-7`，icon 4xl + 名稱 + 計數 |
| Footer | `border-t border-white/5`，4col grid，`py-16` |

### Header 內容順序

```
Logo (bizmap.tw) → Nav links (商家名錄 / 關於) → CTA (免費上架)
```

### Hero 內容順序

```
Section badge → H1 tagline → Subtitle → Search bar → City quick links
```

---

## 5. 卡片系統

### Glass Card 系列

```css
/* 透明淺色 — 導覽列用 */
.glass-card {
  background: rgba(255,255,255,0.7);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255,255,255,0.18);
  border-radius: 16px;
  box-shadow: 0 4px 30px rgba(0,0,0,0.1);
}

/* 透明深色 — 內容卡片 */
.glass-card-dark {
  background: rgba(255,255,255,0.04);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 16px;
}

/* 白色實體 — secondary 內容 */
.card-elevated {
  background: #ffffff;
  border: 1px solid #f0f0f0;
  border-radius: 12px;
}
```

### Hover 效果

- **glass-card-dark**: `background: rgba(255,255,255,0.08)`, `border-color: gold/30`, `translateY(-2px)`, `box-shadow` 加深
- **card-elevated**: `box-shadow` 加大, `border-color: gold`, `translateY(-2px)`
- **Nav link**: `text-white/60 → text-white`, `bg-white/5` on hover
- **按鈕**: `translateY(-2px)`, `box-shadow` 擴散金輝

---

## 6. 按鈕系統

| Variant | 樣式 | 用途 |
|---------|------|------|
| `btn-primary` | Gold bg, ink text, `py-3 px-7` | 主 CTA（免費上架、搜尋） |
| `btn-ghost` | Transparent bg, white border, white/80 text | 次要操作 |
| 標籤連結 | `px-3 py-1.5`, `rounded-pill`, `text-xs` | 縣市快速篩選 |
| Nav link | `px-3.5 py-2`, `rounded-lg`, `text-sm` | 導覽選項 |

---

## 7. 互動動畫

| 時機 | 效果 | 時長 | Easing |
|------|------|------|--------|
| 頁面載入 | Hero fade-in + translate-y | 0.7s | `cubic-bezier(0.16, 1, 0.3, 1)` |
| Card hover | translateY(-2px) + shadow | 0.25s | `ease` |
| 按鈕 hover | translateY(-2px) + glow | 0.25s | `ease` |
| Nav link hover | bg + color transition | 0.15s | `all` |
| Scrollbar | 6px gold-tinted thumb | — | — |

---

## 8. 響應式中斷點

| 裝置 | 欄數 | 變化 |
|------|------|------|
| Mobile (<768px) | 2 columns (grid), 1 column (lists) | 堆疊顯示 |
| Desktop (≥768px) | 4 columns (grid), 3 columns (lists) | 完整佈局 |
| Hero H1 | `text-5xl` (mobile) → `text-7xl` (desktop) | 縮小字級 |

---

## 9. 資料呈現規範

### 商家卡片
- 名稱：`font-semibold text-white`
- 類別：emoji icon + 中文類別名
- 計數：`text-xs text-white/30 font-mono`
- 禁止直接渲染未經 sanitize 的商家輸入

### 統計數字
- 使用 `toLocaleString()` 格式化千分位
- 主數字 `text-3xl font-bold text-gold`
- label `text-xs text-white/30`

### SEO 結構化資料
- 每頁需有 `<script type="application/ld+json">` WebSite + SearchAction
- `<title>` + `<meta description>` 每頁自訂
- `robots.txt` + `llms.txt` 已存在

---

## 10. 缺失功能對照（未在 PRD/SSD 定義內）

以下是目前網站設計中未在設計規範內的行為，供後續補齊：

- [ ] **商家詳情頁 `/business/[id]`** — 設計尚未定義
- [ ] **推薦商家區塊** — Feature Spec 有定義但無 UI mockup
- [ ] **Loading state** — 目前僅有 shimmer animation，無 skeleton 定義
- [ ] **錯誤狀態** — 搜尋無結果、資料載入失敗等錯誤 UI 未規範
- [ ] **黑暗模式切換** — 目前強制深色，無淺色模式定義
- [ ] **行動版導覽** — Navbar 無 hamburger menu，行動版可能溢出

---

## 11. 版本記錄

| 日期 | 版本 | 變更 |
|------|------|------|
| 2026-05-18 | v1 | 初版 — 依據現有 codebase 逆向文件化 |
