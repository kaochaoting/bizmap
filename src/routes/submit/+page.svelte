<svelte:head>
  <title>免費上架商家 — bizmap.tw</title>
  <meta name="description" content="免費將您的商家加入 bizmap.tw 台灣商家名錄，提升在地搜尋曝光度。">
</svelte:head>

<div class="max-w-2xl mx-auto px-6 py-16">
  <div class="text-center mb-12">
    <p class="text-xs font-mono tracking-widest mb-3" style="color: var(--gold)">FREE LISTING</p>
    <h1 class="text-3xl font-bold text-gray-900">免費上架您的商家</h1>
    <p class="text-gray-500 mt-3">填寫以下資料，我們將在 48 小時內完成審核並上架。</p>
  </div>

  <div class="bg-white rounded-2xl border border-gray-100 p-8">
    <div class="space-y-5">
      {#each [['商家名稱','text','您的商家全名'],['商家類別','text','例：餐飲美食、美容美髮'],['縣市','text','例：高雄市'],['地址','text','完整地址'],['聯絡電話','tel','市話或手機'],['網站或 Facebook','url','https://'],['Email','email','方便聯絡的信箱']] as [label, type, placeholder], index}
        <div>
          <label for="field-{index}" class="block text-sm font-medium text-gray-700 mb-1.5">{label}</label>
          <input id="field-{index}" {type} {placeholder}
            class="w-full px-4 py-3 rounded-xl border border-gray-200 text-sm focus:outline-none focus:border-yellow-400 transition-colors bg-gray-50"
          />
        </div>
      {/each}
      <div>
        <label for="business-description" class="block text-sm font-medium text-gray-700 mb-1.5">商家簡介</label>
        <textarea id="business-description" rows="4" placeholder="簡單描述您的商家特色、服務項目..."
          class="w-full px-4 py-3 rounded-xl border border-gray-200 text-sm focus:outline-none focus:border-yellow-400 transition-colors bg-gray-50 resize-none">
        </textarea>
      </div>
      <button class="w-full py-4 rounded-xl font-medium text-sm transition-all hover:-translate-y-0.5"
        style="background: var(--ink); color: white">
        提交上架申請
      </button>
    </div>
  </div>
</div>
