# BizMap PRD

## 定位
BizMap 是 KairosLink 生態圈中的商家名錄聚合層，負責地區、分類與列表型曝光，並將流量導向商家頁或其他承接節點。

## 當前狀態 (2026-05-12)
- **網域**: bizmap.tw
- **部署**: Cloudflare Pages (SvelteKit + adapter-cloudflare)
- **資料量**: ~300 筆真實商家資料（政府開放資料來源）
- **覆蓋**: 4 類別 × 22 縣市
- **資料管線**: 已建立 Twinkle Hub MCP → Bizmap schema pipeline
- **文件**: PRD + SSD 已建立

## 核心任務
- 收錄全台商家（政府開放資料 + 商家自行提交）
- 建立地區頁與分類頁
- 提供列表式商家發現入口
- 導流回商家主頁、預約與分享節點

## 資料來源
| 來源 | 狀態 | 說明 |
|------|------|------|
| 政府開放資料 | ✅ 已上線 | 健保藥局/診所/補習班/餐飲/美容美髮 |
| 商家自行提交 | ✅ 表單已上線 | `/submit` 靜態頁面 |
| 官方網站爬蟲 | 🔜 規劃中 | |
| 合作夥伴匯入 | 🔜 規劃中 | |

## 關聯模組
- K-Core（內部診斷核心）
- Kairos.Site
- QuickNotifys
- MyCal
- 秒傳名片
- Twinkle Hub（資料來源 MCP）

## Roadmap

### Phase 1 (Current) — 資料基礎
- [x] 建立資料 pipeline（Twinkle Hub → JSON）
- [x] 首批 300+ 筆政府開放資料
- [x] 名錄頁面支援搜尋/過濾
- [x] PRD + SSD 文件

### Phase 2 — 擴充資料覆蓋
- [ ] 擴充至 5,000+ 筆（食品業者、民宿、健身中心）
- [ ] 地址正規化與地理編碼
- [ ] 商家詳細頁面 (`/business/[id]`)
- [ ] Google 結構化資料 (LocalBusiness)

### Phase 3 — 互動功能
- [ ] 商家認領流程
- [ ] 地圖整合
- [ ] 評論/評分
- [ ] cron job 自動更新資料
