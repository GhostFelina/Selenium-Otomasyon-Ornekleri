# Dosya Adı: test_klavye.py
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys  # Klavye tuşları için
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


def klavye_aksiyon_testi():
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.maximize_window()
    driver.get("https://www.seyyahlab.com")
    time.sleep(2)

    # 1. Sayfanın en altına in (END tuşu ile)
    print("⬇️ Sayfa en aşağı kaydırılıyor (END Tuşu)...")
    body = driver.find_element(By.TAG_NAME, "body")
    body.send_keys(Keys.END)
    time.sleep(2)

    # 2. Sayfanın en üstüne çık (HOME tuşu ile)
    print("⬆️ Sayfa en yukarı çıkıyor (HOME Tuşu)...")
    body.send_keys(Keys.HOME)
    time.sleep(2)

    # 3. Varsa arama kutusuna odaklan
    try:
        # Not: Sitenin yapısına göre buradaki Class veya ID değişebilir.
        # Genelde 's' name değeri WordPress sitelerde standarttır.
        search_box = driver.find_element(By.NAME, "s")
        search_box.send_keys("Test Otomasyonu")
        print("✍️ Arama kutusuna yazı yazıldı.")
        time.sleep(1)
        search_box.send_keys(Keys.ENTER)
        print("hook️ Enter tuşuna basıldı.")
    except:
        print("⚠️ Arama kutusu standart (name='s') bulunamadı, bu adım atlandı.")

    print("✅ Klavye simülasyon testi tamamlandı.")
    time.sleep(3)
    driver.quit()


if __name__ == "__main__":
    klavye_aksiyon_testi()