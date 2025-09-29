import time
import requests
from datetime import datetime
from playwright.sync_api import sync_playwright
import os

# ===============================
# Configuration
# ===============================
URL = "https://kichikichi.com/kichikichi-reservation/"
TEXT_BEFORE = "When the reservation time arrives, the reservation page will open."
TEXT_CLOSED = "We are currently fully booked. Reservations cannot be made at this time."
NTFY_TOPIC = "kichikichi-alert"
NTFY_URL = f"https://ntfy.sh/{NTFY_TOPIC}"
INTERVAL = 10  # seconds between checks
HTML_DUMP_DIR = "html_snapshots"

TEST_MODE = False
TEST_STATE = "open"

os.makedirs(HTML_DUMP_DIR, exist_ok=True)


# ===============================
# Core logic
# ===============================
def get_state(page):
    """Return state and HTML content"""
    if TEST_MODE:
        return TEST_STATE, "<html>Test HTML</html>"

    page.goto(URL)
    page.wait_for_timeout(3000)
    html = page.content()

    if TEXT_BEFORE in html:
        return "before", html
    elif TEXT_CLOSED in html:
        return "closed", html
    else:
        return "open", html


def notify(state):
    msg_map = {
        "open": f"🚨 KichiKichi reservations are OPEN! Go now: {URL}",
        "closed": "⚠️ KichiKichi reservations are CLOSED.",
        "before": "ℹ️ Reservations have not yet opened."
    }
    msg = msg_map.get(state, f"ℹ️ State changed: {state}")

    # High priority for "open", low for everything else
    priority = 5 if state == "open" else 1

    headers = {"Priority": str(priority)}

    try:
        requests.post(NTFY_URL, data=msg.encode("utf-8"), headers=headers)
        print(f"Notification sent (priority {priority}):", msg)
    except Exception as e:
        print("Notification failed:", e)


def save_html_snapshot(state, html):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(HTML_DUMP_DIR, f"{state}_{timestamp}.html")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Saved HTML snapshot: {filename}")


def main():
    last_state: str | None = None

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        print("Checker started, monitoring every", INTERVAL, "seconds...")
        try:
            while True:
                try:
                    state, html = get_state(page)
                    if state != last_state:
                        print(f"State changed: {state}")
                        notify(state)
                        save_html_snapshot(state, html)

                        # Stop once final state reached
                        if state in ("open", "closed"):
                            break

                        last_state = state
                    else:
                        print(f"[{datetime.now()}] Still in state: {state}")

                except Exception as e:
                    print(f"[{datetime.now()}] Error:", e)

                time.sleep(INTERVAL)

        finally:
            browser.close()
            print("Browser closed gracefully.")


if __name__ == "__main__":
    print("Starting KichiKichi Playwright checker with HTML snapshots...")
    if TEST_MODE:
        print(f"Running in TEST_MODE with TEST_STATE='{TEST_STATE}'")
    main()
