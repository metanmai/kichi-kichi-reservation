import time
import requests
from datetime import datetime
# Import threading for parallel execution
import threading 
from playwright.sync_api import sync_playwright, TimeoutError
import os
import subprocess # New import for running shell commands

# ===============================
# Configuration
# ===============================
URL = "https://kichikichi.com/kichikichi-reservation/"
TEXT_BEFORE = "When the reservation time arrives, the reservation page will open."
TEXT_CLOSED = "We are currently fully booked. Reservations cannot be made at this time."
NTFY_TOPIC = "kichikichi-alert"
NTFY_URL = f"https://ntfy.sh/{NTFY_TOPIC}"
INTERVAL = 1  # seconds between checks
HTML_DUMP_DIR = "html_snapshots"
SUCCESS_SCREENSHOTS_DIR = "success_screenshots" 

# Git Sync Configuration
SYNC_BRANCH = "artifacts-check" # Branch name for saving mid-run artifacts
SYNC_INTERVAL_CHECKS = 10

# Reservation config - Each person gets ONE slot, both Bar and Table
USERS = [
    {"name": "Asha Mehra",        "email": "asha.mehra@gmail.com",        "slot": "17:00"},
    {"name": "Karan Iyer",        "email": "karan.iyer90@outlook.com",    "slot": "18:00"},
    {"name": "Priya Natarajan",   "email": "priya.natarajan@mailinator.com","slot": "19:00"},
    {"name": "Rohit Verma",       "email": "rohit.verma1988@yahoo.com",   "slot": "20:00"},
    {"name": "Sana Kapoor",       "email": "sana.kapoor+test@gmail.com",   "slot": "17:00"},
]


RES_PEOPLE = "3"

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
TEST_MODE = False
TEST_HTML_FILE = "KichiKichi Reservation - ザ・洋食屋・キチキチ.html"
TEST_STATE = "open"

# Create required directories
os.makedirs(HTML_DUMP_DIR, exist_ok=True)
os.makedirs(SUCCESS_SCREENSHOTS_DIR, exist_ok=True)

# Global flag to track the browser instance for cleanup
global_browser = None 

# ===============================
# Helpers
# ===============================
def run_shell_command(command):
    """Execute a shell command and print output/errors."""
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        # print(f"Command success: {result.stdout.strip()}") # Uncomment for detailed debug
    except subprocess.CalledProcessError as e:
        print(f"Shell command failed: {e.cmd}")
        print(f"Stdout: {e.stdout.strip()}")
        print(f"Stderr: {e.stderr.strip()}")
        return False
    return True

def sync_artifacts():
    """Commits and pushes HTML snapshots mid-run to the sync branch."""
    print(f"\n--- Attempting to sync artifacts to branch '{SYNC_BRANCH}' ---")
    
    # 1. Stash any existing changes (optional, but clean)
    run_shell_command("git stash push -u -m 'temporary-stash'")
    
    # 2. Checkout the artifact sync branch
    if not run_shell_command(f"git checkout {SYNC_BRANCH}"):
        # If checkout fails (branch doesn't exist), create it
        print(f"Branch {SYNC_BRANCH} not found. Creating it.")
        if not run_shell_command(f"git checkout -b {SYNC_BRANCH}"):
            print("ERROR: Could not checkout or create sync branch. Skipping sync.")
            # Revert to original branch
            run_shell_command("git checkout master")
            run_shell_command("git stash pop --index || true")
            return

    # 3. Restore the stash (only the files that were stashed)
    run_shell_command("git stash pop --index || true")

    # 4. Add the artifact directories (HTML snapshots and SUCCESS screenshots)
    if not (run_shell_command(f"git add -f {HTML_DUMP_DIR}") and run_shell_command(f"git add -f {SUCCESS_SCREENSHOTS_DIR}")):
        print("ERROR: Failed to git add snapshots.")
        return

    # 5. Commit if there are changes
    if run_shell_command("git diff --cached --exit-code --quiet"):
        print("No new HTML snapshots to commit.")
    else:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        commit_message = f"CI Sync: HTML snapshots up to {timestamp}"
        if run_shell_command(f"git commit -m \"{commit_message}\""):
            print("Commit successful.")
            
            # 6. Push changes to the repository
            # Note: We use --force because the push will happen multiple times from the same job
            if run_shell_command(f"git push origin {SYNC_BRANCH} --force"):
                print(f"Successfully pushed artifacts to {SYNC_BRANCH}")
            else:
                print("ERROR: Failed to push artifacts.")
    
    # 7. Return to the main branch
    run_shell_command("git checkout master")
    print("--- Artifact sync complete ---")


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
            print(f"ERROR: Test HTML file '{TEST_HTML_FILE}' not found. Defaulting to 'before' state.")
            html = ""
        # In TEST_MODE, always return the fixed TEST_STATE
        return TEST_STATE, html

    page.goto(URL, wait_until="load")
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
        
        if state not in ("open", "closed", "before"):
            print(f"[{datetime.now()}] Skipping notify for state {state}")
            return

    try:
        requests.post(NTFY_URL, data=msg.encode("utf-8"), headers={"Priority": str(priority)})
        print(f"Notification sent (priority {priority}): {msg}")
    except Exception as e:
        print(f"Notification failed: {e}")


def save_html_snapshot(state, html, page=None):
    """Save HTML and, if page object is provided, a screenshot."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Save HTML
    html_filename = os.path.join(HTML_DUMP_DIR, f"{state}_{timestamp}.html")
    with open(html_filename, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Saved HTML snapshot: {html_filename}")
    
    # Save screenshot if page object is passed
    if page:
        screenshot_filename = os.path.join(HTML_DUMP_DIR, f"{state}_{timestamp}.png")
        try:
            page.screenshot(path=screenshot_filename, full_page=True)
            print(f"Saved screenshot: {screenshot_filename}")
        except Exception as e:
            print(f"Failed to save screenshot: {e}")



def worker_book_slot(user, seating, reservation_num, total_reservations):
    """
    Core booking logic for a single user/seating combination.
    Launches its own Playwright session.
    """
    slot = user["slot"]
    slot_id = SLOT_MAPPING.get(slot)
    
    if not slot_id:
        print(f"Worker Error: No mapping for slot {slot}, skipping reservation for {user['name']}.")
        return
    
    # --- Playwright Setup (Local to this Thread) ---
    with sync_playwright() as p:
        try:
            # Launch browser in headless mode unless in TEST_MODE
            browser = p.chromium.launch(headless=False)
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

            # Define base filename for screenshot
            safe_slot = slot.replace(":", "")
            safe_name = user["name"].replace(" ", "_")
            
            if TEST_MODE:
                # ==========================================================
                # Simulation of Success Case for TEST_MODE = True
                # ==========================================================
                print("\n[TEST_MODE] Simulating successful form submission...")
                page.wait_for_timeout(2000) # Simulate network lag

                # Screenshot the fully filled form into the success folder
                base_filename = f"SIMULATED_SUCCESS_{safe_name}_{safe_slot}_{seating}.png"
                filename = os.path.join(SUCCESS_SCREENSHOTS_DIR, base_filename)
                page.screenshot(path=filename) 

                # Detailed Success Message
                success_msg = (
                    f"SUCCESS (TEST MODE): {user['name']} - Slot {slot}, {seating} "
                    f"for {RES_PEOPLE} people. Confirmation email address: {user['email']}. "
                    f"(Screenshot saved to: {filename})"
                )
                print(f"\n{success_msg}")
                notify("open", msg=success_msg)
                
            else:
                # ==========================================================
                # Actual Submission Logic for TEST_MODE = False
                # ==========================================================
                print("Submitting form...")
                page.click("#submit-button")
                
                try:
                    page.wait_for_url("**/confirmation", timeout=10000) 
                    success = True
                except TimeoutError:
                    page_content = page.content()
                    if "fully booked" in page_content.lower() or "cannot be made" in page_content.lower():
                        success = False
                    else:
                        success = None
                
                page_content = page.content()
                
                if success is True:
                    # Successful submission screenshot -> success folder
                    base_filename = f"SUCCESS_{safe_name}_{safe_slot}_{seating}.png"
                    filename = os.path.join(SUCCESS_SCREENSHOTS_DIR, base_filename)
                    page.screenshot(path=filename)
                    
                    # Detailed Success Message for Live Run
                    success_msg = (
                        f"SUCCESS: {user['name']} - Slot {slot}, {seating} "
                        f"for {RES_PEOPLE} people. Confirmation email address: {user['email']}. "
                        f"(Screenshot saved to: {filename})"
                    )
                    print(f"\n{success_msg}")
                    notify("open", msg=success_msg)
                elif success is False:
                    # Failure screenshot -> root (or could be placed in a failure folder)
                    base_filename = f"FAILED_{safe_name}_{safe_slot}_{seating}.png"
                    filename = base_filename # Kept in root for now
                    page.screenshot(path=filename)
                    
                    fail_msg = f"FAILED: {user['name']} - {slot} {seating} fully booked (Screenshot: {filename})"
                    print(f"\n{fail_msg}")
                    notify("closed", msg=fail_msg)
                else:
                    # Unknown result screenshot -> success folder (for checking)
                    base_filename = f"UNKNOWN_{safe_name}_{safe_slot}_{seating}.png"
                    filename = os.path.join(SUCCESS_SCREENSHOTS_DIR, base_filename) # Put unknown in success folder for review
                    page.screenshot(path=filename)
                    
                    unknown_msg = f"UNKNOWN: {user['name']} - {slot} {seating} (check screenshot: {filename})"
                    print(f"\n{unknown_msg}")
                    notify("open", msg=unknown_msg)

        except Exception as e:
            error_msg = f"Worker ERROR for {user['name']} - {slot} {seating}: {type(e).__name__} - {e}"
            print(f"\n{error_msg}\n")
            notify("open", msg=error_msg)
            try:
                # Error screenshots stay in the root for easy retrieval
                safe_slot = slot.replace(":", "")
                safe_name = user["name"].replace(" ", "_")
                page.screenshot(path=f"ERROR_{safe_name}_{safe_slot}_{seating}.png")
            except:
                pass


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
    
    # Initialize check counter
    check_count = 0 
    
    with sync_playwright() as p:
        # Launch browser to check initial state (can be headless)
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        notify(None, startup=True)

        print("Checker started...")
        try:
            while True:
                state, html = get_state(page)

                if state != last_state:
                    print(f"State changed: {state}")
                    save_html_snapshot(state, html, page)
                    notify(state)

                    if state == "open":
                        # Close the checker browser before starting the parallel workers
                        browser.close() 
                        auto_book()
                        break

                    last_state = state
                else:
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] Still {state}")

                # --- Mid-Run Artifact Sync Logic ---
                check_count += 1
                # Push artifacts to Git every 60 checks (60 seconds, or 1 minute)
                if check_count % SYNC_INTERVAL_CHECKS == 0: 
                    sync_artifacts()

                time.sleep(INTERVAL)

        finally:
            # FIX: Replace 'is_closed()' with 'is_connected()' to resolve Playwright AttributeError.
            # We close the browser if it exists and is still connected (meaning it wasn't closed before).
            if browser and browser.is_connected():
                browser.close()


if __name__ == "__main__":
    print("Starting KichiKichi checker + auto-booker...")
    if TEST_MODE:
        print(f"Running in TEST_MODE, using {TEST_HTML_FILE}. Success will be SIMULATED for every attempt.")
    
    # === CRITICAL SETUP FOR GIT SYNC ===
    # Configure user credentials for git commit/push
    run_shell_command("git config user.name 'github-actions[bot]'")
    run_shell_command("git config user.email 'github-actions[bot]@users.noreply.github.com'")
    
    main()
