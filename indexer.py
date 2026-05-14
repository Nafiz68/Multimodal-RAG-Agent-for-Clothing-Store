from __future__ import annotations

from pathlib import Path

import chromadb
import torch
from chromadb.api.types import Documents, EmbeddingFunction, Embeddings
from PIL import Image
from transformers import CLIPModel, CLIPProcessor

from database import get_all_products, init_db, seed_sample_products

BASE_DIR = Path(__file__).resolve().parent
CHROMA_DIR = BASE_DIR / "data" / "chroma_store"
COLLECTION_NAME = "product_images"


class CLIPImageEmbeddingFunction(EmbeddingFunction[Documents]):
    def __init__(self, model_name: str = "openai/clip-vit-base-patch32") -> None:
        self.device = "cpu"
        self.processor = CLIPProcessor.from_pretrained(model_name)
        self.model = CLIPModel.from_pretrained(model_name).to(self.device)

    def __call__(self, input: Documents) -> Embeddings:
        raise NotImplementedError("Use encode_image for image embeddings.")

    @torch.inference_mode()
    def encode_image(self, image: Image.Image) -> list[float]:
        image_inputs = self.processor(images=image.convert("RGB"), return_tensors="pt")
        image_inputs = {k: v.to(self.device) for k, v in image_inputs.items()}
        features = self.model.get_image_features(**image_inputs)
        features = torch.nn.functional.normalize(features, p=2, dim=-1)
        return features[0].cpu().tolist()


def build_index() -> None:
    init_db()
    seed_sample_products()

    CHROMA_DIR.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    collection = client.get_or_create_collection(name=COLLECTION_NAME)

    embedder = CLIPImageEmbeddingFunction()
    products = get_all_products()

    for product in products:
        image_path = BASE_DIR / product["image_path"]
        if not image_path.exists():
            print(f"Skipping missing image: {image_path}")
            continue

        with Image.open(image_path) as image:
            embedding = embedder.encode_image(image)

        collection.upsert(
            ids=[product["product_id"]],
            embeddings=[embedding],
            metadatas=[
                {
                    "product_id": product["product_id"],
                    "name": product["name"],
                    "price": float(product["price"]),
                    "image_path": product["image_path"],
                }
            ],
        )
        print(f"Indexed: {product['name']} ({product['product_id']})")

    print(f"Index build complete. Collection: {COLLECTION_NAME}")


if __name__ == "__main__":
    build_index()
