from flask import Flask, request, jsonify
from playwright.sync_api import sync_playwright
import re

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

        with sync_playwright() as p:

            browser = p.chromium.launch(headless=True)

            page = browser.new_page()

            page.goto("https://panfindservice.com/search_pan.php")

            # Fill form
            page.fill('input[name="aadhaar"]', aadhaar)
            page.fill('input[name="mobile"]', mobile)

            # Click Search
            page.click('button:has-text("Search")')

            page.wait_for_timeout(5000)

            html = page.content()

            browser.close()

        # Extract PAN
        pan_match = re.search(
            r'[A-Z]{2}\*{6}[A-Z0-9]{2}',
            html
        )

        if pan_match:

            return jsonify({
                "status": True,
                "aadhaar": aadhaar,
                "partial_pan": pan_match.group()
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
    app.run()
