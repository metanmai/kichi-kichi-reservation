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

# Reservation config - Each person gets ONE slot, both Bar and Table
USERS = [
    {"name": "Tanmai Niranjan", "email": "metanmai@gmail.com", "slot": "17:00"},
    {"name": "Ayush Gupta", "email": "ayush96.gupta@gmail.com", "slot": "18:00"},
    {"name": "Vrishank Shishir", "email": "vrishankshishir@gmail.com", "slot": "19:00"},
    {"name": "Tarush Shankar", "email": "tarush1515@gmail.com", "slot": "20:00"},
    {"name": "Vijeth Jain", "email": "vijethjain@rocketmail.com", "slot": "17:00"},
]

RES_PEOPLE = "5"

# Map seating times to actual slot IDs from the HTML
SLOT_MAPPING = {
    "12:00": "slot_1",  # Arrival: 11:40 A.M. (Seating: 12:00 P.M. - 1:00 P.M.)
    "13:00": "slot_2",  # Arrival: 12:40 P.M. (Seating: 1:00 P.M. - 2:00 P.M.)
    "17:00": "slot_3",  # Arrival: 4:40 P.M. (Seating: 5:00 P.M. - 6:00 P.M.)
    "18:00": "slot_4",  # Arrival: 5:40 P.M. (Seating: 6:00 P.M. - 7:00 P.M.)
    "19:00": "slot_5",  # Arrival: 6:40 P.M. (Seating: 7:00 P.M. - 8:00 P.M.)
    "20:00": "slot_6",  # Arrival: 7:40 P.M. (Seating: 8:00 P.M. - 9:00 P.M.)
}

SEATINGS = ["Bar", "Table"]

# Test mode
TEST_MODE = True
TEST_HTML_FILE = "KichiKichi Reservation - ザ・洋食屋・キチキチ.html"
TEST_STATE = "open"

os.makedirs(HTML_DUMP_DIR, exist_ok=True)

# ===============================
# Helpers
# ===============================
def get_state(page):
    """Return (state, html)"""
    if TEST_MODE:
        with open(TEST_HTML_FILE, encoding="utf-8") as f:
            html = f.read()
        return TEST_STATE, html

    page.goto(URL)
    page.wait_for_timeout(2000)
    html = page.content()

    if TEXT_BEFORE in html:
        return "before", html
    elif TEXT_CLOSED in html:
        return "closed", html
    else:
        return "open", html


def notify(state, msg=None, startup=False):
    """Send notification via ntfy"""
    if startup:
        msg = "KichiKichi checker started."
        priority = 3
    else:
        msg_map = {
            "open": f"Reservations OPEN! Auto-booking now...",
            "closed": "Reservations CLOSED.",
            "before": "Reservations not yet open."
        }
        msg = msg or msg_map.get(state, f"State changed: {state}")
        priority = 5 if state == "open" else 1
        if state not in ("open", "closed"):
            print(f"[{datetime.now()}] Skipping notify for state {state}")
            return

    try:
        requests.post(NTFY_URL, data=msg.encode("utf-8"), headers={"Priority": str(priority)})
        print(f"Notification sent (priority {priority}): {msg}")
    except Exception as e:
        print("Notification failed:", e)


def save_html_snapshot(state, html):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(HTML_DUMP_DIR, f"{state}_{timestamp}.html")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Saved HTML snapshot: {filename}")


def auto_book(page):
    """Submit reservations - each person books 1 Bar + 1 Table for their assigned slot"""
    total_reservations = len(USERS) * len(SEATINGS)
    
    print(f"\nTotal reservations to make: {total_reservations}")
    print("="*60)
    
    reservation_num = 0
    for user in USERS:
        slot = user["slot"]
        slot_id = SLOT_MAPPING.get(slot)
        if not slot_id:
            print(f"No mapping for slot {slot}, skipping")
            continue
        
        for seating in SEATINGS:
            reservation_num += 1
            
            print(f"\n[{reservation_num}/{total_reservations}] {'='*50}")
            print(f"Name: {user['name']}")
            print(f"Email: {user['email']}")
            print(f"Slot: {slot} ({slot_id})")
            print(f"Seating: {seating}")
            print("="*60)

            try:
                # Start fresh
                print("Loading page...")
                if TEST_MODE:
                    page.goto(f"file://{os.path.abspath(TEST_HTML_FILE)}")
                else:
                    page.goto(URL, wait_until="networkidle")
                page.wait_for_timeout(500)

                # Select language
                print("Selecting language: English")
                page.select_option("#language-select", "en")
                page.wait_for_timeout(200)

                # Agree checkbox
                print("Checking agreement checkbox...")
                page.check("#agree")
                page.wait_for_timeout(200)

                # Fill info
                print(f"Filling name: {user['name']}")
                page.fill("#name", user["name"])
                page.wait_for_timeout(100)
                
                print(f"Filling email: {user['email']}")
                page.fill("#email", user["email"])
                page.wait_for_timeout(100)
                
                print(f"Confirming email: {user['email']}")
                page.fill("#confirm_email", user["email"])
                page.wait_for_timeout(100)
                
                print(f"Filling number of people: {RES_PEOPLE}")
                page.fill("#number_of_people", RES_PEOPLE)
                page.wait_for_timeout(200)

                # Seating
                print(f"Selecting seating preference: {seating}")
                page.select_option("#seating_preference", seating)
                page.wait_for_timeout(200)

                # Slot
                print(f"Selecting time slot: {slot_id} ({slot})")
                page.select_option("#time", slot_id)
                page.wait_for_timeout(200)

                # Confirm checkbox
                print("Checking confirmation checkbox...")
                page.check("#confirm-agree")
                page.wait_for_timeout(200)

                if TEST_MODE:
                    print("\n[TEST_MODE] Form filled. Pausing 1 second...")
                    page.wait_for_timeout(1000)
                    print("Skipping submission (TEST_MODE)\n")
                else:
                    # Submit automatically
                    print("Submitting form...")
                    page.click("#submit-button")
                    page.wait_for_load_state("networkidle")
                    page.wait_for_timeout(1000)

                    # Check if submission was successful
                    current_url = page.url
                    page_content = page.content()
                    
                    # Screenshot
                    safe_slot = slot.replace(":", "")
                    safe_name = user["name"].replace(" ", "_")
                    filename = f"result_{safe_name}_{safe_slot}_{seating}.png"
                    page.screenshot(path=filename)
                    
                    # Check for success or failure
                    if "confirmation" in current_url.lower():
                        success_msg = f"SUCCESS: {user['name']} - {slot} {seating} seat booked!"
                        print(f"\n{success_msg}")
                        notify("open", msg=success_msg)
                        print(f"Screenshot saved: {filename}\n")
                    elif "fully booked" in page_content.lower() or "cannot be made" in page_content.lower():
                        fail_msg = f"FAILED: {user['name']} - {slot} {seating} fully booked"
                        print(f"\n{fail_msg}")
                        notify("open", msg=fail_msg)
                    else:
                        # Unknown result - still notify
                        unknown_msg = f"UNKNOWN: {user['name']} - {slot} {seating} (check screenshot)"
                        print(f"\n{unknown_msg}")
                        notify("open", msg=unknown_msg)
                        print(f"Screenshot saved: {filename}\n")

            except Exception as e:
                error_msg = f"ERROR booking for {user['name']} - {slot} {seating}: {e}"
                print(f"\n{error_msg}\n")
                notify("open", msg=error_msg)
                safe_slot = slot.replace(":", "")
                safe_name = user["name"].replace(" ", "_")
                page.screenshot(path=f"error_{safe_name}_{safe_slot}_{seating}.png")

            # Small delay between submissions
            time.sleep(0.5)


# ===============================
# Main
# ===============================
def main():
    last_state = None
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        notify(None, startup=True)

        print("Checker started...")
        try:
            while True:
                state, html = get_state(page)

                if state != last_state:
                    print(f"State changed: {state}")
                    save_html_snapshot(state, html)
                    notify(state)

                    if state == "open":
                        auto_book(page)
                        break

                    last_state = state
                else:
                    print(f"[{datetime.now()}] Still {state}")

                time.sleep(INTERVAL)

        finally:
            browser.close()


if __name__ == "__main__":
    print("Starting KichiKichi checker + auto-booker...")
    if TEST_MODE:
        print(f"Running in TEST_MODE, using {TEST_HTML_FILE}")
    main()