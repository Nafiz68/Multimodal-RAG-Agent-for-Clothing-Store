from __future__ import annotations

from pathlib import Path
from typing import Any

import chromadb
import torch
from PIL import Image
from transformers import CLIPModel, CLIPProcessor

BASE_DIR = Path(__file__).resolve().parent
CHROMA_DIR = BASE_DIR / "data" / "chroma_store"
COLLECTION_NAME = "product_images"


class ImageRetriever:
    def __init__(self, model_name: str = "openai/clip-vit-base-patch32") -> None:
        self.device = "cpu"
        self.processor = CLIPProcessor.from_pretrained(model_name)
        self.model = CLIPModel.from_pretrained(model_name).to(self.device)

        client = chromadb.PersistentClient(path=str(CHROMA_DIR))
        self.collection = client.get_or_create_collection(name=COLLECTION_NAME)

    @torch.inference_mode()
    def encode_image(self, image: Image.Image) -> list[float]:
        image_inputs = self.processor(images=image.convert("RGB"), return_tensors="pt")
        image_inputs = {k: v.to(self.device) for k, v in image_inputs.items()}
        features = self.model.get_image_features(**image_inputs)
        features = torch.nn.functional.normalize(features, p=2, dim=-1)
        return features[0].cpu().tolist()

    def find_similar(
        self,
        image: Image.Image,
        top_k: int = 3,
    ) -> list[dict[str, Any]] | dict[str, Any]:
        query_embedding = self.encode_image(image)

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=["metadatas", "distances"],
        )

        metadatas = (results.get("metadatas") or [[]])[0]
        distances = (results.get("distances") or [[]])[0]

        formatted: list[dict[str, Any]] = []
        for metadata, distance in zip(metadatas, distances):
            distance_value = float(distance)
            confidence = round((1 - distance_value) * 100, 1)
            formatted.append(
                {
                    "product_id": metadata.get("product_id"),
                    "name": metadata.get("name"),
                    "price": metadata.get("price"),
                    "distance": distance_value,
                    "confidence_score": confidence,
                }
            )

        if not formatted:
            return {"match": False, "message": "No confident match found"}

        if formatted[0]["confidence_score"] < 60:
            return {"match": False, "message": "No confident match found"}

        return formatted
