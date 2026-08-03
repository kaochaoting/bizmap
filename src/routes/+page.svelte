<script>
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import indexData from '../../static/data/index.json';

  const categoryIcons = {
    '餐飲美食': '🍜', '美容美髮': '💆', '健身運動': '🏋️',
    '醫療健康': '🏥', '居家服務': '🛠️', '教育補習': '📚',
    '商業服務': '💼', '零售購物': '🛍️', '交通運輸': '⛽',
    '工業製品': '🏭',
  };
  const stats = {
    total: indexData.total,
    cities: Object.keys(indexData.city_counts).length,
    categories: Object.keys(indexData.categories).length,
  };
  const updatedAt = new Intl.DateTimeFormat('zh-TW', {
    year: 'numeric', month: '2-digit', day: '2-digit'
  }).format(new Date(indexData.generated_at));
  const featuredStats = [
    { value: stats.total.toLocaleString(), label: '收錄商家', suffix: '家' },
    { value: String(stats.cities), label: '縣市覆蓋', suffix: '縣市' },
    { value: String(stats.categories), label: '主要類別', suffix: '類別' },
    { value: '100%', label: '免費查詢', suffix: '' },
  ];
  const categories = Object.entries(indexData.category_counts)
    .sort((a, b) => b[1] - a[1])
    .map(([slug, count]) => ({
      icon: categoryIcons[indexData.categories[slug]] || '🏪',
      name: indexData.categories[slug] || slug,
      count: count.toLocaleString(),
      slug,
    }));
  const cityList = Object.entries(indexData.city_counts)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 12)
    .map(([city]) => city);
  let searchQuery = '';
  let searchCategory = '';
  let visible = false;

  const bentoFeatures = [
    { icon: '🔍', title: '精準搜尋', desc: '依類別/縣市快速過濾', colspan: 1, rowspan: 1 },
    { icon: '🗺️', title: '全台覆蓋', desc: '22 縣市商家資訊', colspan: 1, rowspan: 1 },
    { icon: '✅', title: '官方資料源', desc: '政府開放資料驗證', colspan: 1, rowspan: 1 },
    { icon: '📊', title: '定期更新', desc: `資料更新：${updatedAt}`, colspan: 1, rowspan: 1 },
  ];

  function getSpans(i) {
    if (i === 0) return { cols: 2, rows: 1 };
    if (i === categories.length - 1 && categories.length % 2 !== 0) return { cols: 2, rows: 1 };
    return { cols: 1, rows: 1 };
  }

  onMount(() => {
    setTimeout(() => visible = true, 50);
  });

  function searchDirectory() {
    if (!searchCategory) return;
    const params = new URLSearchParams({ category: searchCategory });
    if (searchQuery.trim()) params.set('q', searchQuery.trim());
    goto(`/directory?${params}`);
  }
</script>

<svelte:head>
  <title>bizmap.tw — 台灣商家名錄，找對的在地好店</title>
  <meta name="description" content="台灣在地商家名錄，收錄全台經政府開放資料驗證的商家，涵蓋餐飲、美容、醫療、教育等各類服務。">
  <script type="application/ld+json">
    { "@context": "https://schema.org", "@type": "WebSite",
      "name": "bizmap.tw", "url": "https://bizmap.tw",
      "description": "台灣商家名錄平台",
      "potentialAction": { "@type": "SearchAction",
        "target": "https://bizmap.tw/directory?q={search_term_string}",
        "query-input": "required name=search_term_string" } }
  </script>
</svelte:head>

<!-- ===== HERO SECTION ===== -->
<section class="relative overflow-hidden min-h-[85vh] flex items-center"
  style="background: linear-gradient(160deg, #0c0c0e 0%, #1e2330 40%, #0c0c0e 100%)">

  <!-- Grid pattern overlay -->
  <div class="absolute inset-0 opacity-[0.03]"
    style="background-image: linear-gradient(rgba(200,168,75,0.5) 1px, transparent 1px), linear-gradient(90deg, rgba(200,168,75,0.5) 1px, transparent 1px); background-size: 48px 48px;">
  </div>

  <!-- Radial glow -->
  <div class="absolute top-1/4 left-1/2 -translate-x-1/2 w-[800px] h-[800px] rounded-full opacity-[0.08]"
    style="background: radial-gradient(circle, rgba(200,168,75,0.6) 0%, transparent 70%);">
  </div>

  <div class="relative w-full max-w-6xl mx-auto px-6 py-24">
    <div
      class="max-w-4xl mx-auto text-center mb-16"
      class:opacity-100={visible} class:opacity-0={!visible}
      class:translate-y-0={visible} class:translate-y-8={!visible}
      style="transition: all 0.7s cubic-bezier(0.16, 1, 0.3, 1);"
    >
      <div class="section-label section-label-gold mb-8 mx-auto w-fit">
        <span class="w-1.5 h-1.5 rounded-full bg-gold animate-pulse-slow"></span>
        台灣在地商家名錄平台
      </div>

      <h1 class="text-5xl md:text-7xl font-bold text-white mb-6 leading-[1.1] tracking-tight text-balance">
        找到<span style="color:var(--gold)">對的</span>在地好店
      </h1>
      <p class="text-lg md:text-xl text-white/40 font-light max-w-xl mx-auto mb-12 leading-relaxed">
        收錄全台 {stats.total.toLocaleString()} 家具可追溯來源的商家資料
        <br>
        <span class="text-white/30">快速、精準、值得信賴</span>
      </p>

      <!-- Search bar -->
      <form class="grid sm:grid-cols-[160px_1fr_auto] gap-3 max-w-3xl mx-auto" on:submit|preventDefault={searchDirectory}>
        <select bind:value={searchCategory} required aria-label="商家類別" class="px-4 py-4 rounded-card text-sm bg-white/5 border border-white/10 text-white focus:outline-none focus:border-gold/50">
          <option value="" disabled>先選類別</option>
          {#each categories as category}<option value={category.slug}>{category.name}</option>{/each}
        </select>
        <div class="relative">
          <svg class="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-white/30" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-4.35-4.35M11 19a8 8 0 100-16 8 8 0 000 16z"/>
          </svg>
          <input
            bind:value={searchQuery}
            type="text"
            placeholder="搜尋商家名稱、類別或關鍵字..."
            class="w-full pl-11 pr-5 py-4 rounded-card text-sm bg-white/5 border border-white/10 text-white placeholder-white/25 focus:outline-none focus:border-gold/50 focus:bg-white/[0.07] transition-all"
          />
        </div>
        <button type="submit" class="btn-primary px-7 py-4 justify-center">
          搜尋
        </button>
      </form>
      <p class="text-xs text-white/25 mt-3">為避免一次下載大量資料，請先選擇類別再搜尋。</p>

      <!-- Quick city links -->
      {#if cityList.length}
        <div class="flex flex-wrap justify-center gap-2 mt-8">
          {#each cityList as city}
            <a href="/directory?city={city}"
              class="px-3 py-1.5 rounded-pill text-xs text-white/30 border border-white/10 hover:border-gold/40 hover:text-gold/80 transition-all">
              {city}
            </a>
          {/each}
        </div>
      {/if}
    </div>

    <!-- Bento feature grid -->
    <div class="grid grid-cols-2 md:grid-cols-4 gap-4 max-w-4xl mx-auto">
      {#each bentoFeatures as feat}
        <div class="glass-card-dark p-6 text-center glass-card-dark-hover">
          <div class="text-2xl mb-3">{feat.icon}</div>
          <div class="font-medium text-white text-sm mb-1">{feat.title}</div>
          <div class="text-xs text-white/30">{feat.desc}</div>
        </div>
      {/each}
    </div>
  </div>
</section>

<style>
  select option { color: #111; }
</style>

<!-- ===== STATS SECTION ===== -->
<section class="relative -mt-12 z-10">
  <div class="max-w-4xl mx-auto px-6">
    <div class="glass-card grid grid-cols-2 md:grid-cols-4 gap-1 p-4" style="background:rgba(12,12,14,0.9);">
      {#each featuredStats as stat}
        <div class="text-center py-4">
          <div class="flex items-baseline justify-center gap-0.5">
            <span class="text-3xl font-bold text-gold">{stat.value}</span>
            {#if stat.suffix}
              <span class="text-sm text-white/40">{stat.suffix}</span>
            {/if}
          </div>
          <div class="text-xs text-white/30 mt-1">{stat.label}</div>
        </div>
      {/each}
    </div>
  </div>
</section>

<!-- ===== BENTO CATEGORIES SECTION ===== -->
<section class="py-28 px-6 bg-gradient-to-b from-ink via-ink to-slate/50">
  <div class="max-w-6xl mx-auto">
    <div class="text-center mb-16">
      <div class="section-label section-label-gold mx-auto mb-4 w-fit">BROWSE BY CATEGORY</div>
      <h2 class="text-3xl md:text-4xl font-bold text-white tracking-tight mb-3">依類別瀏覽商家</h2>
      <p class="text-white/30 text-sm">從全台 {stats.total.toLocaleString()} 家商家中快速找到你需要的服務</p>
    </div>

    <div class="grid grid-cols-2 md:grid-cols-4 gap-5">
      {#each categories as cat, i}
        <a href="/directory?category={cat.slug}"
          class="glass-card-dark p-7 glass-card-dark-hover flex flex-col items-center text-center"
          class:md:col-span-2={getSpans(i).cols === 2}
        >
          <div class="text-4xl mb-4">{cat.icon}</div>
          <div class="font-semibold text-white mb-1">{cat.name}</div>
          <div class="text-xs text-white/30 font-mono">{cat.count} 家商家</div>
        </a>
      {/each}
    </div>
  </div>
</section>

<!-- ===== CTA SECTION ===== -->
<section class="py-28 px-6 relative overflow-hidden"
  style="background: linear-gradient(135deg, #0c0c0e 0%, #1e2330 100%)">
  <div class="absolute inset-0 opacity-[0.04]"
    style="background-image: linear-gradient(rgba(200,168,75,0.5) 1px, transparent 1px), linear-gradient(90deg, rgba(200,168,75,0.5) 1px, transparent 1px); background-size: 36px 36px;">
  </div>
  <div class="absolute top-1/2 right-0 w-[400px] h-[400px] rounded-full opacity-[0.06]"
    style="background: radial-gradient(circle, rgba(200,168,75,0.8) 0%, transparent 70%);">
  </div>

  <div class="relative max-w-2xl mx-auto text-center">
    <div class="section-label section-label-gold mx-auto mb-6 w-fit">FOR BUSINESS OWNERS</div>
    <h2 class="text-3xl md:text-4xl font-bold text-white mb-4 tracking-tight">您是商家嗎？</h2>
    <p class="text-white/40 mb-10 max-w-lg mx-auto leading-relaxed">
      免費將您的商家加入 bizmap.tw 名錄，提升 <span class="text-white/70">Google 搜尋</span>與 <span class="text-white/70">AI 摘要</span>的在地曝光度。
    </p>
    <a href="/submit" class="btn-primary px-10 py-4 text-base">
      免費上架商家
      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8l4 4m0 0l-4 4m4-4H3"/>
      </svg>
    </a>
  </div>
</section>
