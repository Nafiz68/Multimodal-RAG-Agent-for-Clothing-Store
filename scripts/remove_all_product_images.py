from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
IMAGES_DIR = BASE / "data" / "product_images"

IMAGES_DIR.mkdir(parents=True, exist_ok=True)

removed = []
for p in IMAGES_DIR.glob('*'):
    if p.is_file():
        try:
            p.unlink()
            removed.append(p.name)
        except Exception as e:
            print(f"failed: {p} -> {e}")

print("removed:", removed)
