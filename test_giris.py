import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def run_seyyahlab_test():
    print("🚀 Test Başlatılıyor: SeyyahLab.com (Yerel Sürücü İle)")
    print("-" * 50)

    # 1. WebDriver Ayarları
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")  # Tarayıcıyı tam ekran başlat

    # ⚠️ ÖNEMLİ: Eğer ChromeDriver PATH'e ekli değilse, parantez içine yolunu yazmalısınız.
    # Örnek: Service("C:\\Drivers\\chromedriver.exe") veya Mac için Service("/usr/local/bin/chromedriver")
    # PATH'e ekliyse içi boş kalabilir.
    service = Service()

    try:
        driver = webdriver.Chrome(service=service, options=options)
    except Exception as e:
        print(
            "❌ Sürücü Hatası: ChromeDriver bulunamadı. Lütfen PATH'e ekli olduğundan emin olun veya Service() içine dosya yolunu yazın.")
        print(f"Hata detayı: {e}")
        return

    try:
        # 2. Siteye Git
        driver.get("https://seyyahlab.com")

        # Sayfanın yüklenmesi için kritik bir elementin (Logo gibi) görünmesini bekle
        wait = WebDriverWait(driver, 10)
        wait.until(EC.visibility_of_element_located((By.TAG_NAME, "h1")))

        # --- TEST ADIMLARI ---

        # A) Sayfa Başlığı
        print(f"✅ Sayfa Başlığı (Title): {driver.title}")

        # B) Header / Logo
        header_h1 = driver.find_element(By.TAG_NAME, "h1").text.replace("\n", " ")
        print(f"✅ Header (Logo): {header_h1}")

        # C) Banner Kontrolü
        try:
            banner = driver.find_element(By.XPATH, "//*[contains(text(), 'Yapım aşamasında')]")
            print(f"⚠️ Banner Durumu: Görüntülendi -> '{banner.text}'")
        except:
            print("ℹ️ Banner Durumu: Görüntülenmedi")

        # D) Hero Bölümü Yazıları
        try:
            hero_text_elements = driver.find_elements(By.XPATH, "//div[contains(@class, 'text-center')]//span")
            print("\n🔍 Hero Bölümü Yazıları:")
            for elem in hero_text_elements:
                if elem.text.strip():
                    print(f"   - {elem.text}")
        except:
            pass

        # E) Arama Çubuğu
        try:
            search_input = driver.find_element(By.TAG_NAME, "input")
            placeholder = search_input.get_attribute("placeholder")
            print(f"\n🔎 Arama Çubuğu Placeholder: '{placeholder}'")
        except:
            print("\n❌ Arama çubuğu bulunamadı.")

        # F) Rehber Kartları
        print("\n📋 Kart Listesi (Rehberler):")
        cards = driver.find_elements(By.TAG_NAME, "h3")
        for index, card in enumerate(cards, 1):
            if card.text.strip():
                print(f"   {index}. {card.text.replace(chr(10), ' ')}")

        # G) Butonlar
        print("\n🔘 Aksiyon Butonları:")
        buttons = driver.find_elements(By.TAG_NAME, "button")
        valid_buttons = [btn.text for btn in buttons if btn.text.strip() != ""]
        print(f"   Bulunanlar: {valid_buttons}")

    except Exception as e:
        print(f"\n❌ Bir Hata Oluştu: {e}")

    finally:
        print("-" * 50)
        print("🏁 Test Tamamlandı.")
        # Konsolu hemen kapatmamak için bekletme (Opsiyonel)
        input("Tarayıcıyı kapatmak için Enter'a basın...")
        driver.quit()


if __name__ == "__main__":
    run_seyyahlab_test()
