# test_handler.py
from drivers.Selinium_adapters import SeleniumBrowser
from pages.regular_apply_handler import RegularApplyHandler
from selenium import webdriver

driver = webdriver.Chrome()
browser = SeleniumBrowser(driver)
handler = RegularApplyHandler(browser)

# Open a test application page
driver.get("https://example.com/job-application")
handler.handle()