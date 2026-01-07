import time
import json
import logging
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# --- LOGLAMA AYARLARI ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class SeyyahLabBot:
    def __init__(self, headless=False):
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
        # Anti-tespit için User-Agent
        chrome_options.add_argument(
            "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

        try:
            logging.info("Sürücü yükleniyor ve tarayıcı başlatılıyor...")
            self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
            self.wait = WebDriverWait(self.driver, 15)
        except Exception as e:
            logging.error(f"Sürücü başlatılamadı: {e}")
            exit()

    def sayfayi_ac(self):
        logging.info(f"{self.base_url} adresine gidiliyor...")
        self.driver.get(self.base_url)
        try:
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            time.sleep(2)
        except Exception as e:
            logging.error(f"Sayfa yüklenirken zaman aşımı: {e}")

    def asagi_kaydir(self):
        logging.info("Sayfa aşağı kaydırılıyor (Lazy loading tetikleniyor)...")
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        while True:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
        self.driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(1)

    def seo_analizi_yap(self):
        logging.info("SEO Analizi yapılıyor...")
        self.data["meta_bilgileri"]["title"] = self.driver.title
        self.data["meta_bilgileri"]["url"] = self.driver.current_url

        try:
            desc = self.driver.find_element(By.XPATH, "//meta[@name='description']")
            self.data["meta_bilgileri"]["description"] = desc.get_attribute("content")
        except:
            self.data["meta_bilgileri"]["description"] = "Bulunamadı"

    def icerik_taramasi(self):
        logging.info("Sayfa içeriği taranıyor...")
        try:
            h1 = self.driver.find_element(By.TAG_NAME, "h1").text
            self.data["sayfa_yapisi"]["h1_baslik"] = h1
        except:
            self.data["sayfa_yapisi"]["h1_baslik"] = "H1 Bulunamadı"

        cards = self.driver.find_elements(By.TAG_NAME, "h3")
        for index, card in enumerate(cards, 1):
            text = card.text.strip()
            if text:
                self.data["icerik"].append({
                    "tip": "Kart/Başlık",
                    "id": index,
                    "metin": text
                })

    def link_ve_gorsel_analizi(self):
        """
        GÜNCELLENMİŞ (AĞIR SİLAH): JavaScript kullanarak Computed Style (Hesaplanmış Stil)
        üzerinden tüm arka plan resimlerini ve SVG'leri zorla çeker.
        """
        logging.info("Link ve Görsel analizi yapılıyor (JavaScript Destekli)...")

        # --- LİNKLER ---
        elements = self.driver.find_elements(By.TAG_NAME, "a")
        self.data["linkler"]["ic_linkler"] = []
        self.data["linkler"]["dis_linkler"] = []

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

        # --- GÖRSELLER (JavaScript Enjeksiyonu) ---
        self.data["gorseller"] = []

        # 1. JavaScript ile sayfadaki TÜM elementlerin hesaplanmış stillerini tara
        # Bu yöntem class içine gizlenmiş resimleri de bulur.
        js_script = """
        var images = [];

        // A) Normal IMG etiketleri
        var imgs = document.getElementsByTagName('img');
        for(var i=0; i<imgs.length; i++) {
            if(imgs[i].src) images.push({src: imgs[i].src, type: 'img_tag'});
        }

        // B) CSS Arka Plan Resimleri (Computed Style)
        var all = document.getElementsByTagName('*');
        for(var i=0; i<all.length; i++) {
            var bg = window.getComputedStyle(all[i]).backgroundImage;
            if (bg !== 'none' && bg.startsWith('url')) {
                // url("...") kısmını temizle
                var cleanUrl = bg.slice(4, -1).replace(/["']/g, "");
                images.push({src: cleanUrl, type: 'css_background'});
            }
        }
        return images;
        """

        found_images = self.driver.execute_script(js_script)

        # Tekrarlayan resimleri temizle (set kullanarak)
        seen_urls = set()
        for img in found_images:
            if img['src'] not in seen_urls:
                self.data["gorseller"].append({
                    "tip": img['type'],
                    "src": img['src'],
                    "alt_text": "JS ile bulundu"
                })
                seen_urls.add(img['src'])

        # C) SVG Kontrolü (Grafik/İkon var mı?)
        svgs = self.driver.find_elements(By.TAG_NAME, "svg")
        if len(svgs) > 0:
            logging.info(f"{len(svgs)} adet SVG elementi bulundu (İkonlar/Grafikler).")
            # SVG'leri görsel sayısına dahil etmiyoruz ama logluyoruz,
            # çünkü bunlar genellikle "fotoğraf" değildir.

        logging.info(f"Toplam {len(self.data['gorseller'])} görsel URL'i (img + css background) yakalandı.")

    def arama_testi(self, arama_terimi="Gezi"):
        try:
            search_input = self.driver.find_element(By.CSS_SELECTOR, "input[type='text'], input[type='search']")
            logging.info(f"Arama çubuğu bulundu. '{arama_terimi}' yazılıyor...")
            self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});",
                                       search_input)
            time.sleep(1)
            search_input.clear()
            search_input.send_keys(arama_terimi)
            self.data["sayfa_yapisi"]["arama_cubugu"] = "Mevcut ve çalışıyor"
        except:
            logging.warning("Arama çubuğu bulunamadı veya etkileşime girilemedi.")
            self.data["sayfa_yapisi"]["arama_cubugu"] = "Bulunamadı"

    def raporla_ve_kapat(self):
        screenshot_name = "seyyahlab_result.png"
        self.driver.save_screenshot(screenshot_name)
        logging.info(f"Ekran görüntüsü kaydedildi: {screenshot_name}")

        json_name = "seyyahlab_data.json"
        with open(json_name, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=4)

        logging.info(f"Veriler JSON olarak kaydedildi: {json_name}")
        logging.info("-" * 50)

        print(f"\n📊 TARAMA ÖZETİ:")
        print(f"   - Başlık: {self.data['meta_bilgileri'].get('title')}")
        print(f"   - Toplam Link: {self.data['linkler']['toplam']}")
        print(f"   - Toplam Görsel (CSS Dahil): {len(self.data['gorseller'])}")
        print(f"   - İçerik Kartları: {len(self.data['icerik'])}")

        self.driver.quit()
        logging.info("Test tamamlandı, tarayıcı kapatıldı.")


if __name__ == "__main__":
    bot = SeyyahLabBot(headless=False)
    bot.sayfayi_ac()
    bot.asagi_kaydir()
    bot.seo_analizi_yap()
    bot.arama_testi("İstanbul Rehberi")
    bot.icerik_taramasi()
    bot.link_ve_gorsel_analizi()
    bot.raporla_ve_kapat()