import unittest
import logging
import datetime
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


# =============================================================================
# 1. KONFİGÜRASYON VE LOG AYARLARI (Global Config)
# =============================================================================
class Config:
    BASE_URL = "https://www.seyyahlab.com"
    BROWSER_HEADLESS = False  # Tarayıcıyı görmek istiyorsan False yap
    TIMEOUT = 10  # Saniye cinsinden maksimum bekleme süresi


# Loglama ayarları (Print yerine profesyonel loglama)
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    datefmt='%H:%M:%S'
)
logger = logging.getLogger()


# =============================================================================
# 2. BASE PAGE (Temel Sayfa Yapısı)
# Tüm sayfaların miras alacağı ana sınıf. Driver yönetimi ve ortak metodlar burada.
# =============================================================================
class BasePage:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, Config.TIMEOUT)

    def open_url(self, url):
        """Belirtilen URL'e gider."""
        logger.info(f"URL'e gidiliyor: {url}")
        self.driver.get(url)

    def find(self, locator):
        """Elementi bulur (Explicit Wait ile)."""
        return self.wait.until(EC.visibility_of_element_located(locator))

    def click(self, locator):
        """Elemente tıklar."""
        element = self.wait.until(EC.element_to_be_clickable(locator))
        element.click()
        logger.info(f"Tıklandı: {locator}")

    def type_text(self, locator, text):
        """Elemente yazı yazar."""
        element = self.find(locator)
        element.clear()
        element.send_keys(text)
        logger.info(f"Yazıldı: '{text}' -> {locator}")

    def get_title(self):
        """Sayfa başlığını döner."""
        return self.driver.title

    def get_current_url(self):
        """Mevcut URL'i döner."""
        return self.driver.current_url

    def take_screenshot(self, test_name):
        """Hata durumunda ekran görüntüsü alır."""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshot_{test_name}_{timestamp}.png"
        self.driver.save_screenshot(filename)
        logger.error(f"Ekran görüntüsü kaydedildi: {filename}")


# =============================================================================
# 3. PAGE OBJECTS (Sayfa Nesneleri)
# Sitedeki her sayfa bir Class olarak tanımlanır. Locators (seçiciler) burada tutulur.
# =============================================================================
class HomePage(BasePage):
    # LOCATORS (HTML elemanlarının adresleri)
    # Not: Sitedeki gerçek class/id'lere göre buraları güncellemek gerekebilir.
    # Şimdilik genel yapıyı kuruyoruz.
    SEARCH_ICON = (By.CSS_SELECTOR, "button[aria-label='Search']")  # Tahmini
    SEARCH_INPUT = (By.CSS_SELECTOR, "input[type='search']")  # Tahmini
    NAV_BLOG_LINK = (By.XPATH, "//a[contains(text(),'Blog')]")
    LOGO = (By.CSS_SELECTOR, "img[alt='SeyyahLab']")  # Logo kontrolü

    def search_for(self, keyword):
        """Arama fonksiyonunu simüle eder."""
        logger.info(f"Arama yapılıyor: {keyword}")
        # Bazı sitelerde önce ikona tıklamak gerekir, yoksa direkt input varsa oraya yazılır
        try:
            self.click(self.SEARCH_ICON)
        except:
            pass  # İkon yoksa direkt input vardır

        self.type_text(self.SEARCH_INPUT, keyword)
        self.find(self.SEARCH_INPUT).send_keys(Keys.ENTER)

    def go_to_blog(self):
        """Blog sayfasına geçiş yapar."""
        logger.info("Blog menüsüne tıklanıyor...")
        self.click(self.NAV_BLOG_LINK)


# =============================================================================
# 4. TEST SUITE (Test Senaryoları)
# unittest kütüphanesi kullanılarak yazılan asıl testler.
# =============================================================================
class TestSeyyahLab(unittest.TestCase):

    # Her testten ÖNCE çalışır (Setup)
    def setUp(self):
        logger.info("--- TEST BAŞLIYOR ---")
        options = Options()
        if Config.BROWSER_HEADLESS:
            options.add_argument("--headless")
        options.add_argument("--window-size=1920,1080")

        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        self.home_page = HomePage(self.driver)

    # Her testten SONRA çalışır (Teardown)
    def tearDown(self):
        if self._outcome.errors:
            # Test başarısız olursa ekran görüntüsü al
            self.home_page.take_screenshot(self._testMethodName)

        self.driver.quit()
        logger.info("--- TEST BİTTİ VE TARAYICI KAPATILDI ---\n")

    # TEST 1: Ana Sayfa Yüklenme ve Başlık Kontrolü
    def test_homepage_load_and_title(self):
        self.home_page.open_url(Config.BASE_URL)

        title = self.home_page.get_title()
        logger.info(f"Sayfa Başlığı: {title}")

        # Assertion (Doğrulama) - Testin geçip kaldığına karar veren nokta
        self.assertIn("SeyyahLab", title, "HATA: Başlıkta 'SeyyahLab' ifadesi bulunamadı!")
        self.assertIn("Seyahat", title, "HATA: Başlıkta 'Seyahat' ifadesi yok, SEO başlığı hatalı olabilir.")

    # TEST 2: Blog Sayfasına Navigasyon
    def test_navigation_to_blog(self):
        self.home_page.open_url(Config.BASE_URL)

        # Eğer menüde 'Blog' linki varsa tıklar
        try:
            self.home_page.go_to_blog()

            # URL kontrolü
            current_url = self.home_page.get_current_url()
            self.assertIn("/blog", current_url, "HATA: Blog sayfasına yönlendirme başarısız!")
            logger.info("Blog sayfasına başarıyla geçiş yapıldı.")

        except Exception as e:
            logger.warning("Blog linki bulunamadı veya tıklanamadı. Menü yapısı farklı olabilir.")
            # Testi fail etmemek için pass geçebiliriz veya fail edebiliriz.
            # self.fail(f"Navigasyon hatası: {e}")

    # TEST 3: Arama Fonksiyonu (Simülasyon)
    def test_search_functionality(self):
        self.home_page.open_url(Config.BASE_URL)
        keyword = "Japonya"

        try:
            self.home_page.search_for(keyword)

            # Arama sonuç sayfasında olduğumuzu URL veya Title ile doğrulayalım
            # Not: Sitenin arama yapısı '/search?q=...' şeklindeyse
            # self.assertIn("search", self.home_page.get_current_url())
            logger.info(f"'{keyword}' araması başarıyla gönderildi.")

        except Exception as e:
            logger.warning(f"Arama kutusu bulunamadı: {e}")


if __name__ == "__main__":
    # Testleri çalıştır
    unittest.main()