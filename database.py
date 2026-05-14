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


def clear_products() -> None:
    with _get_connection() as conn:
        conn.execute("DELETE FROM products")
        conn.commit()


def seed_sample_products() -> None:
    # Seed set aligned to the user-provided product image filenames.
    sample_products = [
        {
            "product_id": "P-COAT-001",
            "name": "Classic Black Coat",
            "description": "Timeless black coat with a tailored fit and warm lining.",
            "price": 129.0,
            "category": "Outerwear",
            "image_path": "data/product_images/coat.jpg",
        },
        {
            "product_id": "P-HOODIE-002",
            "name": "Brown Hoodie",
            "description": "Cozy brown hoodie with a soft fleece interior and adjustable drawstring hood.",
            "price": 58.0,
            "category": "Sweatshirts",
            "image_path": "data/product_images/hoodie.jpg",
        },
        {
            "product_id": "P-JACKET-003",
            "name": "Red Puff Jacket",
            "description": "Casual puff jacket with a cozy fill and adjustable cuffs.",
            "price": 84.0,
            "category": "Outerwear",
            "image_path": "data/product_images/jacket.jpg",
        },
        {
            "product_id": "P-JEANS-004",
            "name": "Blue Jeans",
            "description": "Classic straight-leg jeans with a durable denim finish.",
            "price": 72.0,
            "category": "Jeans",
            "image_path": "data/product_images/Jeans.jpg",
        },
        {
            "product_id": "P-SNEAKERS-005",
            "name": "Everyday white Sneakers",
            "description": "Lightweight sneakers with cushioned soles for daily wear.",
            "price": 64.25,
            "category": "Shoes",
            "image_path": "data/product_images/sneakers.jpg",
        },
        {
            "product_id": "P-TSHIRT-006",
            "name": "Crew Neck green T-Shirt",
            "description": "Soft cotton t-shirt with a regular fit and everyday comfort.",
            "price": 22.0,
            "category": "Tops",
            "image_path": "data/product_images/tshirt.jpg",
        },
    ]

    for product in sample_products:
        insert_product(**product)


def bootstrap() -> None:
    init_db()
    clear_products()
    seed_sample_products()


if __name__ == "__main__":
    bootstrap()
    print(f"Database ready at: {DB_PATH}")
    print(f"Total products: {len(get_all_products())}")
