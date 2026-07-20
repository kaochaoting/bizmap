import { json } from '@sveltejs/kit';
import { isStaleVersion, parseKairosSiteSync } from '$lib/server/kairossite-sync.js';

async function authorized(request, expected) {
  const supplied = request.headers.get('authorization')?.replace(/^Bearer\s+/i, '') || '';
  if (!expected || !supplied) return false;
  const encode = (value) => crypto.subtle.digest('SHA-256', new TextEncoder().encode(value));
  const [left, right] = await Promise.all([encode(supplied), encode(expected)]);
  return new Uint8Array(left).every((byte, index) => byte === new Uint8Array(right)[index]);
}

export async function POST({ request, platform }) {
  const env = platform?.env;
  if (!env?.BIZMAP_KV || !env.KAIROSSITE_SYNC_TOKEN) return json({ error: 'sync_not_configured' }, { status: 503 });
  if (!await authorized(request, env.KAIROSSITE_SYNC_TOKEN)) return json({ error: 'unauthorized' }, { status: 401 });

  let sync;
  try { sync = parseKairosSiteSync(await request.json()); }
  catch (error) { return json({ error: error instanceof Error ? error.message : 'invalid_payload' }, { status: 400 }); }

  const key = `kairossite:business:${sync.businessId}`;
  const current = await env.BIZMAP_KV.get(key, 'json');
  if (isStaleVersion(current, sync.version)) return json({ error: 'stale_version' }, { status: 409 });

  const now = new Date().toISOString();
  const record = sync.operation === 'upsert'
    ? { ...sync, status: 'active', syncedAt: now }
    : { ...current, businessId: sync.businessId, version: sync.version, status: 'hidden', syncedAt: now };
  await env.BIZMAP_KV.put(key, JSON.stringify(record));

  // ponytail: KV has no atomic list update; move the index to D1 if concurrent publishers cause lost updates.
  const index = await env.BIZMAP_KV.get('kairossite:index', 'json') || [];
  const next = [sync.businessId, ...index.filter((id) => id !== sync.businessId)].slice(0, 5000);
  await env.BIZMAP_KV.put('kairossite:index', JSON.stringify(next));

  return json({ status: 'synced', operation: sync.operation, businessId: sync.businessId, version: sync.version });
}
