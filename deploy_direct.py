#!/usr/bin/env python3
"""Deploy to CF Pages using direct upload API."""
import os, json, io, zipfile
import urllib.request

TOKEN = os.environ.get('CLOUDFLARE_API_TOKEN', '')
ACCOUNT = '1369bf328feafa4871b71ef5afde505b'
BUILD_DIR = '/home/dministrator/bizmap/.svelte-kit/cloudflare'

# Step 1: Create zip (without businesses.json)
print("📦 Creating zip...")
buf = io.BytesIO()
total_size = 0
with zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED) as zf:
    for root, dirs, files in os.walk(BUILD_DIR):
        for f in files:
            fpath = os.path.join(root, f)
            arcname = os.path.relpath(fpath, BUILD_DIR)
            if arcname.startswith('.git/'): continue
            if 'businesses.json' in arcname: continue
            zf.write(fpath, arcname)
            total_size += os.path.getsize(fpath)
buf.seek(0)
sz = len(buf.getvalue())
print(f"  {sz/1024/1024:.1f} MB ({total_size/1024/1024:.1f} MB raw)")

if sz > 500 * 1024 * 1024:
    print("⚠️ Zip is >500MB, may take a while to upload")

# Step 2: Create a project's deployment with direct upload
# Based on CF API: POST /accounts/:id/pages/projects/:name/deployments
# with multipart form containing manifest + zip file
print("📤 Uploading...")

boundary = '----HermesDeployBoundary'

# Generate manifest - list all files
manifest_items = []
with zipfile.ZipFile(io.BytesIO(buf.getvalue()), 'r') as zf:
    for name in zf.namelist():
        if not name.endswith('/'):
            info = zf.getinfo(name)
            manifest_items.append({
                "path": name,
                "type": "file",
                "size": info.file_size
            })

# Build multipart body
import uuid
def w(s): return s.encode() if isinstance(s, str) else s

body_parts = []
# Part 1: manifest
body_parts.append(f'--{boundary}\r\n'.encode())
body_parts.append(b'Content-Disposition: form-data; name="manifest"\r\n')
body_parts.append(b'Content-Type: application/json\r\n\r\n')
body_parts.append(json.dumps(manifest_items).encode())
body_parts.append(b'\r\n')

# Part 2: zip file
body_parts.append(f'--{boundary}\r\n'.encode())
body_parts.append(b'Content-Disposition: form-data; name="file"; filename="build.zip"\r\n')
body_parts.append(b'Content-Type: application/zip\r\n\r\n')
body_parts.append(buf.getvalue())
body_parts.append(b'\r\n')

# End
body_parts.append(f'--{boundary}--\r\n'.encode())

body = b''.join(body_parts)

req = urllib.request.Request(
    f'https://api.cloudflare.com/client/v4/accounts/{ACCOUNT}/pages/projects/bizmap/deployments',
    data=body,
    headers={
        'Authorization': f'Bearer {TOKEN}',
        'Content-Type': f'multipart/form-data; boundary={boundary}',
        'Content-Range': f'bytes */{sz}'
    },
    method='POST'
)

try:
    resp = urllib.request.urlopen(req, timeout=600)
    result = json.loads(resp.read())
    if result.get('success'):
        d = result.get('result', {})
        print(f"\n✅ Deploy successful!")
        print(f"  Deploy ID: {d.get('short_id', 'N/A')}")
        print(f"  URL: https://bizmap.tw")
    else:
        print(f"\n❌ API Error: {json.dumps(result.get('errors', result), indent=2)[:1000]}")
except urllib.error.HTTPError as e:
    body = e.read().decode()
    print(f"\n❌ HTTP {e.code}: {body[:1000]}")
except Exception as e:
    print(f"\n❌ Error: {e}")
