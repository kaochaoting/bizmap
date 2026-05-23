<script>
  import { onMount } from 'svelte';
  import { page } from '$app/stores';

  let city = '';
  let indexData = null;
  let businesses = [];
  let loading = true;
  let selectedCategory = '';
  let searchQuery = '';
  let currentPage = 1;
  const PER_PAGE = 30;

  const categoryNames = {
    food: '餐飲美食', beauty: '美容美髮', fitness: '健身運動',
    medical: '醫療健康', home: '居家服務', education: '教育補習',
    business: '商業服務', retail: '零售購物', transport: '交通運輸',
    industrial: '工業製品',
  };
  const categoryIcons = {
    food: '🍜', beauty: '💆', fitness: '🏋️',
    medical: '🏥', home: '🛠️', education: '📚',
    business: '💼', retail: '🛍️', transport: '⛽',
    industrial: '🏭',
  };
  const categoryColor = {
    food: 'bg-orange-500/20 text-orange-300 border-orange-500/30',
    beauty: 'bg-pink-500/20 text-pink-300 border-pink-500/30',
    fitness: 'bg-red-500/20 text-red-300 border-red-500/30',
    medical: 'bg-green-500/20 text-green-300 border-green-500/30',
    home: 'bg-amber-500/20 text-amber-300 border-amber-500/30',
    education: 'bg-purple-500/20 text-purple-300 border-purple-500/30',
    business: 'bg-blue-500/20 text-blue-300 border-blue-500/30',
    retail: 'bg-cyan-500/20 text-cyan-300 border-cyan-500/30',
    transport: 'bg-slate-500/20 text-slate-300 border-slate-500/30',
    industrial: 'bg-stone-500/20 text-stone-300 border-stone-500/30',
  };

  $: totalFiltered = businesses.length;
  $: totalPages = Math.ceil(totalFiltered / PER_PAGE);
  $: paginated = businesses.slice((currentPage - 1) * PER_PAGE, currentPage * PER_PAGE);

  onMount(async () => {
    city = decodeURIComponent($page.params.id || '');
    const params = $page.url.searchParams;
    if (params.get('category')) selectedCategory = params.get('category');
    if (params.get('q')) searchQuery = params.get('q');
    if (params.get('page')) currentPage = parseInt(params.get('page')) || 1;

    try {
      const res = await fetch('/data/index.json');
      indexData = await res.json();
      await loadCategory(); // always load (city-filtered or all)
    } catch (e) {
      console.error('Failed to load index:', e);
    } finally {
      loading = false;
    }
  });

  // Reactive: reload when indexData arrives OR selectedCategory changes
  $: if (indexData) {
    loadCategory();
  }

  // Normalize city: taipei → 台北市, newtaipei → 新北市 etc.
  const CITY_MAP = {
    taipei: '台北市', newtaipei: '新北市', taoyuan: '桃園市',
    taichung: '台中市', tainan: '台南市', kaohsiung: '高雄市',
    yilan: '宜蘭縣', changhua: '彰化縣', yunlin: '雲林縣',
    chiayi: '嘉義市', hsinchu: '新竹市', miaoli: '苗栗縣',
    nantou: '南投縣', keelung: '基隆市', hualien: '花蓮縣',
    pingtung: '屏東縣', taitung: '台東縣', penghu: '澎湖縣',
    kinmen: '金門縣', lienchiang: '連江縣',
  };
  $: normalizedCity = CITY_MAP[city.toLowerCase()] || (city.includes('台') || city.includes('臺') ? city : null);

  async function loadCategory() {
    loading = true;
    try {
      const catFiles = indexData?.files?.[selectedCategory];
      if (!catFiles?.length) { loading = false; return; }

      let allBiz = [];
      for (const fileMeta of catFiles) {
        try {
          const r = await fetch(`/data/${fileMeta.file}`);
          if (!r.ok) continue;
          const d = await r.json();
          if (d.files && Array.isArray(d.files) && !d.businesses?.length) {
            const baseDir = fileMeta.file.replace('.json', '');
            for (const subFile of d.files) {
              const sr = await fetch(`/data/${baseDir}/${subFile}`);
              if (!sr.ok) continue;
              const sd = await sr.json();
              allBiz.push(...(sd.businesses || []));
            }
          } else if (d.businesses?.length) {
            allBiz.push(...d.businesses);
          }
        } catch (e) { /* skip */ }
      }

      // Filter: city + category + search
      // When city param is set: include businesses that have null city (assign city param)
      // When city param is empty: show all
      const cityParam = normalizedCity || city;
      businesses = allBiz
        .filter(b => {
          // City match: if city param set, include null-city rows (they get city assigned below)
          // if city param empty, match all
          const cityMatch = !cityParam
            ? true  // no city filter → show all
            : !b.city  // has cityParam but business has no city → include it (assign below)
              ? true   // null city businesses are shown when a city filter is active
              : (
                b.city === normalizedCity || b.city === city ||
                b.city.toLowerCase() === city.toLowerCase() ||
                b.city.includes(normalizedCity) || normalizedCity.includes(b.city) ||
                (b.city.replace('台','臺') === normalizedCity.replace('台','臺')) ||
                (normalizedCity.replace('台','臺').includes(b.city.replace('台','臺')))
              );
          const catMatch = !selectedCategory || b.category === selectedCategory || b.category === categoryNames[selectedCategory];
          const searchMatch = !searchQuery || (
            (b.business_name || '').includes(searchQuery) ||
            (b.description || '').includes(searchQuery) ||
            (b.tags || []).some(t => t.includes(searchQuery))
          );
          return cityMatch && catMatch && searchMatch;
        })
        .map(b => ({ ...b, city: b.city || normalizedCity || city }));
    } catch (e) {
      console.error(e);
    } finally {
      loading = false;
    }
  }

  function handleCategoryClick(slug) {
    selectedCategory = slug;
    currentPage = 1;
    pushUrl();
    loadCategory();
  }

  function handleCityClick(c) {
    city = c;
    currentPage = 1;
    pushUrl();
    loadCategory();
  }

  function goPage(n) {
    currentPage = n;
    pushUrl();
    if (typeof window !== 'undefined') window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  function pushUrl() {
    if (typeof window === 'undefined') return;
    const params = new URLSearchParams();
    if (selectedCategory) params.set('category', selectedCategory);
    if (searchQuery) params.set('q', searchQuery);
    if (currentPage > 1) params.set('page', currentPage);
    const qs = params.toString();
    history.pushState({}, '', qs ? `?${qs}` : window.location.pathname);
  }

  $: categoryList = indexData ? Object.entries(indexData.categories).map(([slug, name]) => ({
    slug, name,
    icon: categoryIcons[slug] || '🏪',
    count: indexData.category_counts[slug] || 0,
  })).sort((a, b) => b.count - a.count) : [];

  $: cityBreakdown = (() => {
    const counts = {};
    for (const b of businesses) {
      if (b.city) counts[b.city] = (counts[b.city] || 0) + 1;
    }
    return Object.entries(counts).sort((a, b) => b[1] - a[1]);
  })();
</script>

<svelte:head>
  <title>{city || '城市'} 商家名錄 — bizmap.tw</title>
  <meta name="description" content="瀏覽 {city} 本地商家，涵蓋餐飲、零售、服務等各類店家。" />
</svelte:head>

<!-- Page Header -->
<section class="relative overflow-hidden py-14 px-6"
  style="background: linear-gradient(160deg, #0c0c0e 0%, #1e2330 50%, #0c0c0e 100%);">
  <div class="absolute inset-0 opacity-[0.03]"
    style="background-image: linear-gradient(rgba(200,168,75,0.5) 1px, transparent 1px), linear-gradient(90deg, rgba(200,168,75,0.5) 1px, transparent 1px); background-size: 48px 48px;">
  </div>
  <div class="relative max-w-5xl mx-auto">
    <div class="section-label section-label-gold mb-3 w-fit">LOCAL</div>
    <h1 class="text-3xl font-bold text-white tracking-tight mb-2">
      {city ? `📍 ${city}` : '城市名錄'}
    </h1>
    <p class="text-white/30 text-sm">
      {#if indexData && city}
        {city} 收錄 <strong class="text-white/50">{businesses.length.toLocaleString()}</strong> 家商家
      {/if}
    </p>
  </div>
</section>

<div class="max-w-5xl mx-auto px-6 -mt-6 relative z-10">

  <!-- Search + Filters -->
  <div class="glass-card p-4 mb-5" style="background:rgba(12,12,14,0.95); border-color:rgba(255,255,255,0.08);">
    <div class="flex flex-wrap items-center gap-3">
      <!-- Back -->
      <a href="/directory" class="flex items-center gap-1.5 text-sm text-white/40 hover:text-gold transition-colors shrink-0">
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/></svg>
        返回全部
      </a>
      <span class="text-white/10">|</span>

      <!-- Search -->
      <div class="flex-1 min-w-[200px]">
        <div class="relative">
          <svg class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-white/20" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-4.35-4.35M11 19a8 8 0 100-16 8 8 0 000 16z"/>
          </svg>
          <input
            bind:value={searchQuery}
            on:input={() => { currentPage = 1; loadCategory(); }}
            type="text"
            placeholder="搜尋 {city} 商家名稱、標籤..."
            class="w-full pl-10 pr-4 py-2.5 rounded-lg text-sm bg-white/5 border border-white/10 text-white placeholder-white/20 focus:outline-none focus:border-gold/40 transition-all"
          />
        </div>
      </div>

      <!-- Category pills -->
      <div class="flex flex-wrap gap-1.5">
        <button
          on:click={() => handleCategoryClick('')}
          class="px-3 py-1.5 rounded-lg text-xs font-semibold border transition-all shrink-0 whitespace-nowrap
            {!selectedCategory ? 'bg-gold/20 border-gold/50 text-gold shadow-[0_0_8px_rgba(200,168,75,0.3)]' : 'bg-white/5 border-white/10 text-white/50 hover:border-white/20 hover:text-white/70'}"
        >
          📋 全部
        </button>
        {#each categoryList as cat}
          <button
            on:click={() => handleCategoryClick(cat.slug)}
            class="px-3 py-1.5 rounded-lg text-xs font-semibold border transition-all shrink-0 whitespace-nowrap
              {selectedCategory === cat.slug ? 'bg-gold/20 border-gold/50 text-gold shadow-[0_0_8px_rgba(200,168,75,0.3)]' : 'bg-white/5 border-white/10 text-white/50 hover:border-white/20 hover:text-white/70'}"
            title="{cat.count.toLocaleString()} 家"
          >
            {cat.icon} {cat.name}
          </button>
        {/each}
      </div>
    </div>
  </div>

  <!-- Results -->
  {#if loading}
    <div class="text-center py-20">
      <div class="inline-flex items-center gap-3 text-white/30">
        <svg class="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
        </svg>
        載入 {city} 商家資料中...
      </div>
    </div>
  {:else if businesses.length === 0}
    <div class="text-center py-20">
      <div class="text-5xl mb-4 opacity-30">🔍</div>
      <p class="text-lg text-white/40 mb-2">此城市尚無收錄商家</p>
      <a href="/directory" class="text-sm text-gold/60 hover:text-gold transition-colors">瀏覽全部目錄 →</a>
    </div>
  {:else}
    <!-- Results count + sort -->
    <div class="flex justify-between items-center mb-4">
      <p class="text-sm text-white/30 font-mono">
        共 <span class="text-white/60">{totalFiltered.toLocaleString()}</span> 家
        {#if selectedCategory}<span class="text-gold/60"> · {categoryNames[selectedCategory]}</span>{/if}
      </p>
    </div>

    <!-- Business cards -->
    <div class="grid md:grid-cols-2 lg:grid-cols-3 gap-4 pb-16">
      {#each paginated as biz}
        <a
          href="/business/{biz.business_id}"
          class="block glass-card-dark p-5 rounded-xl border border-white/5 hover:border-white/10 transition-all duration-200 hover:-translate-y-0.5 group"
        >
          <div class="flex items-start justify-between mb-3 gap-2">
            <div class="min-w-0 flex-1">
              <div class="flex items-center gap-2 mb-2 flex-wrap">
                {#if biz.city}
                  <span class="text-[10px] px-2 py-0.5 rounded-full bg-white/5 text-white/30 border border-white/5">
                    📍 {biz.city}
                  </span>
                {/if}
                <span class="text-[10px] px-2 py-0.5 rounded-full font-mono uppercase tracking-wider"
                  style="background:rgba(200,168,75,0.12); color:var(--gold); border:1px solid rgba(200,168,75,0.2);">
                  {biz.category || (selectedCategory ? categoryNames[selectedCategory] : '')}
                </span>
              </div>
              <h3 class="font-semibold text-white text-sm group-hover:text-gold transition-colors leading-snug">
                {biz.business_name || '未命名'}
              </h3>
            </div>
          </div>

          {#if biz.description}
            <p class="text-xs text-white/30 leading-relaxed mb-3 line-clamp-2">{biz.description}</p>
          {/if}

          {#if biz.tags?.length}
            <div class="flex flex-wrap gap-1 mb-3">
              {#each biz.tags.slice(0, 3) as tag}
                <span class="text-[10px] px-2 py-0.5 rounded-full bg-white/5 text-white/25">{tag}</span>
              {/each}
            </div>
          {/if}

          <!-- Address + Phone quick access -->
          <div class="text-xs text-white/25 space-y-1 pt-2 border-t border-white/5">
            {#if biz.address}
              <div class="flex items-center gap-1">
                <span class="text-white/15">📍</span>
                <span class="truncate">{biz.address}</span>
              </div>
            {/if}
            {#if biz.phone}
              <div class="flex items-center gap-1">
                <span class="text-white/15">📞</span>
                <span>{biz.phone}</span>
              </div>
            {/if}
          </div>

          <!-- 反向鏈結提示（設為按鈕，避免巢狀<a>） -->
          <div class="mt-2 pt-2 border-t border-white/5 text-right">
            <span class="text-[9px] text-white/15">引用格式 →</span>
          </div>
        </a>
      {/each}
    </div>

    <!-- Pagination -->
    {#if totalPages > 1}
      <div class="flex justify-center items-center gap-1 pb-16">
        <button
          on:click={() => goPage(currentPage - 1)}
          disabled={currentPage === 1}
          class="px-4 py-2 rounded-lg text-sm border transition-all
            {currentPage === 1 ? 'border-white/5 text-white/20 cursor-not-allowed' : 'border-white/10 text-white/50 hover:border-white/20 hover:text-white/70'}"
        >
          上一頁
        </button>
        {#each Array.from({length: Math.min(totalPages, 7)}, (_, i) => i + 1) as p}
          <button
            on:click={() => goPage(p)}
            class="w-9 h-9 rounded-lg text-sm border transition-all
              {p === currentPage ? 'bg-gold/20 border-gold/40 text-gold' : 'border-white/10 text-white/50 hover:border-white/20 hover:text-white/70'}"
          >
            {p}
          </button>
        {/each}
        <button
          on:click={() => goPage(currentPage + 1)}
          disabled={currentPage === totalPages}
          class="px-4 py-2 rounded-lg text-sm border transition-all
            {currentPage === totalPages ? 'border-white/5 text-white/20 cursor-not-allowed' : 'border-white/10 text-white/50 hover:border-white/20 hover:text-white/70'}"
        >
          下一頁
        </button>
      </div>
    {/if}
  {/if}
</div>