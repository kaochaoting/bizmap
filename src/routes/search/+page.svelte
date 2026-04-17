<script>
  import { page } from '$app/stores';
  $: query = $page.url.searchParams.get('q') || '';
</script>

<svelte:head>
  <title>{query ? `"${query}" 搜尋結果` : '搜尋商家'} — bizmap.tw</title>
</svelte:head>

<div class="max-w-6xl mx-auto px-6 py-12">
  <h1 class="text-2xl font-bold text-gray-900 mb-2">
    {query ? `「${query}」的搜尋結果` : '搜尋商家'}
  </h1>
  <p class="text-gray-500 mb-8">資料庫建置中，完整搜尋功能即將上線。</p>
  <a href="/directory" class="px-5 py-3 rounded-xl text-sm font-medium text-white inline-block" style="background: var(--ink)">
    瀏覽商家名錄 →
  </a>
</div>
