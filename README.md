# bizmap.tw

台灣商家名錄平台 — Built with SvelteKit + Tailwind CSS + Cloudflare Pages

## 技術棧
- SvelteKit 2.x
- Tailwind CSS 3.x
- MDSvex
- Cloudflare Pages（部署）

## 開發
```bash
npm install
npm run dev
```

執行 Twinkle 資料集搜尋腳本前，請透過環境變數提供金鑰：

```powershell
$env:TWINKLE_API_KEY = '<your-key>'
python scripts/search_datasets.py
```

如需使用其他 MCP 端點，可設定 `TWINKLE_MCP_URL`。請勿將金鑰寫入程式碼或提交至 Git。

## 部署
推送至 GitHub main branch，Cloudflare Pages 自動建置。
