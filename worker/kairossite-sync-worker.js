import { isStaleVersion, parseKairosSiteSync } from '../src/lib/server/kairossite-sync.js';

const reply = (body, status = 200) => Response.json(body, { status, headers: { 'cache-control': 'no-store' } });

async function authorized(request, expected) {
  const supplied = request.headers.get('authorization')?.replace(/^Bearer\s+/i, '') || '';
  if (!expected || !supplied) return false;
  const encode = (value) => crypto.subtle.digest('SHA-256', new TextEncoder().encode(value));
  const [left, right] = await Promise.all([encode(supplied), encode(expected)]);
  const expectedBytes = new Uint8Array(right);
  return new Uint8Array(left).every((byte, index) => byte === expectedBytes[index]);
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (request.method === 'GET' && url.pathname === '/healthz') return reply({ status: 'ok', service: 'bizmap-kairossite-sync' });
    if (request.method !== 'POST' || !['/sync', '/probe'].includes(url.pathname)) return reply({ error: 'not_found' }, 404);
    if (!env.BIZMAP_KV || !env.KAIROSSITE_SYNC_TOKEN) return reply({ error: 'sync_not_configured' }, 503);
    if (!await authorized(request, env.KAIROSSITE_SYNC_TOKEN)) return reply({ error: 'unauthorized' }, 401);
    if (url.pathname === '/probe') return reply({ status: 'ready', authenticated: true });

    let sync;
    try { sync = parseKairosSiteSync(await request.json()); }
    catch (error) { return reply({ error: error instanceof Error ? error.message : 'invalid_payload' }, 400); }

    const key = `kairossite:business:${sync.businessId}`;
    const current = await env.BIZMAP_KV.get(key, 'json');
    if (isStaleVersion(current, sync.version)) return reply({ error: 'stale_version' }, 409);

    const now = new Date().toISOString();
    const record = sync.operation === 'upsert'
      ? { ...sync, status: 'active', syncedAt: now }
      : { ...current, businessId: sync.businessId, version: sync.version, status: 'hidden', syncedAt: now };
    await env.BIZMAP_KV.put(key, JSON.stringify(record));
    // ponytail: KV has no atomic list update; move the index to D1 if concurrent publishers cause lost updates.
    const index = await env.BIZMAP_KV.get('kairossite:index', 'json') || [];
    await env.BIZMAP_KV.put('kairossite:index', JSON.stringify([sync.businessId, ...index.filter((id) => id !== sync.businessId)].slice(0, 5000)));
    return reply({ status: 'synced', operation: sync.operation, businessId: sync.businessId, version: sync.version });
  }
};
