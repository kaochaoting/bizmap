import test from 'node:test';
import assert from 'node:assert/strict';
import { isStaleVersion, parseKairosSiteSync } from '../src/lib/server/kairossite-sync.js';

test('accepts a valid Kairos.Site upsert and normalizes text', () => {
  const result = parseKairosSiteSync({ operation: 'upsert', payload: {
    businessId: 'business-1', version: '1784540000000', businessName: '  測試  商家 ',
    category: '餐飲', region: '高雄市', siteUrl: 'https://kairossite.com/b/test-shop'
  }});
  assert.equal(result.businessName, '測試 商家');
  assert.equal(result.siteUrl, 'https://kairossite.com/b/test-shop');
});

test('rejects an off-domain URL and stale versions', () => {
  assert.throws(() => parseKairosSiteSync({ operation: 'upsert', payload: {
    businessId: 'business-1', version: '1784540000000', businessName: '測試', category: '餐飲', region: '高雄市', siteUrl: 'https://example.com/b/test'
  }}), /invalid_business/);
  assert.equal(isStaleVersion({ version: '1784540000001' }, '1784540000000'), true);
});

test('accepts a minimal hide payload', () => {
  assert.deepEqual(parseKairosSiteSync({ operation: 'hide', payload: {
    businessId: 'business-1', version: '1784540000002'
  }}), { operation: 'hide', businessId: 'business-1', version: '1784540000002' });
});
