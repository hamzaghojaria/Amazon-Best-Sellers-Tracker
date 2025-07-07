from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse,HTMLResponse
import uvicorn
import os
import json
import time
import multiprocessing
from contextlib import asynccontextmanager
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import atexit
import asyncio

ASSOCIATE_TAG = "your-amazon-associate-tag"  # Replace with your actual Amazon Associate tag
CACHE_DIR = "data"
CACHE_DURATION_SECONDS = 6 * 3600  # 6 hours




async def refresh_all_categories():
    print("[Scheduler] Auto-refreshing all categories...")

    async def refresh_category(cat):
        try:
            data = await scrape_best_sellers(cat)
            save_cached_data(cat, data)
            print(f"[Scheduler] Refreshed: {cat}")
        except Exception as e:
            print(f"[Scheduler] Failed to refresh {cat}: {e}")

    tasks = [refresh_category(cat) for cat in CATEGORY_URLS]
    await asyncio.gather(*tasks)



CATEGORY_URLS = {
    "amazon-devices": "https://www.amazon.com/Best-Sellers-Amazon-Devices-Accessories/zgbs/amazon-devices/ref=zg_bs_nav_amazon-devices_0",
    "amazon-renewed": "https://www.amazon.com/Best-Sellers-Amazon-Renewed/zgbs/amazon-renewed/ref=zg_bs_nav_amazon-renewed_0",
    "appliances": "https://www.amazon.com/Best-Sellers-Appliances/zgbs/appliances/ref=zg_bs_nav_appliances_0",
    "mobile-apps": "https://www.amazon.com/Best-Sellers-Apps-Games/zgbs/mobile-apps/ref=zg_bs_nav_mobile-apps_0",
    "arts-crafts": "https://www.amazon.com/Best-Sellers-Arts-Crafts-Sewing/zgbs/arts-crafts/ref=zg_bs_nav_arts-crafts_0",
    "audible": "https://www.amazon.com/Best-Sellers-Audible-Books-Originals/zgbs/audible/ref=zg_bs_nav_audible_0",
    "automotive": "https://www.amazon.com/Best-Sellers-Automotive/zgbs/automotive/ref=zg_bs_nav_automotive_0",
    "baby-products": "https://www.amazon.com/Best-Sellers-Baby/zgbs/baby-products/ref=zg_bs_nav_baby-products_0",
    "beauty": "https://www.amazon.com/Best-Sellers-Beauty-Personal-Care/zgbs/beauty/ref=zg_bs_nav_beauty_0",
    "books": "https://www.amazon.com/best-sellers-books-Amazon/zgbs/books/ref=zg_bs_nav_books_0",
    "photo": "https://www.amazon.com/best-sellers-camera-photo/zgbs/photo/ref=zg_bs_nav_photo_0",
    "music": "https://www.amazon.com/best-sellers-music-albums/zgbs/music/ref=zg_bs_nav_music_0",
    "wireless": "https://www.amazon.com/Best-Sellers-Cell-Phones-Accessories/zgbs/wireless/ref=zg_bs_nav_wireless_0",
    "fashion": "https://www.amazon.com/Best-Sellers-Clothing-Shoes-Jewelry/zgbs/fashion/ref=zg_bs_nav_fashion_0",
    "coins": "https://www.amazon.com/Best-Sellers-Collectible-Coins/zgbs/coins/ref=zg_bs_nav_coins_0",
    "pc": "https://www.amazon.com/Best-Sellers-Computers-Accessories/zgbs/pc/ref=zg_bs_nav_pc_0",
    "digital-educational-resources": "https://www.amazon.com/Best-Sellers-Digital-Educational-Resources/zgbs/digital-educational-resources/ref=zg_bs_nav_digital-educational-resources_0",
    "digital-music": "https://www.amazon.com/Best-Sellers-Digital-Music/zgbs/dmusic/ref=zg_bs_nav_dmusic_0",
    "electronics": "https://www.amazon.com/Best-Sellers-Electronics/zgbs/electronics/ref=zg_bs_nav_electronics_0",
    "entertainment-collectibles": "https://www.amazon.com/Best-Sellers-Entertainment-Collectibles/zgbs/entertainment-collectibles/ref=zg_bs_nav_entertainment-collectibles_0",
    "gift-cards": "https://www.amazon.com/Best-Sellers-Gift-Cards/zgbs/gift-cards/ref=zg_bs_nav_gift-cards_0",
    "grocery": "https://www.amazon.com/Best-Sellers-Grocery-Gourmet-Food/zgbs/grocery/ref=zg_bs_nav_grocery_0",
    "handmade": "https://www.amazon.com/Best-Sellers-Handmade-Products/zgbs/handmade/ref=zg_bs_nav_handmade_0",
    "health-household": "https://www.amazon.com/Best-Sellers-Health-Household/zgbs/hpc/ref=zg_bs_nav_hpc_0",
    "home-garden": "https://www.amazon.com/Best-Sellers-Home-Kitchen/zgbs/home-garden/ref=zg_bs_nav_home-garden_0",
    "industrial": "https://www.amazon.com/Best-Sellers-Industrial-Scientific/zgbs/industrial/ref=zg_bs_nav_industrial_0",
    "digital-text": "https://www.amazon.com/Best-Sellers-Kindle-Store/zgbs/digital-text/ref=zg_bs_nav_digital-text_0",
    "kitchen": "https://www.amazon.com/Best-Sellers-Kitchen-Dining/zgbs/kitchen/ref=zg_bs_nav_kitchen_0",
    "movies-tv": "https://www.amazon.com/best-sellers-movies-TV-DVD-Blu-ray/zgbs/movies-tv/ref=zg_bs_nav_movies-tv_0",
    "musical-instruments": "https://www.amazon.com/Best-Sellers-Musical-Instruments/zgbs/musical-instruments/ref=zg_bs_nav_musical-instruments_0",
    "office-products": "https://www.amazon.com/Best-Sellers-Office-Products/zgbs/office-products/ref=zg_bs_nav_office-products_0",
    "lawn-garden": "https://www.amazon.com/Best-Sellers-Patio-Lawn-Garden/zgbs/lawn-garden/ref=zg_bs_nav_lawn-garden_0",
    "pet-supplies": "https://www.amazon.com/Best-Sellers-Pet-Supplies/zgbs/pet-supplies/ref=zg_bs_nav_pet-supplies_0",
    "software": "https://www.amazon.com/best-sellers-software/zgbs/software/ref=zg_bs_nav_software_0",
    "sporting-goods": "https://www.amazon.com/Best-Sellers-Sports-Outdoors/zgbs/sporting-goods/ref=zg_bs_nav_sporting-goods_0",
    "sports-collectibles": "https://www.amazon.com/Best-Sellers-Sports-Collectibles/zgbs/sports-collectibles/ref=zg_bs_nav_sports-collectibles_0",
    "Home-Tools": "https://www.amazon.com/Best-Sellers-Tools-Home-Improvement/zgbs/hi/ref=zg_bs_nav_hi_0",
    "toys-and-games": "https://www.amazon.com/Best-Sellers-Toys-Games/zgbs/toys-and-games/ref=zg_bs_nav_toys-and-games_0",
    "unique": "https://www.amazon.com/Best-Sellers-Unique-Finds/zgbs/boost/ref=zg_bs_nav_boost_0",
    "videogames": "https://www.amazon.com/best-sellers-video-games/zgbs/videogames/ref=zg_bs_nav_videogames_0",
}


def load_cached_data(category): 
    cache_file = os.path.join(CACHE_DIR, f"{category}.json")
    if not os.path.exists(cache_file):
        return None

    modified_time = os.path.getmtime(cache_file)
    if time.time() - modified_time > CACHE_DURATION_SECONDS:
        return None  # Cache is stale

    with open(cache_file, "r", encoding="utf-8") as f:
        return json.load(f)

def save_cached_data(category, data):
    os.makedirs(CACHE_DIR, exist_ok=True)
    with open(os.path.join(CACHE_DIR, f"{category}.json"), "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

import httpx
from bs4 import BeautifulSoup

async def scrape_best_sellers(category):
    url = CATEGORY_URLS.get(category.lower())
    if not url:
        return []

    async with httpx.AsyncClient(http2=True, timeout=10.0, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36"
    }) as client:
        response = await client.get(url)
        soup = BeautifulSoup(response.text, "lxml")

    products = []
    items = soup.select("div.p13n-grid-content > div > div")[:60]

    for index, item in enumerate(items, start=1):
        try:
            title = (item.select_one("._cDEzb_p13n-sc-css-line-clamp-1_1Fn1y") or
                     item.select_one("._cDEzb_p13n-sc-css-line-clamp-2_EWgCb") or
                     item.select_one("._cDEzb_p13n-sc-css-line-clamp-3_g3dy1") or
                     item.select_one("div[class*='line-clamp']") or
                     item.select_one("a.a-link-normal"))
            title = title.get_text(strip=True) if title else "N/A"

            link = item.select_one("a.a-link-normal")
            link = link['href'] if link else "#"
            link = f"https://www.amazon.com{link}?tag={ASSOCIATE_TAG}"

            image = item.select_one("img")
            image = image['src'] if image else ""

            price = (item.select_one("span.p13n-sc-price") or
                     item.select_one("span._cDEzb_p13n-sc-price_3mJ9Z") or
                     item.select_one("span.a-price > span.a-offscreen"))
            price = price.get_text(strip=True) if price else "N/A"

            rating = (item.select_one("span.a-icon-alt") or
                      item.select_one("i.a-icon-star span"))
            raw_rating = rating.get_text(strip=True) if rating else "N/A"
            rating = raw_rating.split(" out of")[0] if "out of" in raw_rating else raw_rating

            if title == "N/A" or link == "#" or not image:
                continue

            products.append({
                "rank": index,
                "title": title,
                "link": link,
                "image": image,
                "price": price,
                "rating": rating,
            })

        except Exception as e:
            print(f"[ERROR] #{index}: {e}")
            continue

    return products



# Lifespan handler for startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    if multiprocessing.current_process().name == "MainProcess":
        scheduler = BackgroundScheduler()

        def sync_refresh():
            asyncio.run(refresh_all_categories())

        scheduler.add_job(
            sync_refresh,
            trigger=IntervalTrigger(hours=24),
            id="daily_refresh",
            replace_existing=True
        )
        scheduler.start()
        print("[Scheduler] Started daily async job")
        atexit.register(lambda: scheduler.shutdown())

    yield
    print("[Lifespan] Shutdown...")


app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="Frontend"), name="static")

@app.get("/", response_class=HTMLResponse)
async def serve_frontend():
    with open("Frontend/index.html", "r", encoding="utf-8") as f:
        return f.read()


@app.get("/api/bestsellers/{category}")
async def get_best_sellers(category: str, refresh: bool = Query(False)):
    if not refresh:
        cached = load_cached_data(category)
        if cached:
            return cached

    data = await scrape_best_sellers(category)
    save_cached_data(category, data)
    return data


@app.post("/api/bestsellers/refresh-all")
async def manual_refresh_all():
    await refresh_all_categories()
    return {"status": "Refreshed all categories"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
