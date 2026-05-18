#!/usr/bin/env python3
import urllib.request, json, os

token = os.environ.get('CLOUDFLARE_API_TOKEN', '')
account_id = '1369bf328feafa4871b71ef5afde505b'

# Check latest deployments
req = urllib.request.Request(
    f'https://api.cloudflare.com/client/v4/accounts/{account_id}/pages/projects/bizmap/deployments',
    headers={'Authorization': f'Bearer {token}'}
)
try:
    resp = urllib.request.urlopen(req, timeout=15)
    data = json.loads(resp.read())
    if data.get('success'):
        deploys = data.get('result', [])
        if deploys:
            latest = deploys[0]
            meta = latest.get('deployment_trigger', {}).get('metadata', {})
            commit = meta.get('commit_message', 'N/A')[:60]
            env = latest.get('environment', 'N/A')
            dep_id = latest.get('short_id', 'N/A')
            created = latest.get('created_on', 'N/A')[:16]
            print(f"Latest: {dep_id} | {created} | {env}")
            print(f"Commit: {commit}")
            # Check stages
            for s in latest.get('stages', []):
                print(f"  Stage '{s['name']}': {s.get('status', '?')}")
        else:
            print("No deployments found")
    else:
        print('API Error:', json.dumps(data.get('errors'), indent=2)[:300])
except Exception as e:
    print(f'Error: {e}')
