<script>
  import { page } from '$app/stores';

  const businesses = [
    { id: 1, name: '好食堂餐廳', category: '餐飲美食', city: '高雄', district: '苓雅區', address: '苓雅路123號', phone: '07-123-4567', tags: ['台式料理','合菜','聚餐'] },
    { id: 2, name: '美顏髮廊', category: '美容美髮', city: '高雄', district: '三民區', address: '建工路88號', phone: '07-234-5678', tags: ['剪髮','染髮','護髮'] },
    { id: 3, name: '活力健身房', category: '健身運動', city: '高雄', district: '前鎮區', address: '中華五路200號', phone: '07-345-6789', tags: ['健身','重訓','有氧'] },
    { id: 4, name: '仁愛診所', category: '醫療健康', city: '高雄', district: '鼓山區', address: '明誠路56號', phone: '07-456-7890', tags: ['家醫科','內科'] },
    { id: 5, name: '精英補習班', category: '教育補習', city: '高雄', district: '左營區', address: '重愛路77號', phone: '07-567-8901', tags: ['國中','高中','數學'] },
    { id: 6, name: '整潔居家清潔', category: '居家服務', city: '高雄', district: '楠梓區', address: '後昌路45號', phone: '07-678-9012', tags: ['居家清潔','定期打掃'] },
  ];
</script>

<svelte:head>
  <title>商家名錄 — bizmap.tw</title>
  <meta name="description" content="瀏覽台灣各地商家名錄，涵蓋餐飲、美容、醫療、教育等各類服務。">
</svelte:head>

<div class="max-w-6xl mx-auto px-6 py-12">
  <div class="mb-10">
    <p class="text-xs font-mono tracking-widest mb-2" style="color: var(--gold)">DIRECTORY</p>
    <h1 class="text-3xl font-bold text-gray-900">台灣商家名錄</h1>
    <p class="text-gray-500 mt-2">收錄全台經過驗證的優質商家</p>
  </div>

  <div class="grid md:grid-cols-2 lg:grid-cols-3 gap-5">
    {#each businesses as biz}
      <div class="bg-white rounded-2xl border border-gray-100 p-5 hover:border-yellow-300 hover:-translate-y-1 transition-all">
        <div class="flex items-start justify-between mb-3">
          <div>
            <span class="text-xs px-2 py-0.5 rounded-full bg-yellow-50 text-yellow-700 font-mono">{biz.category}</span>
            <h3 class="font-semibold text-gray-900 mt-2">{biz.name}</h3>
            <p class="text-sm text-gray-500">{biz.city} · {biz.district}</p>
          </div>
        </div>
        <div class="text-sm text-gray-600 space-y-1 mb-4">
          <p>📍 {biz.address}</p>
          <p>📞 {biz.phone}</p>
        </div>
        <div class="flex flex-wrap gap-1.5">
          {#each biz.tags as tag}
            <span class="text-xs px-2 py-0.5 rounded-full bg-gray-100 text-gray-500">{tag}</span>
          {/each}
        </div>
      </div>
    {/each}
  </div>
</div>
