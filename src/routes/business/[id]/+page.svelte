<script>
  import { page } from '$app/stores';
  import { onMount } from 'svelte';

  let business = null;
  let loading = true;
  let error = false;

  $: businessId = $page.params.id;

  const categoryNames = {
    food: '餐飲美食', beauty: '美容美髮', fitness: '健身運動',
    medical: '醫療健康', home: '居家服務', education: '教育補習',
    business: '商業服務', retail: '零售購物', transport: '交通運輸',
    industrial: '工業製品',
  };

  onMount(async () => {
    try {
      // Step 1: Load routing table → find category slug
      const routeRes = await fetch('/data/id-lookup/routing.json');
      const routing = await routeRes.json();
      const slug = routing[businessId];
      if (!slug) { error = true; loading = false; return; }

      // Step 2: Load index to get file list for this category
      const idxRes = await fetch('/data/index.json');
      const idx = await idxRes.json();
      const fileList = (idx.files || {})[slug] || [];
      if (!fileList.length) { error = true; loading = false; return; }

      // Step 3: Iterate files to find matching business
      for (const fm of fileList) {
        const r = await fetch(`/data/${fm.file}`);
        if (!r.ok) continue;
        const d = await r.json();

        // Stub file
        if (d.files && Array.isArray(d.files) && !d.businesses?.length) {
          const baseDir = fm.file.replace('.json', '');
          for (const sf of d.files) {
            const sr = await fetch(`/data/${baseDir}/${sf}`);
            if (!sr.ok) continue;
            const sd = await sr.json();
            const found = (sd.businesses || []).find(b => b.business_id === businessId);
            if (found) { business = found; break; }
          }
        }
        // Direct file
        else if (d.businesses?.length) {
          const found = d.businesses.find(b => b.business_id === businessId);
          if (found) { business = found; break; }
        }
        if (business) break;
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
        <a href="/directory" class="inline-flex items-center gap-2 px-6 py-3 rounded-lg font-medium transition-all hover:-translate-y-0.5"
          style="background:var(--gold); color:var(--ink);">
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
          <a href="/directory?category={categoryNames[business.category_slug] ? business.category_slug : ''}" class="hover:text-gold transition-colors">
            {categoryNames[business.category_slug] || business.category || '分類'}
          </a>
          <span>/</span>
          <span class="text-white/50">{business.business_name}</span>
        </nav>

        <!-- Main card -->
        <div class="glass-card-dark p-8 sm:p-10 rounded-2xl" style="background:rgba(12,12,14,0.96); border-color:rgba(255,255,255,0.06);">

          <!-- Header -->
          <div class="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4 mb-10">
            <div>
              <div class="flex items-center gap-3 mb-4 flex-wrap">
                {#if business.city}
                  <span class="text-[11px] px-3 py-1 rounded-full bg-white/5 text-white/40 border border-white/5">
                    {business.city}
                  </span>
                {/if}
                <span class="text-[11px] px-3 py-1 rounded-full font-mono uppercase tracking-wider"
                  style="background:rgba(200,168,75,0.12); color:var(--gold); border:1px solid rgba(200,168,75,0.2);">
                  {categoryNames[business.category_slug] || business.category || '商家'}
                </span>
              </div>
              <h1 class="text-3xl sm:text-4xl font-bold text-white tracking-tight">{business.business_name}</h1>
              {#if business.region}
                <p class="text-white/40 mt-2">{business.region}</p>
              {/if}
            </div>
          </div>

          <!-- Info Grid — 基礎資料 -->
          <div class="grid sm:grid-cols-2 gap-4 mb-10">
            {#if business.address}
              <div class="flex items-start gap-4 p-5 rounded-xl bg-white/5 border border-white/5">
                <span class="text-xl mt-0.5">📍</span>
                <div class="flex-1 min-w-0">
                  <p class="text-[11px] text-white/30 font-mono uppercase tracking-wider mb-1">地址</p>
                  <p class="text-white/80 mb-2">{business.address}</p>
                  {#if business.district}
                    <p class="text-[10px] text-white/20 mb-2">{business.district}</p>
                  {/if}
                  <a
                    href="https://www.google.com/maps/search/{encodeURIComponent(business.address)}"
                    target="_blank" rel="noopener"
                    class="inline-flex items-center gap-1.5 text-xs text-gold hover:text-gold-light transition-colors"
                  >
                    <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"/></svg>
                    在地圖開啟
                  </a>
                </div>
              </div>
            {/if}
            {#if business.phone}
              <div class="flex items-start gap-4 p-5 rounded-xl bg-white/5 border border-white/5">
                <span class="text-xl mt-0.5">📞</span>
                <div>
                  <p class="text-[11px] text-white/30 font-mono uppercase tracking-wider mb-1">電話</p>
                  <a href="tel:{business.phone.replace(/\s|-|\(|\)/g,'')}"
                    class="text-white/80 hover:text-gold transition-colors text-lg font-medium tracking-wide">
                    {business.phone}
                  </a>
                </div>
              </div>
            {/if}
          </div>

          <!-- City + Region tags -->
          {#if business.city}
            <div class="flex flex-wrap items-center gap-2 mb-8">
              <a href="/city/{business.city}"
                class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium border transition-all hover:-translate-y-0.5"
                style="background:rgba(200,168,75,0.08); border-color:rgba(200,168,75,0.2); color:var(--gold);">
                <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"/></svg>
                {business.city}
              </a>
              {#if business.region}
                <span class="text-xs text-white/20">{business.region}</span>
              {/if}
            </div>
          {/if}

          <!-- Description -->
          {#if business.description}
            <div class="mb-8">
              <p class="text-[11px] text-white/30 font-mono uppercase tracking-wider mb-3">簡介</p>
              <p class="text-white/70 leading-relaxed">{business.description}</p>
            </div>
          {/if}

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

          <!-- ── KairosSite 導引 ─────────────────────────────── -->
          <div class="rounded-xl p-6 text-center"
            style="background: linear-gradient(135deg, rgba(200,168,75,0.08) 0%, rgba(200,168,75,0.03) 100%); border: 1px solid rgba(200,168,75,0.15);">
            <div class="text-2xl mb-2">✨</div>
            <h3 class="text-white font-semibold mb-1">想让这家店拥有自己的网站吗？</h3>
            <p class="text-white/40 text-sm mb-4">使用 KairosSite 快速为商家建立专业形象页，包含预约、地图导航、客户评价等功能。</p>
            <a href="https://kairossite.com" target="_blank" rel="noopener"
              class="inline-flex items-center gap-2 px-5 py-2.5 rounded-lg font-medium text-sm transition-all hover:-translate-y-0.5"
              style="background:var(--gold); color:var(--ink);">
              前往 KairosSite →
            </a>
          </div>

          <!-- Data source -->
          <div class="border-t border-white/5 pt-6 mt-6">
            <p class="text-[11px] text-white/30 font-mono uppercase tracking-wider mb-3">資料來源</p>
            <div class="text-sm text-white/40 space-y-1.5">
              <p>来源：{business.source_name || '政府開放資料'}</p>
              {#if business.source_updated_at}
                <p>更新：{business.source_updated_at.split('T')[0]}</p>
              {/if}
              {#if business.source_url}
                <a href={business.source_url} target="_blank" rel="noopener"
                  class="inline-flex items-center gap-1.5 text-gold hover:text-gold-light transition-colors mt-1">
                  原始資料集 →
                </a>
              {/if}
            </div>
          </div>
        </div>

        <!-- Action buttons -->
        <div class="flex justify-center gap-4 mt-8 flex-wrap">
          <a href="/directory?category={business.category_slug}"
            class="flex items-center gap-2 px-5 py-2.5 rounded-lg text-sm font-medium border transition-all hover:-translate-y-0.5"
            style="border-color:rgba(255,255,255,0.1); color:rgba(255,255,255,0.5);">
            ← 同類商家
          </a>
          <a href="/directory"
            class="flex items-center gap-2 px-5 py-2.5 rounded-lg text-sm font-medium border transition-all hover:-translate-y-0.5"
            style="border-color:rgba(255,255,255,0.1); color:rgba(255,255,255,0.5);">
            商家名錄
          </a>
        </div>

        <!-- Back link -->
        <div class="mt-8 text-center">
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

<style>
  .glass-card-dark {
    backdrop-filter: blur(12px);
    box-shadow: 0 8px 32px rgba(0,0,0,0.4);
  }
</style>