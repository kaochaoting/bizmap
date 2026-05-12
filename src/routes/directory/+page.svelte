<script>
  import { onMount } from 'svelte';
  import { page } from '$app/stores';
  
  let businesses = [];
  let filtered = [];
  let loading = true;
  
  // Filters
  let searchQuery = '';
  let selectedCity = '';
  let selectedCategory = '';
  
  const categories = ['餐飲美食', '美容美髮', '健身運動', '醫療健康', '教育補習', '居家服務', '商業服務', '零售購物', '交通運輸'];
  const cities = ['台北市', '新北市', '桃園市', '台中市', '台南市', '高雄市', '基隆市', '新竹市', '新竹縣', '苗栗縣',
    '彰化縣', '南投縣', '雲林縣', '嘉義市', '嘉義縣', '屏東縣', '宜蘭縣', '花蓮縣', '台東縣', '澎湖縣', '金門縣', '連江縣'];
  
  onMount(async () => {
    try {
      const res = await fetch('/data/businesses.json');
      const data = await res.json();
      businesses = data.businesses || [];
      applyFilters();
    } catch (e) {
      console.error('Failed to load businesses:', e);
    } finally {
      loading = false;
    }
  });
  
  function applyFilters() {
    filtered = businesses.filter(b => {
      if (searchQuery) {
        const q = searchQuery.toLowerCase();
        const match = b.business_name?.toLowerCase().includes(q) ||
          b.tags?.some(t => t.toLowerCase().includes(q)) ||
          b.description?.toLowerCase().includes(q);
        if (!match) return false;
      }
      if (selectedCity && b.city !== selectedCity) return false;
      if (selectedCategory && b.category !== selectedCategory) return false;
      return true;
    });
  }
  
  function getCityCount(city) {
    return businesses.filter(b => b.city === city).length;
  }
  
  function getCategoryCount(cat) {
    return businesses.filter(b => b.category === cat).length;
  }
</script>

<svelte:head>
  <title>商家名錄 — bizmap.tw</title>
  <meta name="description" content="瀏覽台灣各地真實商家名錄，涵蓋餐飲、美容、醫療、教育等各類服務，資料來源為政府開放資料。">
</svelte:head>

<div class="max-w-6xl mx-auto px-6 py-12">
  <div class="mb-8">
    <p class="text-xs font-mono tracking-widest mb-2" style="color: var(--gold)">DIRECTORY</p>
    <h1 class="text-3xl font-bold text-gray-900">台灣商家名錄</h1>
    <p class="text-gray-500 mt-2">
      {#if !loading}
        收錄 <strong>{businesses.length}</strong> 家經政府開放資料驗證的商家，涵蓋 <strong>{new Set(businesses.map(b => b.city).filter(Boolean)).size}</strong> 縣市
      {:else}
        載入中...
      {/if}
    </p>
  </div>

  <!-- Search & Filter Bar -->
  <div class="flex flex-wrap gap-3 mb-8 p-4 bg-white rounded-xl border border-gray-100">
    <input
      bind:value={searchQuery}
      on:input={applyFilters}
      type="text"
      placeholder="搜尋商家名稱、標籤..."
      class="flex-1 min-w-[200px] px-4 py-2.5 rounded-lg border border-gray-200 text-sm focus:outline-none focus:border-yellow-400 transition-colors"
    />
    <select bind:value={selectedCategory} on:change={applyFilters} class="px-3 py-2.5 rounded-lg border border-gray-200 text-sm bg-white focus:outline-none focus:border-yellow-400">
      <option value="">所有類別</option>
      {#each categories as cat}
        {#if getCategoryCount(cat) > 0}
          <option value={cat}>{cat} ({getCategoryCount(cat)})</option>
        {/if}
      {/each}
    </select>
    <select bind:value={selectedCity} on:change={applyFilters} class="px-3 py-2.5 rounded-lg border border-gray-200 text-sm bg-white focus:outline-none focus:border-yellow-400">
      <option value="">所有縣市</option>
      {#each cities as city}
        {#if getCityCount(city) > 0}
          <option value={city}>{city} ({getCityCount(city)})</option>
        {/if}
      {/each}
    </select>
  </div>

  <!-- Results -->
  {#if loading}
    <div class="text-center py-12 text-gray-400">載入商家資料中...</div>
  {:else if filtered.length === 0}
    <div class="text-center py-12 text-gray-400">
      <p class="text-lg mb-2">沒有符合條件的商家</p>
      <p class="text-sm">試試調整搜尋關鍵字或過濾條件</p>
    </div>
  {:else}
    <div class="flex justify-between items-center mb-4">
      <p class="text-sm text-gray-400">共 {filtered.length} 家</p>
    </div>
    <div class="grid md:grid-cols-2 lg:grid-cols-3 gap-5">
      {#each filtered as biz}
        <div class="bg-white rounded-2xl border border-gray-100 p-5 hover:border-yellow-300 hover:-translate-y-1 transition-all">
          <div class="flex items-start justify-between mb-3">
          <div class="min-w-0">
            <span class="text-xs px-2 py-0.5 rounded-full bg-yellow-50 text-yellow-700 font-mono">{biz.category}</span>
            <a href="/business/{biz.business_id}" class="block font-semibold text-gray-900 mt-2 text-base truncate hover:text-yellow-600 transition-colors">{biz.business_name}</a>
              <p class="text-sm text-gray-500">{biz.region || biz.city}</p>
            </div>
          </div>
          <div class="text-sm text-gray-600 space-y-1 mb-3">
            {#if biz.address}
              <p class="truncate">📍 {biz.address}</p>
            {/if}
            {#if biz.phone}
              <p>📞 {biz.phone}</p>
            {/if}
          </div>
          {#if biz.tags && biz.tags.length}
            <div class="flex flex-wrap gap-1.5">
              {#each biz.tags.slice(0, 4) as tag}
                <span class="text-xs px-2 py-0.5 rounded-full bg-gray-100 text-gray-500">{tag}</span>
              {/each}
              {#if biz.tags.length > 4}
                <span class="text-xs px-2 py-0.5 rounded-full bg-gray-100 text-gray-400">+{biz.tags.length - 4}</span>
              {/if}
            </div>
          {/if}
          <div class="mt-3 pt-3 border-t border-gray-50 flex justify-between items-center">
            <span class="text-[10px] text-gray-300">{biz.source_type === 'government_open_data' ? '政府開放資料' : biz.source_type}</span>
          </div>
        </div>
      {/each}
    </div>
  {/if}
</div>
