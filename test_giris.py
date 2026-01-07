import time
import json
import os
import logging
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# --- LOGLAMA AYARLARI ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class SeyyahLabBot:
    def __init__(self, headless=False):
        """
        Botu başlatır ve tarayıcı ayarlarını yapar.
        :param headless: True ise tarayıcı arayüzü açılmadan arka planda çalışır.
        """
        self.base_url = "https://seyyahlab.com"
        self.data = {
            "tarama_zamani": str(datetime.now()),
            "meta_bilgileri": {},
            "sayfa_yapisi": {},
            "icerik": [],
            "linkler": {"toplam": 0, "ic_linkler": [], "dis_linkler": []},
            "gorseller": []
        }

        # Tarayıcı Ayarları
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--disable-notifications")
        # Gerçek bir kullanıcı gibi görünmek için User-Agent
        chrome_options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36")

        try:
            logging.info("Sürücü yükleniyor ve tarayıcı başlatılıyor...")
            # WebDriver Manager ile otomatik sürücü kurulumu
            self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
            self.wait = WebDriverWait(self.driver, 15)
        except Exception as e:
            logging.error(f"Sürücü başlatılamadı: {e}")
            exit()

    def sayfayi_ac(self):
        logging.info(f"{self.base_url} adresine gidiliyor...")
        self.driver.get(self.base_url)
        # Sayfanın ana gövdesinin yüklenmesini bekle
        try:
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            time.sleep(2)  # Ekstra stabilite için kısa bekleme
        except Exception as e:
            logging.error(f"Sayfa yüklenirken zaman aşımı: {e}")

    def asagi_kaydir(self):
        """
        Sayfanın en altına kadar yavaşça kaydırır (Lazy load tetiklemek için).
        """
        logging.info("Sayfa aşağı kaydırılıyor (Lazy loading tetikleniyor)...")
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        while True:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
        # Tekrar yukarı çık
        self.driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(1)

    def seo_analizi_yap(self):
        """Başlık, Meta Açıklama ve Anahtar Kelimeleri çeker."""
        logging.info("SEO Analizi yapılıyor...")
        self.data["meta_bilgileri"]["title"] = self.driver.title
        self.data["meta_bilgileri"]["url"] = self.driver.current_url

        try:
            desc = self.driver.find_element(By.XPATH, "//meta[@name='description']")
            self.data["meta_bilgileri"]["description"] = desc.get_attribute("content")
        except:
            self.data["meta_bilgileri"]["description"] = "Bulunamadı"

        try:
            keywords = self.driver.find_element(By.XPATH, "//meta[@name='keywords']")
            self.data["meta_bilgileri"]["keywords"] = keywords.get_attribute("content")
        except:
            self.data["meta_bilgileri"]["keywords"] = "Bulunamadı"

    def icerik_taramasi(self):
        """Başlıklar, kartlar ve butonları tarar."""
        logging.info("Sayfa içeriği taranıyor...")

        # 1. Logo / H1
        try:
            h1 = self.driver.find_element(By.TAG_NAME, "h1").text
            self.data["sayfa_yapisi"]["h1_baslik"] = h1
        except:
            self.data["sayfa_yapisi"]["h1_baslik"] = "H1 Bulunamadı"

        # 2. Rehber Kartları (H3 veya genel kart yapısı)
        # Not: SeyyahLab yapısına göre class isimleri değişebilir, genel tag tarıyoruz.
        cards = self.driver.find_elements(By.TAG_NAME, "h3")
        for index, card in enumerate(cards, 1):
            text = card.text.strip()
            if text:
                # Varsa kartın içindeki linki de al
                link = "Link yok"
                try:
                    parent_link = card.find_element(By.XPATH, "./..")  # Bir üst ebeveyne bak
                    if parent_link.tag_name == 'a':
                        link = parent_link.get_attribute("href")
                except:
                    pass

                self.data["icerik"].append({
                    "tip": "Kart/Başlık",
                    "id": index,
                    "metin": text,
                    "link": link
                })

        # 3. Banner Kontrolü
        try:
            banner = self.driver.find_element(By.XPATH,
                                              "//*[contains(text(), 'Yapım aşamasında') or contains(text(), 'Coming Soon')]")
            self.data["sayfa_yapisi"]["durum_banneri"] = banner.text
        except:
            self.data["sayfa_yapisi"]["durum_banneri"] = "Yok"

    def link_ve_gorsel_analizi(self):
        """Sayfadaki tüm linkleri ve görselleri analiz eder."""
        logging.info("Link ve Görsel analizi yapılıyor...")

        # Linkler
        elements = self.driver.find_elements(By.TAG_NAME, "a")
        for elem in elements:
            href = elem.get_attribute("href")
            text = elem.text.strip()
            if href:
                if self.base_url in href:
                    self.data["linkler"]["ic_linkler"].append({"text": text, "url": href})
                else:
                    self.data["linkler"]["dis_linkler"].append({"text": text, "url": href})

        self.data["linkler"]["toplam"] = len(self.data["linkler"]["ic_linkler"]) + len(
            self.data["linkler"]["dis_linkler"])

        # Görseller
        images = self.driver.find_elements(By.TAG_NAME, "img")
        for img in images:
            src = img.get_attribute("src")
            alt = img.get_attribute("alt")
            self.data["gorseller"].append({
                "src": src,
                "alt_text": alt if alt else "ALT ETİKETİ YOK (SEO HATASI)"
            })

    def arama_testi(self, arama_terimi="Gezi"):
        """Varsa arama çubuğunu bulur ve test verisi gönderir."""
        try:
            search_input = self.driver.find_element(By.CSS_SELECTOR, "input[type='text'], input[type='search']")
            logging.info(f"Arama çubuğu bulundu. '{arama_terimi}' yazılıyor...")

            # Efektif görünmesi için yavaşça kaydır
            self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});",
                                       search_input)
            time.sleep(1)

            search_input.clear()
            search_input.send_keys(arama_terimi)
            self.data["sayfa_yapisi"]["arama_cubugu"] = "Mevcut ve çalışıyor"
            # Enter'a basma simülasyonu (Opsiyonel)
            # search_input.send_keys(Keys.RETURN)
        except:
            logging.warning("Arama çubuğu bulunamadı veya etkileşime girilemedi.")
            self.data["sayfa_yapisi"]["arama_cubugu"] = "Bulunamadı"

    def raporla_ve_kapat(self):
        """Verileri JSON'a kaydeder, ekran görüntüsü alır ve kapatır."""

        # Ekran Görüntüsü
        screenshot_name = "seyyahlab_result.png"
        self.driver.save_screenshot(screenshot_name)
        logging.info(f"Ekran görüntüsü kaydedildi: {screenshot_name}")

        # JSON Çıktısı
        json_name = "seyyahlab_data.json"
        with open(json_name, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=4)

        logging.info(f"Veriler JSON olarak kaydedildi: {json_name}")
        logging.info("-" * 50)

        # Sonuçların Özeti Konsola
        print(f"\n📊 TARAMA ÖZETİ:")
        print(f"   - Başlık: {self.data['meta_bilgileri'].get('title')}")
        print(f"   - Toplam Link Sayısı: {self.data['linkler']['toplam']}")
        print(f"   - Toplam Görsel Sayısı: {len(self.data['gorseller'])}")
        print(f"   - Bulunan İçerik Kartları: {len(self.data['icerik'])}")

        self.driver.quit()
        logging.info("Test tamamlandı, tarayıcı kapatıldı.")


# --- ÇALIŞTIRMA ---
if __name__ == "__main__":
    # Botu başlat (headless=True yaparsanız tarayıcıyı görmeden çalışır)
    bot = SeyyahLabBot(headless=False)

    bot.sayfayi_ac()
    bot.asagi_kaydir()  # Tüm resimlerin yüklenmesi için
    bot.seo_analizi_yap()
    bot.arama_testi("İstanbul Rehberi")
    bot.icerik_taramasi()
    bot.link_ve_gorsel_analizi()

    bot.raporla_ve_kapat()