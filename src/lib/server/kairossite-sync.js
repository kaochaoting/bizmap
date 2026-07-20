const text = (value, max = 200) => typeof value === 'string' ? value.trim().replace(/\s+/g, ' ').slice(0, max) : '';

export function parseKairosSiteSync(body) {
  if (!body || typeof body !== 'object') throw new Error('invalid_payload');
  const operation = body.operation;
  const payload = body.payload;
  if (!['upsert', 'hide'].includes(operation) || !payload || typeof payload !== 'object') throw new Error('invalid_payload');

  const businessId = text(payload.businessId, 80);
  const version = text(payload.version, 24);
  if (!businessId || !/^\d{10,24}$/.test(version)) throw new Error('invalid_identity');

  if (operation === 'hide') return { operation, businessId, version };

  const businessName = text(payload.businessName, 120);
  const category = text(payload.category, 80);
  const region = text(payload.region, 80);
  const siteUrl = text(payload.siteUrl, 300);
  let url;
  try { url = new URL(siteUrl); } catch { throw new Error('invalid_site_url'); }
  if (!businessName || !category || !region || url.protocol !== 'https:' || url.hostname !== 'kairossite.com' || !url.pathname.startsWith('/b/')) {
    throw new Error('invalid_business');
  }
  return { operation, businessId, version, businessName, category, region, siteUrl: url.href };
}

export function isStaleVersion(current, incoming) {
  return Boolean(current?.version) && BigInt(incoming) < BigInt(current.version);
}
