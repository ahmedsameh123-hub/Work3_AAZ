"""
Resize + compress your photos so the site loads fast on her phone.

1) Put ALL your original photos in the  raw_photos/  folder.
   - A file whose name starts with "hero" (e.g. hero.jpg)  -> static/images/hero.jpg
   - Every other file                                      -> static/images/gallery/
2) Run:  python optimize_images.py
"""
import re
from pathlib import Path
from PIL import Image, ImageOps

BASE = Path(__file__).resolve().parent
RAW = BASE / "raw_photos"
OUT_HERO = BASE / "static" / "images"
OUT_GALLERY = BASE / "static" / "images" / "gallery"
EXT = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tiff"}

OUT_GALLERY.mkdir(parents=True, exist_ok=True)

files = sorted(p for p in RAW.iterdir() if p.suffix.lower() in EXT)
if not files:
    print("No photos found in raw_photos/  (put your photos there first)")

for p in files:
    is_hero = p.stem.lower().startswith("hero")
    max_side = 2000 if is_hero else 1600
    out_name = "hero.jpg" if is_hero else re.sub(r"[^\w\-]+", "_", p.stem) + ".jpg"
    out_path = (OUT_HERO if is_hero else OUT_GALLERY) / out_name

    with Image.open(p) as img:
        img = ImageOps.exif_transpose(img)  # fix phone rotation
        if img.mode not in ("RGB", "L"):
            img = img.convert("RGB")
        img.thumbnail((max_side, max_side), Image.LANCZOS)
        img.save(out_path, "JPEG", quality=82, optimize=True, progressive=True)

    before = p.stat().st_size / 1024
    after = out_path.stat().st_size / 1024
    print(f"{p.name:30s} {before:8.0f} KB -> {after:6.0f} KB   ({out_path.relative_to(BASE)})")

print("\nDone. Refresh the website.")
