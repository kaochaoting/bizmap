#!/usr/bin/env python3
"""Search for datasets matching 3 missing Bizmap categories."""
import subprocess, json, time

API = "https://api.twinkleai.tw/mcp/"
KEY = "***REMOVED***"

def mcp_call(method, params, timeout=60):
    payload = json.dumps({"jsonrpc":"2.0","id":1,"method":method,"params":params})
    r = subprocess.run(["curl", "-s", "--max-time", str(timeout), "-X", "POST", API,
                        "-H", "Content-Type: application/json",
                        "-H", "Accept: application/json, text/event-stream",
                        "-H", f"Authorization: Bearer {KEY}", "-d", payload],
                       capture_output=True, text=True, timeout=timeout+30)
    data = r.stdout
    if "data: " in data:
        data = data.split("data: ", 1)[1].strip()
    return json.loads(data)

# Search for each missing category
searches = [
    ("居家服務", "居家清潔", "economy_business"),
    ("居家服務", "家事服務", "economy_business"),
    ("居家服務", "水電安裝", "economy_business"),
    ("居家服務", "室內裝修", "economy_business"),
    ("居家服務", "居家照護", "health_food"),
    ("商業服務", "商務中心", "economy_business"),
    ("商業服務", "會計", "economy_business"),
    ("商業服務", "法律事務", "economy_business"),
    ("商業服務", "企業管理", "economy_business"),
    ("商業服務", "翻譯", "economy_business"),
    ("零售購物", "零售", "economy_business"),
    ("零售購物", "便利商店", "economy_business"),
    ("零售購物", "百貨公司", "economy_business"),
]

for cat, q, dom in searches:
    print(f"\n[{cat}] searching '{q}' in {dom}...", end=" ", flush=True)
    try:
        res = mcp_call("tools/call", {
            "name": "opendata-search_datasets",
            "arguments": {"query": q, "domain": dom, "limit": 3}
        })
        txt = res["result"]["content"][0]["text"]
        data = json.loads(txt)
        hits = data.get("hits", [])
        if not hits:
            print("(no results)")
        for h in hits:
            print(f"\n  [{h['dataset_id']:7s}] {h['name'][:55]:55s} | {h.get('quality_tier','?'):3s} | norm={h.get('is_normalised','?')}")
    except Exception as e:
        print(f"ERROR: {e}")
    time.sleep(0.3)
