import logging
import time
import os
import pandas as pd  # <-- YENİ: Excel işlemleri için
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


# --- 1. AYARLAR ---
class Config:
    BASE_URL = "https://www.seyyahlab.com"
    TIMEOUT = 20
    HEADLESS = False
    SCREENSHOT_DIR = "raporlar/ekran_goruntuleri"
    EXCEL_DIR = "raporlar/excel_dosyalari"  # <-- YENİ: Excel kayıt yeri


# --- 2. KLASÖR VE LOG HAZIRLIĞI ---
for folder in [Config.SCREENSHOT_DIR, Config.EXCEL_DIR]:
    if not os.path.exists(folder):
        os.makedirs(folder)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger()


# --- 3. DECORATOR (Hata Yakalayıcı) ---
def ekran_goruntusu_al_on_error(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            page_instance = args[0]
            if hasattr(page_instance, 'driver'):
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                dosya_adi = f"{Config.SCREENSHOT_DIR}/HATA_{timestamp}.png"
                page_instance.driver.save_screenshot(dosya_adi)
                logger.error(f"❌ HATA! Görüntü alındı: {dosya_adi}")
            raise e

    return wrapper


# --- 4. BASE PAGE ---
class BasePage:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, Config.TIMEOUT)

    def find(self, locator):
        return self.wait.until(EC.presence_of_element_located(locator))

    def find_all(self, locator):
        """Birden fazla elementi bulur (Liste döner)."""
        return self.wait.until(EC.presence_of_all_elements_located(locator))

    def type_text(self, locator, text):
        element = self.wait.until(EC.visibility_of_element_located(locator))
        element.clear()
        element.send_keys(text)


# --- 5. PAGE OBJECTS ---
class HomePage(BasePage):
    # Seçiciler
    SEARCH_ICON = (By.CSS_SELECTOR, "div.search-icon, button.search-trigger, .header-search")
    SEARCH_INPUT = (By.CSS_SELECTOR, "input[type='search'], input[name='s'], input.search-field")

    def siteye_git(self):
        logger.info(f"Siteye gidiliyor: {Config.BASE_URL}")
        self.driver.get(Config.BASE_URL)

    @ekran_goruntusu_al_on_error
    def arama_yap(self, kelime):
        try:
            WebDriverWait(self.driver, 3).until(EC.element_to_be_clickable(self.SEARCH_ICON)).click()
            logger.info("Arama ikonuna tıklandı.")
        except:
            pass  # İkon yoksa direkt inputa yaz

        self.type_text(self.SEARCH_INPUT, kelime)
        self.find(self.SEARCH_INPUT).send_keys(Keys.ENTER)
        logger.info(f"'{kelime}' aratıldı.")


class SearchResultsPage(BasePage):
    """
    Hem doğrulama yapan hem de veriyi Excel'e kaydeden sınıf.
    """
    # Wordpress yapısına uygun genel seçiciler (Başlık ve Linki kapsayan kartlar)
    ARTICLE_LOCATOR = (By.CSS_SELECTOR, "article, .post, .search-result")
    TITLE_LOCATOR = (By.CSS_SELECTOR, "h2, h3, .entry-title")
    LINK_LOCATOR = (By.TAG_NAME, "a")

    @ekran_goruntusu_al_on_error
    def verileri_excel_yap(self, dosya_ismi="arama_sonuclari"):
        """
        Sayfadaki sonuçları tarar, bir listeye atar ve Excel'e basar.
        """
        self.wait.until(EC.url_contains("s="))
        logger.info("Sonuç sayfası yüklendi, veriler toplanıyor...")

        # Tüm makale kartlarını bul
        kartlar = self.find_all(self.ARTICLE_LOCATOR)

        veri_listesi = []

        for kart in kartlar:
            try:
                # Kartın içindeki başlığı bul
                baslik_elementi = kart.find_element(*self.TITLE_LOCATOR)
                baslik_yazisi = baslik_elementi.text

                # Kartın içindeki linki bul (Genelde başlığın içinde veya kartın kendisinde olur)
                link_elementi = kart.find_element(*self.LINK_LOCATOR)
                link_adresi = link_elementi.get_attribute("href")

                # Listeye sözlük olarak ekle
                veri_listesi.append({
                    "Başlık": baslik_yazisi,
                    "Link": link_adresi,
                    "Tarih": datetime.now().strftime("%Y-%m-%d %H:%M")
                })
                print(f"📥 Veri Alındı: {baslik_yazisi[:30]}...")

            except Exception as e:
                logger.warning(f"Bir karttan veri alınamadı: {e}")
                continue

        # --- EXCEL KAYIT İŞLEMİ (PANDAS) ---
        if veri_listesi:
            df = pd.DataFrame(veri_listesi)  # Veriyi tabloya çevir

            zaman_damgasi = datetime.now().strftime("%Y%m%d_%H%M")
            tam_dosya_yolu = f"{Config.EXCEL_DIR}/{dosya_ismi}_{zaman_damgasi}.xlsx"

            # Excel'e yaz
            df.to_excel(tam_dosya_yolu, index=False)
            logger.info(f"✅ EXCEL OLUŞTURULDU: {tam_dosya_yolu}")
            logger.info(f"Toplam {len(veri_listesi)} satır veri kaydedildi.")
        else:
            logger.warning("Kaydedilecek veri bulunamadı!")


# --- 6. TEST RUNNER ---
class TestSeyyahLab:
    def run_test(self):
        # Ayarlar
        chrome_options = Options()
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--disable-notifications")

        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

        try:
            # Sayfa Nesnelerini Oluştur
            home = HomePage(driver)
            results = SearchResultsPage(driver)

            # --- SENARYO ---
            home.siteye_git()

            aranacak_kelime = "Vize"  # Burayı değiştirebilirsin
            home.arama_yap(aranacak_kelime)

            # Excel Raporu Al
            results.verileri_excel_yap(dosya_ismi=f"Sonuclar_{aranacak_kelime}")

        except Exception as e:
            logger.critical(f"Kritik Hata: {e}")
        finally:
            driver.quit()
            logger.info("Test bitti.")


if __name__ == "__main__":
    app = TestSeyyahLab()
    app.run_test()