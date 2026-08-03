import { json } from '@sveltejs/kit';

const limits = {
  business_name: 120,
  category_slug: 20,
  city: 20,
  district: 20,
  address: 200,
  phone: 40,
  site_url: 300,
  contact_email: 254,
  description: 1000
};
const categories = {
  food: '餐飲美食', beauty: '美容美髮', fitness: '健身運動', medical: '醫療健康',
  home: '居家服務', education: '教育補習', business: '商業服務', retail: '零售購物',
  transport: '交通運輸', industrial: '工業製品'
};
const cities = new Set([
  '台北市', '新北市', '桃園市', '台中市', '台南市', '高雄市', '基隆市', '新竹市',
  '嘉義市', '新竹縣', '苗栗縣', '彰化縣', '南投縣', '雲林縣', '嘉義縣', '屏東縣',
  '宜蘭縣', '花蓮縣', '台東縣', '澎湖縣', '金門縣', '連江縣'
]);
const requiredFields = ['business_name', 'category_slug', 'city', 'address', 'phone', 'contact_email'];

function normalizeText(value) {
  return String(value || '').trim().replace(/\s+/g, ' ');
}

function normalizeUrl(value) {
  const text = normalizeText(value);
  if (!text) return '';
  const url = new URL(/^https?:\/\//i.test(text) ? text : `https://${text}`);
  if (!['http:', 'https:'].includes(url.protocol)) throw new Error('invalid_url');
  return url.toString();
}

async function rateLimit(kv, request) {
  const ip = request.headers.get('CF-Connecting-IP') || 'unknown';
  const digest = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(ip));
  const client = [...new Uint8Array(digest)].slice(0, 8).map((byte) => byte.toString(16).padStart(2, '0')).join('');
  const hour = new Date().toISOString().slice(0, 13);
  const key = `rate:submission:${client}:${hour}`;
  const count = Number(await kv.get(key) || 0);
  if (count >= 5) return false;

  // ponytail: KV counters are best-effort; use a Durable Object if strict atomic limits become necessary.
  await kv.put(key, String(count + 1), { expirationTtl: 7200 });
  return true;
}

export async function POST({ request, platform }) {
  if (!request.headers.get('content-type')?.includes('application/json')) {
    return json({ error: 'invalid_content_type' }, { status: 415 });
  }

  const kv = platform?.env?.BIZMAP_KV;
  if (!kv) return json({ error: 'storage_not_configured' }, { status: 503 });
  if (!await rateLimit(kv, request)) return json({ error: 'rate_limited' }, { status: 429 });

  let body;
  try {
    body = await request.json();
  } catch {
    return json({ error: 'invalid_json' }, { status: 400 });
  }

  if (normalizeText(body.company_fax)) {
    return json({ success: true, review_status: 'pending' });
  }

  const record = Object.fromEntries(Object.keys(limits).map((field) => [field, normalizeText(body[field])]));
  const missing = requiredFields.filter((field) => !record[field]);
  if (missing.length) return json({ error: 'missing_required_fields', fields: missing }, { status: 400 });

  const oversized = Object.entries(limits).filter(([field, limit]) => record[field].length > limit).map(([field]) => field);
  if (oversized.length) return json({ error: 'field_too_long', fields: oversized }, { status: 400 });
  if (!categories[record.category_slug]) return json({ error: 'invalid_category' }, { status: 400 });
  if (!cities.has(record.city)) return json({ error: 'invalid_city' }, { status: 400 });
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(record.contact_email)) {
    return json({ error: 'invalid_email' }, { status: 400 });
  }

  try {
    record.site_url = normalizeUrl(record.site_url);
  } catch {
    return json({ error: 'invalid_url' }, { status: 400 });
  }

  const now = new Date().toISOString();
  const id = `submission_${Date.now()}_${crypto.randomUUID().slice(0, 8)}`;
  const submission = {
    submission_id: id,
    ...record,
    category: categories[record.category_slug],
    source_type: 'owner_submitted',
    source_name: 'BizMap 免費上架表單',
    source_url: 'https://bizmap.tw/submit',
    source_license: '商家自行提交授權',
    source_updated_at: now.slice(0, 10),
    claim_status: 'pending',
    review_status: 'pending',
    removal_status: 'active',
    created_at: now
  };

  await kv.put(`submission:${id}`, JSON.stringify(submission));
  const indexRaw = await kv.get('index:submissions');
  const index = indexRaw ? JSON.parse(indexRaw) : [];
  index.unshift({ id, business_name: submission.business_name, created_at: now, review_status: 'pending' });
  // ponytail: this compact index is best-effort; use D1 if concurrent editorial workflows outgrow KV.
  await kv.put('index:submissions', JSON.stringify(index.slice(0, 1000)));

  return json({ success: true, submission_id: id, review_status: 'pending' });
}
