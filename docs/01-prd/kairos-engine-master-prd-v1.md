# Kairos Engine 生態圈總 PRD v1

## 1. 文件資訊
| 項目 | 內容 |
|---|---|
| 文件名稱 | Kairos Engine 生態圈總 PRD |
| 版本 | v1 |
| 文件性質 | 生態圈總產品需求文件 |
| 核心平台 | Kairos.Site |
| 關聯節點 | AEO Scanner、BizMap、K-Core、KairosLink、QuickNotifys、MyCal、秒傳名片 |
| 目的 | 統一產品定位、模組關係、導流架構、資料邏輯與開發優先順序 |

## 2. 產品願景
Kairos Engine 的目標不是再做一套零散工具，而是建立一套面向中小企業與店家的數位成交基礎設施。這套生態圈要把原本分散的建頁、AI 可見度、名錄曝光、評論管理、預約承接、名片分享與內部健檢流程，整合成一條可追蹤、可補強、可迭代的成交路徑。

### 一句話定位
Kairos Engine 是以 Kairos.Site 為核心的多節點數位成交生態圈。

## 3. 問題定義
中小企業與店家在數位經營上常見的問題包括：
- 有曝光但沒有詢問
- 有商家檔案但品牌資訊不足
- 有流量但沒有承接頁
- 有評論卻沒有管理流程
- 有需求卻不知道該從哪個模組先補
- 內部團隊報價與提案容易憑感覺

### 核心問題陳述
如何建立一套可讓店家快速建構數位軌跡，並讓內部團隊可依需求進行健檢、報告、報價與模組分流的生態圈系統？

## 4. 生態圈組成
| 節點 | 網域/形式 | 正式定位 | 備註 |
|---|---|---|---|
| Kairos.Site | kairossite.com | 生態圈核心主站 | 第一版完成，持續改版中 |
| AEO Scanner | aeo.kairossite.com | 附屬於 Kairos.Site 的 AEO 掃描工具 | 非獨立產品主站 |
| BizMap | bizmap.tw | 商家名錄聚合層 | 亦為 K-Core 附掛位置 |
| K-Core | 附掛於 BizMap 之下 | 內部診斷核心 | 健檢、報告、報價 |
| KairosLink | kairoslink.net | 外連服務官網 | 目前只是官網 |
| QuickNotifys | quicknotifys.com | 商家檔案評論自動化產品 | 生態圈口碑互動節點 |
| MyCal | mycal.tw | 預約與付款承接系統 | 生態圈轉換承接節點 |
| 秒傳名片 | LINE 電子名片 | 分享與聯絡入口 | 生態圈最短分享路徑 |

## 5. 核心原則
1. 各站相互串連、相互導流
2. Kairos.Site 為主要商家資料入口
3. AEO 為附屬工具，不獨立成主產品線
4. BizMap 為聚合名錄層，不重做建頁
5. K-Core 為內部健檢、報告與報價中樞
6. KairosLink 現階段定位為服務官網
7. QuickNotifys、MyCal、秒傳名片為後段互動與承接節點
8. 生態圈整合重點是成交鏈最大化，不是單站最大化

## 6. 目標使用者
### 外部使用者
- 中小企業主
- 在地店家
- 個人工作室
- 行銷代管方

### 內部使用者
- Kairos 內部顧問
- 內部營運/管理員
- 合作夥伴

## 7. 核心流程
### 外部客戶視角
1. 認識 Kairos 生態圈
2. 建立商家頁（Kairos.Site）
3. 掃描 AI 可見度（AEO Scanner）
4. 補名錄曝光（BizMap）
5. 補評論管理（QuickNotifys）
6. 補預約承接（MyCal）
7. 補分享入口（秒傳名片）

### 內部顧問視角
1. 客戶提出需求
2. 建立 K-Core 健檢案件
3. 收集現況資料
4. 產出健檢報告
5. 產出初步報價
6. 映射到對應模組
7. 導入 Kairos 生態圈方案

## 8. 生態圈導流架構
| 當前節點 | 可導向節點 | 目的 |
|---|---|---|
| Kairos.Site | AEO Scanner / BizMap / QuickNotifys / MyCal / 秒傳名片 / K-Core | 將建頁需求延伸到其他節點 |
| AEO Scanner | Kairos.Site / K-Core / BizMap / KairosLink | 將掃描結果轉成補強行動 |
| BizMap | Kairos.Site / MyCal / 秒傳名片 / K-Core | 聚合曝光後導向主頁與承接節點 |
| K-Core | Kairos.Site / BizMap / QuickNotifys / MyCal / 秒傳名片 / KairosLink | 依診斷結果做模組分流 |
| KairosLink | K-Core / Kairos.Site / BizMap | 服務官網導流至生態圈解法 |
| QuickNotifys | Kairos.Site / BizMap / MyCal / K-Core | 從評論管理延伸到其他補強模組 |
| MyCal | Kairos.Site / BizMap / 秒傳名片 | 預約承接後回流品牌與分享節點 |
| 秒傳名片 | Kairos.Site / MyCal / 社群 / LINE | 快速分享與聯絡交換 |

## 9. 資料原則
### 主資料原則
Kairos.Site 為主要商家資料入口，其他節點原則上不重複維護主資料，只做展示、衍生、導流或狀態映射。

### 建議一致欄位
- business_id
- 商家名稱
- 類別
- 地區
- 主頁連結
- 預約連結
- 名片連結
- 模組啟用狀態

## 10. 功能範圍總覽
- Kairos.Site：建頁、後台、圖片、治理、發布
- AEO Scanner：掃描、診斷、修正建議
- BizMap：收錄、地區頁、分類頁、聚合導流
- K-Core：健檢案件、報告、報價、模組映射
- KairosLink：服務介紹與導流
- QuickNotifys：評論通知、追蹤、回覆建議、管理後台
- MyCal：預約、付款、通知、承接
- 秒傳名片：LINE 電子名片、分享與聯絡交換

## 11. 管理與治理
- Kairos.Site 可下架、刪除與停權不適頁面
- BizMap 可控制商家收錄狀態
- K-Core 可控管內部案件與報價流程
- QuickNotifys 可查看評論處理狀態
- 各節點需保留人工處理與審核能力

## 12. 成功指標
- 建頁完成率
- AEO 使用率
- BizMap 收錄率
- 健檢案件數
- 報價轉換率
- QuickNotifys 啟用率
- MyCal 串接率
- 生態圈交叉啟用率
- 跨站導流率

## 13. 開發優先順序
1. K-Core MVP
2. Kairos.Site 主站持續改版
3. AEO Scanner + BizMap 基本同步
4. QuickNotifys
5. MyCal + 秒傳名片
6. KairosLink 對接生態圈導流

## 14. MVP 定義
### 必做
1. Kairos.Site 作為主站與資料入口
2. AEO Scanner 作為附屬診斷工具
3. BizMap 作為聚合曝光層
4. K-Core 作為內部健檢與報價中樞
5. QuickNotifys PRD 與基本產品定義完成
6. 生態圈基本導流關係成立
7. 各節點關鍵欄位與商家識別邏輯建立

### 第二階段
1. 各節點更完整的狀態同步
2. 更進階的 AEO 建議
3. QuickNotifys 多店與模板能力
4. MyCal 深度串接
5. 更細緻的跨站追蹤與推薦

### 非本期範圍
- 單一超級後台整併所有產品
- 高自由度網站編輯器
- 完整 CRM 替代方案
- 各節點完全合併為一個站

## 15. 產品邊界
Kairos Engine 生態圈不是把所有東西做成一模一樣，而是讓各節點維持清楚定位，並透過導流、資料邏輯與顧問流程形成一條連續的成交路徑。

### 不做什麼
- 不以最好看的官網為核心
- 不在首版做超大型單體平台
- 不讓每個節點都自己維護完整主資料

### 要做好的事
- 讓商家更容易被看見
- 讓顧問更容易做健檢與報價
- 讓各節點形成可持續流動的產品網路
- 讓曝光、口碑、預約與分享被串起來

## 16. 結論
Kairos Engine 是一套以 Kairos.Site 為核心、由 AEO Scanner、BizMap、K-Core、KairosLink、QuickNotifys、MyCal 與秒傳名片共同組成的多節點數位成交生態圈。它的核心不是單點工具，而是讓中小企業的建頁、曝光、健檢、口碑、預約與分享形成一條可被管理、可被導流、可被持續優化的成交路徑。
