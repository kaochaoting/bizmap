<script>
  import { page } from '$app/stores';
  $: query = $page.url.searchParams.get('q') || '';
</script>

<svelte:head>
  <title>{query ? `"${query}" 搜尋結果` : '搜尋商家'} — bizmap.tw</title>
</svelte:head>

<section class="relative overflow-hidden py-20 px-6" style="background: linear-gradient(160deg, #0c0c0e 0%, #1e2330 50%, #0c0c0e 100%);">
  <div class="absolute inset-0 opacity-[0.03]"
    style="background-image: linear-gradient(rgba(200,168,75,0.5) 1px, transparent 1px), linear-gradient(90deg, rgba(200,168,75,0.5) 1px, transparent 1px); background-size: 48px 48px;">
  </div>
  <div class="relative max-w-3xl mx-auto">
    <div class="section-label section-label-gold mb-4 w-fit">SEARCH</div>
    <h1 class="text-4xl font-bold text-white tracking-tight mb-3">
      {query ? `「${query}」的搜尋結果` : '搜尋商家'}
    </h1>
    <p class="text-white/40">資料庫建置中，完整搜尋功能即將上線。</p>
  </div>
</section>

<div class="max-w-3xl mx-auto px-6 -mt-8 relative z-10 pb-24 text-center">
  <div class="glass-card-dark p-12" style="background:rgba(12,12,14,0.95);">
    <div class="text-5xl mb-6 opacity-40">🔍</div>
    <p class="text-white/50 mb-2">完整搜尋功能開發中</p>
    <p class="text-white/30 text-sm mb-8">目前資料已收錄超過 24 萬家商家，搜尋引擎正加緊優化中</p>
    <a href="/directory" class="btn-primary">
      瀏覽商家名錄
      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8l4 4m0 0l-4 4m4-4H3"/>
      </svg>
    </a>
  </div>
</div>
