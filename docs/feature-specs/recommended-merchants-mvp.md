# BizMap 推薦商家區塊 MVP 規格

## 目的
在商家詳情頁加入「推薦商家」區塊，先用最小成本驗證：
1. 使用者是否會繼續點擊其他商家
2. 哪種排序規則較能提升導流
3. 是否能為後續廣告位、精選曝光、跨店導流建立基礎

---

## 一句話定義
在每個商家頁底部顯示 3 筆推薦商家卡片，依簡單規則排序，並記錄曝光、點擊與跳轉行為。

---

## MVP 範圍
### 要做
- 在商家詳情頁新增「推薦商家」區塊
- 預設顯示 3 筆推薦商家
- 建立一版可落地的排序規則
- 記錄 impression / click / outbound click 事件
- 提供未來接廣告位與人工置頂的擴充欄位

### 先不做
- 不做複雜推薦演算法
- 不做個人化推薦
- 不做 A/B testing 後台
- 不做商家自助購買推薦位
- 不做推薦理由文案生成

---

## 使用者故事
### 訪客
- 當我進入某商家頁時，我可以看到其他可能有興趣的店家
- 當我對目前店家不完全有興趣時，我可以快速切到同類商家

### 平台管理者
- 我希望先用簡單規則測試推薦區塊是否能提升站內導流
- 我希望未來能把推薦區塊延伸成精選曝光或廣告位

---

## 版位位置
建議放在商家詳情頁的下半部，優先順序如下：
1. 商家基本資訊
2. 圖片 / 服務 / 聯絡方式
3. 地圖 / 外部連結
4. 推薦商家區塊

區塊標題建議：
- 你可能也會想看
- 附近同類店家
- 更多相關商家

MVP 建議先固定使用：**你可能也會想看**

---

## 推薦資料規則（MVP v1）
### 過濾條件
從資料集中篩選符合以下條件的商家：
- 不可為目前商家自己
- 必須為已發布 / 可見商家
- 優先同 category
- 若同 category 不足 3 筆，再補同 region 商家
- 若仍不足 3 筆，再補其他已發布商家

### 排序規則
依以下優先級排序：
1. `is_featured` 為 true 者優先
2. 與目前商家 `category` 相同者優先
3. 與目前商家 `region` 相同者優先
4. `updated_at` 較新者優先
5. `business_name` 作為最後穩定排序

### 顯示數量
- 固定 3 筆

---

## 建議資料欄位
若目前尚未存在，可先在型別或 mock data 補以下欄位：

```ts
interface Business {
  business_id: string;
  business_name: string;
  slug: string;
  category?: string;
  region?: string;
  cover_image_url?: string;
  short_description?: string;
  is_published?: boolean;
  is_featured?: boolean;
  updated_at?: string;
}
```

---

## UI 規格
### 卡片內容
每張推薦卡至少包含：
- 封面圖（若無則用 placeholder）
- 商家名稱
- 類別
- 地區
- 簡短描述（最多 2 行，可截斷）
- CTA：查看商家

### 桌機
- 3 欄 grid

### 手機
- 1 欄或橫向滑動卡片
- 若開發成本低，優先採 1 欄堆疊

### 樣式方向
- 保持現有 Tailwind 風格
- 視覺上需與主內容有明顯區隔
- hover 時卡片要有輕微陰影或位移回饋

---

## 事件追蹤規格
MVP 先做最基本事件埋點。

### 事件 1：推薦區塊曝光
事件名：`recommended_merchants_impression`

建議 payload：
```json
{
  "source_business_id": "當前商家ID",
  "recommended_business_ids": ["id1", "id2", "id3"],
  "page_type": "business_detail"
}
```

### 事件 2：推薦卡片點擊
事件名：`recommended_merchants_click`

建議 payload：
```json
{
  "source_business_id": "當前商家ID",
  "target_business_id": "被點擊商家ID",
  "position": 1,
  "page_type": "business_detail"
}
```

### 事件 3：點擊外部連結（若推薦頁後續有出站）
事件名：`recommended_merchants_outbound_click`

---

## 技術拆解建議
### 1. 建立純函式
新增：
- `src/lib/utils/getRecommendedBusinesses.ts`

函式責任：
- 接收 current business 與全量 businesses
- 回傳排序後前 3 筆結果

### 2. 建立元件
新增：
- `src/lib/components/business/RecommendedBusinesses.svelte`

元件 props 建議：
```ts
currentBusiness: Business;
allBusinesses: Business[];
recommendedBusinesses?: Business[];
```

### 3. 商家詳情頁串接
在商家詳情頁載入推薦資料並渲染元件

可能位置：
- `src/routes/.../[slug]/+page.svelte`
- 或對應商家詳情頁檔案

### 4. 埋點封裝
若專案尚未有 analytics helper，可先新增：
- `src/lib/utils/analytics.ts`

至少提供：
- `trackEvent(name, payload)`

若目前沒有正式分析工具，可先：
- `console.info` 保留介面
- 或預留呼叫 Cloudflare / GA4 的接口

---

## 驗收標準
### 功能驗收
- 商家頁底部可看到推薦商家區塊
- 每頁固定顯示 3 筆推薦卡
- 不會推薦到自己
- 同類別商家優先
- 類別不足時會回補其他店家
- 點擊卡片可進入對應商家頁

### 技術驗收
- 推薦邏輯集中在純函式，不要寫死在 Svelte 模板內
- 元件與資料邏輯分離
- TypeScript 型別不報錯
- 手機與桌機版面都可用

### 追蹤驗收
- 區塊顯示時可觸發 impression
- 點擊推薦卡時可觸發 click

---

## 後續擴充方向
- 加入人工置頂推薦位
- 加入付費精選商家位
- 加入「同區域熱門店家」切換邏輯
- 加入 A/B test：標題文案、排序策略、卡片樣式
- 加入 AI / 規則混合推薦

---

## 給 Codex 的直接執行提示詞
```text
你現在要為 `kaochaoting/bizmap` 專案實作一個 MVP 功能：在商家詳情頁加入「推薦商家」區塊。

【目標】
在每個商家頁底部顯示 3 筆推薦商家卡片，並以簡單規則排序，同時加入最基本的曝光與點擊事件埋點。

【技術背景】
- 專案為 SvelteKit + Tailwind CSS
- 部署環境為 Cloudflare Pages
- 你需要先閱讀現有商家詳情頁結構、商家資料型別與資料來源
- 請優先沿用現有元件與樣式習慣，不要大幅重構

【實作要求】
1. 找出商家詳情頁檔案與商家資料來源
2. 新增純函式 `src/lib/utils/getRecommendedBusinesses.ts`
3. 純函式邏輯如下：
   - 排除當前商家自己
   - 只取已發布商家
   - 同 category 優先
   - category 不足 3 筆時補同 region
   - 仍不足再補其他已發布商家
   - 排序優先級：`is_featured` > 同 category > 同 region > `updated_at` 新到舊 > `business_name`
   - 最終回傳 3 筆
4. 新增元件 `src/lib/components/business/RecommendedBusinesses.svelte`
5. 元件需顯示：
   - 封面圖（無圖時 placeholder）
   - 商家名稱
   - 類別
   - 地區
   - 簡短描述（2 行截斷）
   - CTA 按鈕或連結：查看商家
6. 將元件接到商家詳情頁底部
7. 版面要求：
   - 桌機 3 欄 grid
   - 手機 1 欄堆疊
   - 使用 Tailwind，風格與現有頁面一致
8. 新增基本埋點工具；若專案沒有 analytics 系統，先建立 `src/lib/utils/analytics.ts`
9. 追蹤事件至少包含：
   - `recommended_merchants_impression`
   - `recommended_merchants_click`
10. impression 事件在區塊首次出現時觸發一次；click 事件在點擊推薦卡時觸發
11. 型別要補齊；若既有 `Business` 型別沒有需要欄位，請以最小變更方式擴充
12. 避免把推薦邏輯直接寫在 Svelte 模板內
13. 完成後請同步：
   - 說明你修改了哪些檔案
   - 說明推薦規則
   - 說明如何驗證功能與事件埋點

【交付格式】
- 直接修改專案檔案
- 若缺少必要資料或欄位，請做合理最小假設並在最後列出
- 最後輸出：變更摘要 + 測試方式 + 後續可擴充建議
```

---

## 建議 commit message
```text
feat: add recommended merchants section on business detail pages
```

## 建議 PR 標題
```text
feat(bizmap): add recommended merchants MVP on business detail page
```
