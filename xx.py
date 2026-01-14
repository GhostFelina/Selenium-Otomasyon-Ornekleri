# Dosya Adı: test_mobil.py
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager


def mobil_test():
    mobile_emulation = {"deviceName": "iPhone 12 Pro"}

    chrome_options = Options()
    chrome_options.add_experimental_option("mobileEmulation", mobile_emulation)

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    print("📱 iPhone 12 Pro modunda site açılıyor...")
    driver.get("https://www.seyyahlab.com")
    time.sleep(3)  # Yüklenmeyi gör

    print(f"Başlık: {driver.title}")
    driver.save_screenshot("iphone_gorunumu.png")
    print("📷 Mobil ekran görüntüsü alındı.")

    driver.quit()


if __name__ == "__main__":
    mobil_test()