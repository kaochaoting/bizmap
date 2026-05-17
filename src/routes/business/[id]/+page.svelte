<script>
  import { page } from '$app/stores';
  import { onMount } from 'svelte';

  let business = null;
  let loading = true;
  let error = false;

  $: businessId = $page.params.id;

  onMount(async () => {
    try {
      // Step 1: Load routing table to find which category this business is in
      const routeRes = await fetch('/data/id-lookup/routing.json');
      const routing = await routeRes.json();
      const slug = routing[businessId];

      if (!slug) {
        error = true;
        loading = false;
        return;
      }

      // Step 2: Load the category data to find the business
      // For large categories, we need to know the region
      // Try the region-split approach: load index.json to find file structure
      const idxRes = await fetch('/data/index.json');
      const idx = await idxRes.json();
      const fileMeta = (idx.files || {})[slug];

      if (!fileMeta) {
        error = true;
        loading = false;
        return;
      }

      // Fetch from all files for this slug (should only be 1-5 files for large cats)
      const filePromises = fileMeta.map(f => fetch(`/data/${f.file}`).then(r => r.json()));
      const allData = await Promise.all(filePromises);

      for (const data of allData) {
        const bizs = data.businesses || [];
        const found = bizs.find(b => b.business_id === businessId);
        if (found) {
          business = found;
          break;
        }
      }

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

<div class="min-h-screen" style="background: #0c0c0e;">
  {#if loading}
    <div class="flex items-center justify-center py-32">
      <div class="flex items-center gap-3 text-white/30">
        <svg class="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
        </svg>
        載入中...
      </div>
    </div>
  {:else if error}
    <div class="flex items-center justify-center py-32 px-6">
      <div class="text-center">
        <div class="text-6xl mb-6 opacity-40">🔍</div>
        <h2 class="text-2xl font-bold text-white mb-2">找不到此商家</h2>
        <p class="text-white/40 mb-8">商家 ID 不存在或已被移除。</p>
        <a href="/directory" class="btn-primary">
          ← 回到商家名錄
        </a>
      </div>
    </div>
  {:else}
    <div class="pt-28 pb-24">
      <div class="max-w-4xl mx-auto px-6">
        <!-- Breadcrumb -->
        <nav class="flex items-center gap-2 text-sm text-white/30 mb-8 font-mono">
          <a href="/directory" class="hover:text-gold transition-colors">商家名錄</a>
          <span>/</span>
          <span class="text-white/50">{business.business_name}</span>
        </nav>

        <!-- Main card -->
        <div class="glass-card-dark p-8 sm:p-10" style="background:rgba(12,12,14,0.96); border-color:rgba(255,255,255,0.06);">
          <!-- Header -->
          <div class="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4 mb-10">
            <div>
              <span class="inline-flex text-[11px] px-3 py-1 rounded-full font-mono uppercase tracking-wider mb-4"
                style="background:rgba(200,168,75,0.12); color:var(--gold); border:1px solid rgba(200,168,75,0.2);">
                {business.category}
              </span>
              <h1 class="text-3xl sm:text-4xl font-bold text-white tracking-tight">{business.business_name}</h1>
              <p class="text-white/40 mt-2">{business.region || business.city}</p>
            </div>
          </div>

          <!-- Info Grid -->
          <div class="grid sm:grid-cols-2 gap-4 mb-10">
            {#if business.address}
              <div class="flex items-start gap-4 p-5 rounded-xl bg-white/5 border border-white/5">
                <span class="text-xl mt-0.5">📍</span>
                <div>
                  <p class="text-[11px] text-white/30 font-mono uppercase tracking-wider mb-1">地址</p>
                  <p class="text-white/80">{business.address}</p>
                </div>
              </div>
            {/if}
            {#if business.phone}
              <div class="flex items-start gap-4 p-5 rounded-xl bg-white/5 border border-white/5">
                <span class="text-xl mt-0.5">📞</span>
                <div>
                  <p class="text-[11px] text-white/30 font-mono uppercase tracking-wider mb-1">電話</p>
                  <p class="text-white/80">{business.phone}</p>
                </div>
              </div>
            {/if}
            {#if business.description}
              <div class="sm:col-span-2 flex items-start gap-4 p-5 rounded-xl bg-white/5 border border-white/5">
                <span class="text-xl mt-0.5">📝</span>
                <div>
                  <p class="text-[11px] text-white/30 font-mono uppercase tracking-wider mb-1">簡介</p>
                  <p class="text-white/70 leading-relaxed">{business.description}</p>
                </div>
              </div>
            {/if}
          </div>

          <!-- Tags -->
          {#if business.tags && business.tags.length}
            <div class="mb-8">
              <p class="text-[11px] text-white/30 font-mono uppercase tracking-wider mb-3">標籤</p>
              <div class="flex flex-wrap gap-2">
                {#each business.tags as tag}
                  <span class="text-sm px-3 py-1.5 rounded-full bg-white/5 text-white/40 border border-white/5">{tag}</span>
                {/each}
              </div>
            </div>
          {/if}

          <!-- Data source -->
          <div class="border-t border-white/5 pt-6">
            <p class="text-[11px] text-white/30 font-mono uppercase tracking-wider mb-3">資料來源</p>
            <div class="text-sm text-white/40 space-y-1.5">
              <p>來源：{business.source_name || '政府開放資料'}</p>
              {#if business.source_url}
                <a href={business.source_url} target="_blank" rel="noopener"
                  class="inline-flex items-center gap-1.5 text-gold hover:text-gold-light transition-colors mt-1">
                  原始資料集 →
                </a>
              {/if}
            </div>
          </div>
        </div>

        <!-- Back link -->
        <div class="mt-10 text-center">
          <a href="/directory"
            class="inline-flex items-center gap-2 text-sm text-white/30 hover:text-gold transition-colors">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"/>
            </svg>
            回到商家名錄
          </a>
        </div>
      </div>
    </div>
  {/if}
</div>
