# BizMap SSD — System Specification Document

## 1. 系統概述

BizMap 是一個台灣在地商家名錄平台，使用 SvelteKit + Cloudflare Pages 建置，商家資料直接以靜態 JSON 檔提供，無後端伺服器。

### 技術棧
- **前端框架**: SvelteKit 2 + Svelte 4
- **部署平台**: Cloudflare Pages (adapter-cloudflare)
- **資料格式**: 靜態 JSON file
- **資料來源管線**: Twinkle Hub MCP → 政府開放資料
- **CSS**: Tailwind CSS

## 2. 架構

```
bizmap.tw
├── 靜態網站 (SvelteKit + Cloudflare Pages)
│   ├── / (首頁)
│   ├── /directory (商家名錄)
│   ├── /search (搜尋)
│   ├── /submit (商家提交)
│   └── /about (關於)
├── 資料
│   ├── static/data/businesses.json (公開 JSON API)
│   └── data/seed-businesses.json (原始檔)
└── 資料管線
    └── scripts/bizmap_pipeline.py (Twinkle Hub MCP → JSON)
```

### 資料流程

```
Twinkle Hub MCP API
    ↓ (opendata-query_rows)
scripts/bizmap_pipeline.py
    ↓ (transform to Bizmap schema)
data/seed-businesses.json  +  static/data/businesses.json
    ↓ (git push → CF Pages deploy)
bizmap.tw/data/businesses.json  (公開存取)
    ↓
SvelteKit pages (fetch at runtime)
```

## 3. 資料模型

### Business Entry Schema

| 欄位 | 型態 | 說明 |
|------|------|------|
| business_id | string | 唯一識別碼 (biz_ + md5 前 12 碼) |
| business_name | string | 商家名稱 |
| category | string | 類別 (餐飲美食/美容美髮/醫療健康/教育補習/...) |
| category_slug | string | 類別英文 slug |
| region | string | 地區 (ex: "台北市 松山區") |
| city | string | 縣市 |
| district | string | 區/鄉/鎮 |
| address | string | 完整地址 |
| phone | string | 電話號碼 |
| site_url | string | 官方網站 |
| booking_url | string | 預約連結 |
| card_url | string | 數位名片連結 |
| description | string | 簡短描述 |
| tags | string[] | 標籤 |
| source_type | string | 資料來源類型 (government_open_data/owner_submitted/official_site/manual_verified/partner_import/google_indexed_page) |
| source_name | string | 來源機關名稱 |
| source_url | string | 來源 URL |
| source_license | string | 資料授權條款 |
| source_updated_at | string | 資料更新日期 (ISO) |
| claim_status | string | 認領狀態 (unclaimed/claimed/verified) |
| review_status | string | 審核狀態 (pending/approved/rejected) |
| removal_status | string | 下架狀態 (active/removed) |
| module_statuses | dict | 各模組啟用狀態 |

### Module Statuses

| 模組 | 用途 | 狀態值 |
|------|------|--------|
| bizmap | 名錄曝光 | active/inactive |
| aeo_scanner | SEO 掃描 | not_started/in_progress/completed |
| quicknotifys | 快速通知 | active/inactive |
| mycal | 線上預約 | active/inactive |
| k_core | 內部診斷核心 | not_started/in_progress/completed |
| card | 數位名片 | active/inactive |

## 4. 資料來源管線

### Twinkle Hub MCP 工具

使用 `opendata-*` 系列工具查詢政府開放資料：
- `opendata-search_datasets` — 搜尋資料集
- `opendata-query_rows` — 查詢資料列 (支援 SQL WHERE)
- `opendata-get_dataset` — 取得 metadata + schema

### 對應資料集

| Bizmap 類別 | Gov Dataset ID | 來源機關 | 規模 |
|------------|---------------|---------|------|
| 醫療健康 - 藥局 | 39284 | 衛福部健保署 | ~9,882 |
| 醫療健康 - 診所 | 39283 | 衛福部健保署 | ~24,480 |
| 醫療健康 - 醫院 | 39282 | 衛福部健保署 | ~371 |
| 教育補習 | 124223 | 新北市教育局 | ~2,917 |
| 餐飲美食(公司) | 32681 | 經濟部商業署 | ~205,240 |
| 美容美髮(商登) | 108376 | 經濟部商業署 | ~69,434 |
| 零售購物(公司) | 166154 | 經濟部商業署 | 六都百萬級 |
| 民宿 | 83645 | 臺中市觀光局 | ~數百 |

### Pipeline 執行

```bash
python3 scripts/bizmap_pipeline.py
```

設定 `PER_DATASET` 變數控制每資料集筆數。輸出到:
- `data/seed-businesses.json` — 原始數據
- `static/data/businesses.json` — 公開 API (同步寫入)

## 5. 部署流程

```bash
# 1. 更新資料
python3 scripts/bizmap_pipeline.py

# 2. 建置測試
npm run build

# 3. 提交
git add .
git commit -m "bizmap: update data + pages"
git push origin main
# → Cloudflare Pages 自動部署
```

## 6. SEO 與 AI 可發現性

- `llms.txt` (`/llms.txt`) — 提供 AI 爬蟲結構化資訊
- `robots.txt` — 允許主要爬蟲
- `static/data/businesses.json` — 公開 JSON 供第三方與 AI 使用
- Schema.org `WebSite` + `SearchAction` structured data
- 每個類別/縣市都有獨立頁面路徑

## 7. 安全考量

- API key (`sk-POQ...`) 僅存於本機 pipeline 腳本，不進 git
- 所有商家資料來自政府開放資料（無 PII）
- `source_license: "政府開放資料授權條款-第1版"` 標註每筆資料
- 無使用者登入/後端 API，無攻擊面
- 提交表單 (`/submit`) 為靜態頁面，目前無後端處理

## 8. 未來擴展

- [ ] 更多資料集（餐飲業者登錄、民宿、健身中心）
- [ ] Twtools 整合（地址驗證、電話格式檢查）
- [ ] 商家詳細頁面 (`/business/[id]`)
- [ ] 地圖整合 (Leaflet / Google Maps)
- [ ] 商家認領流程
- [ ] 自動化 pipeline (cron job 每週更新)
