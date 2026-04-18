<script>
  import { onMount } from 'svelte';

  const categories = [
    { icon: '🍜', name: '餐飲美食', count: '2,840+', slug: 'food' },
    { icon: '💆', name: '美容美髮', count: '1,560+', slug: 'beauty' },
    { icon: '🏋️', name: '健身運動', count: '890+', slug: 'fitness' },
    { icon: '🏥', name: '醫療健康', count: '1,230+', slug: 'medical' },
    { icon: '🛠️', name: '居家服務', count: '720+', slug: 'home' },
    { icon: '📚', name: '教育補習', count: '960+', slug: 'education' },
    { icon: '💼', name: '商業服務', count: '1,100+', slug: 'business' },
    { icon: '🛍️', name: '零售購物', count: '2,200+', slug: 'retail' },
  ];

  const cities = ['台北', '新北', '桃園', '台中', '台南', '高雄', '新竹', '嘉義'];

  let searchQuery = '';
  let visible = false;
  onMount(() => { setTimeout(() => visible = true, 50); });
</script>

<svelte:head>
  <title>bizmap.tw — 台灣商家名錄，找對的在地好店</title>
  <meta name="description" content="台灣最完整的在地商家名錄，收錄餐飲、美容、醫療、教育等各類商家，幫助您快速找到附近優質店家。">
  <script type="application/ld+json">
    {
      "@context": "https://schema.org",
      "@type": "WebSite",
      "name": "bizmap.tw",
      "url": "https://bizmap.tw",
      "description": "台灣商家名錄平台",
      "potentialAction": {
        "@type": "SearchAction",
        "target": "https://bizmap.tw/search?q={search_term_string}",
        "query-input": "required name=search_term_string"
      }
    }
  </script>
</svelte:head>

<!-- HERO -->
<section class="relative overflow-hidden py-24 px-6" style="background: linear-gradient(135deg, #0c0c0e 0%, #1e2330 100%)">
  <div class="absolute inset-0 opacity-5"
    style="background-image: linear-gradient(rgba(200,168,75,0.4) 1px, transparent 1px), linear-gradient(90deg, rgba(200,168,75,0.4) 1px, transparent 1px); background-size: 48px 48px;">
  </div>
  <div
    class="relative max-w-4xl mx-auto text-center"
    style:opacity={visible ? 1 : 0}
    style:transform={visible ? 'translateY(0)' : 'translateY(20px)'}
    style:transition="all 0.6s ease"
  >
    <div class="inline-flex items-center gap-2 px-4 py-1.5 rounded-full text-xs font-mono mb-8"
      style="background: rgba(200,168,75,0.15); border: 1px solid rgba(200,168,75,0.3); color: #c8a84b;">
      <span class="w-1.5 h-1.5 rounded-full bg-yellow-400 animate-pulse"></span>
      台灣在地商家名錄平台
    </div>
    <h1 class="text-4xl md:text-6xl font-bold text-white mb-6 leading-tight">
      找到<span style="color: #c8a84b">對的</span>在地好店<br>
      <span class="text-2xl md:text-3xl font-light text-gray-400">快速、精準、值得信賴</span>
    </h1>
    <p class="text-gray-400 text-lg mb-10 max-w-xl mx-auto">
      收錄台灣 12,000+ 家經過驗證的在地商家，每筆資料均含完整聯絡資訊與 Google 地圖整合。
    </p>

    <!-- Search bar -->
    <div class="flex gap-3 max-w-xl mx-auto">
      <input
        bind:value={searchQuery}
        type="text"
        placeholder="搜尋商家名稱、類別或關鍵字..."
        class="flex-1 px-5 py-4 rounded-xl text-sm bg-white/10 border border-white/20 text-white placeholder-gray-500 focus:outline-none focus:border-yellow-400 transition-colors"
      />
      <a href="/search?q={searchQuery}" class="px-6 py-4 rounded-xl font-medium text-sm transition-all hover:-translate-y-0.5 whitespace-nowrap" style="background: #c8a84b; color: #0c0c0e;">
        搜尋
      </a>
    </div>

    <!-- City quick links -->
    <div class="flex flex-wrap justify-center gap-2 mt-6">
      {#each cities as city}
        <a href="/directory?city={city}" class="px-3 py-1.5 rounded-full text-xs text-gray-400 border border-white/10 hover:border-yellow-400/50 hover:text-yellow-400 transition-all">
          {city}
        </a>
      {/each}
    </div>
  </div>
</section>

<!-- STATS -->
<section class="py-12 bg-white border-b border-gray-100">
  <div class="max-w-4xl mx-auto px-6 grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
    {#each [['12,000+','收錄商家'],['22','縣市覆蓋'],['8','主要類別'],['100%','免費查詢']] as [num, label]}
      <div>
        <div class="text-3xl font-bold" style="color: var(--ink)">{num}</div>
        <div class="text-sm text-gray-500 mt-1">{label}</div>
      </div>
    {/each}
  </div>
</section>

<!-- CATEGORIES -->
<section class="py-20 px-6">
  <div class="max-w-6xl mx-auto">
    <div class="text-center mb-12">
      <p class="text-xs font-mono tracking-widest mb-3" style="color: var(--gold)">BROWSE BY CATEGORY</p>
      <h2 class="text-3xl font-bold text-gray-900">依類別瀏覽商家</h2>
    </div>
    <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
      {#each categories as cat}
        <a href="/directory?category={cat.slug}"
          class="group p-6 rounded-2xl border border-gray-100 bg-white hover:border-yellow-300 hover:-translate-y-1 transition-all text-center">
          <div class="text-4xl mb-3">{cat.icon}</div>
          <div class="font-medium text-gray-900 mb-1">{cat.name}</div>
          <div class="text-xs text-gray-400">{cat.count} 家商家</div>
        </a>
      {/each}
    </div>
  </div>
</section>

<!-- CTA: Free listing -->
<section class="py-20 px-6" style="background: var(--ink)">
  <div class="max-w-2xl mx-auto text-center">
    <p class="text-xs font-mono tracking-widest mb-4" style="color: var(--gold)">FOR BUSINESS OWNERS</p>
    <h2 class="text-3xl font-bold text-white mb-4">您是商家嗎？</h2>
    <p class="text-gray-400 mb-8">免費將您的商家加入 bizmap.tw 名錄，提升 Google 搜尋與 AI 摘要的在地曝光度。</p>
    <a href="/submit"
      class="inline-flex items-center gap-2 px-8 py-4 rounded-xl font-medium transition-all hover:-translate-y-1"
      style="background: var(--gold); color: var(--ink)">
      免費上架商家 →
    </a>
  </div>
</section>
