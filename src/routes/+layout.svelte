<script>
  import '../app.css';
  import { page } from '$app/stores';

  $: isHome = $page.url.pathname === '/';
</script>

<!-- Navigation -->
<nav class="fixed top-4 left-1/2 -translate-x-1/2 z-50 w-[calc(100%-2rem)] max-w-5xl">
  <div class="glass-card px-6 h-14 flex items-center justify-between" style="background:rgba(12,12,14,0.85); backdrop-filter:blur(24px); border-color:rgba(255,255,255,0.08);">
    <a href="/" class="flex items-center gap-2 font-bold text-lg tracking-tight">
      <span class="text-white">
        biz<span style="color:var(--gold)">map</span>
      </span>
      <span class="text-[11px] font-normal text-white/30 font-mono tracking-wider">.tw</span>
    </a>
    <div class="flex items-center gap-1">
      <a href="/directory" class="px-3.5 py-2 rounded-lg text-sm text-white/60 hover:text-white hover:bg-white/5 transition-all">
        商家名錄
      </a>
      <a href="/about" class="px-3.5 py-2 rounded-lg text-sm text-white/60 hover:text-white hover:bg-white/5 transition-all">
        關於
      </a>
      <a href="/submit" class="ml-2 px-4 py-2 rounded-lg text-sm font-medium transition-all hover:-translate-y-0.5" style="background:var(--gold); color:var(--ink);">
        免費上架
      </a>
    </div>
  </div>
</nav>

<!-- Main Content -->
<main class="min-h-screen" class:pt-0={isHome} class:pt-24={!isHome}>
  <slot />
</main>

<!-- Footer -->
<footer class="border-t border-white/5 bg-ink-950">
  <div class="max-w-6xl mx-auto px-6 py-16">
    <div class="grid grid-cols-1 md:grid-cols-4 gap-10 mb-12">
      <div class="md:col-span-2">
        <div class="flex items-center gap-2 font-bold text-lg text-white mb-4">
          biz<span style="color:var(--gold)">map</span><span class="text-[11px] font-normal text-white/30 font-mono">.tw</span>
        </div>
        <p class="text-sm text-white/40 leading-relaxed max-w-sm">
          台灣在地商家名錄平台 — 收錄全台經政府開放資料驗證的商家資訊，讓消費者快速找到值得信賴的在地好店。
        </p>
      </div>
      <div>
        <div class="text-xs font-mono tracking-widest text-white/30 mb-4 uppercase">資源</div>
        <div class="flex flex-col gap-3">
          <a href="/directory" class="text-sm text-white/50 hover:text-gold transition-colors">商家名錄</a>
          <a href="/about" class="text-sm text-white/50 hover:text-gold transition-colors">關於平台</a>
          <a href="/submit" class="text-sm text-white/50 hover:text-gold transition-colors">免費上架</a>
        </div>
      </div>
      <div>
        <div class="text-xs font-mono tracking-widest text-white/30 mb-4 uppercase">連結</div>
        <div class="flex flex-col gap-3">
          <a href="https://kairoslink.tw" class="text-sm text-white/50 hover:text-gold transition-colors">KairosLink</a>
          <a href="https://github.com/kaochaoting" class="text-sm text-white/50 hover:text-gold transition-colors">GitHub</a>
        </div>
      </div>
    </div>
    <div class="pt-8 border-t border-white/5 flex flex-col md:flex-row justify-between items-center gap-4">
      <div class="text-xs text-white/20">
        &copy; {new Date().getFullYear()} bizmap.tw — 台灣商家名錄
      </div>
      <div class="text-xs text-white/20">
        Powered by <a href="https://kairoslink.tw" class="text-white/40 hover:text-gold transition-colors">KairosLink</a>
      </div>
    </div>
  </div>
</footer>
