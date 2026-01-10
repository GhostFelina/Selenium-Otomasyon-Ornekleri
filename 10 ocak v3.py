# Dosya Adı: test_linkler.py
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


def link_kontrol():
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.get("https://www.seyyahlab.com")

    # Sayfadaki tüm 'a' etiketlerini bul (Linkler)
    linkler = driver.find_elements(By.TAG_NAME, "a")

    print(f"🔎 Sayfada toplam {len(linkler)} adet link bulundu.\n")

    sayac = 1
    for link in linkler:
        url = link.get_attribute("href")
        metin = link.text
        # Boş linkleri atla, dolu olanları yaz
        if url:
            print(f"{sayac}. Link Metni: '{metin}' -> Adres: {url}")
            sayac += 1

    print("\n✅ Link taraması bitti.")
    driver.quit()


if __name__ == "__main__":
    link_kontrol()