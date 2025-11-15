#!/usr/bin/env python3
"""Test the parakeet design in the browser"""

from playwright.sync_api import sync_playwright
import time

def capture_parakeet():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page(viewport={'width': 1920, 'height': 1080})

        print("Navigating to localhost:3003...")
        page.goto('http://localhost:3003', timeout=60000)

        print("Waiting for page to load...")
        time.sleep(3)

        # Scroll to top to see the parakeet
        page.evaluate("window.scrollTo(0, 0)")
        time.sleep(1)

        print("Taking screenshot...")
        page.screenshot(path='/Users/erichowens/coding/friendly-parakeet/website/parakeet_final.png', full_page=False)

        print("Screenshot saved to parakeet_final.png")
        print("\nLeaving browser open for visual inspection...")
        print("Press Ctrl+C to close")

        try:
            time.sleep(300)  # Keep open for 5 minutes
        except KeyboardInterrupt:
            print("\nClosing browser...")

        browser.close()

if __name__ == '__main__':
    capture_parakeet()
