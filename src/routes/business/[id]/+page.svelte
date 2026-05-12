<script>
  import { page } from '$app/stores';
  import { onMount } from 'svelte';
  
  let business = null;
  let loading = true;
  let error = false;
  
  $: businessId = $page.params.id;
  
  onMount(async () => {
    try {
      const res = await fetch('/data/businesses.json');
      const data = await res.json();
      business = data.businesses.find(b => b.business_id === businessId) || null;
      if (!business) error = true;
    } catch (e) {
      error = true;
      console.error('Failed to load business:', e);
    } finally {
      loading = false;
    }
  });
</script>

<svelte:head>
  <title>{business ? business.business_name + ' — bizmap.tw' : '商家詳細 — bizmap.tw'}</title>
  <meta name="description" content={business?.description || '台灣在地商家資訊'}>
</svelte:head>

<div class="max-w-4xl mx-auto px-6 py-12">
  {#if loading}
    <div class="text-center py-12 text-gray-400">載入中...</div>
  {:else if error}
    <div class="text-center py-12">
      <p class="text-6xl mb-4">🔍</p>
      <h2 class="text-2xl font-bold text-gray-900 mb-2">找不到此商家</h2>
      <p class="text-gray-500 mb-6">商家 ID「{businessId}」不存在或已被移除。</p>
      <a href="/directory" class="inline-flex items-center gap-2 px-6 py-3 rounded-xl font-medium" style="background: var(--ink); color: white;">
        ← 回到商家名錄
      </a>
    </div>
  {:else}
    <nav class="text-sm text-gray-400 mb-8">
      <a href="/directory" class="hover:text-gray-600">商家名錄</a>
      <span class="mx-2">/</span>
      <a href="/directory?category={business.category_slug}" class="hover:text-gray-600">{business.category}</a>
      <span class="mx-2">/</span>
      <span class="text-gray-700">{business.business_name}</span>
    </nav>
    
    <div class="bg-white rounded-2xl border border-gray-100 p-8 sm:p-10">
      <!-- Header -->
      <div class="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4 mb-8">
        <div>
          <span class="inline-block text-xs px-3 py-1 rounded-full bg-yellow-50 text-yellow-700 font-mono mb-3">{business.category}</span>
          <h1 class="text-3xl sm:text-4xl font-bold text-gray-900">{business.business_name}</h1>
          <p class="text-gray-500 mt-2">{business.region || business.city}</p>
        </div>
      </div>
      
      <!-- Info Grid -->
      <div class="grid sm:grid-cols-2 gap-6 mb-8">
        {#if business.address}
          <div class="flex items-start gap-3 p-4 bg-gray-50 rounded-xl">
            <span class="text-xl mt-0.5">📍</span>
            <div>
              <p class="text-xs text-gray-400 font-mono uppercase mb-1">地址</p>
              <p class="text-gray-800">{business.address}</p>
            </div>
          </div>
        {/if}
        {#if business.phone}
          <div class="flex items-start gap-3 p-4 bg-gray-50 rounded-xl">
            <span class="text-xl mt-0.5">📞</span>
            <div>
              <p class="text-xs text-gray-400 font-mono uppercase mb-1">電話</p>
              <p class="text-gray-800">{business.phone}</p>
            </div>
          </div>
        {/if}
        {#if business.description}
          <div class="sm:col-span-2 flex items-start gap-3 p-4 bg-gray-50 rounded-xl">
            <span class="text-xl mt-0.5">📝</span>
            <div>
              <p class="text-xs text-gray-400 font-mono uppercase mb-1">簡介</p>
              <p class="text-gray-800">{business.description}</p>
            </div>
          </div>
        {/if}
      </div>
      
      <!-- Tags -->
      {#if business.tags && business.tags.length}
        <div class="mb-8">
          <p class="text-xs text-gray-400 font-mono uppercase mb-2">標籤</p>
          <div class="flex flex-wrap gap-2">
            {#each business.tags as tag}
              <span class="text-sm px-3 py-1 rounded-full bg-gray-100 text-gray-600">{tag}</span>
            {/each}
          </div>
        </div>
      {/if}
      
      <!-- Source info -->
      <div class="border-t border-gray-100 pt-6">
        <p class="text-xs text-gray-400 font-mono uppercase mb-2">資料來源</p>
        <div class="text-sm text-gray-500 space-y-1">
          <p>來源：{business.source_name}</p>
          <p>授權：{business.source_license}</p>
          <p>更新：{business.source_updated_at}</p>
          {#if business.source_url}
            <a href={business.source_url} target="_blank" rel="noopener" class="text-yellow-600 hover:text-yellow-700 underline underline-offset-2">
              原始資料集 →
            </a>
          {/if}
        </div>
      </div>
    </div>
    
    <!-- Back link -->
    <div class="mt-8 text-center">
      <a href="/directory" class="inline-flex items-center gap-2 text-sm text-gray-500 hover:text-gray-700">
        ← 回到商家名錄
      </a>
    </div>
  {/if}
</div>
