import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

# Ayarlar
options = Options()
options.add_argument("--window-size=1920,1080")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

print("--- LİNKLER TARANIYOR ---")
driver.get("https://www.seyyahlab.com")
time.sleep(5)  # Sayfa tam otursun diye uzun bekliyoruz

# Sayfadaki TÜM <a> etiketlerini bul
linkler = driver.find_elements(By.TAG_NAME, "a")

print(f"Toplam {len(linkler)} adet link bulundu.\n")

for i, link in enumerate(linkler):
    try:
        metin = link.text
        adres = link.get_attribute("href")

        # Sadece boş olmayan, işe yarar linkleri yazdır
        if metin or adres:
            print(f"[{i}] Metin: '{metin}'  |  Link: {adres}")
    except:
        print(f"[{i}] -- Okunamadı --")

print("\n--- TARAMA BİTTİ ---")
driver.quit()