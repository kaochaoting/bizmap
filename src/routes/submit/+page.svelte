<svelte:head>
  <title>免費上架商家 — bizmap.tw</title>
  <meta name="description" content="免費將您的商家加入 bizmap.tw 台灣商家名錄，提升在地搜尋曝光度。">
</svelte:head>

<section class="relative overflow-hidden py-20 px-6" style="background: linear-gradient(160deg, #0c0c0e 0%, #1e2330 50%, #0c0c0e 100%);">
  <div class="absolute inset-0 opacity-[0.03]"
    style="background-image: linear-gradient(rgba(200,168,75,0.5) 1px, transparent 1px), linear-gradient(90deg, rgba(200,168,75,0.5) 1px, transparent 1px); background-size: 48px 48px;">
  </div>
  <div class="relative max-w-3xl mx-auto text-center">
    <div class="section-label section-label-gold mx-auto mb-4 w-fit">FREE LISTING</div>
    <h1 class="text-4xl font-bold text-white tracking-tight mb-3">免費上架您的商家</h1>
    <p class="text-white/40">填寫以下資料，我們將在 48 小時內完成審核並上架。</p>
  </div>
</section>

<div class="max-w-2xl mx-auto px-6 -mt-8 relative z-10 pb-24">
  <div class="glass-card-dark p-8" style="background:rgba(12,12,14,0.95);">
    <div class="space-y-5">
      {#each [['商家名稱','text','您的商家全名'],['商家類別','text','例：餐飲美食、美容美髮'],['縣市','text','例：高雄市'],['地址','text','完整地址'],['聯絡電話','tel','市話或手機'],['網站或 Facebook','url','https://'],['Email','email','方便聯絡的信箱']] as [label, type, placeholder], index}
        <div>
          <label for="field-{index}" class="block text-sm font-medium text-white/60 mb-1.5">{label}</label>
          <input id="field-{index}" {type} {placeholder}
            class="w-full px-4 py-3 rounded-card text-sm bg-white/5 border border-white/10 text-white placeholder-white/20 focus:outline-none focus:border-gold/40 transition-all"
          />
        </div>
      {/each}
      <div>
        <label for="business-description" class="block text-sm font-medium text-white/60 mb-1.5">商家簡介</label>
        <textarea id="business-description" rows="4" placeholder="簡單描述您的商家特色、服務項目..."
          class="w-full px-4 py-3 rounded-card text-sm bg-white/5 border border-white/10 text-white placeholder-white/20 focus:outline-none focus:border-gold/40 transition-all resize-none">
        </textarea>
      </div>
      <button class="btn-primary w-full justify-center py-4">
        提交上架申請
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8l4 4m0 0l-4 4m4-4H3"/>
        </svg>
      </button>
    </div>
  </div>
</div>
