#!/usr/bin/env python3
"""Search Twinkle Hub for datasets relevant to each Bizmap category."""
import subprocess, json, sys, time

API = "https://api.twinkleai.tw/mcp/"
KEY = "sk-POQczvJ9YJP1IpAncQws3w"
HEADERS = {"Content-Type": "application/json",
           "Accept": "application/json, text/event-stream",
           "Authorization": f"Bearer {KEY}"}

def mcp_call(method, params):
    payload = json.dumps({"jsonrpc":"2.0","id":1,"method":method,"params":params})
    r = subprocess.run(["curl", "-s", "--max-time", "60", "-X", "POST", API,
                        "-H", f"Content-Type: application/json",
                        "-H", "Accept: application/json, text/event-stream",
                        "-H", f"Authorization: Bearer {KEY}",
                        "-d", payload],
                       capture_output=True, text=True, timeout=120)
    data = r.stdout
    if "data: " in data:
        data = data.split("data: ", 1)[1].strip()
    return json.loads(data)

# Define searches per category
searches = [
    ("餐飲美食", "食品業者登錄", "health_food"),
    ("餐飲美食", "餐館業", "economy_business"),
    ("醫療健康", "健保特約醫事機構", "health_food"),
    ("醫療健康", "診所", "health_food"),
    ("美容美髮", "美容", "economy_business"),
    ("健身運動", "健身", "economy_business"),
    ("教育補習", "短期補習班", "education_research"),
    ("居家服務", "居家清潔", "economy_business"),
    ("商業服務", "商務中心", "economy_business"),
    ("餐飲美食", "民宿", "culture_tourism_sport"),
    ("零售購物", "零售", "economy_business"),
    ("醫療健康", "藥局", "health_food"),
]

print("=== Dataset Search Results ===\n")
for cat, query, domain in searches:
    try:
        res = mcp_call("tools/call", {
            "name": "opendata-search_datasets",
            "arguments": {"query": query, "domain": domain, "limit": 5}
        })
        txt = res["result"]["content"][0]["text"]
        data = json.loads(txt)
        hits = data.get("hits", data.get("datasets", []))
        print(f"\n## [{cat}] {query}")
        for h in hits[:3]:
            print(f"   {h.get('dataset_id','?'):8s} | {h.get('name','?')[:50]:50s} | {h.get('quality_tier','?')}")
    except Exception as e:
        print(f"[{cat}] {query}: ERROR {e}")
    time.sleep(0.3)
