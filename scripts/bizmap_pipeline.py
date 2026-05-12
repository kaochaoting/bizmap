#!/usr/bin/env python3
"""
Bizmap Data Pipeline v2: Twinkle Hub → Bizmap seed-businesses.json
Ingests government open data from multiple sources and transforms to Bizmap schema.
"""
import subprocess, json, sys, hashlib, time, os, re
from pathlib import Path

API = "https://api.twinkleai.tw/mcp/"
KEY = "***REMOVED***"
BIZMAP_DIR = Path("/home/dministrator/bizmap")
DATA_DIR = BIZMAP_DIR / "data"
PUBLIC_DIR = BIZMAP_DIR / "static" / "data"

# How many rows to pull per dataset (0 = all, but that could be huge)
# Start with ~50-100 per dataset for a meaningful initial batch
PER_DATASET = 50

def mcp_call(method, params, timeout=90):
    payload = json.dumps({"jsonrpc":"2.0","id":1,"method":method,"params":params})
    r = subprocess.run(["curl", "-s", "--max-time", str(timeout), "-X", "POST", API,
                        "-H", "Content-Type: application/json",
                        "-H", "Accept: application/json, text/event-stream",
                        "-H", f"Authorization: Bearer {KEY}",
                        "-d", payload],
                       capture_output=True, text=True, timeout=timeout+30)
    data = r.stdout
    if "data: " in data:
        data = data.split("data: ", 1)[1].strip()
    return json.loads(data)

def safe(val):
    """Return stripped string or empty string."""
    if val is None:
        return ""
    return str(val).strip()

def parse_address(address):
    """Extract city, district from Taiwan address string."""
    if not address:
        return "", ""
    # Normalize full-width/half-width
    address = address.replace('（', '(').replace('）', ')').replace(' ', '')
    city, district = "", ""
    m = re.match(r'(臺北市|台北市|新北市|桃園市|臺中市|台中市|臺南市|台南市|高雄市|'
                 r'基隆市|新竹市|嘉義市|新竹縣|苗栗縣|彰化縣|南投縣|雲林縣|'
                 r'嘉義縣|屏東縣|宜蘭縣|花蓮縣|臺東縣|台東縣|澎湖縣|金門縣|連江縣)', address)
    if m:
        city = m.group(1)
        rest = address[len(city):]
        m2 = re.match(r'([\u4e00-\u9fff]{2,4}(?:區|鄉|鎮|市))', rest)
        if m2:
            district = m2.group(1)
    city = city.replace('臺', '台')
    return city, district

def make_biz_id(biz):
    raw = f"{biz['source_type']}:{biz['business_name']}:{biz.get('address','')}"
    return "biz_" + hashlib.md5(raw.encode()).hexdigest()[:12]

def base_fields():
    return {
        "site_url": "", "booking_url": "", "card_url": "",
        "claim_status": "unclaimed", "review_status": "approved",
        "removal_status": "active",
        "module_statuses": {
            "bizmap": "active", "aeo_scanner": "not_started",
            "quicknotifys": "inactive", "mycal": "inactive",
            "k_core": "not_started", "card": "inactive"
        }
    }

def transform_pharmacy(row, cols):
    d = dict(zip(cols, row))
    name = safe(d.get("醫事機構名稱"))
    addr = safe(d.get("地址"))
    phone = safe(d.get("電話"))
    kind = safe(d.get("醫事機構種類"))
    city, district = parse_address(addr)
    if not name:
        return None
    return {
        "business_name": name, "category": "醫療健康", "category_slug": "medical",
        "city": city, "district": district, "region": f"{city} {district}".strip(),
        "address": addr, "phone": phone,
        "description": f"健保特約藥局（{kind}）" if kind else "健保特約藥局",
        "tags": ["藥局", "健保", "醫療"],
        "source_type": "government_open_data",
        "source_name": "衛生福利部中央健康保險署",
        "source_url": "https://data.gov.tw/dataset/39284",
        "source_license": "政府開放資料授權條款-第1版",
        "source_updated_at": time.strftime("%Y-%m-%d"),
        **base_fields()
    }

def transform_clinic(row, cols):
    d = dict(zip(cols, row))
    name = safe(d.get("醫事機構名稱"))
    addr = safe(d.get("地址"))
    phone = safe(d.get("電話"))
    spec = safe(d.get("診療科別"))
    city, district = parse_address(addr)
    if not name:
        return None
    tags = ["診所", "醫療"]
    if spec and spec not in ("-", ""):
        for s in spec.replace("、", ",").split(","):
            s = s.strip().replace("科", "")
            if s:
                tags.append(s)
    return {
        "business_name": name, "category": "醫療健康", "category_slug": "medical",
        "city": city, "district": district, "region": f"{city} {district}".strip(),
        "address": addr, "phone": phone,
        "description": f"健保特約診所（{spec or '一般科'}）",
        "tags": tags,
        "source_type": "government_open_data",
        "source_name": "衛生福利部中央健康保險署",
        "source_url": "https://data.gov.tw/dataset/39283",
        "source_license": "政府開放資料授權條款-第1版",
        "source_updated_at": time.strftime("%Y-%m-%d"),
        **base_fields()
    }

def transform_cramschool(row, cols):
    d = dict(zip(cols, row))
    name = safe(d.get("c_schoolname"))
    district_name = safe(d.get("district"))
    addr = safe(d.get("address"))
    if not name:
        return None
    full_addr = f"{district_name}{addr}" if district_name and addr else addr or district_name
    tags = ["補習班", "教育"]
    for kw in ["文理", "技藝", "語文", "音樂", "美術", "舞蹈"]:
        if kw in name:
            tags.append(kw)
    return {
        "business_name": name, "category": "教育補習", "category_slug": "education",
        "city": "新北市", "district": district_name, "region": f"新北市 {district_name}".strip(),
        "address": full_addr, "phone": "",
        "description": "新北市政府立案短期補習班",
        "tags": tags,
        "source_type": "government_open_data",
        "source_name": "新北市政府教育局",
        "source_url": "https://data.gov.tw/dataset/124223",
        "source_license": "政府開放資料授權條款-第1版",
        "source_updated_at": time.strftime("%Y-%m-%d"),
        **base_fields()
    }

def transform_hospital(row, cols):
    d = dict(zip(cols, row))
    name = safe(d.get("醫事機構名稱"))
    addr = safe(d.get("地址"))
    phone = safe(d.get("電話"))
    kind = safe(d.get("醫事機構種類"))
    city, district = parse_address(addr)
    if not name:
        return None
    return {
        "business_name": name, "category": "醫療健康", "category_slug": "medical",
        "city": city, "district": district, "region": f"{city} {district}".strip(),
        "address": addr, "phone": phone,
        "description": f"健保特約{kind}" if kind else "健保特約地區醫院",
        "tags": ["醫院", "醫療", "健保"],
        "source_type": "government_open_data",
        "source_name": "衛生福利部中央健康保險署",
        "source_url": "https://data.gov.tw/dataset/39282",
        "source_license": "政府開放資料授權條款-第1版",
        "source_updated_at": time.strftime("%Y-%m-%d"),
        **base_fields()
    }

def transform_restaurant_reg(row, cols):
    """商業登記(依營業項目別)－餐館業"""
    d = dict(zip(cols, row))
    name = safe(d.get("商業名稱") or d.get("商業名稱"))
    addr = safe(d.get("地址") or "")
    city, district = parse_address(addr) if addr else ("", "")
    phone = ""
    if not name:
        return None
    return {
        "business_name": name, "category": "餐飲美食", "category_slug": "food",
        "city": city, "district": district, "region": f"{city} {district}".strip(),
        "address": addr, "phone": phone,
        "description": "經濟部商業登記餐館業",
        "tags": ["餐飲", "美食"],
        "source_type": "government_open_data",
        "source_name": "經濟部商業發展署",
        "source_url": "https://data.gov.tw/dataset/32681",
        "source_license": "政府開放資料授權條款-第1版",
        "source_updated_at": time.strftime("%Y-%m-%d"),
        **base_fields()
    }

def transform_beauty_reg(row, cols):
    """商業登記(依營業項目別)－美容美髮服務"""
    d = dict(zip(cols, row))
    name = safe(d.get("商業名稱") or "")
    addr = safe(d.get("地址") or "")
    city, district = parse_address(addr) if addr else ("", "")
    phone = ""
    if not name:
        return None
    return {
        "business_name": name, "category": "美容美髮", "category_slug": "beauty",
        "city": city, "district": district, "region": f"{city} {district}".strip(),
        "address": addr, "phone": phone,
        "description": "經濟部商業登記美容美髮服務業",
        "tags": ["美容", "美髮"],
        "source_type": "government_open_data",
        "source_name": "經濟部商業發展署",
        "source_url": "https://data.gov.tw/dataset/108376",
        "source_license": "政府開放資料授權條款-第1版",
        "source_updated_at": time.strftime("%Y-%m-%d"),
        **base_fields()
    }

def query_and_transform(dataset_id, label, transform_fn, limit=PER_DATASET):
    print(f"  [{label}] querying dataset {dataset_id} (limit={limit})...", end=" ", flush=True)
    try:
        res = mcp_call("tools/call", {
            "name": "opendata-query_rows",
            "arguments": {"dataset_id": dataset_id, "limit": limit}
        }, timeout=180)
        txt = res["result"]["content"][0]["text"]
        data = json.loads(txt)
        cols = data.get("columns", [])
        rows = data.get("rows", [])
        print(f"{len(rows)} rows, {len(cols)} cols")
        
        entries = []
        for row in rows:
            try:
                biz = transform_fn(row, cols)
                if biz:
                    biz["business_id"] = make_biz_id(biz)
                    entries.append(biz)
            except Exception as e:
                print(f"    SKIP: {e}")
        return entries
    except Exception as e:
        print(f"ERROR: {e}")
        return []

def main():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    PUBLIC_DIR.mkdir(parents=True, exist_ok=True)
    
    print("=" * 60)
    print("Bizmap Data Pipeline v2")
    print(f"Ingesting {PER_DATASET} rows per dataset")
    print(time.strftime("%Y-%m-%d %H:%M:%S"))
    print("=" * 60)
    
    datasets = [
        ("39284", "健保藥局", transform_pharmacy),
        ("39283", "診所", transform_clinic),
        ("39282", "地區醫院", transform_hospital),
        ("124223", "新北補習班", transform_cramschool),
        ("32681", "商業登記餐館業", transform_restaurant_reg),
        ("108376", "美容美髮商業登記", transform_beauty_reg),
    ]
    
    all_businesses = []
    for ds_id, label, fn in datasets:
        entries = query_and_transform(ds_id, label, fn)
        all_businesses.extend(entries)
        time.sleep(0.5)
    
    # Deduplicate
    seen = set()
    unique = []
    for b in all_businesses:
        bid = b["business_id"]
        if bid not in seen:
            seen.add(bid)
            unique.append(b)
    
    print(f"\n{'='*60}")
    print(f"Total raw: {len(all_businesses)}")
    print(f"Total unique: {len(unique)}")
    
    # Build output
    output = {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.gmtime()),
        "policy": "docs/01-prd/bizmap-data-policy-v1.md",
        "source_files": ["data/seed-businesses.json"],
        "count": len(unique),
        "businesses": unique
    }
    
    # Write seed-businesses.json
    out_path = DATA_DIR / "seed-businesses.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"Written: {out_path} ({os.path.getsize(out_path)} bytes)")
    
    # Write static/data/businesses.json for direct serving
    pub_path = PUBLIC_DIR / "businesses.json"
    with open(pub_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"Written: {pub_path} ({os.path.getsize(pub_path)} bytes)")
    
    # Stats
    cats = {}
    cities = set()
    for b in unique:
        c = b["category"]
        cats[c] = cats.get(c, 0) + 1
        if b.get("city"):
            cities.add(b["city"])
    print(f"\nCategory breakdown:")
    for c, n in sorted(cats.items(), key=lambda x: -x[1]):
        print(f"  {c}: {n}")
    print(f"Cities: {len(cities)} → {sorted(cities)}")
    print("\nDone!")

if __name__ == "__main__":
    main()
