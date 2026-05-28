from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
import re
import time
import os

app = Flask(__name__)

@app.route("/")
def home():
    return jsonify({
        "status": True,
        "message": "Aadhaar PAN API Running"
    })

@app.route("/aadhaar-pan", methods=["GET"])
def aadhaar_pan():

    aadhaar = request.args.get("aadhaar")
    mobile = request.args.get("mobile")

    if not aadhaar or not mobile:
        return jsonify({
            "status": False,
            "message": "aadhaar and mobile required"
        })

    try:

        chrome_options = Options()

        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")

        chrome_bin = os.environ.get("GOOGLE_CHROME_BIN")
        chrome_driver = os.environ.get("CHROMEDRIVER_PATH")

        if chrome_bin:
            chrome_options.binary_location = chrome_bin

        service = Service(chrome_driver)

        driver = webdriver.Chrome(
            service=service,
            options=chrome_options
        )

        driver.get("https://panfindservice.com/search_pan.php")

        wait = WebDriverWait(driver, 20)

        # Aadhaar input
        aadhaar_input = wait.until(
            EC.presence_of_element_located((By.NAME, "aadhaar"))
        )

        aadhaar_input.send_keys(aadhaar)

        # Mobile input
        mobile_input = driver.find_element(By.NAME, "mobile")

        mobile_input.send_keys(mobile)

        # Search button
        search_btn = driver.find_element(
            By.XPATH,
            "//button[contains(text(),'Search')]"
        )

        search_btn.click()

        time.sleep(5)

        html = driver.page_source

        driver.quit()

        # Extract PAN
        pan_match = re.search(
            r'[A-Z]{2}\*{6}[A-Z0-9]{2}',
            html
        )

        if pan_match:

            partial_pan = pan_match.group()

            return jsonify({
                "status": True,
                "aadhaar": aadhaar,
                "partial_pan": partial_pan
            })

        return jsonify({
            "status": False,
            "message": "PAN not found"
        })

    except Exception as e:

        return jsonify({
            "status": False,
            "error": str(e)
        })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
