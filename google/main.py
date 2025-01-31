from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time

def google_search_with_selenium(query):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")

    service = Service('/path/to/chromedriver')
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        driver.get("https://www.google.com")

        search_box = driver.find_element(By.NAME, "q")
        search_box.send_keys(query)
        search_box.send_keys(Keys.RETURN)

        time.sleep(3)

        html_content = driver.page_source

        links = []
        search_results = driver.find_elements(By.CSS_SELECTOR, "div.g")
        for result in search_results[:5]:
            link = result.find_element(By.TAG_NAME, "a").get_attribute("href")
            if link:
                links.append(link)

        return html_content, links

    finally:
        driver.quit()

query = "Python programming"
html_content, first_five_links = google_search_with_selenium(query)

if html_content and first_five_links:
    print("HTML Content:")
    print(html_content[:1000]) 

    print("\nFirst Five Links:")
    for link in first_five_links:
        print(link)
