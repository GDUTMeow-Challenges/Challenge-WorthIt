from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from utils.log import get_logger
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
}).then(response => {
    if (!response.ok) {
        throw new Error('Network response was not ok ' + response.statusText);
    }
    console.log(response.json());
});"""

logger = get_logger("bot")

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

        logger.info("Triggered bot access...")

        driver.get("http://127.0.0.1:5000")
        driver.add_cookie(
            {
                "name": "FLAG",
                "value": os.environ.get("A1CTF_FLAG", "FLAG{THIS_IS_A_TEST_FLAG}"),
            }
        )
        logger.info(driver.get_cookies())

        logger.info("FLAG cookie set.")
        logger.info("Logging in...")
        driver.execute_script(LOGIN_FUNC, USERNAME, PASSWORD)
        time.sleep(3)
        logger.info("Login submitted.")
        logger.info(driver.get_cookies())

        logger.info("Triggering XSS...")
        driver.get("http://127.0.0.1:5000")
        time.sleep(3)  # 加载时间，要渲染页面，不然出不来
        logger.info("Done.")
    except Exception as e:
        logger.info(f"An error occurred: {e}")
    finally:
        if driver:
            driver.quit()
            logger.info("Driver quit.")


if __name__ == "__main__":
    trigger_bot_access()
    logger.info("Bot access triggered successfully.")
