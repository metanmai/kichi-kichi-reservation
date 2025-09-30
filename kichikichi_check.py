import time
import requests
from datetime import datetime
# Import threading for parallel execution
import threading 
from playwright.sync_api import sync_playwright, TimeoutError
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
    """
    Check the current reservation state.
    Return (state, html)
    """
    if TEST_MODE:
        try:
            with open(TEST_HTML_FILE, encoding="utf-8") as f:
                html = f.read()
        except FileNotFoundError:
            # If test file doesn't exist, we can't test properly
            print(f"ERROR: Test HTML file '{TEST_HTML_FILE}' not found. Defaulting to 'before' state.")
            html = ""
        return TEST_STATE, html

    page.goto(URL, wait_until="load")
    # Wait for content to load, 2 seconds maximum
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
        
        # Only notify for 'open' state once the state has been confirmed
        if state not in ("open", "closed", "before"):
            print(f"[{datetime.now()}] Skipping notify for state {state}")
            return

    try:
        # Note: NTFY_URL is accessed globally
        requests.post(NTFY_URL, data=msg.encode("utf-8"), headers={"Priority": str(priority)})
        print(f"Notification sent (priority {priority}): {msg}")
    except Exception as e:
        print(f"Notification failed: {e}")


def save_html_snapshot(state, html):
    """Save the HTML content to a file."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    # HTML_DUMP_DIR is accessed globally
    filename = os.path.join(HTML_DUMP_DIR, f"{state}_{timestamp}.html")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Saved HTML snapshot: {filename}")


def worker_book_slot(user, seating, reservation_num, total_reservations):
    """
    Core booking logic for a single user/seating combination.
    Launches its own Playwright session.
    """
    slot = user["slot"]
    slot_id = SLOT_MAPPING.get(slot) # SLOT_MAPPING is accessed globally
    
    if not slot_id:
        print(f"Worker Error: No mapping for slot {slot}, skipping reservation for {user['name']}.")
        return
    
    # --- Playwright Setup (Local to this Thread) ---
    # This ensures thread safety, as each thread gets its own browser instance.
    with sync_playwright() as p:
        try:
            # Launch browser in headless mode unless in TEST_MODE
            browser = p.chromium.launch(headless=not TEST_MODE)
            page = browser.new_page()

            print(f"\n[{reservation_num}/{total_reservations}] {'='*50}")
            print(f"Worker for: {user['name']} | Slot: {slot} | Seating: {seating}")
            print("="*60)

            # Start fresh
            print("Loading page...")
            if TEST_MODE:
                page.goto(f"file://{os.path.abspath(TEST_HTML_FILE)}", wait_until="load")
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
            
            print(f"Filling number of people: {RES_PEOPLE}") # RES_PEOPLE is accessed globally
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
                # Note: Changed to use page.wait_for_selector for success indicator
                # to handle potential issues with wait_for_load_state('networkidle')
                # in a high-load scenario.
                page.click("#submit-button")
                
                # Wait for the confirmation page to load or a timeout to occur (e.g., if page is fully booked)
                try:
                    # Wait for up to 10 seconds for the URL to change, indicating submission
                    page.wait_for_url("**/confirmation", timeout=10000) 
                    success = True
                except TimeoutError:
                    # Check the content if URL didn't change (might be a soft error on the same page)
                    page_content = page.content()
                    if "fully booked" in page_content.lower() or "cannot be made" in page_content.lower():
                        success = False
                    else:
                        success = None # Unknown state
                
                # Check result
                page_content = page.content()
                
                # Screenshot
                safe_slot = slot.replace(":", "")
                safe_name = user["name"].replace(" ", "_")
                filename = f"result_{safe_name}_{safe_slot}_{seating}.png"
                page.screenshot(path=filename)
                
                if success is True:
                    success_msg = f"SUCCESS: {user['name']} - {slot} {seating} seat booked! (Screenshot: {filename})"
                    print(f"\n{success_msg}")
                    notify("open", msg=success_msg)
                elif success is False:
                    fail_msg = f"FAILED: {user['name']} - {slot} {seating} fully booked (Screenshot: {filename})"
                    print(f"\n{fail_msg}")
                    notify("closed", msg=fail_msg) # Use 'closed' priority 1 for failure message
                else:
                    # Unknown result - still notify
                    unknown_msg = f"UNKNOWN: {user['name']} - {slot} {seating} (check screenshot: {filename})"
                    print(f"\n{unknown_msg}")
                    notify("open", msg=unknown_msg)

        except Exception as e:
            error_msg = f"Worker ERROR for {user['name']} - {slot} {seating}: {type(e).__name__} - {e}"
            print(f"\n{error_msg}\n")
            notify("open", msg=error_msg)
            # Try to screenshot the error page if possible
            try:
                safe_slot = slot.replace(":", "")
                safe_name = user["name"].replace(" ", "_")
                page.screenshot(path=f"error_{safe_name}_{safe_slot}_{seating}.png")
            except:
                pass # Ignore if screenshot fails


def auto_book():
    """
    Submits reservations by creating a separate thread for each individual booking 
    (User x Seating).
    """
    total_reservations = len(USERS) * len(SEATINGS)
    
    print(f"\nStarting {total_reservations} parallel reservation attempts...")
    print("="*60)
    
    threads = []
    reservation_num = 0

    for user in USERS:
        for seating in SEATINGS:
            reservation_num += 1
            
            # Create a thread for each booking attempt
            thread = threading.Thread(
                target=worker_book_slot,
                args=(user, seating, reservation_num, total_reservations),
                name=f"Booker-{user['name']}-{seating}"
            )
            threads.append(thread)
            thread.start()

    # Wait for all threads to complete before exiting the auto_book function
    for t in threads:
        t.join()
        
    print("\nAll reservation threads completed.")


# ===============================
# Main
# ===============================
def main():
    last_state = None
    
    # We only need one Playwright instance here for the initial state check
    with sync_playwright() as p:
        # Launch browser to check initial state (can be headless)
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        notify(None, startup=True)

        print("Checker started...")
        try:
            while True:
                # Use the main thread's browser instance for checking the state
                state, html = get_state(page)

                if state != last_state:
                    print(f"State changed: {state}")
                    save_html_snapshot(state, html)
                    # Notify about the state change before attempting to book
                    notify(state)

                    if state == "open":
                        # Close the checker browser, as auto_book will launch many new ones
                        browser.close() 
                        # Execute the parallel booking
                        auto_book()
                        break

                    last_state = state
                else:
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] Still {state}")

                time.sleep(INTERVAL)

        finally:
            # Ensure the main browser is closed if the loop breaks or errors
            if browser and not browser.is_closed():
                browser.close()


if __name__ == "__main__":
    print("Starting KichiKichi checker + auto-booker...")
    if TEST_MODE:
        print(f"Running in TEST_MODE, using {TEST_HTML_FILE}. Reservations will be simulated.")
    main()
