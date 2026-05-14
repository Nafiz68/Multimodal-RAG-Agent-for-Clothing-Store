from __future__ import annotations

import unittest
from pathlib import Path

from PIL import Image

from retriever import ImageRetriever


class TestImageRetriever(unittest.TestCase):
    def test_find_similar_returns_expected_structure(self) -> None:
        sample_image_path = Path("data/product_images/dress_001.jpg")
        self.assertTrue(sample_image_path.exists(), "Sample image is missing")

        retriever = ImageRetriever()
        with Image.open(sample_image_path) as image:
            results = retriever.find_similar(image=image, top_k=3)

        self.assertIsInstance(results, list)
        self.assertGreater(len(results), 0)

        first = results[0]
        self.assertIn("product_id", first)
        self.assertIn("name", first)
        self.assertIn("price", first)
        self.assertIn("distance", first)
        self.assertIn("confidence_score", first)
        self.assertEqual(first["product_id"], "P-DRESS-001")


if __name__ == "__main__":
    unittest.main()
