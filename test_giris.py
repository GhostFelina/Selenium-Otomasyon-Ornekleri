from selenium import webdriver  # <--- Bu satır olmazsa çalışmaz!
import time

# 1. Chrome'u aç
driver = webdriver.Chrome()

# 2. Siteye git
driver.get("http://www.seyyahlab.com")

# 3. 10 saniye bekle
time.sleep(10)

# 4. Kapat
driver.quit()

from selenium import webdriver
import time

driver = webdriver.Chrome()
driver.get("http://www.seyyahlab.com")