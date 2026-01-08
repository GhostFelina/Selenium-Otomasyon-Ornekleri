import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime


# --- FONKSİYONLAR (İŞÇİLER) ---
# Profesyonel kodlarda işlemler parçalara ayrılır.

def tarayiciyi_baslat():
    """Tarayıcıyı en uygun ayarlarla başlatır."""
    print("🚀 Test Ortamı Hazırlanıyor...")
    chrome_options = Options()
    # chrome_options.add_argument("--headless") # İstersen tarayıcıyı hiç görmeden arkada çalıştırmak için bu yorumu kaldır.
    chrome_options.add_argument("--start-maximized")  # Tam ekran
    chrome_options.add_argument("--disable-notifications")  # "Bildirimlere izin ver" kutucuklarını engelle

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    return driver


def rapor_yazdir(mesaj, durum="BİLGİ"):
    """Konsola renkli ve düzenli log basar."""
    zaman = datetime.now().strftime("%H:%M:%S")
    ikon = "✅" if durum == "BAŞARILI" else "❌" if durum == "HATA" else "ℹ️"
    print(f"[{zaman}] {ikon} {durum}: {mesaj}")


def ekran_goruntusu_al(driver, ad):
    """Kanıt için fotoğraf çeker."""
    dosya_adi = f"kanit_{ad}.png"
    driver.save_screenshot(dosya_adi)
    rapor_yazdir(f"Ekran görüntüsü kaydedildi: {dosya_adi}")


# --- ANA SENARYO (FİLMİN KENDİSİ) ---

def test_senaryosu():
    driver = tarayiciyi_baslat()
    wait = WebDriverWait(driver, 15)  # En fazla 15 saniye bekle (Akıllı Bekleme)
    target_url = "https://www.seyyahlab.com"

    try:
        # 1. ADIM: SİTEYE GİRİŞ
        driver.get(target_url)
        rapor_yazdir(f"{target_url} adresine gidildi.")

        # Sayfanın gerçekten yüklendiğini anlamak için "title"ın gelmesini bekle
        wait.until(lambda d: len(d.title) > 1)
        rapor_yazdir(f"Site Başlığı Doğrulandı: {driver.title}", "BAŞARILI")

        # 2. ADIM: ARAMA TESTİ (Search Box)
        # Sitenin yapısına göre buradaki seçiciyi (CSS Selector) güncellemen gerekebilir.
        # Genelde arama kutuları 'input[type="search"]' veya 'input[type="text"]' olur.
        keyword = "İstanbul"

        try:
            # Arama kutusunun sayfada görünür olmasını bekle (Tıklanabilir olana kadar bekle)
            search_box = wait.until(EC.visibility_of_element_located(
                (By.CSS_SELECTOR, "input[type='search'], input[name='q'], .search-field")))

            search_box.clear()  # Önce temizle
            search_box.send_keys(keyword)  # Yaz
            rapor_yazdir(f"Arama kutusuna '{keyword}' yazıldı.")

            # Enter'a bas
            search_box.send_keys(Keys.RETURN)

            # 3. ADIM: SONUÇLARIN GELMESİNİ BEKLE
            # Arama yapıldıktan sonra URL değişir veya sonuçlar listelenir.
            # Burada URL içinde 's=İstanbul' veya 'search' kelimesinin geçmesini bekliyoruz.
            wait.until(EC.url_contains("s=") or EC.url_contains("search"))

            rapor_yazdir("Arama sonuç sayfası yüklendi.", "BAŞARILI")
            ekran_goruntusu_al(driver, "arama_sonucu")

            # Ekstra Kontrol: Sayfada sonuç bulundu mu?
            page_source = driver.page_source.lower()
            if keyword.lower() in page_source:
                rapor_yazdir(f"İçerikte '{keyword}' kelimesi başarıyla bulundu!", "BAŞARILI")
            else:
                rapor_yazdir(f"Uyarı: Sayfa açıldı ama '{keyword}' kelimesi metinlerde bulunamadı.", "HATA")

        except Exception as e:
            rapor_yazdir(f"Arama kutusu bulunamadı veya etkileşime girilemedi. Hata: {e}", "HATA")
            ekran_goruntusu_al(driver, "arama_hatasi")

    except Exception as genel_hata:
        rapor_yazdir(f"Test sırasında kritik hata: {genel_hata}", "HATA")
        ekran_goruntusu_al(driver, "kritik_hata")

    finally:
        # 4. ADIM: KAPANIŞ
        rapor_yazdir("Test tamamlandı, tarayıcı kapatılıyor.")
        driver.quit()


if __name__ == "__main__":
    test_senaryosu()