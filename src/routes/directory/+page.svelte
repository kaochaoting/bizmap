<script>
  import { onMount } from 'svelte';
  import { page } from '$app/stores';

  let businesses = [];
  let loading = true;
  let loadingCategory = false;

  // Index data
  let indexData = null;
  let categoryList = [];
  let cityCounts = {};

  // Filters
  let searchQuery = '';
  let selectedCity = '';
  let selectedCategory = '';
  let sortBy = 'default';

  // Current data context
  let currentCategorySlug = '';
  let currentRegion = '';

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

  // Region mapping for large categories
  const regions = [
    { key: 'taipei_north', label: '北區', cities: ['台北市', '新北市', '基隆市', '桃園市', '新竹市', '新竹縣', '苗栗縣'] },
    { key: 'taichung_central', label: '中區', cities: ['台中市', '彰化縣', '南投縣', '雲林縣'] },
    { key: 'kaohsiung_south', label: '南區', cities: ['嘉義市', '嘉義縣', '台南市', '高雄市', '屏東縣'] },
    { key: 'hualien_east', label: '東區', cities: ['宜蘭縣', '花蓮縣', '台東縣'] },
    { key: 'outlying_islands', label: '離島', cities: ['澎湖縣', '金門縣', '連江縣'] },
  ];

  $: largeCategory = ['retail', 'home', 'business'].includes(currentCategorySlug);

  function getRegionForCity(city) {
    for (const r of regions) {
      if (r.cities.includes(city)) return r.key;
    }
    return 'other';
  }

  // Load index on mount, then check URL params
  onMount(async () => {
    try {
      const res = await fetch('/data/index.json');
      indexData = await res.json();
      categoryList = (indexData.files ? Object.entries(indexData.files) : [])
        .map(([slug, files]) => ({
          slug,
          name: categoryNames[slug] || slug,
          icon: categoryIcons[slug] || '🏪',
          count: indexData.category_counts[slug] || 0,
          files,
        }))
        .sort((a, b) => b.count - a.count);
      cityCounts = indexData.city_counts || {};

      // Check URL params for category
      const params = new URLSearchParams(window.location.search);
      const catParam = params.get('category');
      const cityParam = params.get('city');
      const qParam = params.get('q');

      if (catParam) selectedCategory = catParam;
      if (cityParam) selectedCity = cityParam;
      if (qParam) searchQuery = qParam;

      if (selectedCategory) {
        await loadCategory(selectedCategory);
      }
    } catch (e) {
      console.error('Failed to load index:', e);
    } finally {
      loading = false;
    }
  });

  async function loadCategory(slug) {
    loadingCategory = true;
    currentCategorySlug = slug;
    businesses = [];

    try {
      const cat = categoryList.find(c => c.slug === slug);
      if (!cat) { loadingCategory = false; return; }

      // Determine which region/region files to load
      let filesToLoad = [];
      if (cat.files.length === 1 && cat.files[0].region === 'all') {
        filesToLoad = [cat.files[0].file];
      } else {
        // Large category with region splits
        // If a city is selected, load only that region
        let targetRegion = 'all';
        if (selectedCity) {
          targetRegion = getRegionForCity(selectedCity);
        }
        currentRegion = targetRegion;

        if (targetRegion !== 'all') {
          // Load all city-level files within this region
          const rf = cat.files.filter(f => f.region === targetRegion);
          if (rf.length) filesToLoad = rf.map(f => f.file);
        }
        if (filesToLoad.length === 0) {
          // Load all regions
          filesToLoad = cat.files.map(f => f.file);
        }
      }

      // Fetch all needed files
      const allBiz = [];
      for (const file of filesToLoad) {
        const res = await fetch(`/data/${file}`);
        const data = await res.json();
        const bizs = data.businesses || [];
        allBiz.push(...bizs);
      }
      businesses = allBiz;
      applyFilters();
    } catch (e) {
      console.error(`Failed to load category ${slug}:`, e);
    } finally {
      loadingCategory = false;
    }
  }

  async function handleCategoryChange() {
    if (selectedCategory) {
      await loadCategory(selectedCategory);
    } else {
      businesses = [];
      currentCategorySlug = '';
    }
  }

  function applyFilters() {
    if (!businesses.length) return;
    let result = [...businesses];

    if (searchQuery) {
      const q = searchQuery.toLowerCase();
      result = result.filter(b =>
        b.business_name?.toLowerCase().includes(q) ||
        b.tags?.some(t => t.toLowerCase().includes(q)) ||
        b.description?.toLowerCase().includes(q)
      );
    }
    if (selectedCity && !largeCategory) {
      result = result.filter(b => b.city === selectedCity);
    }

    if (sortBy === 'name') {
      result.sort((a, b) => (a.business_name || '').localeCompare(b.business_name || ''));
    } else if (sortBy === 'city') {
      result.sort((a, b) => (a.city || '').localeCompare(b.city || ''));
    }

    // Reassign to trigger reactivity
    businesses = result;
  }

  $: activeFilters = [selectedCity, selectedCategory, searchQuery].filter(Boolean).length;
</script>

<svelte:head>
  <title>{selectedCategory ? categoryNames[selectedCategory] || selectedCategory : '商家名錄'} — bizmap.tw</title>
  <meta name="description" content="瀏覽台灣各地真實商家名錄，涵蓋餐飲、美容、醫療、教育等各類服務，資料來源為政府開放資料。">
</svelte:head>

<!-- Page Header -->
<section class="relative overflow-hidden py-20 px-6"
  style="background: linear-gradient(160deg, #0c0c0e 0%, #1e2330 50%, #0c0c0e 100%);">
  <div class="absolute inset-0 opacity-[0.03]"
    style="background-image: linear-gradient(rgba(200,168,75,0.5) 1px, transparent 1px), linear-gradient(90deg, rgba(200,168,75,0.5) 1px, transparent 1px); background-size: 48px 48px;">
  </div>
  <div class="relative max-w-6xl mx-auto">
    <div class="section-label section-label-gold mb-4 w-fit">DIRECTORY</div>
    <h1 class="text-4xl font-bold text-white tracking-tight mb-2">
      {selectedCategory ? categoryNames[selectedCategory] || selectedCategory : '台灣商家名錄'}
    </h1>
    <p class="text-white/40">
      {#if indexData}
        收錄 <strong class="text-white/70">{indexData.total.toLocaleString()}</strong> 家商家，涵蓋 <strong class="text-white/70">{Object.keys(indexData.city_counts || {}).length}</strong> 縣市
      {:else}
        載入中...
      {/if}
    </p>
  </div>
</section>

<div class="max-w-6xl mx-auto px-6 -mt-8 relative z-10">
  <!-- Filter bar -->
  <div class="glass-card p-5 mb-10 flex flex-wrap items-end gap-4" style="background:rgba(12,12,14,0.95); border-color:rgba(255,255,255,0.08);">
    <!-- Category selector -->
    <div class="min-w-[180px]">
      <label class="block text-[11px] text-white/30 font-mono tracking-wider mb-1.5 uppercase">類別</label>
      <select bind:value={selectedCategory} on:change={handleCategoryChange}
        class="w-full px-3 py-2.5 rounded-lg text-sm bg-white/5 border border-white/10 text-white/80 focus:outline-none focus:border-gold/40 transition-all appearance-none">
        <option value="" class="bg-ink">選擇類別⋯</option>
        {#each categoryList as cat}
          <option value={cat.slug} class="bg-ink">{cat.icon} {cat.name} ({cat.count.toLocaleString()})</option>
        {/each}
      </select>
    </div>

    <!-- Search (within loaded category) -->
    {#if businesses.length > 0}
      <div class="flex-1 min-w-[200px]">
        <label class="block text-[11px] text-white/30 font-mono tracking-wider mb-1.5 uppercase">搜尋（{currentCategorySlug}）</label>
        <div class="relative">
          <svg class="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-white/20" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-4.35-4.35M11 19a8 8 0 100-16 8 8 0 000 16z"/>
          </svg>
          <input
            bind:value={searchQuery}
            on:input={applyFilters}
            type="text"
            placeholder="商家名稱、標籤..."
            class="w-full pl-9 pr-4 py-2.5 rounded-lg text-sm bg-white/5 border border-white/10 text-white placeholder-white/20 focus:outline-none focus:border-gold/40 transition-all"
          />
        </div>
      </div>

      <!-- City (only for non-large-categories) -->
      {#if !largeCategory}
        <div class="min-w-[150px]">
          <label class="block text-[11px] text-white/30 font-mono tracking-wider mb-1.5 uppercase">縣市</label>
          <select bind:value={selectedCity} on:change={applyFilters}
            class="w-full px-3 py-2.5 rounded-lg text-sm bg-white/5 border border-white/10 text-white/80 focus:outline-none focus:border-gold/40 transition-all appearance-none">
            <option value="" class="bg-ink">所有縣市</option>
            {#each Object.entries(cityCounts) as [city, count]}
              <option value={city} class="bg-ink">{city} ({count.toLocaleString()})</option>
            {/each}
          </select>
        </div>
      {:else}
        <!-- Region selector for large categories -->
        <div class="min-w-[150px]">
          <label class="block text-[11px] text-white/30 font-mono tracking-wider mb-1.5 uppercase">區域</label>
          <select bind:value={selectedCity} on:change={handleCategoryChange}
            class="w-full px-3 py-2.5 rounded-lg text-sm bg-white/5 border border-white/10 text-white/80 focus:outline-none focus:border-gold/40 transition-all appearance-none">
            <option value="" class="bg-ink">全區域</option>
            {#each regions as r}
              <option value={r.cities[0]} class="bg-ink">{r.label}</option>
            {/each}
          </select>
        </div>
      {/if}

      <!-- Sort -->
      <div class="min-w-[130px]">
        <label class="block text-[11px] text-white/30 font-mono tracking-wider mb-1.5 uppercase">排序</label>
        <select bind:value={sortBy} on:change={applyFilters}
          class="w-full px-3 py-2.5 rounded-lg text-sm bg-white/5 border border-white/10 text-white/80 focus:outline-none focus:border-gold/40 transition-all appearance-none">
          <option value="default" class="bg-ink">預設</option>
          <option value="name" class="bg-ink">名稱 A-Z</option>
          <option value="city" class="bg-ink">縣市</option>
        </select>
      </div>
    {/if}
  </div>

    <!-- Category picker (no category selected yet) -->
    {#if !loading && !selectedCategory}
      <div class="text-center py-10">
        <div class="text-5xl mb-4 opacity-30">📂</div>
        <p class="text-lg text-white/40 mb-2">請先選擇一個類別</p>
        <p class="text-sm text-white/20">上方選擇類別後，即可瀏覽該類別的商家資訊</p>

        <div class="grid grid-cols-2 md:grid-cols-5 gap-4 mt-10 max-w-3xl mx-auto">
          {#each categoryList as cat}
            <button on:click={() => { selectedCategory = cat.slug; handleCategoryChange(); }}
              class="glass-card-dark p-4 glass-card-dark-hover text-center cursor-pointer border-0"
            >
              <div class="text-3xl mb-2">{cat.icon}</div>
              <div class="font-medium text-white text-sm mb-1">{cat.name}</div>
              <div class="text-xs text-white/30">{cat.count.toLocaleString()} 家</div>
            </button>
          {/each}
        </div>
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
          載入 {categoryNames[currentCategorySlug] || currentCategorySlug} 資料中...
        </div>
      </div>
    {:else if selectedCategory && businesses.length === 0 && !loadingCategory}
      <div class="text-center py-20">
        <div class="text-5xl mb-4 opacity-30">🔍</div>
        <p class="text-lg text-white/40 mb-2">沒有符合條件的商家</p>
        <p class="text-sm text-white/20">試試調整搜尋關鍵字或過濾條件</p>
      </div>
    {:else if businesses.length > 0}
      <!-- Results header -->
      <div class="flex justify-between items-center mb-6">
        <p class="text-sm text-white/30 font-mono">
          共 <span class="text-white/60">{businesses.length.toLocaleString()}</span> 家
          {#if activeFilters > 0}
            <span class="text-gold/60">（已過濾）</span>
          {/if}
        </p>
      </div>

      <!-- Results grid -->
      <div class="grid md:grid-cols-2 lg:grid-cols-3 gap-5 pb-24">
        {#each businesses as biz}
          <div class="glass-card-dark p-6 glass-card-dark-hover flex flex-col">
            <div class="flex items-start justify-between mb-3">
              <div class="min-w-0 flex-1">
                <div class="flex items-center gap-2 mb-2">
                  <span class="text-[10px] px-2 py-0.5 rounded-full font-mono uppercase tracking-wider"
                    style="background:rgba(200,168,75,0.12); color:var(--gold); border:1px solid rgba(200,168,75,0.2);">
                    {biz.category}
                  </span>
                </div>
                <a href="/business/{biz.business_id}"
                  class="block font-semibold text-white text-base truncate hover:text-gold transition-colors">
                  {biz.business_name}
                </a>
                <p class="text-sm text-white/30">{biz.region || biz.city}</p>
              </div>
            </div>

            <div class="text-sm text-white/40 space-y-1.5 mb-4 flex-1">
              {#if biz.address}
                <p class="truncate flex items-center gap-1.5">
                  <span>📍</span>
                  <span>{biz.address}</span>
                </p>
              {/if}
              {#if biz.phone}
                <p class="flex items-center gap-1.5">
                  <span>📞</span>
                  <span>{biz.phone}</span>
                </p>
              {/if}
            </div>

            {#if biz.tags && biz.tags.length}
              <div class="flex flex-wrap gap-1.5 mt-auto pt-3 border-t border-white/5">
                {#each biz.tags.slice(0, 3) as tag}
                  <span class="text-[11px] px-2 py-0.5 rounded-full bg-white/5 text-white/30">{tag}</span>
                {/each}
                {#if biz.tags.length > 3}
                  <span class="text-[11px] px-2 py-0.5 rounded-full bg-white/5 text-white/20">+{biz.tags.length - 3}</span>
                {/if}
              </div>
            {/if}
          </div>
        {/each}
      </div>
    {/if}
</div>
