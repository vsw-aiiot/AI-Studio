from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import requests
import feedparser
import logging

router = APIRouter()
templates = Jinja2Templates(directory="studio/templates")
logger = logging.getLogger(__name__)


@router.get("/api/news")
def get_news():
    # Add switcher for change region so user can change location to get associated info in dashboard.  
    logger.info("Get news initiated")
    rss_url = "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml"
    feed = feedparser.parse(rss_url)

    news_list = []
    for entry in feed.entries[:6]:
        image_url = None

        # Try to extract media content
        if "media_content" in entry and entry.media_content:
            image_url = entry.media_content[0].get("url")
        elif "media_thumbnail" in entry and entry.media_thumbnail:
            image_url = entry.media_thumbnail[0].get("url")

        news_list.append({
            "title": entry.title,
            "link": entry.link,
            "published": entry.published,
            "image": image_url,
        })

    return {"news": news_list}

