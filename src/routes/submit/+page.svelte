<script>
  const categories = {
    food: '餐飲美食', beauty: '美容美髮', fitness: '健身運動', medical: '醫療健康',
    home: '居家服務', education: '教育補習', business: '商業服務', retail: '零售購物',
    transport: '交通運輸', industrial: '工業製品'
  };
  const cities = [
    '台北市', '新北市', '桃園市', '台中市', '台南市', '高雄市',
    '基隆市', '新竹市', '嘉義市', '新竹縣', '苗栗縣', '彰化縣',
    '南投縣', '雲林縣', '嘉義縣', '屏東縣', '宜蘭縣', '花蓮縣',
    '台東縣', '澎湖縣', '金門縣', '連江縣'
  ];

  const emptyForm = () => ({
    business_name: '', category_slug: '', city: '', district: '', address: '', phone: '',
    site_url: '', contact_email: '', description: '', company_fax: ''
  });

  let form = emptyForm();
  let status = 'idle';
  let message = '';

  async function submitListing() {
    status = 'submitting';
    message = '';

    try {
      const response = await fetch('/api/submissions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(form)
      });
      const result = await response.json();
      if (!response.ok) throw new Error(result.error || 'submit_failed');

      status = 'success';
      message = result.submission_id
        ? `申請已送出，案件編號：${result.submission_id}`
        : '申請已送出，將進入人工審核。';
      form = emptyForm();
    } catch (error) {
      status = 'error';
      message = error.message === 'rate_limited'
        ? '送出次數過多，請稍後再試。'
        : error.message === 'storage_not_configured'
          ? '提交服務尚未完成設定，請改用 hello@kairoslink.tw 聯繫。'
          : '資料未送出，請檢查必填欄位與格式後再試一次。';
    }
  }
</script>

<svelte:head>
  <title>免費上架商家 — bizmap.tw</title>
  <meta name="description" content="免費將您的商家加入 bizmap.tw 台灣商家名錄，資料經人工審核後上架。">
</svelte:head>

<section class="relative overflow-hidden py-20 px-6" style="background: linear-gradient(160deg, #0c0c0e 0%, #1e2330 50%, #0c0c0e 100%);">
  <div class="absolute inset-0 opacity-[0.03]" style="background-image: linear-gradient(rgba(200,168,75,0.5) 1px, transparent 1px), linear-gradient(90deg, rgba(200,168,75,0.5) 1px, transparent 1px); background-size: 48px 48px;"></div>
  <div class="relative max-w-3xl mx-auto text-center">
    <div class="section-label section-label-gold mx-auto mb-4 w-fit">商家資料申請</div>
    <h1 class="text-4xl font-bold text-white tracking-tight mb-3">免費上架您的商家</h1>
    <p class="text-white/40">送出後進入人工審核；不會直接公開。</p>
  </div>
</section>

<div class="max-w-2xl mx-auto px-6 -mt-8 relative z-10 pb-24">
  <div class="glass-card-dark p-8" style="background:rgba(12,12,14,0.95);">
    <form class="space-y-5" on:submit|preventDefault={submitListing}>
      <div>
        <label for="business_name" class="block text-sm font-medium text-white/60 mb-1.5">商家名稱</label>
        <input id="business_name" bind:value={form.business_name} maxlength="120" required autocomplete="organization" placeholder="您的商家全名" class="form-field" />
      </div>

      <div class="grid sm:grid-cols-2 gap-5">
        <div>
          <label for="category_slug" class="block text-sm font-medium text-white/60 mb-1.5">商家類別</label>
          <select id="category_slug" bind:value={form.category_slug} required class="form-field">
            <option value="" disabled>請選擇類別</option>
            {#each Object.entries(categories) as [slug, name]}
              <option value={slug}>{name}</option>
            {/each}
          </select>
        </div>
        <div>
          <label for="city" class="block text-sm font-medium text-white/60 mb-1.5">縣市</label>
          <select id="city" bind:value={form.city} required class="form-field">
            <option value="" disabled>請選擇縣市</option>
            {#each cities as city}<option value={city}>{city}</option>{/each}
          </select>
        </div>
      </div>

      <div class="grid sm:grid-cols-[1fr_2fr] gap-5">
        <div>
          <label for="district" class="block text-sm font-medium text-white/60 mb-1.5">行政區</label>
          <input id="district" bind:value={form.district} maxlength="20" autocomplete="address-level3" placeholder="例：苓雅區" class="form-field" />
        </div>
        <div>
          <label for="address" class="block text-sm font-medium text-white/60 mb-1.5">地址</label>
          <input id="address" bind:value={form.address} maxlength="200" required autocomplete="street-address" placeholder="完整地址" class="form-field" />
        </div>
      </div>

      <div class="grid sm:grid-cols-2 gap-5">
        <div>
          <label for="phone" class="block text-sm font-medium text-white/60 mb-1.5">聯絡電話</label>
          <input id="phone" type="tel" bind:value={form.phone} maxlength="40" required autocomplete="tel" placeholder="市話或手機" class="form-field" />
        </div>
        <div>
          <label for="contact_email" class="block text-sm font-medium text-white/60 mb-1.5">聯絡信箱</label>
          <input id="contact_email" type="email" bind:value={form.contact_email} maxlength="254" required autocomplete="email" placeholder="name@example.com" class="form-field" />
        </div>
      </div>

      <div>
        <label for="site_url" class="block text-sm font-medium text-white/60 mb-1.5">網站或 Facebook</label>
        <input id="site_url" type="url" bind:value={form.site_url} maxlength="300" autocomplete="url" placeholder="https://" class="form-field" />
      </div>

      <div>
        <label for="description" class="block text-sm font-medium text-white/60 mb-1.5">商家簡介</label>
        <textarea id="description" rows="4" bind:value={form.description} maxlength="1000" placeholder="服務項目、營業特色或需要補充的資訊" class="form-field resize-none"></textarea>
      </div>

      <div class="absolute -left-[9999px]" aria-hidden="true">
        <label for="company_fax">公司傳真</label>
        <input id="company_fax" bind:value={form.company_fax} tabindex="-1" autocomplete="off" />
      </div>

      {#if message}
        <p role="status" aria-live="polite" class="rounded-card p-4 text-sm {status === 'success' ? 'bg-green-500/10 text-green-300' : 'bg-red-500/10 text-red-300'}">{message}</p>
      {/if}

      <button type="submit" disabled={status === 'submitting'} class="btn-primary w-full justify-center py-4 disabled:opacity-50 disabled:cursor-wait">
        {status === 'submitting' ? '送出中…' : '提交上架申請'}
      </button>
      <p class="text-xs text-white/25 text-center">送出代表您同意我們為審核及聯絡目的處理以上資料。</p>
    </form>
  </div>
</div>

<style>
  :global(.form-field) {
    width: 100%;
    border-radius: var(--radius-card);
    border: 1px solid rgb(255 255 255 / 0.1);
    background: rgb(255 255 255 / 0.05);
    padding: 0.75rem 1rem;
    color: white;
    font-size: 0.875rem;
    transition: border-color 200ms, background-color 200ms;
  }
  :global(.form-field:focus) {
    outline: 2px solid rgb(200 168 75 / 0.35);
    outline-offset: 2px;
    border-color: rgb(200 168 75 / 0.6);
  }
  :global(select.form-field option) { color: #111; }
</style>
