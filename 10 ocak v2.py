# Dosya Adı: test_hiz.py
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time


def performans_testi():
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    url = "https://www.seyyahlab.com"

    print(f"⏱ Hız testi başlıyor: {url}")
    driver.get(url)

    # JavaScript ile tarayıcı içindeki performans verisini çekiyoruz
    navigation_start = driver.execute_script("return window.performance.timing.navigationStart")
    load_event_end = driver.execute_script("return window.performance.timing.loadEventEnd")

    # Hesaplama (Bitiş - Başlangıç = Geçen Süre)
    yuklenme_suresi = (load_event_end - navigation_start) / 1000

    print(f"✅ Site Tam Yüklenme Süresi: {yuklenme_suresi} saniye")

    if yuklenme_suresi > 3:
        print("⚠️ Uyarı: Site 3 saniyeden geç açılıyor, optimizasyon lazım!")
    else:
        print("🚀 Harika! Site çok hızlı.")

    driver.quit()


if __name__ == "__main__":
    performans_testi()