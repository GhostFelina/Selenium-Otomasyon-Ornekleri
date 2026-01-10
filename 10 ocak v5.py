import time
import logging
from datetime import datetime
import os

# Selenium Kütüphaneleri
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager


class SeyyahLabTester:
    """
    Bu sınıf, seyyahlab.com sitesi için profesyonel bir test otomasyonu
    çerçevesi sunar. Hataları yakalar, raporlar ve ekran görüntüsü alır.
    """

    def __init__(self, target_url):
        self.url = target_url
        self.driver = None
        self.wait = None

        # LOGLAMA AYARLARI (Müşteriye sunulacak raporun temeli)
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler("test_raporu.log", mode='w', encoding='utf-8'),  # Dosyaya yazar
                logging.StreamHandler()  # Konsola yazar
            ]
        )
        self.logger = logging.getLogger()

    def setup_driver(self):
        """
        Chrome tarayıcısını 'Robust' (Sağlam) ayarlarla başlatır.
        """
        self.logger.info("🔧 Test Ortamı Hazırlanıyor...")

        chrome_options = Options()
        # chrome_options.add_argument("--headless") # Tarayıcıyı görmeden arka planda çalıştırmak istersen bunu aç.
        chrome_options.add_argument("--start-maximized")  # Tam ekran başla
        chrome_options.add_argument("--incognito")  # Gizli sekme (Önbellek sorunlarını önler)
        chrome_options.add_argument("--disable-notifications")  # Bildirimleri engelle

        # Tarayıcıyı ayağa kaldır
        try:
            self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
            # 15 saniyelik bir 'Güvenlik Görevlisi' (Wait) atıyoruz
            self.wait = WebDriverWait(self.driver, 15)
            self.logger.info("✅ Chrome başarıyla başlatıldı.")
        except Exception as e:
            self.logger.error(f"❌ Driver başlatılırken hata oluştu: {e}")
            raise  # Hatayı yukarı fırlat ki program dursun

    def capture_screenshot(self, step_name):
        """
        Kanıt toplama fonksiyonu. Testin o anki görüntüsünü kaydeder.
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshot_{step_name}_{timestamp}.png"
        try:
            self.driver.save_screenshot(filename)
            self.logger.info(f"📸 Ekran görüntüsü alındı: {filename}")
        except Exception as e:
            self.logger.warning(f"⚠️ Ekran görüntüsü alınamadı: {e}")

    def run_health_check(self):
        """
        Ana test senaryosunu çalıştırır.
        """
        try:
            # 1. ADIM: Siteye Git
            self.logger.info(f"🌍 {self.url} adresine gidiliyor...")
            self.driver.get(self.url)

            # 2. ADIM: Sayfanın yüklendiğini doğrula (Title Kontrolü)
            expected_keyword = "Seyyah"  # Başlıkta geçmesi gereken kelime

            # Burada 'Güvenlik Görevlisi' (Wait) devreye giriyor. Title gelene kadar bekler.
            if self.wait.until(EC.title_contains(expected_keyword)):
                actual_title = self.driver.title
                self.logger.info(f"✅ Sayfa Başlığı Doğrulandı: {actual_title}")

            # 3. ADIM: Ana gövdenin (Body) görünür olmasını bekle
            body_element = self.wait.until(EC.visibility_of_element_located((By.TAG_NAME, "body")))
            self.logger.info("✅ Ana sayfa içeriği görünür durumda.")

            # Kanıt alalım
            self.capture_screenshot("homepage_loaded")

            # 4. ADIM: Sayfadaki Linkleri Analiz Et (Mini Audit)
            links = self.driver.find_elements(By.TAG_NAME, "a")
            self.logger.info(f"🔍 Sayfada toplam {len(links)} adet link bulundu.")

            # İlk 5 linki kontrol edelim (Demo amaçlı, hepsini taramak uzun sürer)
            for index, link in enumerate(links[:5], start=1):
                url_href = link.get_attribute("href")
                link_text = link.text
                if url_href:
                    self.logger.info(f"   ➡️ Link {index}: Text='{link_text}' | URL={url_href}")
                else:
                    self.logger.warning(f"   ⚠️ Link {index}: Boş veya geçersiz link bulundu.")

            # 5. ADIM: Footer (Alt Bilgi) Görünüyor mu?
            # Sayfayı aşağı kaydır (JavaScript ile)
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)  # Kaydırma animasyonu için kısa bir mola (Zorunlu değil ama insan gözü için iyi)
            self.capture_screenshot("footer_area")
            self.logger.info("⬇️ Sayfa sonuna inildi.")

        except TimeoutException:
            self.logger.error("⏳ HATA: Beklenen element zamanında gelmedi! Site yavaş olabilir.")
            self.capture_screenshot("timeout_error")
        except NoSuchElementException:
            self.logger.error("❌ HATA: Aranan element sayfada bulunamadı.")
        except Exception as e:
            self.logger.error(f"💥 Beklenmedik bir hata oluştu: {e}")
        finally:
            self.tear_down()

    def tear_down(self):
        """
        Temizlik işlemi. Tarayıcıyı kapatır.
        """
        if self.driver:
            self.logger.info("🛑 Test bitti. Tarayıcı kapatılıyor...")
            self.driver.quit()


# --- UYGULAMA ÇALIŞTIRMA BLOĞU ---
if __name__ == "__main__":
    # Kullanıcının sitesini hedefliyoruz
    target_site = "https://www.seyyahlab.com"

    # Test robotumuzu oluşturuyoruz
    bot = SeyyahLabTester(target_site)

    # Testi başlatıyoruz
    bot.setup_driver()
    bot.run_health_check()