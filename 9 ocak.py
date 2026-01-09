import logging
import time
import os
from datetime import datetime
from functools import wraps
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


# --- 1. AYARLAR (CONFIG) ---
class Config:
    BASE_URL = "https://www.seyyahlab.com"
    TIMEOUT = 20  # Saniye
    HEADLESS = False  # Tarayıcıyı gizli çalıştırmak için True yap
    SCREENSHOT_DIR = "raporlar/ekran_goruntuleri"


# --- 2. LOGLAMA AYARLARI ---
# Klasör yoksa oluştur
if not os.path.exists(Config.SCREENSHOT_DIR):
    os.makedirs(Config.SCREENSHOT_DIR)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("test_loglari.log", mode='w', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger()


# --- 3. DECORATOR (Hata Anında Otomatik Screenshot) ---
def ekran_goruntusu_al_on_error(func):
    """Bir fonksiyon hata verirse otomatik ekran görüntüsü alan süslü fonksiyon."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            # args[0] genelde 'self'tir, yani Page class'ıdır.
            page_instance = args[0]
            if hasattr(page_instance, 'driver'):
                driver = page_instance.driver
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                dosya_adi = f"{Config.SCREENSHOT_DIR}/HATA_{func.__name__}_{timestamp}.png"
                driver.save_screenshot(dosya_adi)
                logger.error(f"❌ HATA ALINDI! Ekran görüntüsü kaydedildi: {dosya_adi}")
            raise e

    return wrapper


# --- 4. BASE PAGE (TEMEL SINIF) ---
class BasePage:
    """Tüm sayfaların atası. Driver ve ortak wait metodlarını içerir."""

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, Config.TIMEOUT)

    def find(self, locator):
        """Elementi görünür olana kadar bekler ve bulur."""
        return self.wait.until(EC.visibility_of_element_located(locator))

    def click(self, locator):
        """Elemente tıklanabilir olana kadar bekler ve tıklar."""
        element = self.wait.until(EC.element_to_be_clickable(locator))
        element.click()

    def type_text(self, locator, text):
        """Elementi bulur, temizler ve yazıyı yazar."""
        element = self.find(locator)
        element.clear()
        element.send_keys(text)
        logger.info(f"Yazı yazıldı: '{text}' -> {locator}")

    def get_title(self):
        return self.driver.title


# --- 5. PAGE OBJECTS (SAYFA SINIFLARI) ---
class HomePage(BasePage):
    """Sadece Ana Sayfa ile ilgili elementler ve işlemler buradadır."""

    # Locators (Değişirse sadece burayı güncellersin)
    # NOT: Sitede gerçek bir arama butonu Class'ı veya ID'si neyse buraya yazılmalı.
    # Örnek olarak genel CSS selectorler kullanıyorum.
    SEARCH_ICON = (By.CSS_SELECTOR, "div.search-icon, button.search-trigger, .header-search")
    SEARCH_INPUT = (By.CSS_SELECTOR, "input[type='search'], input[name='s'], input.search-field")

    def siteye_git(self):
        logger.info(f"Siteye gidiliyor: {Config.BASE_URL}")
        self.driver.get(Config.BASE_URL)

    @ekran_goruntusu_al_on_error
    def arama_yap(self, kelime):
        """Arama kutusunu bulur ve arama yapar."""
        # Bazen arama inputu gizlidir, önce bir ikona tıklamak gerekir.
        # Eğer ikon yoksa doğrudan inputa yazmayı dener.
        try:
            # 2 saniyelik hızlı bir kontrol yapıyoruz, ikon var mı diye
            WebDriverWait(self.driver, 3).until(EC.element_to_be_clickable(self.SEARCH_ICON)).click()
            logger.info("Arama ikonuna tıklandı.")
        except:
            logger.info("Arama ikonu bulunamadı veya gerekli değil, direkt input aranıyor.")

        self.type_text(self.SEARCH_INPUT, kelime)
        self.find(self.SEARCH_INPUT).send_keys(Keys.ENTER)
        logger.info(f"'{kelime}' için Enter tuşuna basıldı.")


class SearchResultsPage(BasePage):
    """Arama Sonuç Sayfası işlemleri."""

    # Genel blog/wordpress başlık yapıları
    RESULT_TITLES = (By.CSS_SELECTOR, "h2.post-title, .entry-title, article h3, .search-result h2")

    @ekran_goruntusu_al_on_error
    def sonuclari_dogrula(self, aranan_kelime):
        """Sonuçların yüklendiğini ve aranan kelimeyi içerip içermediğini kontrol eder."""
        self.wait.until(EC.url_contains("s=") or EC.url_contains("search"))
        logger.info("URL değişimi doğrulandı.")

        # Sayfadaki makale başlıklarını çek
        basliklar = self.wait.until(EC.presence_of_all_elements_located(self.RESULT_TITLES))

        bulundu = False
        logger.info(f"Bulunan Makale Sayısı: {len(basliklar)}")

        for baslik in basliklar:
            text = baslik.text.lower()
            logger.info(f"Sonuç Başlığı: {text}")
            if aranan_kelime.lower() in text:
                bulundu = True
                # break # Hepsini loglamak istersen bu break'i kaldır.

        if bulundu:
            logger.info("✅ TEST BAŞARILI: İlgili içerik sonuçlarda bulundu.")
        else:
            logger.warning(f"⚠️ UYARI: Sonuçlar listelendi ama başlıklarda '{aranan_kelime}' tam eşleşmedi.")


# --- 6. TEST RUNNER (TESTİ ÇALIŞTIRAN KISIM) ---
class TestSeyyahLab:

    def setup_method(self):
        """Her testten önce çalışır."""
        chrome_options = Options()
        if Config.HEADLESS:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--disable-notifications")

        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        logger.info("Test Ortamı Başlatıldı.")

    def teardown_method(self):
        """Her testten sonra çalışır."""
        if self.driver:
            self.driver.quit()
            logger.info("Tarayıcı kapatıldı.")

    def run_test(self):
        self.setup_method()
        try:
            # POM Kullanımı: Test kodları artık çok temiz!
            # Adeta İngilizce cümle okur gibi:

            home = HomePage(self.driver)
            results = SearchResultsPage(self.driver)

            # 1. Ana sayfaya git
            home.siteye_git()

            # 2. Başlığı kontrol et
            current_title = home.get_title()
            logger.info(f"Sayfa Başlığı: {current_title}")

            # 3. Arama yap
            home.arama_yap("Vize")  # Burayı değiştirebilirsin

            # 4. Sonuçları kontrol et
            results.sonuclari_dogrula("Vize")

        except Exception as e:
            logger.critical(f"🛑 TEST PATLADI: {e}")
            # Ana seviyede de ekran görüntüsü alalım garanti olsun
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.driver.save_screenshot(f"{Config.SCREENSHOT_DIR}/FATAL_ERROR_{timestamp}.png")

        finally:
            self.teardown_method()


# --- UYGULAMAYI BAŞLAT ---
if __name__ == "__main__":
    app = TestSeyyahLab()
    app.run_test()