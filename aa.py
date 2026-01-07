from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time

# Sadece yapıyı görmek için hızlı kurulum
options = webdriver.ChromeOptions()
options.add_argument("--headless")  # Arka planda çalışsın
options.add_argument(
    "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

print("🕵️  SeyyahLab HTML Analizi Başlıyor...")
driver.get("https://seyyahlab.com")
time.sleep(3)  # Yüklenmesini bekle

try:
    # Rehber kartlarından birini bulalım (h3 etiketi içeren bir div muhtemelen)
    # H3'ün içinde bulunduğu ana kutuyu (parent) bulmaya çalışıyoruz
    sample_header = driver.find_element(By.TAG_NAME, "h3")

    # H3'ün 2-3 seviye yukarısındaki ana kapsayıcıyı alalım
    card_container = sample_header.find_element(By.XPATH, "./..")  # 1 üst
    try:
        card_container = card_container.find_element(By.XPATH, "./..")  # 2 üst
    except:
        pass

    print("-" * 30)
    print("Mevcut Kartın HTML Kodları:")
    print("-" * 30)
    print(card_container.get_attribute('outerHTML'))
    print("-" * 30)

    # Ayrıca sayfadaki ilk SVG ve PICTURE elementine bakalım
    try:
        svg = driver.find_element(By.TAG_NAME, "svg")
        print("\n✅ SVG Bulundu! Örnek: <svg ...>")
    except:
        print("\n❌ SVG Bulunamadı.")

    try:
        pic = driver.find_element(By.TAG_NAME, "picture")
        print("✅ PICTURE/SOURCE Bulundu! (Modern resim formatı)")
    except:
        print("❌ PICTURE etiketi bulunamadı.")

except Exception as e:
    print(f"Hata: {e}")

driver.quit()