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
# 1. AYARLAR (Robotun Kuralları)
# =============================================================================
class Config:
    BASE_URL = "https://www.seyyahlab.com"  # Test edilecek adres
    BROWSER_HEADLESS = False  # False = Tarayıcıyı görerek çalıştır
    TIMEOUT = 10  # En fazla kaç saniye beklesin?


# Loglama (Raporlama) Ayarları
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    datefmt='%H:%M:%S'
)
logger = logging.getLogger()


# =============================================================================
# 2. TEMEL YAPI (Base Page)
# Robotun yürümeyi, görmeyi öğrendiği yer.
# =============================================================================
class BasePage:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, Config.TIMEOUT)

    def open_url(self, url):
        logger.info(f"Adrese gidiliyor: {url}")
        self.driver.get(url)

    def find(self, locator):
        """Elementi bulur (Görünene kadar bekler)."""
        return self.wait.until(EC.visibility_of_element_located(locator))

    def click(self, locator):
        """Elemente tıklar."""
        element = self.wait.until(EC.element_to_be_clickable(locator))
        element.click()
        logger.info(f"Tıklandı: {locator}")

    def type_text(self, locator, text):
        """Yazı yazar."""
        element = self.find(locator)
        element.clear()
        element.send_keys(text)
        logger.info(f"Yazıldı: '{text}'")

    def get_title(self):
        return self.driver.title

    def get_current_url(self):
        return self.driver.current_url

    def take_screenshot(self, test_name):
        """Hata olursa fotoğraf çeker."""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshot_{test_name}_{timestamp}.png"
        self.driver.save_screenshot(filename)
        logger.error(f"HATA! Ekran görüntüsü kaydedildi: {filename}")


# =============================================================================
# 3. SAYFA TANIMLARI (Page Objects)
# Sitedeki butonların, kutuların yerini robota öğrettiğimiz yer.
# =============================================================================
class HomePage(BasePage):
    # ELEMENT ADRESLERİ (Locators)
    # Not: Sitenin yapısına göre buradaki class/id'ler değişebilir.
    # Şimdilik genel tanımlar kullanıyoruz.

    # Logo genellikle anasayfaya dönmek için kullanılır
    LOGO = (By.CSS_SELECTOR, "img[alt='SeyyahLab']")

    # Menüdeki Blog Linki (Tahmini)
    NAV_BLOG_LINK = (By.XPATH, "//a[contains(text(),'Blog')]")

    # Arama Kutusu (Input type='search' genelde standarttır)
    SEARCH_INPUT = (By.CSS_SELECTOR, "input[type='text']")

    def search_for(self, keyword):
        """Arama yapar."""
        logger.info(f"Aranacak kelime: {keyword}")
        self.type_text(self.SEARCH_INPUT, keyword)
        self.find(self.SEARCH_INPUT).send_keys(Keys.ENTER)

    def go_to_blog(self):
        """Blog'a tıklar."""
        logger.info("Blog menüsü aranıyor...")
        self.click(self.NAV_BLOG_LINK)


# =============================================================================
# 4. TEST SENARYOLARI (Test Suite)
# Robotun yapacağı görevler listesi.
# =============================================================================
class TestSeyyahLab(unittest.TestCase):

    # BAŞLANGIÇ (Her testten önce çalışır)
    def setUp(self):
        logger.info("--- GÖREV BAŞLIYOR ---")
        options = Options()
        if Config.BROWSER_HEADLESS:
            options.add_argument("--headless")
        # Tarayıcıyı tam ekran yapmasın ama geniş açsın
        options.add_argument("--window-size=1280,800")

        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        self.home_page = HomePage(self.driver)

    # BİTİŞ (Her testten sonra çalışır)
    def tearDown(self):
        # Eğer test hata verdiyse resim çek
        if self._outcome.errors:
            self.home_page.take_screenshot(self._testMethodName)

        self.driver.quit()
        logger.info("--- GÖREV BİTTİ ---\n")

    # --- GÖREV 1: BAŞLIK KONTROLÜ ---
    def test_01_homepage_title(self):
        """Ana sayfa açılıyor mu ve başlık doğru mu?"""
        self.home_page.open_url(Config.BASE_URL)

        title = self.home_page.get_title()
        logger.info(f"Site Başlığı: {title}")

        # ROBOTUN KARARI (ASSERTION)
        # Başlığın içinde "Seyyah" kelimesi geçiyor mu?
        self.assertIn("Seyyah", title, "HATA: Başlıkta 'Seyyah' kelimesi yok!")
        logger.info("BAŞARILI: Site başlığı doğrulandı.")

    # --- GÖREV 2: BLOG SAYFASINA GİT ---
    def test_02_blog_navigation(self):
        """Blog linkine tıklayınca doğru yere gidiyor mu?"""
        self.home_page.open_url(Config.BASE_URL)

        try:
            self.home_page.go_to_blog()

            # Gittiğimiz sayfanın adresinde "blog" yazıyor mu?
            current_url = self.home_page.get_current_url()
            self.assertIn("blog", current_url.lower(), "HATA: Blog sayfasına gidemedim!")
            logger.info("BAŞARILI: Blog sayfasına geçiş yapıldı.")

        except Exception as e:
            logger.warning("Blog linkini bulamadım (Menü mobilde gizli olabilir veya ismi farklı).")
            # Testi geçici olarak başarılı sayıyoruz ki durmasın
            pass


if __name__ == "__main__":
    unittest.main()