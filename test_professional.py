import unittest
import logging
import datetime
import time
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
# 1. AYARLAR
# =============================================================================
class Config:
    BASE_URL = "https://www.seyyahlab.com"
    BROWSER_HEADLESS = False
    TIMEOUT = 15


logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    datefmt='%H:%M:%S'
)
logger = logging.getLogger()


# =============================================================================
# 2. TEMEL YAPI (Base Page)
# =============================================================================
class BasePage:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, Config.TIMEOUT)

    def open_url(self, url):
        logger.info(f"Adrese gidiliyor: {url}")
        self.driver.get(url)

    def find(self, locator):
        return self.wait.until(EC.presence_of_element_located(locator))

    def click(self, locator):
        """Önce normal tıklar, olmazsa JS ile zorla tıklar."""
        try:
            element = self.wait.until(EC.element_to_be_clickable(locator))
            element.click()
            logger.info(f"Normal Tıklandı: {locator}")
        except Exception as e:
            logger.warning(f"Normal tıklama başarısız, JS Click deneniyor... ({e})")
            # Elementi tekrar bul ve JS ile tıkla
            element = self.driver.find_element(*locator)
            self.driver.execute_script("arguments[0].click();", element)
            logger.info(f"JS ile ZORLA Tıklandı: {locator}")

    def get_title(self):
        return self.driver.title

    def get_current_url(self):
        return self.driver.current_url

    def take_screenshot(self, test_name):
        timestamp = datetime.datetime.now().strftime("%H%M%S")
        filename = f"FAIL_{test_name}_{timestamp}.png"
        self.driver.save_screenshot(filename)
        logger.error(f"HATA! Ekran görüntüsü: {filename}")


# =============================================================================
# 3. SAYFA TANIMLARI
# =============================================================================
class HomePage(BasePage):
    # LOGO
    LOGO = (By.CSS_SELECTOR, "img[alt='SeyyahLab']")

    # BLOG LİNKİ (Hem mobilde hem masaüstünde yakalamak için geniş kapsamlı)
    # Strateji: İçinde 'Blog' yazan VEYA href'i '/blog' olan linki bul
    NAV_BLOG_LINK = (By.XPATH, "//a[contains(text(), 'Blog')] | //a[contains(@href, '/blog')]")

    def go_to_blog(self):
        logger.info("Blog menüsü aranıyor...")
        self.click(self.NAV_BLOG_LINK)


# =============================================================================
# 4. TEST SENARYOLARI
# =============================================================================
class TestSeyyahLab(unittest.TestCase):

    def setUp(self):
        logger.info(f"--- TEST: {self._testMethodName} ---")
        options = Options()
        if Config.BROWSER_HEADLESS:
            options.add_argument("--headless")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-blink-features=AutomationControlled")

        # HATA VEREN SATIR BURASIYDI, DÜZELTİLDİ:
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

        self.home_page = HomePage(self.driver)

    def tearDown(self):
        try:
            if hasattr(self, '_outcome'):
                result = self._outcome.result
                if result.errors or result.failures:
                    self.home_page.take_screenshot(self._testMethodName)
        except:
            pass
        self.driver.quit()
        logger.info("--- BİTTİ ---\n")

    def test_01_homepage_title(self):
        self.home_page.open_url(Config.BASE_URL)
        title = self.home_page.get_title()
        logger.info(f"Başlık: {title}")
        self.assertIn("Seyyah", title)
        logger.info("✅ Başlık Doğrulandı.")

    def test_02_blog_navigation(self):
        self.home_page.open_url(Config.BASE_URL)
        time.sleep(2)  # Sayfa tam otursun

        try:
            self.home_page.go_to_blog()

            # Yönlendirme için bekle
            time.sleep(3)

            current_url = self.home_page.get_current_url()
            logger.info(f"Şu anki URL: {current_url}")

            self.assertIn("blog", current_url.lower(), "URL içinde 'blog' kelimesi yok!")
            logger.info("✅ Blog sayfasına başarıyla geçildi.")

        except Exception as e:
            logger.error(f"❌ Blog testi hatası: {e}")
            self.fail(f"Blog menüsü bulunamadı. Hata: {e}")


if __name__ == "__main__":
    unittest.main()