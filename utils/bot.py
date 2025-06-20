from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import time
import copy
import os

LOGIN_FUNC = """
const username = arguments[0];
const password = arguments[1];

fetch('/api/public/login', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({ username, password })
});"""


def trigger_bot_access():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.binary_location = "/usr/local/bin/google-chrome"

    service = Service(executable_path="/usr/local/bin/chromedriver")

    driver = webdriver.Chrome(options=options, service=service)
    driver.set_page_load_timeout(60)

    try:
        USERNAME = "Luminoria"
        PASSWORD = "20061105"

        print("Triggered bot access...")

        driver.get("http://127.0.0.1:5000")
        driver.add_cookie(
            {
                "name": "FLAG",
                "value": os.environ.get("FLAG", "FLAG{THIS_IS_A_TEST_FLAG}"),
            }
        )
        print(driver.get_cookies())

        print("FLAG cookie set.")
        print("Logging in...")
        driver.execute_script(LOGIN_FUNC, USERNAME, PASSWORD)
        time.sleep(3)
        print("Login submitted.")
        print(driver.get_cookies())

        print("Triggering XSS...")
        driver.get("http://127.0.0.1:5000")
        time.sleep(3)  # 加载时间，要渲染页面，不然出不来
        print("Done.")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if driver:
            driver.quit()
            print("Driver quit.")


if __name__ == "__main__":
    trigger_bot_access()
    print("Bot access triggered successfully.")
