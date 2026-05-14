from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
IMAGES_DIR = BASE / "data" / "product_images"
PLACEHOLDERS = [
    "tshirt_006.jpg",
    "jeans_007.jpg",
    "sneakers_008.jpg",
    "hoodie_009.jpg",
    "denim_jacket_010.jpg",
]

IMAGES_DIR.mkdir(parents=True, exist_ok=True)

removed = []
for name in PLACEHOLDERS:
    p = IMAGES_DIR / name
    if p.exists():
        p.unlink()
        removed.append(name)

print("removed:", removed)
