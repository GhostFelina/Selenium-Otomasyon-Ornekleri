import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

# Ayarlar
options = Options()
options.add_argument("--window-size=1920,1080")
# Bot olduğumuzu gizleyelim, belki site içeriği saklıyordur
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument(
    "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

print("\n--- SAYFA TARANIYOR ---")
driver.get("https://www.seyyahlab.com")
time.sleep(5)  # Sayfanın iyice yüklenmesini bekle

# Sayfadaki TÜM tıklanabilir (link) öğeleri bul
linkler = driver.find_elements(By.TAG_NAME, "a")

print(f"Toplam {len(linkler)} adet link bulundu.\n")

print("-" * 50)
for i, link in enumerate(linkler):
    try:
        metin = link.text.strip()  # Boşlukları temizle
        adres = link.get_attribute("href")

        # Sadece içi dolu olanları yazdır ki ekran kirlenmesin
        if metin and len(metin) > 2:
            print(f"[{i}] METİN: {metin}  --->  ADRES: {adres}")
        elif adres and "blog" in adres:
            print(f"[{i}] (İsimsiz ama Blog Linki): {adres}")

    except:
        continue  # Hata veren linki geç

print("-" * 50)
print("\n--- TARAMA BİTTİ ---")
driver.quit()