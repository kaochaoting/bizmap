<script>
  import indexData from '../../../static/data/index.json';

  const total = indexData.total.toLocaleString();
  const cityCount = Object.keys(indexData.city_counts).length;
</script>

<svelte:head>
  <title>關於 bizmap.tw — 台灣商家名錄</title>
</svelte:head>

<section class="relative overflow-hidden py-20 px-6" style="background: linear-gradient(160deg, #0c0c0e 0%, #1e2330 50%, #0c0c0e 100%);">
  <div class="absolute inset-0 opacity-[0.03]"
    style="background-image: linear-gradient(rgba(200,168,75,0.5) 1px, transparent 1px), linear-gradient(90deg, rgba(200,168,75,0.5) 1px, transparent 1px); background-size: 48px 48px;">
  </div>
  <div class="relative max-w-3xl mx-auto">
    <div class="section-label section-label-gold mb-4 w-fit">ABOUT</div>
    <h1 class="text-4xl font-bold text-white tracking-tight mb-3">關於 bizmap.tw</h1>
    <p class="text-white/40">資料來源可追溯的台灣在地商家名錄</p>
  </div>
</section>

<div class="max-w-3xl mx-auto px-6 -mt-8 relative z-10 pb-24">
  <div class="glass-card-dark p-8 sm:p-10 space-y-6" style="background:rgba(12,12,14,0.95);">
    <p class="text-white/70 leading-relaxed">
      bizmap.tw 是由 <a href="https://kairoslink.tw" class="text-gold hover:text-gold-light transition-colors">KairosLink</a> 團隊建立與維護的台灣在地商家名錄。
    </p>
    <p class="text-white/60 leading-relaxed">
      我們相信每一家在地商家都應該被找到。透過系統化的資料收集與 NAP（名稱、地址、電話）一致性管理，bizmap.tw 幫助商家建立可信賴的數位存在，同時讓消費者快速找到所需服務。
    </p>

    <div class="pt-6 border-t border-white/5">
      <h2 class="text-xl font-semibold text-white mb-4">我們的使命</h2>
      <p class="text-white/60 leading-relaxed">
        讓台灣每一家優質在地商家，都能在 Google 搜尋與 AI 摘要中被正確找到。
      </p>
    </div>

    <div class="pt-6 border-t border-white/5">
      <h2 class="text-xl font-semibold text-white mb-4">聯絡我們</h2>
      <p class="text-white/60 leading-relaxed">
        商家上架、資料更正、合作洽詢，請聯繫：
        <a href="mailto:hello@kairoslink.tw" class="text-gold hover:text-gold-light transition-colors">hello@kairoslink.tw</a>
      </p>
    </div>

    <!-- Stats card -->
    <div class="pt-6 border-t border-white/5">
      <div class="grid grid-cols-2 md:grid-cols-3 gap-4">
        <div class="text-center p-4 rounded-xl bg-white/5">
          <div class="text-2xl font-bold text-gold">{total}</div>
          <div class="text-xs text-white/30 mt-1">收錄商家</div>
        </div>
        <div class="text-center p-4 rounded-xl bg-white/5">
          <div class="text-2xl font-bold text-gold">{cityCount}</div>
          <div class="text-xs text-white/30 mt-1">縣市覆蓋</div>
        </div>
        <div class="text-center p-4 rounded-xl bg-white/5">
          <div class="text-2xl font-bold text-gold">100%</div>
          <div class="text-xs text-white/30 mt-1">政府來源</div>
        </div>
      </div>
    </div>
  </div>
</div>
