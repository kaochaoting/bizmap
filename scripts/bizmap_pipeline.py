#!/usr/bin/env python3
"""
Bizmap Data Pipeline v3 — Full-scale ingestion from Twinkle Hub MCP
"""
import subprocess, json, sys, hashlib, time, os, re
from pathlib import Path

API = "https://api.twinkleai.tw/mcp/"
KEY = "sk-POQczvJ9YJP1IpAncQws3w"
BIZMAP_DIR = Path("/home/dministrator/bizmap")
DATA_DIR = BIZMAP_DIR / "data"
PUBLIC_DIR = BIZMAP_DIR / "static" / "data"

PER_DATASET = 200  # per dataset, set 0 for all

def mcp_call(method, params, timeout=120):
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
    return "" if val is None else str(val).strip()

def parse_address(address):
    if not address:
        return "", ""
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

def base():
    return {"site_url": "","booking_url": "","card_url": "","claim_status": "unclaimed",
            "review_status": "approved","removal_status": "active",
            "module_statuses": {"bizmap":"active","aeo_scanner":"not_started",
                                "quicknotifys":"inactive","mycal":"inactive",
                                "k_core":"not_started","card":"inactive"}}

# --- Transformers ---

def t_pharmacy(row, cols):
    d = dict(zip(cols, row)); n=safe(d.get("醫事機構名稱")); a=safe(d.get("地址")); c,dst=parse_address(a)
    if not n: return None
    return {"business_name":n,"category":"醫療健康","category_slug":"medical","city":c,"district":dst,
            "region":f"{c} {dst}".strip(),"address":a,"phone":safe(d.get("電話")),
            "description":"健保特約藥局","tags":["藥局","健保","醫療"],
            "source_type":"government_open_data","source_name":"衛生福利部中央健康保險署",
            "source_url":"https://data.gov.tw/dataset/39284","source_license":"政府開放資料授權條款-第1版",
            "source_updated_at":time.strftime("%Y-%m-%d"), **base()}

def t_clinic(row, cols):
    d = dict(zip(cols, row)); n=safe(d.get("醫事機構名稱")); a=safe(d.get("地址")); c,dst=parse_address(a)
    if not n: return None
    spec=safe(d.get("診療科別")); tags=["診所","醫療"]
    if spec and spec!="-":
        for s in spec.replace("、",",").split(","):
            s=s.strip().replace("科",""); 
            if s: tags.append(s)
    return {"business_name":n,"category":"醫療健康","category_slug":"medical","city":c,"district":dst,
            "region":f"{c} {dst}".strip(),"address":a,"phone":safe(d.get("電話")),
            "description":f"健保特約診所（{spec or '一般科'}）","tags":tags,
            "source_type":"government_open_data","source_name":"衛生福利部中央健康保險署",
            "source_url":"https://data.gov.tw/dataset/39283","source_license":"政府開放資料授權條款-第1版",
            "source_updated_at":time.strftime("%Y-%m-%d"), **base()}

def t_hospital(row, cols):
    d = dict(zip(cols, row)); n=safe(d.get("醫事機構名稱")); a=safe(d.get("地址")); c,dst=parse_address(a)
    if not n: return None
    kind=safe(d.get("醫事機構種類"))
    return {"business_name":n,"category":"醫療健康","category_slug":"medical","city":c,"district":dst,
            "region":f"{c} {dst}".strip(),"address":a,"phone":safe(d.get("電話")),
            "description":f"健保特約{kind}" if kind else "健保特約地區醫院","tags":["醫院","醫療","健保"],
            "source_type":"government_open_data","source_name":"衛生福利部中央健康保險署",
            "source_url":"https://data.gov.tw/dataset/39282","source_license":"政府開放資料授權條款-第1版",
            "source_updated_at":time.strftime("%Y-%m-%d"), **base()}

def t_cramschool(row, cols):
    d = dict(zip(cols, row)); n=safe(d.get("c_schoolname")); dst_name=safe(d.get("district")); addr=safe(d.get("address"))
    if not n: return None
    fa=f"{dst_name}{addr}" if dst_name and addr else addr or dst_name
    tags=["補習班","教育"]
    for kw in ["文理","技藝","語文","音樂","美術","舞蹈","珠心算","圍棋"]:
        if kw in n: tags.append(kw)
    return {"business_name":n,"category":"教育補習","category_slug":"education","city":"新北市","district":dst_name,
            "region":f"新北市 {dst_name}".strip(),"address":fa,"phone":"",
            "description":"新北市政府立案短期補習班","tags":tags,
            "source_type":"government_open_data","source_name":"新北市政府教育局",
            "source_url":"https://data.gov.tw/dataset/124223","source_license":"政府開放資料授權條款-第1版",
            "source_updated_at":time.strftime("%Y-%m-%d"), **base()}

def t_restaurant(row, cols):
    d = dict(zip(cols, row)); n=safe(d.get("商業名稱") or ""); a=safe(d.get("地址") or ""); c,dst=parse_address(a)
    if not n: return None
    return {"business_name":n,"category":"餐飲美食","category_slug":"food","city":c,"district":dst,
            "region":f"{c} {dst}".strip(),"address":a,"phone":"",
            "description":"經濟部商業登記餐館業","tags":["餐飲","美食"],
            "source_type":"government_open_data","source_name":"經濟部商業發展署",
            "source_url":"https://data.gov.tw/dataset/32681","source_license":"政府開放資料授權條款-第1版",
            "source_updated_at":time.strftime("%Y-%m-%d"), **base()}

def t_beauty(row, cols):
    d = dict(zip(cols, row)); n=safe(d.get("商業名稱") or ""); a=safe(d.get("地址") or ""); c,dst=parse_address(a)
    if not n: return None
    return {"business_name":n,"category":"美容美髮","category_slug":"beauty","city":c,"district":dst,
            "region":f"{c} {dst}".strip(),"address":a,"phone":"",
            "description":"經濟部商業登記美容美髮服務業","tags":["美容","美髮"],
            "source_type":"government_open_data","source_name":"經濟部商業發展署",
            "source_url":"https://data.gov.tw/dataset/108376","source_license":"政府開放資料授權條款-第1版",
            "source_updated_at":time.strftime("%Y-%m-%d"), **base()}

def t_sports_venue(row, cols):
    d = dict(zip(cols, row)); n=safe(d.get("場館名稱")); a=safe(d.get("場地地址") or d.get("地址","")); c,dst=parse_address(a)
    if not n: return None
    tags=["運動","健身"]
    if "游泳池" in n or "泳池" in n: tags.append("游泳")
    if "籃球" in n: tags.append("籃球")
    if "羽球" in n: tags.append("羽球")
    if "健身房" in n or "健身" in n: tags.append("健身房")
    return {"business_name":n,"category":"健身運動","category_slug":"fitness","city":c or "台中市","district":dst,
            "region":f"台中市 {dst}".strip(),"address":a,"phone":"",
            "description":"臺中市運動場館","tags":tags,
            "source_type":"government_open_data","source_name":"臺中市政府運動局",
            "source_url":"https://data.gov.tw/dataset/108629","source_license":"政府開放資料授權條款-第1版",
            "source_updated_at":time.strftime("%Y-%m-%d"), **base()}

def t_bnb(row, cols):
    """臺中市好客民宿"""
    d = dict(zip(cols, row)); n=safe(d.get("中文名稱")); a=safe(d.get("地址")); c,dst=parse_address(a)
    p=safe(d.get("電話或手機"))
    if not n: return None
    tags=["民宿","住宿","好客"]
    return {"business_name":n,"category":"餐飲美食","category_slug":"food","city":c or "台中市","district":dst,
            "region":f"台中市 {dst}".strip(),"address":a,"phone":p,
            "description":"交通部觀光局好客民宿（臺中市）","tags":tags,
            "source_type":"government_open_data","source_name":"臺中市政府觀光旅遊局",
            "source_url":"https://data.gov.tw/dataset/83645","source_license":"政府開放資料授權條款-第1版",
            "source_updated_at":time.strftime("%Y-%m-%d"), **base()}

def t_slimming(row, cols):
    """瘦身美容業公司登記"""
    d = dict(zip(cols, row)); n=safe(d.get("公司名稱")); a=safe(d.get("公司地址")); c,dst=parse_address(a)
    if not n: return None
    return {"business_name":n,"category":"美容美髮","category_slug":"beauty","city":c,"district":dst,
            "region":f"{c} {dst}".strip(),"address":a,"phone":"",
            "description":"經濟部公司登記瘦身美容業","tags":["美容","瘦身","SPA"],
            "source_type":"government_open_data","source_name":"經濟部商業發展署",
            "source_url":"https://data.gov.tw/dataset/26259","source_license":"政府開放資料授權條款-第1版",
            "source_updated_at":time.strftime("%Y-%m-%d"), **base()}

# --- New transformers for missing categories ---

def t_cleaning(row, cols):
    """建築物清潔服務業 (公司登記) → 居家服務"""
    d = dict(zip(cols, row)); n=safe(d.get("公司名稱") or ""); a=safe(d.get("公司地址") or ""); c,dst=parse_address(a)
    if not n: return None
    return {"business_name":n,"category":"居家服務","category_slug":"home","city":c,"district":dst,
            "region":f"{c} {dst}".strip(),"address":a,"phone":"",
            "description":"經濟部公司登記建築物清潔服務業","tags":["清潔","居家","打掃"],
            "source_type":"government_open_data","source_name":"經濟部商業發展署",
            "source_url":"https://data.gov.tw/dataset/32689","source_license":"政府開放資料授權條款-第1版",
            "source_updated_at":time.strftime("%Y-%m-%d"), **base()}

def t_building_mgmt(row, cols):
    """公寓大廈管理服務業 (商業登記) → 居家服務"""
    d = dict(zip(cols, row)); n=safe(d.get("商業名稱") or ""); a=safe(d.get("商業地址") or ""); c,dst=parse_address(a)
    if not n: return None
    return {"business_name":n,"category":"居家服務","category_slug":"home","city":c,"district":dst,
            "region":f"{c} {dst}".strip(),"address":a,"phone":"",
            "description":"經濟部商業登記公寓大廈管理服務業","tags":["物業管理","公寓","居家服務"],
            "source_type":"government_open_data","source_name":"經濟部商業發展署",
            "source_url":"https://data.gov.tw/dataset/81101","source_license":"政府開放資料授權條款-第1版",
            "source_updated_at":time.strftime("%Y-%m-%d"), **base()}

def t_convenience_store(row, cols):
    """便利商店 (商業登記) → 零售購物"""
    d = dict(zip(cols, row)); n=safe(d.get("商業名稱") or ""); a=safe(d.get("商業地址") or ""); c,dst=parse_address(a)
    if not n: return None
    return {"business_name":n,"category":"零售購物","category_slug":"retail","city":c,"district":dst,
            "region":f"{c} {dst}".strip(),"address":a,"phone":"",
            "description":"經濟部商業登記便利商店","tags":["便利商店","零售","購物"],
            "source_type":"government_open_data","source_name":"經濟部商業發展署",
            "source_url":"https://data.gov.tw/dataset/108388","source_license":"政府開放資料授權條款-第1版",
            "source_updated_at":time.strftime("%Y-%m-%d"), **base()}

def t_department_store(row, cols):
    """百貨公司業 (公司登記) → 零售購物"""
    d = dict(zip(cols, row)); n=safe(d.get("公司名稱") or ""); a=safe(d.get("公司地址") or ""); c,dst=parse_address(a)
    if not n: return None
    return {"business_name":n,"category":"零售購物","category_slug":"retail","city":c,"district":dst,
            "region":f"{c} {dst}".strip(),"address":a,"phone":"",
            "description":"經濟部公司登記百貨公司業","tags":["百貨","零售","購物"],
            "source_type":"government_open_data","source_name":"經濟部商業發展署",
            "source_url":"https://data.gov.tw/dataset/45654","source_license":"政府開放資料授權條款-第1版",
            "source_updated_at":time.strftime("%Y-%m-%d"), **base()}

def t_translation(row, cols):
    """翻譯業 (商業登記) → 商業服務"""
    d = dict(zip(cols, row)); n=safe(d.get("商業名稱") or ""); a=safe(d.get("商業地址") or ""); c,dst=parse_address(a)
    if not n: return None
    return {"business_name":n,"category":"商業服務","category_slug":"business","city":c,"district":dst,
            "region":f"{c} {dst}".strip(),"address":a,"phone":"",
            "description":"經濟部商業登記翻譯業","tags":["翻譯","商業服務","語言"],
            "source_type":"government_open_data","source_name":"經濟部商業發展署",
            "source_url":"https://data.gov.tw/dataset/108375","source_license":"政府開放資料授權條款-第1版",
            "source_updated_at":time.strftime("%Y-%m-%d"), **base()}

# === NEW: Top 5 priority datasets ===

def t_gas_station(row, cols):
    """加油站業 (商業登記) → 交通運輸"""
    d = dict(zip(cols, row)); n=safe(d.get("商業名稱") or ""); a=safe(d.get("商業地址") or ""); c,dst=parse_address(a)
    if not n: return None
    return {"business_name":n,"category":"交通運輸","category_slug":"transport","city":c,"district":dst,
            "region":f"{c} {dst}".strip(),"address":a,"phone":"",
            "description":"經濟部商業登記加油站業","tags":["加油站","交通","加油"],
            "source_type":"government_open_data","source_name":"經濟部商業發展署",
            "source_url":"https://data.gov.tw/dataset/81098","source_license":"政府開放資料授權條款-第1版",
            "source_updated_at":time.strftime("%Y-%m-%d"), **base()}

def t_supermarket(row, cols):
    """超級市場業 (商業登記) → 零售購物"""
    d = dict(zip(cols, row)); n=safe(d.get("商業名稱") or ""); a=safe(d.get("商業地址") or ""); c,dst=parse_address(a)
    if not n: return None
    return {"business_name":n,"category":"零售購物","category_slug":"retail","city":c,"district":dst,
            "region":f"{c} {dst}".strip(),"address":a,"phone":"",
            "description":"經濟部商業登記超級市場業","tags":["超市","零售","購物"],
            "source_type":"government_open_data","source_name":"經濟部商業發展署",
            "source_url":"https://data.gov.tw/dataset/125955","source_license":"政府開放資料授權條款-第1版",
            "source_updated_at":time.strftime("%Y-%m-%d"), **base()}

def t_security(row, cols):
    """保全業 (商業登記) → 居家服務"""
    d = dict(zip(cols, row)); n=safe(d.get("商業名稱") or ""); a=safe(d.get("商業地址") or ""); c,dst=parse_address(a)
    if not n: return None
    return {"business_name":n,"category":"居家服務","category_slug":"home","city":c,"district":dst,
            "region":f"{c} {dst}".strip(),"address":a,"phone":"",
            "description":"經濟部商業登記保全業","tags":["保全","安全","居家"],
            "source_type":"government_open_data","source_name":"經濟部商業發展署",
            "source_url":"https://data.gov.tw/dataset/81120","source_license":"政府開放資料授權條款-第1版",
            "source_updated_at":time.strftime("%Y-%m-%d"), **base()}

def t_real_estate(row, cols):
    """不動產仲介經紀業 (商業登記) → 商業服務"""
    d = dict(zip(cols, row)); n=safe(d.get("商業名稱") or ""); a=safe(d.get("商業地址") or ""); c,dst=parse_address(a)
    if not n: return None
    return {"business_name":n,"category":"商業服務","category_slug":"business","city":c,"district":dst,
            "region":f"{c} {dst}".strip(),"address":a,"phone":"",
            "description":"經濟部商業登記不動產仲介經紀業","tags":["不動產","仲介","租屋","買房"],
            "source_type":"government_open_data","source_name":"經濟部商業發展署",
            "source_url":"https://data.gov.tw/dataset/81110","source_license":"政府開放資料授權條款-第1版",
            "source_updated_at":time.strftime("%Y-%m-%d"), **base()}

def t_car_rental(row, cols):
    """小客車租賃業 (商業登記) → 交通運輸"""
    d = dict(zip(cols, row)); n=safe(d.get("商業名稱") or ""); a=safe(d.get("商業地址") or ""); c,dst=parse_address(a)
    if not n: return None
    return {"business_name":n,"category":"交通運輸","category_slug":"transport","city":c,"district":dst,
            "region":f"{c} {dst}".strip(),"address":a,"phone":"",
            "description":"經濟部商業登記小客車租賃業","tags":["租車","交通","運輸"],
            "source_type":"government_open_data","source_name":"經濟部商業發展署",
            "source_url":"https://data.gov.tw/dataset/81106","source_license":"政府開放資料授權條款-第1版",
            "source_updated_at":time.strftime("%Y-%m-%d"), **base()}

# --- Pipeline ---

datasets = [
    ("39284", "健保藥局", t_pharmacy),
    ("39283", "診所", t_clinic),
    ("39282", "地區醫院", t_hospital),
    ("124223", "新北補習班", t_cramschool),
    ("32681", "商業登記餐館業", t_restaurant),
    ("108376", "美容美髮商業登記", t_beauty),
    ("108629", "臺中運動場館", t_sports_venue),
    ("83645", "臺中好客民宿", t_bnb),
    ("26259", "瘦身美容業公司", t_slimming),
    ("32689", "建築物清潔服務業", t_cleaning),
    ("81101", "公寓大廈管理服務業", t_building_mgmt),
    ("108388", "便利商店", t_convenience_store),
    ("45654", "百貨公司業", t_department_store),
    ("108375", "翻譯業", t_translation),
    ("81098", "加油站業", t_gas_station),
    ("125955", "超級市場業", t_supermarket),
    ("81120", "保全業", t_security),
    ("81110", "不動產仲介業", t_real_estate),
    ("81106", "小客車租賃業", t_car_rental),
]

def run():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    PUBLIC_DIR.mkdir(parents=True, exist_ok=True)
    
    print("="*60)
    print(f"Bizmap Pipeline v3 — {len(datasets)} datasets x {PER_DATASET} each")
    print(time.strftime("%Y-%m-%d %H:%M:%S"))
    print("="*60)
    
    all_biz = []
    for ds_id, label, fn in datasets:
        print(f"  [{label}] querying {ds_id}...", end=" ", flush=True)
        try:
            res = mcp_call("tools/call", {
                "name": "opendata-query_rows",
                "arguments": {"dataset_id": ds_id, "limit": PER_DATASET}
            }, timeout=180)
            txt = res["result"]["content"][0]["text"]
            data = json.loads(txt)
            cols = data.get("columns", [])
            rows = data.get("rows", [])
            
            entries = []
            for row in rows:
                try:
                    biz = fn(row, cols)
                    if biz:
                        biz["business_id"] = make_biz_id(biz)
                        entries.append(biz)
                except Exception as e:
                    pass
            print(f"{len(rows)} rows → {len(entries)} valid")
            all_biz.extend(entries)
        except Exception as e:
            print(f"ERROR: {e}")
        time.sleep(0.5)
    
    # Dedup
    seen = set()
    unique = []
    for b in all_biz:
        bid = b["business_id"]
        if bid not in seen:
            seen.add(bid)
            unique.append(b)
    
    print(f"\n{'='*60}")
    print(f"Total raw: {len(all_biz)}, Unique: {len(unique)}")
    
    output = {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.gmtime()),
        "policy": "docs/01-prd/bizmap-data-policy-v1.md",
        "source_files": ["data/seed-businesses.json"],
        "count": len(unique),
        "businesses": unique
    }
    
    for path in [DATA_DIR/"seed-businesses.json", PUBLIC_DIR/"businesses.json"]:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        print(f"Written: {path} ({os.path.getsize(path)} bytes)")
    
    cats = {}; cities = set()
    for b in unique:
        cats[b["category"]] = cats.get(b["category"], 0) + 1
        if b.get("city"): cities.add(b["city"])
    print(f"\nCategory breakdown:")
    for c,n in sorted(cats.items(), key=lambda x:-x[1]):
        print(f"  {c}: {n}")
    print(f"Cities: {len(cities)} — {sorted(cities)}")
    print("\nDone!")

if __name__ == "__main__":
    run()
