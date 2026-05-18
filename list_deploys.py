#!/usr/bin/env python3
import urllib.request, json, os

token = os.environ.get('CLOUDFLARE_API_TOKEN', '')
account_id = '1369bf328feafa4871b71ef5afde505b'

req = urllib.request.Request(
    f'https://api.cloudflare.com/client/v4/accounts/{account_id}/pages/projects/bizmap/deployments',
    headers={'Authorization': f'Bearer {token}'}
)
try:
    resp = urllib.request.urlopen(req, timeout=15)
    data = json.loads(resp.read())
    if data.get('success'):
        deploys = data.get('result', [])
        print(f"Total: {len(deploys)}")
        for d in deploys[:5]:
            meta = d.get('deployment_trigger', {}).get('metadata', {})
            print(f"  {d.get('short_id', '?')} | {d.get('created_on', '?')[:16]} | {d.get('environment', '?')} | {meta.get('commit_message', '?')[:60]}")
    else:
        print('API Error:', data.get('errors'))
except Exception as e:
    print(f'Error: {e}')
