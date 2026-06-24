from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
ASSETS_DIR = PROJECT_ROOT / "assets"
INPUT_IMAGES_DIR = ASSETS_DIR / "inputs" / "images"
INPUT_VIDEOS_DIR = ASSETS_DIR / "inputs" / "videos"
OUTPUT_IMAGES_DIR = ASSETS_DIR / "outputs" / "images"
OUTPUT_VIDEOS_DIR = ASSETS_DIR / "outputs" / "videos"
OUTPUT_SCREENSHOTS_DIR = ASSETS_DIR / "outputs" / "screenshots"
DOCS_DIR = PROJECT_ROOT / "docs"


def ensure_project_dirs() -> None:
    for path in (
        INPUT_IMAGES_DIR,
        INPUT_VIDEOS_DIR,
        OUTPUT_IMAGES_DIR,
        OUTPUT_VIDEOS_DIR,
        OUTPUT_SCREENSHOTS_DIR,
        DOCS_DIR,
    ):
        path.mkdir(parents=True, exist_ok=True)


def ensure_parent_dir(path: str | Path) -> Path:
    resolved = Path(path).expanduser().resolve()
    resolved.parent.mkdir(parents=True, exist_ok=True)
    return resolved
