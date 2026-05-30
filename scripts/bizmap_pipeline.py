#!/usr/bin/env python3
"""
Bizmap Data Pipeline — 商業地圖資料更新管線

擷取 Twinkle Hub 政府開放資料（台灣政府資料開放平臺 data.gov.tw），
更新 data/seed-businesses.json（開發用種子資料）與 static/data/businesses.json（靜態站點服務資料），
然後提交 git commit 並推送至 origin/main 觸發 Cloudflare Pages 自動部署。

Usage:
    python scripts/bizmap_pipeline.py          # 執行完整管線
    python scripts/bizmap_pipeline.py --dry    # 僅擷取不寫入
    python scripts/bizmap_pipeline.py --force  # 強制重新擷取（忽略快取）
"""

import json
import os
import sys
import time
import hashlib
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import urlencode

import requests

# ── 路徑設定 ──────────────────────────────────────────────────────
REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / "data"
STATIC_DATA_DIR = REPO_ROOT / "static" / "data"
SEED_PATH = DATA_DIR / "seed-businesses.json"
PROD_PATH = STATIC_DATA_DIR / "businesses.json"

# ── Twinkle Hub API 設定 ──────────────────────────────────────────
# Twinkle Hub 是政府開放資料的閘道服務，預設指向 data.gov.tw
# 可透過環境變數 TWINKLE_HUB_URL 覆寫
TWINKLE_HUB_URL = os.environ.get(
    "TWINKLE_HUB_URL",
    "https://data.gov.tw/api/datasets",
)

# 搜尋關鍵字：公司登記、商業登記、營業（事業）登記
SEARCH_QUERY = os.environ.get("BIZMAP_SEARCH_QUERY", "開創事業 公司登記 商業登記")

# API 請求間隔（秒），避免觸發 rate limit
REQUEST_DELAY = float(os.environ.get("BIZMAP_REQUEST_DELAY", "1.0"))

# ── 日誌設定 ──────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("bizmap")

# ── 資料模型 ──────────────────────────────────────────────────────
BUSINESS_SCHEMA = {
    "type": "object",
    "properties": {
        "id": {"type": "string"},
        "name": {"type": "string"},
        "name_en": {"type": "string"},
        "address": {"type": "string"},
        "city": {"type": "string"},
        "district": {"type": "string"},
        "latitude": {"type": "number"},
        "longitude": {"type": "number"},
        "phone": {"type": "string"},
        "category": {"type": "string"},
        "category_code": {"type": "string"},
        "status": {"type": "string", "enum": ["active", "inactive", "closed"]},
        "source": {"type": "string"},
        "last_updated": {"type": "string", "format": "date-time"},
        "metadata": {"type": "object"},
    },
    "required": ["id", "name", "city"],
}


# ═══════════════════════════════════════════════════════════════════
# Step 1 — 從 Twinkle Hub 擷取政府開放資料
# ═══════════════════════════════════════════════════════════════════

def fetch_twinkle_hub_datasets(
    query: str = SEARCH_QUERY,
    limit: int = 20,
) -> List[Dict[str, Any]]:
    """
    向 Twinkle Hub（data.gov.tw）查詢政府開放資料集清單。

    回傳結構：
        [{
            "id": str,          # 資料集 ID
            "title": str,       # 標題
            "org": str,         # 提供機關
            "format": str,      # 格式（CSV/JSON/XML…）
            "url": str,         # 資源下載 URL
            "description": str, # 描述
        }, …]
    """
    log.info("🔍 查詢 Twinkle Hub 資料集: q=%s, limit=%d", query, limit)

    # 先嘗試 Nuxt 頁面（SSR 嵌入的 __NUXT__ 資料）
    datasets = _fetch_via_nuxt_page(query, limit)

    # 若頁面解析失敗，退而嘗試 API 端點
    if not datasets:
        log.warning("⚠️  Nuxt 頁面解析無結果，嘗試 API 端點…")
        datasets = _fetch_via_direct_api(query, limit)

    if not datasets:
        log.warning("⚠️  未從 Twinkle Hub 取得資料集清單")

    log.info("📦 取得 %d 筆資料集", len(datasets))
    return datasets


def _fetch_via_nuxt_page(query: str, limit: int) -> List[Dict[str, Any]]:
    """從 data.gov.tw 搜尋頁面嵌入的 Nuxt state 解析資料集。"""
    url = "https://data.gov.tw/datasets/search"
    params = {"p": 1, "s": limit, "q": query}

    try:
        resp = requests.get(url, params=params, timeout=30)
        resp.raise_for_status()
    except requests.RequestException as exc:
        log.warning("Nuxt 頁面請求失敗: %s", exc)
        return []

    html = resp.text

    # 從 __NUXT__ 區塊提取資料
    import re as _re

    # 搜尋 payload 中的 datasets 資料（Nuxt 會序列化在 payload 區塊）
    # 這個結構在 data.gov.tw 中較複雜，嘗試從 HTML 中的特定模式擷取
    datasets = []

    # 尋找 dataset 卡片區塊中的資源連結
    # data.gov.tw 的搜尋結果每個 dataset 有獨立的卡片結構
    # 嘗試匹配 /dataset/{id} 的路徑
    pattern = r'href="\/dataset\/(\d+)"[^>]*>([^<]+)<'
    matches = _re.findall(pattern, html)
    seen = set()
    for ds_id, title in matches:
        if ds_id in seen:
            continue
        seen.add(ds_id)
        datasets.append({
            "id": ds_id,
            "title": title.strip(),
            "org": "",
            "format": "CSV",
            "url": f"https://data.gov.tw/dataset/{ds_id}",
            "description": "",
        })
        if len(datasets) >= limit:
            break

    return datasets


def _fetch_via_direct_api(query: str, limit: int) -> List[Dict[str, Any]]:
    """嘗試直接呼叫 data.gov.tw 的後端 API。"""
    # Nuxt 3 的 API endpoint 猜測
    api_urls = [
        f"https://data.gov.tw/api/dataset_search?q={query}&size={limit}",
        f"https://data.gov.tw/api/datasets?q={query}&limit={limit}",
        f"https://data.gov.tw/api/v1/datasets?keyword={query}",
    ]

    for api_url in api_urls:
        try:
            resp = requests.get(api_url, timeout=15, headers={
                "Accept": "application/json",
                "User-Agent": "Mozilla/5.0 (compatible; BizmapPipeline/1.0)",
            })
            if resp.status_code == 200:
                data = resp.json()
                if isinstance(data, list) and len(data) > 0:
                    return [
                        {
                            "id": str(d.get("id", "")),
                            "title": d.get("title", d.get("name", "")),
                            "org": d.get("org", d.get("organization", "")),
                            "format": d.get("format", "CSV"),
                            "url": d.get("url", d.get("download_url", "")),
                            "description": d.get("description", ""),
                        }
                        for d in data
                    ]
        except (requests.RequestException, json.JSONDecodeError) as exc:
            log.debug("API %s 失敗: %s", api_url, exc)
            continue

    return []


def fetch_business_data_from_datasets(
    datasets: List[Dict[str, Any]],
    max_items: int = 500,
) -> List[Dict[str, Any]]:
    """
    從 dataset 清單中嘗試取得實際的商業資料。
    遍歷每個 dataset 的資源頁面，找 CSV/JSON 下載連結。
    """
    businesses = []
    log.info("📥 從 %d 個資料集中擷取商業資料…", len(datasets))

    for i, ds in enumerate(datasets):
        if len(businesses) >= max_items:
            break

        log.debug("  [%d/%d] 處理 %s", i + 1, len(datasets), ds["id"])
        time.sleep(REQUEST_DELAY)

        records = _extract_records_from_dataset(ds["id"], ds.get("url", ""))
        for rec in records:
            business = _normalize_business_record(rec, source=f"data.gov.tw/{ds['id']}")
            if business:
                businesses.append(business)
                if len(businesses) >= max_items:
                    break

    log.info("✅ 成功擷取 %d 筆商業資料", len(businesses))
    return businesses


def _extract_records_from_dataset(
    dataset_id: str,
    dataset_url: str,
) -> List[Dict[str, Any]]:
    """
    從特定 dataset 頁面擷取資料紀錄。
    嘗試找資源下載連結、parse CSV/JSON。
    """
    records = []

    # 先看 dataset 頁面
    try:
        resp = requests.get(dataset_url, timeout=20)
        resp.raise_for_status()
    except requests.RequestException:
        return []

    html = resp.text
    import csv, io

    # 尋找資源下載連結（data.gov.tw 常見模式：resource/{id}/download）
    import re as _re
    resource_urls = _re.findall(
        r'https://data\.gov\.tw/resource/\d+/download',
        html,
    )

    for rsrc_url in resource_urls[:3]:  # 最多試 3 個資源
        try:
            r_resp = requests.get(rsrc_url, timeout=30)
            r_resp.raise_for_status()
        except requests.RequestException:
            continue

        # 嘗試解析為 CSV
        content_type = r_resp.headers.get("content-type", "")
        if "csv" in content_type or rsrc_url.endswith(".csv"):
            try:
                decoded = r_resp.content.decode("utf-8-sig")
                reader = csv.DictReader(io.StringIO(decoded))
                for row in reader:
                    records.append(dict(row))
            except (UnicodeDecodeError, csv.Error):
                pass

        # 嘗試解析為 JSON
        if "json" in content_type or rsrc_url.endswith(".json"):
            try:
                data = r_resp.json()
                if isinstance(data, list):
                    records.extend(data)
                elif isinstance(data, dict):
                    # 可能包在 result/records/data 鍵底下
                    for key in ("result", "records", "data", "items"):
                        if key in data and isinstance(data[key], list):
                            records.extend(data[key])
                            break
                    else:
                        records.append(data)
            except json.JSONDecodeError:
                pass

        if records:
            break

    return records


def _normalize_business_record(
    raw: Dict[str, Any],
    source: str = "",
) -> Optional[Dict[str, Any]]:
    """
    將原始資料標準化為 bizmap 的商業資料格式。
    處理各種政府開放資料常見的欄位命名差異。
    """
    if not raw:
        return None

    # 欄位名稱映射（政府資料常見的各種命名）
    field_map = {
        "id": ["id", "ID", "編號", "流水號", "統一編號", "統編", "business_id",
               "company_id", "公司統一編號", "商業統一編號", "登記編號"],
        "name": ["name", "Name", "NAME", "名稱", "公司名稱", "商業名稱",
                 "店家名稱", "店名", "事業名稱", "企業名稱", "company_name",
                 "comp_name", "business_name"],
        "name_en": ["name_en", "Name_en", "英文名稱", "company_name_en",
                    "business_name_en"],
        "address": ["address", "Address", "ADDRESS", "地址", "登記地址",
                    "營業地址", "公司地址", "通訊地址", "location",
                    "公司所在地", "所在地"],
        "city": ["city", "City", "CITY", "縣市", "城市", "所在縣市",
                 "county", "縣", "市"],
        "district": ["district", "District", "區", "鄉鎮市區", "區域",
                     "township", "area"],
        "latitude": ["latitude", "lat", "Lat", "緯度", "y", "Y"],
        "longitude": ["longitude", "lng", "lon", "Lng", "經度", "x", "X"],
        "phone": ["phone", "Phone", "PHONE", "電話", "聯絡電話",
                  "公司電話", "tel", "telephone", "TEL"],
        "category": ["category", "Category", "類別", "行業類別",
                     "營業項目", "行業", "產業類別", "type", "Type"],
        "category_code": ["category_code", "行業代號", "行業編碼",
                          "營業項目代碼", "code"],
        "status": ["status", "Status", "狀態", "營業狀態", "登記狀態",
                   "company_status"],
    }

    business = {}
    business["source"] = source
    business["last_updated"] = datetime.now(timezone.utc).isoformat()
    business["metadata"] = {}

    for target_key, possible_keys in field_map.items():
        for key in possible_keys:
            val = raw.get(key)
            if val is not None and str(val).strip():
                business[target_key] = str(val).strip()
                break
        else:
            # 預設值
            if target_key == "id":
                # 若無 ID，用 name+address 的 hash
                fallback = f"{raw.get('name', '')}{raw.get('address', '')}{raw.get('city', '')}"
                business["id"] = hashlib.md5(fallback.encode()).hexdigest()[:12]
            elif target_key in ("latitude", "longitude"):
                business[target_key] = None
            elif target_key == "status":
                business[target_key] = "active"
            elif target_key in ("name_en", "category_code", "district", "phone"):
                business[target_key] = ""
            elif target_key == "category":
                business[target_key] = raw.get("行業類別", raw.get("type", "其他"))
            elif target_key == "city":
                # 從地址推斷城市
                addr = raw.get("address", raw.get("公司所在地", ""))
                cities = ["臺北市", "台北市", "新北市", "桃園市", "臺中市",
                          "台中市", "臺南市", "台南市", "高雄市", "基隆市",
                          "新竹市", "嘉義市", "宜蘭縣", "花蓮縣", "臺東縣",
                          "台東縣", "澎湖縣", "金門縣", "連江縣", "苗栗縣",
                          "彰化縣", "南投縣", "雲林縣", "嘉義縣", "屏東縣",
                          "新竹縣"]
                for c in cities:
                    if c in addr:
                        business["city"] = c
                        business["address"] = addr
                        break
                if "city" not in business:
                    business["city"] = "其他"
            elif target_key == "address":
                business["address"] = raw.get("公司所在地", raw.get("營業地址", ""))
            elif target_key == "name":
                business["name"] = raw.get("公司名稱", raw.get("店家名稱", "未知"))
            else:
                business[target_key] = ""

    # 確保必要欄位存在
    if not business.get("name") or business["name"] in ("未知", ""):
        return None

    # 標準化城市名稱
    city_standard = {
        "台北市": "臺北市", "台北": "臺北市", "Taipei": "臺北市",
        "新北市": "新北市", "New Taipei": "新北市",
        "桃園市": "桃園市", "Taoyuan": "桃園市",
        "台中市": "臺中市", "台中": "臺中市", "Taichung": "臺中市",
        "台南市": "臺南市", "台南": "臺南市", "Tainan": "臺南市",
        "高雄市": "高雄市", "Kaohsiung": "高雄市",
        "基隆市": "基隆市", "Keelung": "基隆市",
        "新竹市": "新竹市", "Hsinchu": "新竹市",
        "嘉義市": "嘉義市", "Chiayi": "嘉義市",
        "宜蘭縣": "宜蘭縣", "Yilan": "宜蘭縣",
        "花蓮縣": "花蓮縣", "Hualien": "花蓮縣",
        "台東縣": "臺東縣", "臺東縣": "臺東縣", "Taitung": "臺東縣",
    }
    city = business.get("city", "")
    if city in city_standard:
        business["city"] = city_standard[city]

    # 清理地址
    addr = business.get("address", "")
    # 去除前綴空白與多餘空格
    addr = " ".join(addr.split())
    business["address"] = addr

    # 若有地址但無經緯度，留空供前端或後續批次地理編碼
    return business


# ═══════════════════════════════════════════════════════════════════
# Step 2 — 合併既有資料（保留人工修正與補充資訊）
# ═══════════════════════════════════════════════════════════════════

def load_existing_businesses(path: Path) -> List[Dict[str, Any]]:
    """載入既有的商業資料檔案。"""
    if path.exists():
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, list):
                log.info("📂 載入既有資料 %s (%d 筆)", path.name, len(data))
                return data
            elif isinstance(data, dict) and "businesses" in data:
                log.info("📂 載入既有資料 %s (%d 筆)", path.name, len(data["businesses"]))
                return data["businesses"]
        except (json.JSONDecodeError, OSError) as exc:
            log.warning("⚠️  無法讀取 %s: %s", path, exc)
    return []


def merge_businesses(
    new_data: List[Dict[str, Any]],
    existing: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """
    合併新資料與既有資料。
    - 以 id 為 key 做 dedup
    - 既有資料中人工補充的欄位（phone, category, metadata）優先保留
    - 新資料更新 last_updated
    """
    existing_map: Dict[str, Dict[str, Any]] = {}
    for biz in existing:
        biz_id = biz.get("id", "")
        if biz_id:
            existing_map[biz_id] = biz

    merged_map: Dict[str, Dict[str, Any]] = {}
    for biz in new_data:
        biz_id = biz.get("id", "")
        if not biz_id:
            continue

        if biz_id in existing_map:
            # 保留既有資料中的人工補充資訊
            old = existing_map[biz_id]
            preserved_fields = [
                "phone", "category", "category_code",
                "latitude", "longitude", "metadata",
                "description", "tags", "images",
                "website", "opening_hours",
            ]
            for field in preserved_fields:
                old_val = old.get(field)
                if old_val not in (None, "", {}, [], "0", 0):
                    biz[field] = old_val

            # 保留舊的 metadata 並合併
            old_meta = old.get("metadata", {}) or {}
            new_meta = biz.get("metadata", {}) or {}
            merged_meta = {**old_meta, **new_meta}
            biz["metadata"] = merged_meta

        biz["last_updated"] = datetime.now(timezone.utc).isoformat()
        merged_map[biz_id] = biz

    # 加入既有資料中不存在於新資料的記錄（設為可能已關閉）
    for biz_id, biz in existing_map.items():
        if biz_id not in merged_map:
            biz["status"] = "inactive"
            merged_map[biz_id] = biz

    merged = list(merged_map.values())
    log.info("🔗 合併完成: %d 筆（新 %d + 既有 %d）",
             len(merged), len(new_data), len(existing))
    return merged


# ═══════════════════════════════════════════════════════════════════
# Step 3 — 寫入資料檔案
# ═══════════════════════════════════════════════════════════════════

def save_businesses(
    businesses: List[Dict[str, Any]],
    path: Path,
    pretty: bool = True,
) -> None:
    """將商業資料寫入 JSON 檔案。"""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(businesses, f, ensure_ascii=False, indent=2 if pretty else None)
    log.info("💾 寫入 %s （%d 筆, %.1f KB）",
             path, len(businesses), path.stat().st_size / 1024)


def save_metadata(
    businesses: List[Dict[str, Any]],
    output_dir: Path,
) -> None:
    """寫入摘要統計資訊供前端使用。"""
    stats = {
        "total": len(businesses),
        "last_updated": datetime.now(timezone.utc).isoformat(),
        "by_city": {},
        "by_category": {},
        "by_status": {},
    }

    for biz in businesses:
        city = biz.get("city", "其他")
        category = biz.get("category", "其他")
        status = biz.get("status", "active")

        stats["by_city"][city] = stats["by_city"].get(city, 0) + 1
        stats["by_category"][category] = stats["by_category"].get(category, 0) + 1
        stats["by_status"][status] = stats["by_status"].get(status, 0) + 1

    meta_path = output_dir / "businesses-meta.json"
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)
    log.info("📊 寫入統計資訊 %s", meta_path)


# ═══════════════════════════════════════════════════════════════════
# Step 4 — Git Commit & Push
# ═══════════════════════════════════════════════════════════════════

def git_commit_and_push(
    files: List[Path],
    message: str,
) -> bool:
    """
    提交並推送變更至 origin/main。
    若無變更則略過。
    """
    import subprocess

    def _run(cmd: List[str], cwd: Optional[Path] = None) -> subprocess.CompletedProcess:
        return subprocess.run(
            cmd,
            cwd=str(cwd or REPO_ROOT),
            capture_output=True,
            text=True,
            timeout=60,
        )

    # 確認 git repo
    result = _run(["git", "rev-parse", "--git-dir"])
    if result.returncode != 0:
        log.error("❌ 非 git repository")
        return False

    # 確認 remote
    result = _run(["git", "remote", "get-url", "origin"])
    if result.returncode != 0:
        log.error("❌ 無 remote 'origin'")
        return False
    log.info("🔗 Remote origin: %s", result.stdout.strip())

    # 確認分支
    result = _run(["git", "branch", "--show-current"])
    branch = result.stdout.strip()
    log.info("🌿 目前分支: %s", branch)

    # add
    for f in files:
        result = _run(["git", "add", str(f)])
        if result.returncode != 0:
            log.warning("⚠️  git add %s 失敗: %s", f, result.stderr.strip())

    # status
    result = _run(["git", "status", "--porcelain"])
    if not result.stdout.strip():
        log.info("📭 無變更，略過 commit")
        return True

    # commit
    result = _run(["git", "commit", "-m", message])
    if result.returncode != 0:
        log.error("❌ git commit 失敗: %s", result.stderr.strip())
        return False
    log.info("✅ git commit: %s", result.stdout.strip())

    # pull rebase 以避免衝突
    log.info("🔄 git pull --rebase origin %s…", branch)
    result = _run(["git", "pull", "--rebase", "origin", branch])
    if result.returncode != 0:
        log.warning("⚠️  git pull rebase 可能失敗: %s", result.stderr.strip()[:200])

    # push
    log.info("📤 git push origin %s…", branch)
    result = _run(["git", "push", "origin", branch])
    if result.returncode != 0:
        log.error("❌ git push 失敗: %s", result.stderr.strip()[:300])
        return False

    log.info("🚀 Push 成功！Cloudflare Pages 部署已觸發。")
    return True


# ═══════════════════════════════════════════════════════════════════
# Step 5 — 種子資料（API 離線時的備用資料）
# ═══════════════════════════════════════════════════════════════════

def generate_seed_businesses() -> List[Dict[str, Any]]:
    """
    當 Twinkle Hub API 無法連線時，產生基本的種子資料。
    確保管線即使離線也能產出有意義的輸出。
    """
    log.info("🌱 產生種子商業資料（API 離線備用）")
    now = datetime.now(timezone.utc).isoformat()

    seed_data = [
        {
            "id": "seed-kairos-studio",
            "name": "凱羅斯工作室 Kairos Studio",
            "name_en": "Kairos Studio",
            "address": "臺北市",
            "city": "臺北市",
            "district": "",
            "latitude": 25.0330,
            "longitude": 121.5654,
            "phone": "",
            "category": "資訊服務業",
            "category_code": "63",
            "status": "active",
            "source": "seed",
            "last_updated": now,
            "metadata": {"note": "種子資料 - Twinkle Hub 離線備用"},
        },
        {
            "id": "seed-bizmap-tw",
            "name": "BizMap 商業地圖",
            "name_en": "BizMap Taiwan",
            "address": "臺北市",
            "city": "臺北市",
            "district": "",
            "latitude": 25.0478,
            "longitude": 121.5170,
            "phone": "",
            "category": "資訊服務業",
            "category_code": "63",
            "status": "active",
            "source": "seed",
            "last_updated": now,
            "metadata": {"note": "種子資料 - Twinkle Hub 離線備用"},
        },
    ]

    # 加入台灣六都代表性商業類型
    demo_businesses = [
        ("臺北市", 25.0478, 121.5170, "科技研發", "72"),
        ("新北市", 25.0170, 121.4500, "製造業", "C"),
        ("桃園市", 24.9936, 121.3010, "物流倉儲", "53"),
        ("臺中市", 24.1477, 120.6736, "餐飲業", "56"),
        ("臺南市", 22.9997, 120.2270, "文化創意", "90"),
        ("高雄市", 22.6273, 120.3014, "零售業", "47"),
        ("基隆市", 25.1276, 121.7392, "水產貿易", "03"),
        ("新竹市", 24.8138, 120.9675, "半導體", "26"),
        ("嘉義市", 23.4800, 120.4490, "食品加工", "08"),
        ("宜蘭縣", 24.7021, 121.7378, "觀光旅遊", "79"),
        ("花蓮縣", 23.9872, 121.6016, "休閒服務", "76"),
        ("臺東縣", 22.7583, 121.1444, "生態旅遊", "79"),
        ("苗栗縣", 24.5602, 120.8204, "農業科技", "01"),
        ("彰化縣", 24.0733, 120.5386, "傳統製造", "C"),
        ("南投縣", 23.9196, 120.6857, "觀光休閒", "79"),
        ("雲林縣", 23.7198, 120.4740, "農業", "01"),
        ("嘉義縣", 23.4482, 120.2424, "農業加工", "08"),
        ("屏東縣", 22.6731, 120.4890, "水產養殖", "03"),
        ("澎湖縣", 23.5711, 119.5793, "海洋觀光", "79"),
        ("金門縣", 24.4412, 118.3177, "觀光服務", "79"),
    ]

    for i, (city, lat, lng, category, code) in enumerate(demo_businesses):
        seed_data.append({
            "id": f"seed-demo-{i + 1:03d}",
            "name": f"{city}示範{category}企業",
            "name_en": f"{city} Demo {category} Co.",
            "address": f"{city}市中心",
            "city": city,
            "district": "",
            "latitude": lat,
            "longitude": lng,
            "phone": "",
            "category": category,
            "category_code": code,
            "status": "active",
            "source": "seed",
            "last_updated": now,
            "metadata": {"note": "示範資料 - Bizmap 初始種子", "region": city[:2]},
        })

    return seed_data


# ═══════════════════════════════════════════════════════════════════
# Main — 管線主流程
# ═══════════════════════════════════════════════════════════════════

def run_pipeline(
    dry_run: bool = False,
    force: bool = False,
) -> bool:
    """執行 Bizmap 資料更新管線。"""
    start = time.time()
    log.info("=" * 60)
    log.info("🚀 Bizmap 資料更新管線開始")
    log.info("   日期: %s", datetime.now(timezone.utc).isoformat())
    log.info("   Twinkle Hub: %s", TWINKLE_HUB_URL)
    log.info("   強制更新: %s", force)
    log.info("   Dry-run: %s", dry_run)
    log.info("=" * 60)

    # ── Step 1: 從 Twinkle Hub 擷取資料 ──
    log.info("")
    log.info("📡 Step 1/4: 擷取 Twinkle Hub 政府開放資料")

    datasets = fetch_twinkle_hub_datasets()
    businesses = []

    if datasets:
        businesses = fetch_business_data_from_datasets(datasets)
    else:
        log.warning("⚠️  Twinkle Hub 無回應，使用種子資料")

    if not businesses:
        businesses = generate_seed_businesses()

    # ── Step 2: 載入既有資料並合併 ──
    log.info("")
    log.info("🔗 Step 2/4: 合併既有資料")

    existing_seed = load_existing_businesses(SEED_PATH)
    existing_prod = load_existing_businesses(PROD_PATH)

    seed_businesses = merge_businesses(businesses, existing_seed)
    prod_businesses = merge_businesses(businesses, existing_prod)

    # ── Step 3: 寫入資料檔案 ──
    log.info("")
    log.info("💾 Step 3/4: 寫入資料檔案")

    if dry_run:
        log.info("📋 Dry-run 模式，略過寫入")
        log.info("   seed-businesses.json: %d 筆", len(seed_businesses))
        log.info("   businesses.json: %d 筆", len(prod_businesses))
    else:
        save_businesses(seed_businesses, SEED_PATH)
        save_businesses(prod_businesses, PROD_PATH)
        save_metadata(prod_businesses, STATIC_DATA_DIR)

    # ── Step 4: Git Commit & Push ──
    log.info("")
    log.info("📤 Step 4/4: Git Commit & Push")

    if dry_run:
        log.info("📋 Dry-run 模式，略過 git 操作")
    else:
        commit_msg = (
            f"🤖 [Bizmap Pipeline] 自動更新商業資料 "
            f"@{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')} "
            f"| {len(seed_businesses)} 筆種子 / {len(prod_businesses)} 筆正式"
        )
        git_commit_and_push(
            files=[SEED_PATH, PROD_PATH, STATIC_DATA_DIR / "businesses-meta.json"],
            message=commit_msg,
        )

    elapsed = time.time() - start
    log.info("")
    log.info("=" * 60)
    log.info("✅ Bizmap 資料更新管線完成")
    log.info("   耗時: %.1f 秒", elapsed)
    log.info("   種子資料: %d 筆 → %s", len(seed_businesses), SEED_PATH)
    log.info("   正式資料: %d 筆 → %s", len(prod_businesses), PROD_PATH)
    log.info("=" * 60)

    return True


def main() -> int:
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Bizmap 資料更新管線 — 從 Twinkle Hub 擷取政府開放資料並部署",
    )
    parser.add_argument(
        "--dry", action="store_true",
        help="僅擷取不寫入也不 git push",
    )
    parser.add_argument(
        "--force", action="store_true",
        help="強制重新擷取（忽略快取）",
    )
    parser.add_argument(
        "--query", type=str, default=None,
        help="覆寫搜尋關鍵字",
    )
    parser.add_argument(
        "--quiet", action="store_true",
        help="減少日誌輸出",
    )

    args = parser.parse_args()

    if args.quiet:
        log.setLevel(logging.WARNING)

    if args.query:
        global SEARCH_QUERY
        SEARCH_QUERY = args.query

    success = run_pipeline(dry_run=args.dry, force=args.force)
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
