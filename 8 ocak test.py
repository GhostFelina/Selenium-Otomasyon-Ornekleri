import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException


def test_seyyahlab_home():
    # --- 1. AYARLAR VE KURULUM ---
    print("Test Başlatılıyor: SeyyahLab...")

    # Tarayıcı ayarları (Headless mod kapalı, tarayıcıyı görelim)
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")  # Tam ekran başla

    # Driver kurulumu (Otomatik sürüm yönetimi ile)
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    target_url = "https://www.seyyahlab.com"

    try:
        # --- 2. SİTEYE GİDİŞ ---
        print(f"Siteye gidiliyor: {target_url}")
        driver.get(target_url)
        time.sleep(3)  # Sayfanın tam yüklenmesi için kısa bekleme (Daha profesyonel yöntem: WebDriverWait)

        # --- 3. TEMEL KONTROLLER ---

        # A. URL Kontrolü (Yönlendirme yapıldı mı?)
        current_url = driver.current_url
        if "seyyahlab.com" in current_url:
            print("✅ URL Doğrulama Başarılı.")
        else:
            print(f"❌ HATA: Yanlış URL -> {current_url}")

        # B. Başlık (Title) Kontrolü
        page_title = driver.title
        print(f"Sayfa Başlığı: {page_title}")
        if len(page_title) > 0:
            print("✅ Sayfa başlığı mevcut.")
        else:
            print("❌ Uyarı: Sayfa başlığı boş!")

        # --- 4. ELEMENT KONTROLLERİ ---
        # Not: Sitenin kaynak koduna göre bu seçicileri (class, id) güncellemelisin.
        # Aşağıdakiler genel HTML yapılarına göre tahmini kontrollerdir.

        # Logo veya Ana Başlık (H1) Kontrolü
        try:
            # Genelde logolar 'nav' içinde veya 'h1' etiketiyle bulunur.
            # Sitenin yapısına göre burayı güncelle: driver.find_element(By.ID, "logo-id") gibi.
            header_element = driver.find_element(By.TAG_NAME, "h1")
            print(f"✅ H1 Başlığı Bulundu: {header_element.text}")
        except NoSuchElementException:
            print("❌ Uyarı: H1 etiketi bulunamadı (Tasarımda olmayabilir).")

        # Navigasyon (Menü) Kontrolü
        try:
            nav_bar = driver.find_element(By.TAG_NAME, "nav")
            print("✅ Navigasyon (Menü) barı mevcut.")

            # Menü linklerini say
            links = nav_bar.find_elements(By.TAG_NAME, "a")
            print(f"ℹ️ Menüde {len(links)} adet link bulundu.")
        except NoSuchElementException:
            print("❌ Uyarı: <nav> etiketi bulunamadı.")

        # --- 5. ETKİLEŞİM VE GÖRSELLİK ---

        # Sayfayı aşağı kaydır (Footer'ı görmek için)
        print("Sayfa aşağı kaydırılıyor...")
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)

        # Ekran Görüntüsü Al (Kanıt)
        screenshot_name = "seyyahlab_test_sonucu.png"
        driver.save_screenshot(screenshot_name)
        print(f"📷 Ekran görüntüsü kaydedildi: {screenshot_name}")

        print("\n--- TEST BAŞARIYLA TAMAMLANDI ---")

    except Exception as e:
        print(f"\n❌ BEKLENMEYEN BİR HATA OLUŞTU: {e}")

    finally:
        # --- 6. KAPANIŞ ---
        print("Tarayıcı kapatılıyor...")
        driver.quit()


if __name__ == "__main__":
    test_seyyahlab_home()