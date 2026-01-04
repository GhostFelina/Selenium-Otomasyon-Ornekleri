import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

# --- ROBOT AYARLARI ---
# Robotumuz Chrome kullanacak
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized") # Ekranı tam boy açsın

# Robotu çalıştırıyoruz (Driver)
driver = webdriver.Chrome(options=options)

try:
    print("🚀 ROBOT: İş başı yaptım patron! SeyyahLab'a gidiyorum...")

    # 1. ADIM: SİTEYE GİT
    driver.get("https://seyyahlab.com")
    time.sleep(3) # Sayfanın yüklenmesini 3 saniye bekle (Gözle görebilmek için)

    # 2. ADIM: TABELA KONTROLÜ (BAŞLIK)
    site_basligi = driver.title
    print(f"👀 ROBOT: Site başlığını okudum: -> {site_basligi}")

    # Burası senin KONTROL noktan.
    # Eğer başlıkta "Seyyah" kelimesi geçiyorsa test başarılıdır.
    if "Seyyah" in site_basligi:
        print("✅ TEST BAŞARILI: Tabela doğru, 'Seyyah' kelimesi var!")
    else:
        print("❌ TEST HATALI: Başlıkta 'Seyyah' kelimesini bulamadım!")

    # 3. ADIM: ETRAFI GEZME (SCROLL)
    print("⬇️ ROBOT: Sayfayı aşağı kaydırıyorum...")
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2) # Kaydırmayı görmen için bekliyor

    # 4. ADIM: FOTOĞRAF ÇEKME (KANIT)
    foto_adi = "seyyahlab_kontrol.png"
    driver.save_screenshot(foto_adi)
    print(f"📸 ROBOT: Sitenin fotoğrafını çektim ve '{foto_adi}' olarak kaydettim.")

except Exception as hata:
    # Eğer bir kaza olursa burası çalışır
    print(f"💥 ROBOT: Bir sorun çıktı patron! Hata: {hata}")

finally:
    # 5. ADIM: DÜKKANI KAPATMA
    print("🏁 ROBOT: Görev tamamlandı, tarayıcıyı kapatıyorum.")
    driver.quit()