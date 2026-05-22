#!/usr/bin/env python3
"""
Bizmap Output Optimizer v2
Strips boilerplate fields, splits into per-category+region+city files,
creates lightweight index and compact ID lookup.

v2: Large region-level files (>40MB) are auto-split by city to stay under
    GitHub's 50MB recommended file limit.
"""
import json, os, time
from pathlib import Path
from collections import Counter

BIZMAP_DIR = Path("/home/dministrator/bizmap")
DATA_DIR = BIZMAP_DIR / "data"
PUBLIC_DIR = BIZMAP_DIR / "static" / "data"
CAT_DIR = PUBLIC_DIR / "category"
ID_DIR = PUBLIC_DIR / "id-lookup"

# Fields needed by frontend
KEPT_FIELDS = [
    "business_id", "business_name", "category", "category_slug",
    "city", "district", "region", "address", "phone",
    "description", "tags", "source_name", "source_url", "source_updated_at",
]

# Split large categories by region for manageable file sizes
REGION_MAP = {
    "taipei_north": ["台北市", "新北市", "基隆市", "桃園市", "新竹市", "新竹縣", "苗栗縣"],
    "taichung_central": ["台中市", "彰化縣", "南投縣", "雲林縣"],
    "kaohsiung_south": ["嘉義市", "嘉義縣", "台南市", "高雄市", "屏東縣"],
    "hualien_east": ["宜蘭縣", "花蓮縣", "台東縣"],
    "outlying_islands": ["澎湖縣", "金門縣", "連江縣"],
}

LARGE_CATEGORY_THRESHOLD = 80000
# Files exceeding this size (in bytes) will be further split by city
LARGE_FILE_THRESHOLD = 40 * 1024 * 1024  # 40MB

def region_key(city):
    for rname, cities in REGION_MAP.items():
        if city in cities:
            return rname
    return "other"

def optimize(biz):
    out = {}
    for k in KEPT_FIELDS:
        v = biz.get(k)
        if v is not None and v != "" and v != [] and v != {}:
            out[k] = v
    return out

def run():
    t0 = time.time()
    
    path = DATA_DIR / "seed-businesses.json"
    print(f"Reading {path}...")
    with open(path) as f:
        data = json.load(f)
    bizs = data.get("businesses", data)
    total_raw = len(bizs)
    print(f"Loaded {total_raw} businesses")
    
    # Compress each entry
    compressed = [optimize(b) for b in bizs]
    raw_size = sum(len(json.dumps(b, ensure_ascii=False)) for b in bizs)
    opt_size = sum(len(json.dumps(b, ensure_ascii=False)) for b in compressed)
    print(f"Field compression: {raw_size:,}B \u2192 {opt_size:,}B ({opt_size/raw_size*100:.0f}%)")
    
    # Group by category
    by_cat = {}
    for b in compressed:
        slug = b.get("category_slug", "other")
        by_cat.setdefault(slug, []).append(b)
    
    # Split large categories by region, then split massive region files by city
    slug_buckets = {}
    for b in compressed:
        slug = b.get("category_slug", "other")
        entries_for_cat = by_cat.get(slug, [])
        bucket = slug
        if len(entries_for_cat) > LARGE_CATEGORY_THRESHOLD:
            city = b.get("city", "")
            rk = region_key(city)
            bucket = f"{slug}/{rk}"
        slug_buckets.setdefault(bucket, []).append(b)
    
    # Second pass: if a region bucket is too large, split by city
    # Estimate file size as ~760 bytes per entry (based on empirical data)
    AVG_ENTRY_BYTES = 760
    final_buckets = {}
    for bucket, entries in slug_buckets.items():
        est_size = len(entries) * AVG_ENTRY_BYTES
        parts = bucket.split("/")
        if len(parts) == 2 and est_size > LARGE_FILE_THRESHOLD:
            # Split by city within this region
            slug, region = parts
            by_city = {}
            for e in entries:
                city = e.get("city", "other")
                by_city.setdefault(city, []).append(e)
            for city, city_entries in sorted(by_city.items()):
                city_bucket = f"{bucket}/{city}"
                final_buckets[city_bucket] = city_entries
        else:
            final_buckets[bucket] = entries
    
    # Write per-bucket files
    CAT_DIR.mkdir(parents=True, exist_ok=True)
    total_opt_size = 0
    cat_files = {}
    
    for bucket, entries in sorted(final_buckets.items()):
        parts = bucket.split("/")
        slug = parts[0]
        region = parts[1] if len(parts) > 1 else None
        city = parts[2] if len(parts) > 2 else None
        cat_name = entries[0].get("category", slug) if entries else slug
        
        if city:
            # Three-level: category/region/city.json
            out_dir = CAT_DIR / slug / region
            out_dir.mkdir(parents=True, exist_ok=True)
            out_path = out_dir / f"{city}.json"
            file_key = f"category/{slug}/{region}/{city}.json"
        elif region:
            out_dir = CAT_DIR / slug
            out_dir.mkdir(parents=True, exist_ok=True)
            out_path = out_dir / f"{region}.json"
            file_key = f"category/{slug}/{region}.json"
        else:
            out_path = CAT_DIR / f"{slug}.json"
            file_key = f"category/{slug}.json"
        
        output = {"category": cat_name, "category_slug": slug,
                  "region": region or "all", "city": city or "all", "count": len(entries),
                  "businesses": entries}
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        
        fsize = out_path.stat().st_size
        total_opt_size += fsize
        print(f"  {file_key}: {len(entries):>6} entries, {fsize/1024/1024:.1f}MB")
        
        cat_files.setdefault(slug, []).append({
            "region": region or "all",
            "city": city or "all",
            "file": file_key,
            "count": len(entries),
        })
    
    # Per-slug ID lookup (compact, just ID arrays)
    ID_DIR.mkdir(parents=True, exist_ok=True)
    id_map = {}
    for bucket, entries in final_buckets.items():
        slug = bucket.split("/")[0]
        ids = [b["business_id"] for b in entries if b.get("business_id")]
        id_map.setdefault(slug, []).extend(ids)
    
    id_size_total = 0
    for slug, ids in sorted(id_map.items()):
        id_file = ID_DIR / f"{slug}.json"
        with open(id_file, "w", encoding="utf-8") as f:
            json.dump(ids, f, ensure_ascii=False, separators=(",", ":"))
        sz = id_file.stat().st_size
        id_size_total += sz
        print(f"  id-lookup/{slug}.json: {len(ids):>6} IDs, {sz/1024:.1f}KB")
    
    # Compact ID→slug routing map for individual page lookup
    routing = {}
    for slug, ids in id_map.items():
        for bid in ids:
            routing[bid] = slug
    routing_file = ID_DIR / "routing.json"
    with open(routing_file, "w", encoding="utf-8") as f:
        json.dump(routing, f, ensure_ascii=False, separators=(",", ":"))
    rsz = routing_file.stat().st_size
    print(f"  id-lookup/routing.json: {len(routing):>6} entries, {rsz/1024:.1f}KB")
    id_size_total += rsz
    
    # Lightweight index (counts + file map only, no full ID map)
    cat_counts = {}
    cat_names = {}
    for slug, entries in by_cat.items():
        cat_counts[slug] = len(entries)
        cat_names[slug] = entries[0].get("category", slug) if entries else slug
    
    city_counts = Counter()
    for b in compressed:
        c = b.get("city")
        if c:
            city_counts[c] += 1
    
    index = {
        "total": total_raw,
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "categories": cat_names,
        "category_counts": cat_counts,
        "city_counts": dict(city_counts.most_common()),
        "files": dict(sorted(cat_files.items())),
    }
    index_file = PUBLIC_DIR / "index.json"
    with open(index_file, "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=2)
    idx_size = index_file.stat().st_size
    print(f"\n  index.json: {idx_size/1024:.1f}KB")
    
    # Search index (compact: key+name+city per entry)
    search_idx = []
    for b in compressed:
        bid = b.get("business_id")
        bname = b.get("business_name", "")
        bcity = b.get("city", "")
        bslug = b.get("category_slug", "")
        if bid and bname:
            search_idx.append({"i": bid, "n": bname, "c": bcity, "s": bslug})
    search_file = PUBLIC_DIR / "search-index.json"
    with open(search_file, "w", encoding="utf-8") as f:
        json.dump(search_idx, f, ensure_ascii=False, separators=(",", ":"))
    srch_size = search_file.stat().st_size
    print(f"  search-index.json: {srch_size/1024:.1f}KB ({len(search_idx)} entries)")
    
    elapsed = time.time() - t0
    print(f"\n{'='*50}")
    print(f"Before: {raw_size/1024/1024:.1f}MB  (single file, 23 fields)")
    print(f"After:  {total_opt_size/1024/1024:.1f}MB  (split + stripped)")
    print(f"        + {idx_size/1024:.1f}KB index.json")
    print(f"        + {srch_size/1024:.1f}KB search-index.json")
    print(f"        + {id_size_total/1024:.1f}KB id-lookup/")
    print(f"        = {(total_opt_size + idx_size + srch_size + id_size_total)/1024/1024:.1f}MB total")
    print(f"Time:   {elapsed:.1f}s")
    print(f"{'='*50}")

if __name__ == "__main__":
    run()
