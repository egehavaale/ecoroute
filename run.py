import uvicorn
import webbrowser
import threading
import time
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("EcoRoute")

def open_browser():
    time.sleep(1.2)
    url = "http://127.0.0.1:8000"
    logger.info(f"Tarayıcı açılıyor: {url}")
    try:
        webbrowser.open(url)
    except Exception:
        pass

if __name__ == "__main__":
    logger.info("=" * 65)
    logger.info(" EcoRoute / UrbanEco Tracker - Smart City Logistics Dashboard")
    logger.info("=" * 65)
    logger.info(" Sunucu başlatılıyor: http://127.0.0.1:8000")
    logger.info(" Swagger API Dokümantasyonu: http://127.0.0.1:8000/docs")
    logger.info("=" * 65)
    
    threading.Thread(target=open_browser, daemon=True).start()
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)