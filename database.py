from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "products.db"


def _get_connection() -> sqlite3.Connection:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with _get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS products (
                product_id   TEXT PRIMARY KEY,
                name         TEXT NOT NULL,
                description  TEXT,
                price        REAL,
                category     TEXT,
                image_path   TEXT NOT NULL
            );
            """
        )
        conn.commit()


def insert_product(
    product_id: str,
    name: str,
    description: str,
    price: float,
    category: str,
    image_path: str,
) -> None:
    with _get_connection() as conn:
        conn.execute(
            """
            INSERT OR REPLACE INTO products
            (product_id, name, description, price, category, image_path)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (product_id, name, description, price, category, image_path),
        )
        conn.commit()


def get_product_by_id(product_id: str) -> dict[str, Any] | None:
    with _get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM products WHERE product_id = ?", (product_id,)
        ).fetchone()
        return dict(row) if row else None


def get_all_products() -> list[dict[str, Any]]:
    with _get_connection() as conn:
        rows = conn.execute("SELECT * FROM products ORDER BY product_id").fetchall()
        return [dict(row) for row in rows]


def seed_sample_products() -> None:
    sample_products = [
        {
            "product_id": "P-DRESS-001",
            "name": "Floral Midi Summer Dress",
            "description": "Lightweight floral midi dress with a fitted waist and breathable fabric.",
            "price": 59.99,
            "category": "Dresses",
            "image_path": "data/product_images/dress_001.jpg",
        },
        {
            "product_id": "P-SHIRT-002",
            "name": "Classic Oxford Button-Down Shirt",
            "description": "Crisp cotton oxford shirt with a tailored fit for everyday wear.",
            "price": 44.5,
            "category": "Shirts",
            "image_path": "data/product_images/shirt_002.jpg",
        },
        {
            "product_id": "P-JEANS-003",
            "name": "Slim Fit Indigo Denim Jeans",
            "description": "Mid-rise slim fit jeans in stretch indigo denim with five-pocket styling.",
            "price": 72.0,
            "category": "Jeans",
            "image_path": "data/product_images/jeans_003.jpg",
        },
        {
            "product_id": "P-JACKET-004",
            "name": "Lightweight Utility Jacket",
            "description": "Water-resistant utility jacket with zip closure and adjustable cuffs.",
            "price": 89.0,
            "category": "Jackets",
            "image_path": "data/product_images/jacket_004.jpg",
        },
        {
            "product_id": "P-SHOES-005",
            "name": "Everyday Knit Sneakers",
            "description": "Comfortable knit sneakers with cushioned sole for all-day walking.",
            "price": 64.25,
            "category": "Shoes",
            "image_path": "data/product_images/sneakers_005.jpg",
        },
    ]

    for product in sample_products:
        insert_product(**product)


def bootstrap() -> None:
    init_db()
    seed_sample_products()


if __name__ == "__main__":
    bootstrap()
    print(f"Database ready at: {DB_PATH}")
    print(f"Total products: {len(get_all_products())}")
