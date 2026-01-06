import time
from selenium import webdriver
from selenium.webdriver.common.by import By

# --- ROBOT AYARLARI ---
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
driver = webdriver.Chrome(options=options)

try:
    print("🚀 ROBOT: Giriş yapmaya gidiyorum...")

    # 1. Siteyi Aç
    driver.get("https://seyyahlab.com")
    time.sleep(3)  # Site kendine gelsin diye bekliyoruz

    # 2. Butonu Bul (Senin verdiğin adres)
    # Bu adresi senin verdiğin XPath ile güncelledim:
    buton_adresi = '//*[@id="root"]/div/div[2]/div[2]/div[1]/button[2]/span'

    print(f"🔎 ROBOT: Şu adresteki butonu arıyorum: {buton_adresi}")

    # Elementi bul
    giris_butonu = driver.find_element(By.XPATH, buton_adresi)

    # 3. TIKLA!
    giris_butonu.click()
    print("👆 ROBOT: Butona tıkladım! (Umarım çalışmıştır)")

    # 4. Sonucu Görmek İçin Bekle
    time.sleep(5)

    # Kanıt fotoğrafı alalım
    driver.save_screenshot("tiklama_sonrasi.png")
    print("📸 ROBOT: Tıklama sonrası ekran görüntüsünü aldım.")

except Exception as hata:
    print(f"💥 ROBOT: Butonu bulamadım veya tıklayamadım. Hata: {hata}")

finally:
    print("🏁 ROBOT: Görev bitti, çıkıyorum.")
    driver.quit()