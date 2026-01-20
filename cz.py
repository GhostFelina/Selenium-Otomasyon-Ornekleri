import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager


# --- RENKLİ ÇIKTI İÇİN (Konsolda şık görünsün) ---
class Renk:
    YESIL = '\033[92m'
    KIRMIZI = '\033[91m'
    SARI = '\033[93m'
    RESET = '\033[0m'


def test_rapor(test_adi, durum, detay=""):
    if durum:
        print(f"{test_adi}: {Renk.YESIL}[GEÇTİ]{Renk.RESET} {detay}")
    else:
        print(f"{test_adi}: {Renk.KIRMIZI}[KALDI]{Renk.RESET} {detay}")


# --- AYARLAR ---
TARGET_URL = "http://www.seyyahlab.com/"  # Buraya test edilecek adresi yaz
# Eğer localhost'ta deneyeceksen: "http://localhost:3000" gibi değiştir.

# Tarayıcıyı başlat
chrome_options = Options()
# chrome_options.add_argument("--headless") # Tarayıcıyı görmeden çalıştırmak istersen bu yorumu aç
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

try:
    print(f"{Renk.SARI}--- SEYYAHLAB SEO TESTİ BAŞLIYOR: {TARGET_URL} ---{Renk.RESET}\n")
    driver.get(TARGET_URL)
    time.sleep(2)  # Sayfanın yüklenmesi için kısa bir bekleme

    # ---------------------------------------------------------
    # TEST 1: META ETİKETLERİ (Title ve Description)
    # ---------------------------------------------------------
    site_basligi = driver.title
    test_rapor("1. Site Başlığı (Title)", len(site_basligi) > 0, f"- Bulunan: {site_basligi}")

    try:
        description = driver.find_element(By.XPATH, "//meta[@name='description']").get_attribute("content")
        test_rapor("1. Meta Açıklama (Description)", len(description) > 0, f"- Uzunluk: {len(description)} karakter")
    except:
        test_rapor("1. Meta Açıklama", False, "- Meta description etiketi bulunamadı!")

    # ---------------------------------------------------------
    # TEST 2: SEMANTIC HTML (Main, Header, Nav, Footer Kontrolü)
    # ---------------------------------------------------------
    etiketler = ["header", "main", "footer", "nav"]
    eksik_etiketler = []

    for etiket in etiketler:
        if len(driver.find_elements(By.TAG_NAME, etiket)) == 0:
            eksik_etiketler.append(etiket)

    test_rapor("2. Semantic HTML Yapısı", len(eksik_etiketler) == 0,
               f"- Eksikler: {eksik_etiketler}" if eksik_etiketler else "- Tüm ana yapı etiketleri mevcut.")

    # ---------------------------------------------------------
    # TEST 3: SCHEMA MARKUP (JSON-LD)
    # ---------------------------------------------------------
    schemas = driver.find_elements(By.XPATH, "//script[@type='application/ld+json']")
    test_rapor("3. Schema Markup (JSON-LD)", len(schemas) > 0, f"- Bulunan Schema sayısı: {len(schemas)}")

    # ---------------------------------------------------------
    # TEST 4: SITEMAP & ROBOTS.TXT (Requests ile kontrol)
    # ---------------------------------------------------------
    # Selenium yerine Requests kullanıyoruz çünkü HTTP durum kodunu (200 OK) görmek daha kesin sonuç verir.
    robots_url = f"{TARGET_URL}/robots.txt"
    sitemap_url = f"{TARGET_URL}/sitemap.xml"

    resp_robots = requests.get(robots_url)
    test_rapor("4. Robots.txt Erişimi", resp_robots.status_code == 200, f"- Durum Kodu: {resp_robots.status_code}")

    resp_sitemap = requests.get(sitemap_url)
    test_rapor("4. Sitemap.xml Erişimi", resp_sitemap.status_code == 200, f"- Durum Kodu: {resp_sitemap.status_code}")

    # ---------------------------------------------------------
    # TEST 5: OPEN GRAPH (Sosyal Medya Kartları)
    # ---------------------------------------------------------
    og_etiketleri = ["og:title", "og:image", "og:description"]
    eksik_og = []

    for og in og_etiketleri:
        # meta property="og:title" şeklinde arıyoruz
        if len(driver.find_elements(By.XPATH, f"//meta[@property='{og}']")) == 0:
            eksik_og.append(og)

    test_rapor("5. Open Graph (Sosyal Medya)", len(eksik_og) == 0,
               f"- Eksikler: {eksik_og}" if eksik_og else "- Sosyal medya etiketleri tam.")

    # ---------------------------------------------------------
    # TEST 6: GÖRSEL OPTİMİZASYONU (Alt Text ve Lazy Loading)
    # ---------------------------------------------------------
    resimler = driver.find_elements(By.TAG_NAME, "img")
    alt_eksik = 0
    lazy_yok = 0
    toplam_resim = len(resimler)

    if toplam_resim > 0:
        for img in resimler:
            alt_text = img.get_attribute("alt")
            loading = img.get_attribute("loading")

            if not alt_text:
                alt_eksik += 1
            if loading != "lazy":
                lazy_yok += 1  # Not: Hero image (en üstteki) lazy olmamalıdır, bu genel bir kontroldür.

        detay_msg = f"- Toplam: {toplam_resim}, Alt etiketi eksik: {alt_eksik}, Lazy olmayan: {lazy_yok}"
        basari = alt_eksik == 0  # Sadece alt text'i kritik hata saydım
        test_rapor("6. Görsel Optimizasyonu (Alt Tag)", basari, detay_msg)
    else:
        test_rapor("6. Görsel Optimizasyonu", True, "- Sayfada hiç resim bulunamadı.")

    # ---------------------------------------------------------
    # TEST 7: BAŞLIK HİYERARŞİSİ (H1, H2 Kontrolü)
    # ---------------------------------------------------------
    h1_sayisi = len(driver.find_elements(By.TAG_NAME, "h1"))
    h2_sayisi = len(driver.find_elements(By.TAG_NAME, "h2"))

    # H1 etiketi SEO için sayfada MUTLAKA 1 tane olmalıdır. 0 veya 1'den fazla olması hatadır.
    h1_durum = h1_sayisi == 1
    test_rapor("7. Başlık Hiyerarşisi (H1)", h1_durum, f"- Bulunan H1 sayısı: {h1_sayisi} (Olması gereken: 1)")

    print(f"\n{Renk.SARI}--- H2 Başlıkları ({h2_sayisi} adet) ---{Renk.RESET}")
    # İlk 3 H2 başlığını yazdıralım ki doğru mu bakalım
    for h2 in driver.find_elements(By.TAG_NAME, "h2")[:3]:
        print(f" -> {h2.text}")

except Exception as e:
    print(f"\n{Renk.KIRMIZI}!!! TEST SIRASINDA KRİTİK HATA OLUŞTU !!!{Renk.RESET}")
    print(e)

finally:
    print(f"\n{Renk.SARI}--- TEST TAMAMLANDI, TARAYICI KAPATILIYOR ---{Renk.RESET}")
    driver.quit()