from playwright.sync_api import sync_playwright
import os
import shutil

urls_to_try = [
    "https://playgba.org/games/gba-8820",
    "https://www.eggermath.com/pokemon-firered",
    "https://classicemu.com/games/pokemon-firered.html",
    "https://gbapokemon.com/play/pokemon-fire-red",
    "https://arcadespot.com/game/pokemon-fire-red-evolution",
]

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, args=["--ignore-certificate-errors"])
    context = browser.new_context(ignore_https_errors=True)
    page = context.new_page()
    
    success_url = None
    for url in urls_to_try:
        print(f"\nTrying: {url}")
        try:
            page.goto(url, wait_until="networkidle", timeout=30000)
            print(f"  Page title: {page.title()}")
            
            screenshot_path = f"/tmp/pokemon_game_{url.replace('https://', '').replace('/', '_')}.png"
            page.screenshot(path=screenshot_path, full_page=True)
            
            size = os.path.getsize(screenshot_path)
            print(f"  Screenshot saved: {screenshot_path} ({size} bytes)")
            
            if size > 100000:
                print(f"  SUCCESS: Found working page at {url}")
                shutil.copy(screenshot_path, "/tmp/pokemon_game.png")
                success_url = url
                break
                
        except Exception as e:
            print(f"  Error: {e}")
    
    browser.close()

print(f"\nResult URL: {success_url}")
if os.path.exists("/tmp/pokemon_game.png"):
    print(f"Final screenshot: /tmp/pokemon_game.png ({os.path.getsize('/tmp/pokemon_game.png')} bytes)")
else:
    print("No screenshot found")