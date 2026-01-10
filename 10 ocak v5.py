# Dosya Adı: test_vurgulama.py
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


# --- YARDIMCI FONKSİYON ---
def elementi_boya(driver, element):
    """
    Bu fonksiyon, verilen elementin etrafına JavaScript ile Kırmızı Çerçeve çizer.
    Görsel sunum ve hata ayıklama (debugging) için harikadır.
    """
    # JavaScript: Elementin stilini değiştir, kenarlık (border) ekle
    driver.execute_script(
        "arguments[0].setAttribute('style', 'border: 4px solid red; background: yellow; color: black;');", element)
    time.sleep(0.5)  # Gözümüz görsün diye yarım saniye bekle


# --- ANA TEST ---
def sunum_modu_testi():
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.maximize_window()

    url = "https://www.seyyahlab.com"
    print(f"🎨 Sunum Modu Başlatılıyor: {url}")
    driver.get(url)
    time.sleep(2)

    try:
        # 1. Ana Başlığı (H1) Bul ve Boya
        try:
            baslik = driver.find_element(By.TAG_NAME, "h1")
            print("Element Bulundu: Ana Başlık (H1)")
            elementi_boya(driver, baslik)
        except:
            print("H1 bulunamadı.")

        # 2. Sayfadaki Görselleri Bul ve İlk 3 Tanesini Boya
        gorseller = driver.find_elements(By.TAG_NAME, "img")
        print(f"Sayfada {len(gorseller)} görsel bulundu. İlk 3 tanesi işaretleniyor...")

        for i, gorsel in enumerate(gorseller):
            if i < 3:  # Sadece ilk 3 görseli boya
                elementi_boya(driver, gorsel)
            else:
                break

        # 3. Menü Linklerini (Nav içindeki a tagleri) Boya
        try:
            menu_linkleri = driver.find_elements(By.CSS_SELECTOR, "nav a")
            print("Menü linkleri işaretleniyor...")
            for link in menu_linkleri:
                elementi_boya(driver, link)
        except:
            pass

        # 4. Sayfayı Aşağı Kaydır ve Son Hali Kaydet
        driver.execute_script("window.scrollTo(0, 300);")
        time.sleep(1)

        dosya_adi = "boyanmis_sayfa.png"
        driver.save_screenshot(dosya_adi)
        print