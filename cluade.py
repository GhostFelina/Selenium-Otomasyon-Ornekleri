from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime
import os


def run_professional_automation():
    """
    Profesyonel Web Otomasyon Fonksiyonu
    Müşteri projelerinde kullanıma hazır, sağlam yapı
    """
    driver = None

    try:
        # ADIM 1: Chrome Tarayıcısını Profesyonel Ayarlarla Hazırla
        print("=" * 60)
        print("🚀 OTOMASYON BAŞLIYOR...")
        print("=" * 60)

        chrome_options = Options()
        chrome_options.add_argument("--start-maximized")  # Tam ekran başlat
        chrome_options.add_argument("--incognito")  # Gizli mod (temiz oturum)
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")  # Bot tespitini zorlaştır
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)

        # WebDriver Manager ile otomatik driver yönetimi
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)

        print("✅ Tarayıcı başarıyla başlatıldı (Gizli Mod, Tam Ekran)")

        # ADIM 2: Hedef Siteye Git ve Yüklenmeyi Bekle
        target_url = "https://www.seyyahlab.com"
        print(f"\n🌐 Hedefe gidiliyor: {target_url}")
        driver.get(target_url)

        # Sayfa başlığının yüklenmesini dinamik olarak bekle (max 10 saniye)
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))

        page_title = driver.title
        print(f"✅ Sayfa Başlığı: '{page_title}'")
        print(f"✅ Mevcut URL: {driver.current_url}")

        # ADIM 3: Link Analizi (Müşteriye değer katacak veri toplama)
        print("\n📊 LİNK ANALİZİ YAPILIYOR...")

        # Tüm linklerin yüklenmesini bekle
        wait.until(EC.presence_of_all_elements_located((By.TAG_NAME, "a")))

        all_links = driver.find_elements(By.TAG_NAME, "a")
        total_links = len(all_links)

        # Detaylı analiz
        valid_links = [link for link in all_links if link.get_attribute("href")]
        empty_links = total_links - len(valid_links)

        print(f"✅ Toplam Link Sayısı: {total_links}")
        print(f"   ├─ Geçerli Linkler (href olan): {len(valid_links)}")
        print(f"   └─ Boş Linkler (href olmayan): {empty_links}")

        # İlk 5 linki örnek olarak göster
        if len(valid_links) > 0:
            print("\n📌 İlk 5 Geçerli Link Örneği:")
            for i, link in enumerate(valid_links[:5], 1):
                href = link.get_attribute("href")
                text = link.text.strip() or "[Metin Yok]"
                print(f"   {i}. {text[:50]} -> {href[:60]}...")

        # ADIM 4: Kullanıcı Gibi Davran - Sayfayı Scroll Et
        print("\n⬇️ Sayfa en alta kaydırılıyor (Kullanıcı simülasyonu)...")

        # Sayfanın tamamen yüklenmesini bekle
        driver.execute_script("return document.readyState") == "complete"

        # Sayfa yüksekliğini al ve en alta in
        page_height = driver.execute_script("return document.body.scrollHeight")
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Scroll sonrası yeni elementlerin yüklenmesini bekle (dinamik siteler için)
        wait.until(lambda d: d.execute_script("return document.readyState") == "complete")

        print(f"✅ Sayfa başarıyla kaydırıldı (Yükseklik: {page_height}px)")

        # ADIM 5: Kanıt Toplama - Ekran Görüntüsü Al
        print("\n📸 EKRAN GÖRÜNTÜSÜ ALINIYOR...")

        # Dosya adında tarih-saat damgası kullan
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        screenshot_name = f"proof_seyyahlab_{timestamp}.png"

        # Screenshots klasörü oluştur (yoksa)
        os.makedirs("screenshots", exist_ok=True)
        screenshot_path = os.path.join("screenshots", screenshot_name)

        driver.save_screenshot(screenshot_path)
        print(f"✅ Ekran görüntüsü kaydedildi: {screenshot_path}")

        # BAŞARI RAPORU
        print("\n" + "=" * 60)
        print("🎉 OTOMASYON BAŞARIYLA TAMAMLANDI!")
        print("=" * 60)
        print(f"📊 Toplam İşlem Süresi: {datetime.now()}")
        print(f"📁 Kanıt Dosyası: {screenshot_path}")
        print("=" * 60)

    except Exception as e:
        # Hata yönetimi - Müşteriye detaylı rapor sunabilirsin
        print("\n" + "=" * 60)
        print("❌ HATA OLUŞTU!")
        print("=" * 60)
        print(f"Hata Tipi: {type(e).__name__}")
        print(f"Hata Mesajı: {str(e)}")
        print("=" * 60)

        # Hata durumunda da ekran görüntüsü al (debugging için)
        if driver:
            try:
                error_screenshot = f"screenshots/error_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                os.makedirs("screenshots", exist_ok=True)
                driver.save_screenshot(error_screenshot)
                print(f"📸 Hata ekran görüntüsü: {error_screenshot}")
            except:
                pass

    finally:
        # Tarayıcıyı mutlaka kapat (Kaynak sızıntısını önle)
        if driver:
            print("\n🔒 Tarayıcı kapatılıyor...")
            driver.quit()
            print("✅ Tarayıcı başarıyla kapatıldı. Sistem temiz!")


# Programı çalıştır
if __name__ == "__main__":
    run_professional_automation()