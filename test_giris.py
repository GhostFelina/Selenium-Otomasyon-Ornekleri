from selenium import webdriver
import time

driver = webdriver.Chrome()
driver.maximize_window()

driver.get("http://www.seyyahlab.com")
time.sleep(5)


driver.quit()

