import time
import requests
from datetime import datetime
import threading
from playwright.sync_api import sync_playwright, TimeoutError
import os
import subprocess

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
SYNC_BRANCH = "artifacts-check"
SYNC_INTERVAL_CHECKS = 60

USERS = [
    {"name": "Asha Mehra",        "email": "asha.mehra@gmail.com",        "slot": "17:00"},
    {"name": "Karan Iyer",        "email": "karan.iyer90@outlook.com",    "slot": "18:00"},
    {"name": "Priya Natarajan",   "email": "priya.natarajan@mailinator.com","slot": "19:00"},
    {"name": "Rohit Verma",       "email": "rohit.verma1988@yahoo.com",   "slot": "20:00"},
    {"name": "Sana Kapoor",       "email": "sana.kapoor+test@gmail.com",   "slot": "17:00"},
]

RES_PEOPLE = "3"

SLOT_MAPPING = {
    "12:00": "slot_1",
    "13:00": "slot_2",
    "17:00": "slot_3",
    "18:00": "slot_4",
    "19:00": "slot_5",
    "20:00": "slot_6",
}

SEATINGS = ["Bar", "Table"]

TEST_MODE = os.getenv("TEST_MODE", "false").lower() == "true"

print(f"TEST_MODE: {TEST_MODE}")

TEST_HTML_FILE = "KichiKichi Reservation - ザ・洋食屋・キチキチ.html"
TEST_STATE = "open"

os.makedirs(HTML_DUMP_DIR, exist_ok=True)
os.makedirs(SUCCESS_SCREENSHOTS_DIR, exist_ok=True)

global_browser = None

# ===============================
# Helpers
# ===============================
def run_shell_command(command):
    """Execute a shell command and print output/errors."""
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        print(f"Shell command failed: {e.cmd}")
        print(f"Stdout: {e.stdout.strip()}")
        print(f"Stderr: {e.stderr.strip()}")
        return False
    return True

def sync_artifacts():
    """Commits and pushes HTML snapshots and screenshots mid-run to the sync branch."""
    print(f"\n--- Attempting to sync artifacts to branch '{SYNC_BRANCH}' ---")

    # Save current git config
    old_name_result = subprocess.run("git config --get user.name", shell=True, capture_output=True, text=True)
    old_email_result = subprocess.run("git config --get user.email", shell=True, capture_output=True, text=True)
    old_name = old_name_result.stdout.strip()
    old_email = old_email_result.stdout.strip()

    # Set CI user only for artifact commits
    run_shell_command("git config user.name 'github-actions[bot]'")
    run_shell_command("git config user.email 'github-actions[bot]@users.noreply.github.com'")

    # Determine default branch dynamically
    try:
        result = subprocess.run(
            "git remote show origin | grep 'HEAD branch' | cut -d' ' -f5",
            shell=True, capture_output=True, text=True, check=True
        )
        default_branch = result.stdout.strip() or "master"
    except subprocess.CalledProcessError:
        default_branch = "master"
    print(f"Default branch detected: {default_branch}")

    # Stash changes before switching branch
    run_shell_command("git stash push -u -m 'temp-before-sync' || true")

    # Checkout sync branch
    if not run_shell_command(f"git checkout {SYNC_BRANCH}"):
        print(f"Branch {SYNC_BRANCH} not found. Creating it.")
        if not run_shell_command(f"git checkout -b {SYNC_BRANCH}"):
            print("ERROR: Could not checkout or create sync branch. Skipping sync.")
            run_shell_command(f"git checkout {default_branch}")
            run_shell_command("git stash pop --index || true")
            return

    # Pop stash so artifact files are available
    run_shell_command("git stash pop --index || true")

    # Add artifacts (force add)
    for path in [HTML_DUMP_DIR, SUCCESS_SCREENSHOTS_DIR]:
        if os.path.exists(path) and any(os.scandir(path)):
            run_shell_command(f"git add -f {path}")

    # Commit changes if any
    has_changes = subprocess.run("git diff --cached --exit-code --quiet", shell=True).returncode != 0
    if has_changes:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        commit_message = f"CI Sync: HTML snapshots up to {timestamp}"
        if run_shell_command(f"git commit -m \"{commit_message}\""):
            run_shell_command(f"git push origin {SYNC_BRANCH} --force")
            print(f"Artifacts pushed to {SYNC_BRANCH}")
    else:
        print("No new artifacts to commit.")

    # Optionally return to default branch (safe in CI to skip)
    # run_shell_command(f"git checkout {default_branch}")

    # Restore original Git config
    if old_name:
        run_shell_command(f"git config user.name \"{old_name}\"")
    if old_email:
        run_shell_command(f"git config user.email \"{old_email}\"")

    print("--- Artifact sync complete ---")

def get_state(page):
    """Check reservation page state and return (state, html)."""
    if TEST_MODE:
        try:
            with open(TEST_HTML_FILE, encoding="utf-8") as f:
                html = f.read()
        except FileNotFoundError:
            html = ""
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
    """Send notification via ntfy."""
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

    if state not in ("open", "closed", "before") and not startup:
        print(f"[{datetime.now()}] Skipping notify for state {state}")
        return

    try:
        requests.post(NTFY_URL, data=msg.encode("utf-8"), headers={"Priority": str(priority)})
        print(f"Notification sent (priority {priority}): {msg}")
    except Exception as e:
        print(f"Notification failed: {e}")

def save_html_snapshot(state, html, page=None):
    """Save HTML and optional screenshot."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    html_filename = os.path.join(HTML_DUMP_DIR, f"{state}_{timestamp}.html")
    with open(html_filename, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Saved HTML snapshot: {html_filename}")

    if page:
        screenshot_filename = os.path.join(HTML_DUMP_DIR, f"{state}_{timestamp}.png")
        try:
            page.screenshot(path=screenshot_filename, full_page=True)
            print(f"Saved screenshot: {screenshot_filename}")
        except Exception as e:
            print(f"Failed to save screenshot: {e}")

# ===============================
# Booking worker
# ===============================
def worker_book_slot(user, seating, reservation_num, total_reservations):
    slot = user["slot"]
    slot_id = SLOT_MAPPING.get(slot)
    if not slot_id:
        print(f"No mapping for slot {slot}, skipping {user['name']}.")
        return

    with sync_playwright() as p:
        try:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()

            print(f"[{reservation_num}/{total_reservations}] Booking: {user['name']} | {slot} | {seating}")

            # Load page
            if TEST_MODE:
                page.goto(f"file://{os.path.abspath(TEST_HTML_FILE)}", wait_until="load")
            else:
                page.goto(URL, wait_until="networkidle")
            page.wait_for_timeout(500)

            # Fill form
            page.select_option("#language-select", "en")
            page.check("#agree")
            page.fill("#name", user["name"])
            page.fill("#email", user["email"])
            page.fill("#confirm_email", user["email"])
            page.fill("#number_of_people", RES_PEOPLE)
            page.select_option("#seating_preference", seating)
            page.select_option("#time", slot_id)
            page.check("#confirm-agree")
            page.wait_for_timeout(200)

            # Screenshots and notifications
            safe_slot = slot.replace(":", "")
            safe_name = user["name"].replace(" ", "_")

            if TEST_MODE:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = os.path.join(SUCCESS_SCREENSHOTS_DIR, f"SUCCESS_{safe_name}_{safe_slot}_{seating}_{timestamp}.png")

                page.screenshot(path=filename)
                msg = f"SUCCESS (TEST MODE): {user['name']} - Slot {slot}, {seating}"
                print(msg)
                notify("open", msg=msg)
            else:
                page.click("#submit-button")
                try:
                    page.wait_for_url("**/confirmation", timeout=10000)
                    success = True
                except TimeoutError:
                    content = page.content()
                    success = False if "fully booked" in content.lower() else None

                if success:
                    filename = os.path.join(SUCCESS_SCREENSHOTS_DIR, f"SUCCESS_{safe_name}_{safe_slot}_{seating}.png")
                    page.screenshot(path=filename)
                    msg = f"SUCCESS: {user['name']} - {slot} {seating}"
                    print(msg)
                    notify("open", msg=msg)
                elif success is False:
                    filename = f"FAILED_{safe_name}_{safe_slot}_{seating}.png"
                    page.screenshot(path=filename)
                    msg = f"FAILED: {user['name']} - {slot} {seating} fully booked"
                    print(msg)
                    notify("closed", msg=msg)
                else:
                    filename = os.path.join(SUCCESS_SCREENSHOTS_DIR, f"UNKNOWN_{safe_name}_{safe_slot}_{seating}.png")
                    page.screenshot(path=filename)
                    msg = f"UNKNOWN: {user['name']} - {slot} {seating}"
                    print(msg)
                    notify("open", msg=msg)

        except Exception as e:
            msg = f"ERROR for {user['name']} - {slot} {seating}: {e}"
            print(msg)
            notify("open", msg=msg)
            try:
                page.screenshot(path=f"ERROR_{safe_name}_{safe_slot}_{seating}.png")
            except:
                pass

def auto_book():
    total_reservations = len(USERS) * len(SEATINGS)
    threads = []
    reservation_num = 0

    for user in USERS:
        for seating in SEATINGS:
            reservation_num += 1
            t = threading.Thread(target=worker_book_slot, args=(user, seating, reservation_num, total_reservations))
            threads.append(t)
            t.start()

    for t in threads:
        t.join()
    print("All reservation threads completed.")

# ===============================
# Main
# ===============================
def main():
    last_state = None
    check_count = 0

    with sync_playwright() as p:
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
                    last_state = state

                    if state == "open":
                        browser.close()
                        auto_book()
                        # Force sync artifacts in TEST_MODE or after booking
                        sync_artifacts()
                        break
                else:
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] Still {state}")

                check_count += 1
                if check_count % SYNC_INTERVAL_CHECKS == 0:
                    sync_artifacts()

                time.sleep(INTERVAL)

        finally:
            if browser and browser.is_connected():
                browser.close()

if __name__ == "__main__":
    print("Starting KichiKichi checker + auto-booker...")
    if TEST_MODE:
        print(f"TEST_MODE: using {TEST_HTML_FILE}, success simulated for every attempt.")

    main()
