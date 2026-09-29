from pathlib import Path
import shutil


ROOT = Path(__file__).resolve().parent
DIST_DIR = ROOT / "dist"
PUBLIC_FILES = (
    "index.html",
    "about.html",
    "accommodation.html",
    "booking-terms.html",
    "booking.html",
    "contact.html",
    "dining.html",
    "experiences.html",
    "house-rules.html",
    "privacy.html",
    "tripadvisor-widget.html",
    "script.js",
    "styles.css",
)


def build_site():
    if DIST_DIR.exists():
        shutil.rmtree(DIST_DIR)
    DIST_DIR.mkdir()

    for filename in PUBLIC_FILES:
        shutil.copy2(ROOT / filename, DIST_DIR / filename)
    shutil.copytree(ROOT / "assets", DIST_DIR / "assets")

    print(f"Static site built in {DIST_DIR}")


if __name__ == "__main__":
    build_site()