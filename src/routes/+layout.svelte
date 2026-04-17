<script>
  import '../app.css';
  import { page } from '$app/stores';
</script>

<nav class="fixed top-0 left-0 right-0 z-50 bg-white/90 backdrop-blur border-b border-gray-100">
  <div class="max-w-6xl mx-auto px-6 h-16 flex items-center justify-between">
    <a href="/" class="font-bold text-xl text-gray-900">
      biz<span style="color:var(--gold)">map</span><span class="text-sm font-normal text-gray-400">.tw</span>
    </a>
    <div class="flex items-center gap-6 text-sm text-gray-500">
      <a href="/directory" class="hover:text-gray-900 transition-colors">商家名錄</a>
      <a href="/about" class="hover:text-gray-900 transition-colors">關於</a>
      <a href="/submit" class="px-4 py-2 rounded-lg text-white text-sm font-medium transition-all hover:-translate-y-0.5" style="background:var(--ink)">免費上架</a>
    </div>
  </div>
</nav>

<main class="pt-16">
  <slot />
</main>

<footer class="mt-20 border-t border-gray-100 py-12 bg-gray-50">
  <div class="max-w-6xl mx-auto px-6 flex flex-col md:flex-row justify-between items-center gap-4 text-sm text-gray-400">
    <span>© 2024 bizmap.tw — 台灣商家名錄</span>
    <span>Powered by <a href="https://kairoslink.tw" class="hover:text-gray-600">KairosLink</a></span>
  </div>
</footer>
