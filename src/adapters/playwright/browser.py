from __future__ import annotations
from pathlib import Path
from playwright.sync_api import sync_playwright


def capture_html(html_path: Path, out_png: Path, viewport=(1280, 720)) -> None:
    out_png.parent.mkdir(parents=True, exist_ok=True)
    url = html_path.resolve().as_uri()
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        try:
            page = browser.new_page(viewport={"width": viewport[0], "height": viewport[1]})
            page.goto(url, wait_until="load")
            page.screenshot(path=str(out_png), full_page=False)
        finally:
            browser.close()


