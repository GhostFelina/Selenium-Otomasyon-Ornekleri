from selenium import webdriver
import time

# 1. Chrome'u aç
driver = webdriver.Chrome()

# 2. Google'a git
driver.get("https://www.google.com")

# 3. 5 saniye bekle (görebilmemiz için)
time.sleep(5)

# 4. Kapat
driver.quit()