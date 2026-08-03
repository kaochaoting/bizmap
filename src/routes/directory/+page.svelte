<script>
  import { onMount, tick } from 'svelte';
  import staticIndexData from '../../../static/data/index.json';

  // ─── State ──────────────────────────────────────────────────────────────────
  let allBusinesses = [];
  let businesses = [];
  let loading = false;
  let loadingCategory = false;

  const indexData = staticIndexData;

  // Filters
  let searchQuery = '';
  let selectedCity = '';
  let selectedCategory = '';
  let sortBy = 'default';

  // Pagination
  const PAGE_SIZE = 36;
  let currentPage = 1;
  let totalFiltered = 0;
  $: totalPages = Math.ceil(totalFiltered / PAGE_SIZE);
  $: paginated = businesses.slice((currentPage - 1) * PAGE_SIZE, currentPage * PAGE_SIZE);

  // URL sync
  let initialLoadDone = false;

  // ─── Category meta ──────────────────────────────────────────────────────────
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
  const categoryList = Object.entries(indexData.categories).map(([slug, name]) => ({
    slug,
    name,
    icon: categoryIcons[slug] || '🏪',
    count: indexData.category_counts[slug] || 0,
  })).sort((a, b) => b.count - a.count);
  // Category color palette (Tailwind bg/text classes)
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

  // ─── Sync initial filters ───────────────────────────────────────────────────
  onMount(async () => {
    const params = new URLSearchParams(window.location.search);
    if (params.get('category')) selectedCategory = params.get('category');
    if (params.get('city')) selectedCity = params.get('city');
    if (params.get('q')) searchQuery = params.get('q');
    if (params.get('page')) currentPage = parseInt(params.get('page')) || 1;

    if (selectedCategory) await loadCategory(selectedCategory, true);
    initialLoadDone = true;
  });

  // ─── Category loader ─────────────────────────────────────────────────────────
  async function loadCategory(slug, fromUrl = false) {
    if (!slug) { allBusinesses = []; businesses = []; totalFiltered = 0; return; }
    loadingCategory = true;
    selectedCategory = slug;
    currentPage = fromUrl ? (parseInt(new URLSearchParams(window.location.search).get('page')) || 1) : 1;

    try {
      const catFiles = indexData?.files?.[slug];
      if (!catFiles?.length) { loadingCategory = false; return; }

      let allBiz = [];

      for (const fileMeta of catFiles) {
        const filePath = fileMeta.file;
        try {
          const r = await fetch(`/data/${filePath}`);
          if (!r.ok) continue;
          const d = await r.json();

          // Stub file: has `files` array but no `businesses` → load each sub-file
          if (d.files && Array.isArray(d.files) && !d.businesses?.length) {
            const baseDir = filePath.replace('.json', '');
            for (const subFile of d.files) {
              const subPath = `${baseDir}/${subFile}`;
              const sr = await fetch(`/data/${subPath}`);
              if (!sr.ok) continue;
              const sd = await sr.json();
              allBiz.push(...(sd.businesses || []));
            }
          }
          // Direct file with businesses
          else if (d.businesses?.length) {
            allBiz.push(...d.businesses);
          }
        } catch (e) {
          console.warn(`Failed to load ${fileMeta.file}:`, e);
        }
      }

      allBusinesses = allBiz.map(b => ({
        ...b,
        city: b.city || '',
        region: b.region || '',
      }));

      applyFilters(false);

      if (!fromUrl) pushUrl();
    } catch (e) {
      console.error(`Failed to load category ${slug}:`, e);
    } finally {
      loadingCategory = false;
    }
  }

  // ─── Filter & sort ──────────────────────────────────────────────────────────
  function applyFilters(push = true) {
    let result = [...allBusinesses];

    if (selectedCity) {
      result = result.filter(b =>
        b.city === selectedCity || (b.city && b.city.includes(selectedCity))
      );
    }

    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase();
      result = result.filter(b =>
        b.business_name?.toLowerCase().includes(q) ||
        b.tags?.some(t => t.toLowerCase().includes(q)) ||
        b.description?.toLowerCase().includes(q)
      );
    }

    if (sortBy === 'name') {
      result.sort((a, b) => (a.business_name || '').localeCompare(b.business_name || ''));
    } else if (sortBy === 'city') {
      result.sort((a, b) => (a.city || '').localeCompare(b.city || ''));
    }

    businesses = result;
    totalFiltered = result.length;
    currentPage = 1;
    if (push) pushUrl();
  }

  // ─── URL sync ───────────────────────────────────────────────────────────────
  function pushUrl() {
    if (!initialLoadDone) return;
    const params = new URLSearchParams();
    if (selectedCategory) params.set('category', selectedCategory);
    if (selectedCity) params.set('city', selectedCity);
    if (searchQuery) params.set('q', searchQuery);
    if (currentPage > 1) params.set('page', currentPage);
    const newUrl = params.toString()
      ? `${window.location.pathname}?${params.toString()}`
      : window.location.pathname;
    window.history.replaceState({}, '', newUrl);
  }

  // ─── Handlers ───────────────────────────────────────────────────────────────
  function handleCategoryClick(slug) {
    selectedCity = '';
    searchQuery = '';
    loadCategory(slug);
  }

  function handleCityClick(city) {
    selectedCity = city;
    applyFilters();
  }

  function handleSearchInput() {
    applyFilters();
  }

  function handleSortChange() {
    applyFilters();
  }

  function goPage(n) {
    currentPage = n;
    pushUrl();
    tick().then(() => window.scrollTo({ top: 0, behavior: 'smooth' }));
  }

  // ─── City counts (from loaded data) ─────────────────────────────────────────
  $: cityBreakdown = (() => {
    const counts = {};
    for (const b of allBusinesses) {
      if (b.city) counts[b.city] = (counts[b.city] || 0) + 1;
    }
    return Object.entries(counts).sort((a, b) => b[1] - a[1]);
  })();

</script>

<svelte:head>
  <title>{selectedCategory ? categoryNames[selectedCategory] || selectedCategory : '商家名錄'} — bizmap.tw</title>
  <meta name="description" content="瀏覽台灣各地真實商家名錄，涵蓋餐飲、美容、醫療、教育等各類服務，資料來源為政府開放資料。" />
</svelte:head>

<!-- Page Header -->
<section class="relative overflow-hidden py-14 px-6"
  style="background: linear-gradient(160deg, #0c0c0e 0%, #1e2330 50%, #0c0c0e 100%);">
  <div class="absolute inset-0 opacity-[0.03]"
    style="background-image: linear-gradient(rgba(200,168,75,0.5) 1px, transparent 1px), linear-gradient(90deg, rgba(200,168,75,0.5) 1px, transparent 1px); background-size: 48px 48px;">
  </div>
  <div class="relative max-w-5xl mx-auto">
    <div class="section-label section-label-gold mb-3 w-fit">DIRECTORY</div>
    <h1 class="text-3xl font-bold text-white tracking-tight mb-2">
      {selectedCategory ? categoryNames[selectedCategory] || selectedCategory : '台灣商家名錄'}
    </h1>
    <p class="text-white/30 text-sm">
      {#if indexData}
        收錄 <strong class="text-white/50">{indexData.total.toLocaleString()}</strong> 家商家，涵蓋
        <strong class="text-white/50">{Object.keys(indexData.city_counts || {}).length}</strong> 縣市
      {/if}
    </p>
  </div>
</section>

<div class="max-w-5xl mx-auto px-6 -mt-6 relative z-10">

  <!-- ── Search + Back ─────────────────────────────────────────── -->
  <div class="glass-card p-4 mb-5" style="background:rgba(12,12,14,0.95); border-color:rgba(255,255,255,0.08);">
    <div class="flex flex-wrap items-center gap-3">
      <!-- Back to categories -->
      {#if selectedCategory}
        <button
          on:click={() => { selectedCategory = ''; selectedCity = ''; searchQuery = ''; allBusinesses = []; businesses = []; totalFiltered = 0; pushUrl(); }}
          class="flex items-center gap-1.5 text-sm text-white/40 hover:text-gold transition-colors shrink-0"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/></svg>
          返回
        </button>
        <span class="text-white/10">|</span>
      {/if}

      <!-- Search -->
      <div class="flex-1 min-w-[200px]">
        <div class="relative">
          <svg class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-white/20" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-4.35-4.35M11 19a8 8 0 100-16 8 8 0 000 16z"/>
          </svg>
          <input
            bind:value={searchQuery}
            on:input={() => { applyFilters(); }}
            on:keydown={(e) => { if (e.key === 'Enter') applyFilters(); }}
            type="text"
            placeholder="搜尋商家名稱、標籤...（Enter 搜尋）"
            class="w-full pl-10 pr-4 py-2.5 rounded-lg text-sm bg-white/5 border border-white/10 text-white placeholder-white/20 focus:outline-none focus:border-gold/40 transition-all"
          />
        </div>
      </div>

      <!-- Category pills -->
      <div class="flex flex-wrap gap-1.5 max-w-[600px]">
        <button
          on:click={() => { selectedCategory = ''; selectedCity = ''; searchQuery = ''; allBusinesses = []; businesses = []; totalFiltered = 0; pushUrl(); }}
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

<!-- ── Category Grid (when no category selected) ──────────── -->
  {#if !loading && !selectedCategory}
    <div class="mb-8">
      <!-- Top: quick search bar -->
      <div class="relative mb-5">
        <div class="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
          <svg class="w-5 h-5 text-white/20" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-4.35-4.35M11 19a8 8 0 100-16 8 8 0 000 16z"/>
          </svg>
        </div>
        <input
          bind:value={searchQuery}
          on:input={() => { applyFilters(); }}
          on:keydown={(e) => { if (e.key === 'Enter') applyFilters(); }}
          type="text"
          placeholder="🔍 搜尋商家名稱、類別或城市...（Enter 搜尋）"
          class="w-full pl-12 pr-4 py-4 rounded-2xl text-sm bg-white/5 border border-white/10 text-white placeholder-white/20 focus:outline-none focus:border-gold/40 focus:bg-white/8 transition-all"
          style="font-size:15px;"
        />
      </div>

      <p class="text-xs text-white/20 font-mono mb-4 uppercase tracking-wider">
        共收錄 <strong class="text-white/50">{indexData?.total?.toLocaleString() || '...'}</strong> 家，選擇類別探索
      </p>

      <!-- Category cards grid -->
      <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-3">
        {#each categoryList as cat}
          {@const topCities = Object.entries(
            indexData?.city_counts ? Object.entries(indexData.city_counts)
              .filter(([c]) => c && ['food','beauty','fitness','medical','home','education','business','retail','transport','industrial'].includes(cat.slug))
              .reduce((acc, [city, cnt]) => { acc[city] = cnt; return acc; }, {})
              : {}
          ).sort((a,b) => b[1]-a[1]).slice(0,3)}
          <button
            on:click={() => handleCategoryClick(cat.slug)}
            class="relative group glass-card-dark-hover p-4 rounded-xl text-center cursor-pointer border transition-all duration-200 hover:-translate-y-1
              {categoryColor[cat.slug] || 'bg-white/10 text-white/60'}
              {!selectedCategory ? 'opacity-100' : selectedCategory === cat.slug ? 'ring-1 ring-gold/40' : 'opacity-40'}"
            style="background: rgba(255,255,255,0.02);"
          >
            <!-- Icon container with glow -->
            <div class="relative mb-3">
              <div class="w-16 h-16 rounded-2xl mx-auto flex items-center justify-center text-2xl shadow-lg
                {categoryColor[cat.slug] || 'bg-white/10 text-white/60'}
                group-hover:scale-110 transition-transform duration-200"
                style="box-shadow: 0 4px 24px rgba(0,0,0,0.4); background: rgba(255,255,255,0.06);">
                <!-- SVG icon (Lucide-style inline SVG) -->
                {#if cat.slug === 'food'}
                  <svg class="w-8 h-8" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M3 2v7c0 1.1.9 2 2 2h4a2 2 0 002-2V2"/><path d="M7 2v20"/><path d="M21 15V2v0a5 5 0 00-5 5v6c0 1.1.9 2 2 2h3zm0 0v7"/></svg>
                {:else if cat.slug === 'beauty'}
                  <svg class="w-8 h-8" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="6" cy="6" r="3"/><path d="M8.12 8.12L12 12"/><path d="M20 4L8.12 15.88"/><circle cx="6" cy="18" r="3"/><path d="M14.8 14.8L20 20"/></svg>
                {:else if cat.slug === 'fitness'}
                  <svg class="w-8 h-8" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M6.5 6.5L17.5 17.5M17.5 6.5L6.5 17.5"/><path d="M3 12h3m12 0h3M12 3v3m0 12v3"/></svg>
                {:else if cat.slug === 'medical'}
                  <svg class="w-8 h-8" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0016.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 002 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z"/><path d="M3 22h18"/></svg>
                {:else if cat.slug === 'home'}
                  <svg class="w-8 h-8" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M14.7 6.3a1 1 0 000 1.4l1.6 1.6a1 1 0 001.4 0l3.77-3.77a6 6 0 01-7.94 7.94l-6.91 6.91a2.12 2.12 0 01-3-3l6.91-6.91a6 6 0 017.94-7.94l-3.76 3.76z"/></svg>
                {:else if cat.slug === 'education'}
                  <svg class="w-8 h-8" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M22 10v6M2 10l10-5 10 5-10 5z"/><path d="M6 12v5c3 3 9 3 12 0v-5"/></svg>
                {:else if cat.slug === 'business'}
                  <svg class="w-8 h-8" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect width="20" height="14" x="2" y="7" rx="2" ry="2"/><path d="M16 21V5a2 2 0 00-2-2h-4a2 2 0 00-2 2v16"/></svg>
                {:else if cat.slug === 'retail'}
                  <svg class="w-8 h-8" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M6 2L3 6v14a2 2 0 002 2h14a2 2 0 002-2V6l-3-4z"/><line x1="3" y1="6" x2="21" y2="6"/><path d="M16 10a4 4 0 01-8 0"/></svg>
                {:else if cat.slug === 'transport'}
                  <svg class="w-8 h-8" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M3 11l19-9-9 19-2-8-8-2z"/></svg>
                {:else if cat.slug === 'industrial'}
                  <svg class="w-8 h-8" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M2 20a2 2 0 002 2h16a2 2 0 002-2V8l-7 5V8l-7 5V4a2 2 0 00-2-2H4a2 2 0 00-2 2Z"/></svg>
                {:else}
                  <span class="text-2xl">{cat.icon}</span>
                {/if}
              </div>
              <!-- Active ring -->
              {#if selectedCategory === cat.slug}
                <div class="absolute inset-0 rounded-2xl border-2 border-gold/50 animate-pulse" style="animation-duration:2s;"></div>
              {/if}
            </div>

            <!-- Category name -->
            <div class="font-semibold text-white/90 text-sm mb-1 leading-tight">{cat.name}</div>

            <!-- Count -->
            <div class="text-xs text-white/30 mb-2">{cat.count.toLocaleString()} 家</div>

            <!-- City SEO tags (top 3 cities for this category) -->
            {#if indexData?.city_counts}
              {@const catCities = Object.entries(indexData.city_counts)
                .filter(([c]) => c)
                .sort((a,b) => b[1]-a[1])
                .slice(0, 4)}
              {#if catCities.length > 0}
                <div class="flex flex-wrap justify-center gap-1">
                  {#each catCities.slice(0,3) as [city, cnt]}
                    <a
                      href="/city/{encodeURIComponent(city)}?category={cat.slug}"
                      on:click|stopPropagation
                      class="text-[9px] px-1.5 py-0.5 rounded-full bg-white/5 text-white/40 border border-white/5 hover:text-gold/80 hover:border-gold/30 transition-all"
                      title="{city} · {cnt} 家"
                    >
                      {city}
                    </a>
                  {/each}
                  {#if catCities.length > 3}
                    <span class="text-[9px] px-1.5 py-0.5 rounded-full bg-white/5 text-white/20">+{catCities.length - 3}</span>
                  {/if}
                </div>
              {/if}
            {/if}

            <!-- SEO: 反向鏈結提示 -->
            <div class="mt-2 pt-2 border-t border-white/5">
              <a
                href="/city/taipei?category={cat.slug}"
                on:click|stopPropagation
                class="text-[9px] text-white/15 hover:text-gold/50 transition-colors"
              >
                → 台北 · 新北 · 台中
              </a>
            </div>
          </button>
        {/each}
      </div>
    </div>
  <!-- ── Category Results ─────────────────────────────────────── -->
  {:else if selectedCategory}
    <div class="mb-6">
      <!-- Results header -->
      <div class="flex justify-between items-center mb-4">
        <p class="text-sm text-white/30 font-mono">
          {#if loadingCategory}
            載入中...
          {:else}
            共 <span class="text-white/60">{totalFiltered.toLocaleString()}</span> 家
            {#if selectedCity}<span class="text-gold/60"> · {selectedCity}</span>{/if}
            {#if searchQuery}<span class="text-gold/60"> · 「{searchQuery}」</span>{/if}
          {/if}
        </p>
        <div class="flex items-center gap-2">
          <!-- Sort -->
          <select bind:value={sortBy} on:change={handleSortChange}
            class="px-3 py-1.5 rounded-lg text-xs bg-white/5 border border-white/10 text-white/70 focus:outline-none focus:border-gold/40 transition-all appearance-none">
            <option value="default">預設排序</option>
            <option value="name">名稱 A-Z</option>
            <option value="city">依縣市</option>
          </select>
        </div>
      </div>

      <!-- City pills (only show when businesses loaded) -->
      {#if !loadingCategory && businesses.length > 0}
        <div class="flex flex-wrap gap-2 mb-5">
          <button
            on:click={() => handleCityClick('')}
            class="px-3 py-1.5 rounded-full text-xs font-medium border transition-all
              {!selectedCity ? 'bg-gold/20 border-gold/40 text-gold' : 'bg-white/5 border-white/10 text-white/40 hover:text-white/70'}"
          >
            全部縣市
          </button>
          {#each cityBreakdown as [city, count]}
            <button
              on:click={() => handleCityClick(city)}
              class="px-3 py-1.5 rounded-full text-xs font-medium border transition-all
                {selectedCity === city ? 'bg-gold/20 border-gold/40 text-gold' : 'bg-white/5 border-white/10 text-white/40 hover:text-white/70'}"
            >
              {city} <span class="opacity-50">{count}</span>
            </button>
          {/each}
        </div>
      {/if}

      <!-- Loading state -->
      {#if loadingCategory}
        <div class="text-center py-20">
          <div class="inline-flex items-center gap-3 text-white/30">
            <svg class="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
            </svg>
            載入 {categoryNames[selectedCategory]} 資料中...
          </div>
        </div>

      <!-- Empty state -->
      {:else if businesses.length === 0}
        <div class="text-center py-20">
          <div class="text-5xl mb-4 opacity-30">🔍</div>
          <p class="text-lg text-white/40 mb-2">沒有符合條件的商家</p>
          <p class="text-sm text-white/20">試試調整搜尋關鍵字或過濾條件</p>
        </div>

      <!-- Business cards -->
      {:else}
        <div class="grid md:grid-cols-2 lg:grid-cols-3 gap-4 pb-16">
          {#each paginated as biz}
            <a
              href="/business/{biz.business_id}"
              class="block glass-card-dark p-5 rounded-xl border border-white/5 hover:border-white/10 transition-all duration-200 hover:-translate-y-0.5 group"
            >
              <!-- Header -->
              <div class="flex items-start justify-between mb-3 gap-2">
                <div class="min-w-0 flex-1">
                  <div class="flex items-center gap-2 mb-2 flex-wrap">
                    {#if biz.city}
                      <span class="text-[10px] px-2 py-0.5 rounded-full bg-white/5 text-white/30 border border-white/5">
                        {biz.city}
                      </span>
                    {/if}
                    <span class="text-[10px] px-2 py-0.5 rounded-full font-mono uppercase tracking-wider"
                      style="background:rgba(200,168,75,0.12); color:var(--gold); border:1px solid rgba(200,168,75,0.2);">
                      {biz.category || categoryNames[selectedCategory]}
                    </span>
                  </div>
                  <h3 class="font-semibold text-white text-sm group-hover:text-gold transition-colors leading-snug truncate">
                    {biz.business_name || '未命名'}
                  </h3>
                </div>
              </div>

              <!-- Description -->
              {#if biz.description}
                <p class="text-xs text-white/30 leading-relaxed mb-3 line-clamp-2">{biz.description}</p>
              {/if}

              <!-- Tags -->
              {#if biz.tags?.length}
                <div class="flex flex-wrap gap-1 mb-3">
                  {#each biz.tags.slice(0, 3) as tag}
                    <span class="text-[10px] px-2 py-0.5 rounded-full bg-white/5 text-white/25">{tag}</span>
                  {/each}
                  {#if biz.tags.length > 3}
                    <span class="text-[10px] px-2 py-0.5 rounded-full bg-white/5 text-white/15">+{biz.tags.length - 3}</span>
                  {/if}
                </div>
              {/if}

              <!-- Meta -->
              <div class="text-xs text-white/25 space-y-1 pt-2 border-t border-white/5">
                {#if biz.source_name}
                  <p class="truncate">來源：{biz.source_name}</p>
                {/if}
                {#if biz.source_updated_at}
                  <p>更新：{biz.source_updated_at.split('T')[0]}</p>
                {/if}
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
              {#if totalPages > 7 && p === 3 && currentPage > 5}
                <span class="text-white/20 px-2">...</span>
              {/if}
              {#if totalPages > 7 && p === 5 && currentPage < totalPages - 3}
                <span class="text-white/20 px-2">...</span>
              {/if}
              <button
                on:click={() => goPage(p)}
                class="w-9 h-9 rounded-lg text-sm border transition-all
                  {p === currentPage
                    ? 'bg-gold/20 border-gold/40 text-gold'
                    : 'border-white/10 text-white/50 hover:border-white/20 hover:text-white/70'}"
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

            <span class="text-xs text-white/20 ml-2">{currentPage} / {totalPages}</span>
          </div>
        {/if}
      {/if}
    </div>
  {/if}
</div>

<style>
  :global(.line-clamp-2) {
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }
</style>
