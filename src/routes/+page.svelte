<script>
  import { onMount } from 'svelte';

  const categoryMap = {
    'food': '餐飲美食', 'beauty': '美容美髮', 'fitness': '健身運動',
    'medical': '醫療健康', 'home': '居家服務', 'education': '教育補習',
    'business': '商業服務', 'retail': '零售購物', 'transport': '交通運輸',
  };
  const categoryIcons = {
    '餐飲美食': '🍜', '美容美髮': '💆', '健身運動': '🏋️',
    '醫療健康': '🏥', '居家服務': '🛠️', '教育補習': '📚',
    '商業服務': '💼', '零售購物': '🛍️', '交通運輸': '⛽',
  };
  const categorySlugs = {
    '餐飲美食': 'food', '美容美髮': 'beauty', '健身運動': 'fitness',
    '醫療健康': 'medical', '居家服務': 'home', '教育補習': 'education',
    '商業服務': 'business', '零售購物': 'retail', '交通運輸': 'transport',
  };

  let businesses = [];
  let stats = { total: 0, cities: 0, categories: 0 };
  let categories = [];
  let searchQuery = '';
  let visible = false;

  onMount(async () => {
    setTimeout(() => visible = true, 50);
    try {
      const res = await fetch('/data/businesses.json');
      const data = await res.json();
      businesses = data.businesses || [];
      
      const citySet = new Set(businesses.map(b => b.city).filter(Boolean));
      const catCounts = {};
      businesses.forEach(b => {
        if (b.category) catCounts[b.category] = (catCounts[b.category] || 0) + 1;
      });
      
      stats = {
        total: businesses.length,
        cities: citySet.size,
        categories: Object.keys(catCounts).length,
      };
      
      categories = Object.entries(catCounts)
        .sort((a, b) => b[1] - a[1])
        .map(([name, count]) => ({
          icon: categoryIcons[name] || '🏪',
          name,
          count: count.toLocaleString(),
          slug: categorySlugs[name] || name,
        }));
      
      // Add categories not yet present with 0 count
      for (const [slug, name] of Object.entries(categoryMap)) {
        if (!catCounts[name]) {
          categories.push({
            icon: categoryIcons[name] || '🏪',
            name,
            count: '0',
            slug,
          });
        }
      }
    } catch (e) {
      console.error('Failed to load businesses:', e);
    }
  });
</script>

<svelte:head>
  <title>bizmap.tw — 台灣商家名錄，找對的在地好店</title>
  <meta name="description" content="台灣在地商家名錄，收錄全台經政府開放資料驗證的商家，涵蓋餐飲、美容、醫療、教育等各類服務。">
  <script type="application/ld+json">
    { "@context": "https://schema.org", "@type": "WebSite",
      "name": "bizmap.tw", "url": "https://bizmap.tw",
      "description": "台灣商家名錄平台",
      "potentialAction": { "@type": "SearchAction",
        "target": "https://bizmap.tw/search?q={search_term_string}",
        "query-input": "required name=search_term_string" } }
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
      {stats.total > 0
        ? `收錄全台 ${stats.total.toLocaleString()} 家經政府開放資料驗證的商家，覆蓋 ${stats.cities} 縣市。`
        : '收錄全台經政府開放資料驗證的商家，資料持續擴充中。'}
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
    {#if businesses.length}
      <div class="flex flex-wrap justify-center gap-2 mt-6">
        {#each [...new Set(businesses.map(b => b.city).filter(Boolean))].slice(0, 12) as city}
          <a href="/directory?city={city}" class="px-3 py-1.5 rounded-full text-xs text-gray-400 border border-white/10 hover:border-yellow-400/50 hover:text-yellow-400 transition-all">
            {city}
          </a>
        {/each}
      </div>
    {/if}
  </div>
</section>

<!-- STATS -->
<section class="py-12 bg-white border-b border-gray-100">
  <div class="max-w-4xl mx-auto px-6 grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
    {#each [[(stats.total || 0).toLocaleString()+'家','收錄商家'],[(stats.cities || '0')+'縣市','縣市覆蓋'],[(stats.categories || '0')+'類別','主要類別'],['100%','免費查詢']] as [num, label]}
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
