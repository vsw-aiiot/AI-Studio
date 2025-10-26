from fastapi import APIRouter, Query
import os, time, logging, re, requests, feedparser
from html import unescape
import re
from bs4 import BeautifulSoup 

router = APIRouter()
logger = logging.getLogger(__name__)

IMG_TAG_RE = re.compile(r'<img[^>]+src="([^"]+)"', re.IGNORECASE)

# ---------- Config ----------
NEWSAPI_KEY = os.getenv("NEWSAPI_KEY", "").strip()
DEFAULT_LIMIT = 6
TTL_SECONDS = 300  # cache 5 minutes

# Map simple region codes -> Google News RSS params (hl, gl, ceid)
GOOGLE_RSS_REGIONS = {
    "us": ("en-US", "US", "US:en"),
    "in": ("en-IN", "IN", "IN:en"),
    "uk": ("en-GB", "GB", "GB:en"),
    "au": ("en-AU", "AU", "AU:en"),
    "ca": ("en-CA", "CA", "CA:en"),
    "sg": ("en-SG", "SG", "SG:en"),
    "de": ("de-DE", "DE", "DE:de"),
    "fr": ("fr-FR", "FR", "FR:fr"),
    "es": ("es-ES", "ES", "ES:es"),
}

NYT_RSS = "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml"

# Simple in-memory TTL cache
_cache = {}  # key -> (timestamp, payload)


# ---------- Helpers ----------
def _now() -> float:
    return time.time()

def _get_cache(key: str):
    item = _cache.get(key)
    if not item:
        return None
    ts, payload = item
    if (_now() - ts) > TTL_SECONDS:
        _cache.pop(key, None)
        return None
    return payload

def _set_cache(key: str, payload):
    _cache[key] = (_now(), payload)

# IMG_TAG_RE = re.compile(r'<img[^>]+src="([^"]+)"', re.IGNORECASE)

def _extract_image(entry):
    """
    Try all possible image sources:
    1. media:content / media:thumbnail
    2. <img> tags in summary/content
    3. og:image / twitter:image meta (for NewsAPI URLs)
    """

    # 1️⃣ Media tags
    if "media_content" in entry and entry.media_content:
        url = entry.media_content[0].get("url")
        if url: return url
    if "media_thumbnail" in entry and entry.media_thumbnail:
        url = entry.media_thumbnail[0].get("url")
        if url: return url

    # 2️⃣ Inline <img> in HTML body
    html_blob = ""
    if "content" in entry and entry.content:
        html_blob = " ".join([c.get("value", "") for c in entry.content])
    elif "summary" in entry:
        html_blob = entry.summary or ""
    if html_blob:
        soup = BeautifulSoup(html_blob, "html.parser")
        img_tag = soup.find("img")
        if img_tag and img_tag.get("src"):
            return img_tag["src"]

    # 3️⃣ Fallback: scrape og:image metadata if link provided (optional)
    #    Only run for Google RSS / NewsAPI since NYT already has images
    link = getattr(entry, "link", None)
    if link:
        try:
            resp = requests.get(link, timeout=3)
            soup = BeautifulSoup(resp.text, "html.parser")
            og_img = soup.find("meta", property="og:image")
            if og_img and og_img.get("content"):
                return og_img["content"]
        except Exception:
            pass

    return None

def _normalize_entry(entry):
    return {
        "title": unescape(getattr(entry, "title", "Untitled")),
        "link": getattr(entry, "link", ""),
        "published": getattr(entry, "published", "") or getattr(entry, "updated", ""),
        "image": _extract_image(entry),
    }

def _fetch_rss(url: str, limit: int):
    feed = feedparser.parse(url)
    items = []
    for e in feed.entries[:limit]:
        items.append(_normalize_entry(e))
    return items

def _google_news_rss(region: str) -> str:
    # Defaults to US if unknown region
    hl, gl, ceid = GOOGLE_RSS_REGIONS.get(region.lower(), GOOGLE_RSS_REGIONS["us"])
    return f"https://news.google.com/rss?hl={hl}&gl={gl}&ceid={ceid}"

def _fetch_newsapi(region: str, limit: int):
    # NewsAPI country expects ISO 3166-1 alpha-2 (e.g., 'us', 'in')
    url = "https://newsapi.org/v2/top-headlines"
    params = {
        "country": region.lower() if region.lower() in GOOGLE_RSS_REGIONS else "us",
        "pageSize": limit,
        "apiKey": NEWSAPI_KEY,
    }
    r = requests.get(url, params=params, timeout=10)
    r.raise_for_status()
    data = r.json()

    items = []
    for a in (data.get("articles") or [])[:limit]:
        items.append({
            "title": a.get("title") or "Untitled",
            "link": a.get("url") or "",
            "published": a.get("publishedAt") or "",
            "image": a.get("urlToImage"),
        })
    return items

def _response(news, source, region):
    return {"news": news, "source": source, "region": region}


# ---------- Endpoint ----------
@router.get("/api/news")
def get_news(
    region: str = Query(default="us", description="Region code like us, in, uk, ..."),
    limit: int = Query(default=DEFAULT_LIMIT, ge=1, le=20),
    provider: str = Query(default="auto", description="auto | newsapi | google_rss | nyt"),
):
    """
    Fallback chain:
      provider=newsapi  -> NewsAPI (if NEWSAPI_KEY set) else fallback
      provider=google_rss -> Google News RSS (region)
      provider=nyt -> NYT RSS
      provider=auto (default):
         1) NewsAPI (if key present)
         2) Google News RSS (region)
         3) NYT RSS
    """
    key = f"{region}:{limit}:{provider}"
    cached = _get_cache(key)
    if cached:
        return cached

    logger.info("Get news initiated (region=%s, limit=%s, provider=%s)", region, limit, provider)

    # 1) Explicit providers:
    try:
        if provider == "newsapi":
            if not NEWSAPI_KEY:
                logger.warning("provider=newsapi but NEWSAPI_KEY not set; falling back")
            else:
                news = _fetch_newsapi(region, limit)
                payload = _response(news, "newsapi", region)
                _set_cache(key, payload)
                return payload

        if provider == "google_rss":
            rss_url = _google_news_rss(region)
            news = _fetch_rss(rss_url, limit)
            payload = _response(news, "google_rss", region)
            _set_cache(key, payload)
            return payload

        if provider == "nyt":
            news = _fetch_rss(NYT_RSS, limit)
            payload = _response(news, "nyt", region)
            _set_cache(key, payload)
            return payload

        # 2) AUTO provider (smart fallback)
        # a) NewsAPI if available
        if NEWSAPI_KEY:
            try:
                news = _fetch_newsapi(region, limit)
                payload = _response(news, "newsapi", region)
                _set_cache(key, payload)
                return payload
            except Exception as e:
                logger.warning("NewsAPI failed: %s", e)

        # b) Google News RSS per region
        try:
            rss_url = _google_news_rss(region)
            news = _fetch_rss(rss_url, limit)
            payload = _response(news, "google_rss", region)
            _set_cache(key, payload)
            return payload
        except Exception as e:
            logger.warning("Google RSS failed: %s", e)

        # c) NYT fallback
        news = _fetch_rss(NYT_RSS, limit)
        payload = _response(news, "nyt", region)
        _set_cache(key, payload)
        return payload

    except Exception as e:
        logger.exception("Unexpected error in /api/news: %s", e)
        # Last-resort empty payload
        empty = _response([], "error", region)
        _set_cache(key, empty)
        return empty
