import assert from 'node:assert/strict';
import test from 'node:test';

import { POST } from '../src/routes/api/submissions/+server.js';


function mockKv() {
  const values = new Map();
  return {
    values,
    get: async (key) => values.get(key) ?? null,
    put: async (key, value) => values.set(key, value)
  };
}

function request(body, ip = '203.0.113.1') {
  return new Request('https://bizmap.tw/api/submissions', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'CF-Connecting-IP': ip },
    body: JSON.stringify(body)
  });
}

const validSubmission = {
  business_name: '測試商家',
  category: '餐飲美食',
  category_slug: 'food',
  city: '高雄市',
  district: '苓雅區',
  address: '測試路 1 號',
  phone: '07-1234567',
  site_url: 'example.com',
  contact_email: 'owner@example.com',
  description: '僅供自動測試'
};

test('stores a valid submission as pending', async () => {
  const kv = mockKv();
  const response = await POST({ request: request(validSubmission), platform: { env: { BIZMAP_KV: kv } } });
  const result = await response.json();

  assert.equal(response.status, 200);
  assert.equal(result.review_status, 'pending');
  const stored = JSON.parse(kv.values.get(`submission:${result.submission_id}`));
  assert.equal(stored.review_status, 'pending');
  assert.equal(stored.site_url, 'https://example.com/');
});

test('rejects invalid contact data', async () => {
  const kv = mockKv();
  const response = await POST({
    request: request({ ...validSubmission, contact_email: 'invalid' }, '203.0.113.2'),
    platform: { env: { BIZMAP_KV: kv } }
  });

  assert.equal(response.status, 400);
  assert.equal((await response.json()).error, 'invalid_email');
});

test('rejects categories outside the published taxonomy', async () => {
  const kv = mockKv();
  const response = await POST({
    request: request({ ...validSubmission, category_slug: 'admin' }, '203.0.113.4'),
    platform: { env: { BIZMAP_KV: kv } }
  });

  assert.equal(response.status, 400);
  assert.equal((await response.json()).error, 'invalid_category');
});

test('rate limits repeated submissions', async () => {
  const kv = mockKv();
  let response;
  for (let attempt = 0; attempt < 6; attempt += 1) {
    response = await POST({
      request: request(validSubmission, '203.0.113.3'),
      platform: { env: { BIZMAP_KV: kv } }
    });
  }

  assert.equal(response.status, 429);
  assert.equal((await response.json()).error, 'rate_limited');
});
