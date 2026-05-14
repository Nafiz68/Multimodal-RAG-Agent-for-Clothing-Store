from __future__ import annotations

import json
import os
import re
from typing import Any

from PIL import Image

from database import get_product_by_id
from retriever import ImageRetriever

from langchain.agents import AgentType, initialize_agent
from langchain.tools import Tool
from langchain_community.llms import HuggingFaceHub
from dotenv import load_dotenv

load_dotenv()


class ClothingAgent:
    def __init__(self) -> None:
        self.retriever = ImageRetriever()
        self._current_image: Image.Image | None = None

        self.system_prompt = (
            "You are a helpful assistant for a clothing store. "
            "When a customer sends a photo, identify the product and "
            "return its details in this exact JSON format using the keys "
            "product_id, name, description, price, confidence_score, and message."
        )

        self.tools = [
            Tool(
                name="product_lookup",
                func=self._product_lookup_tool,
                description=(
                    "Use this tool to identify a clothing product from the current customer image "
                    "and return the matching product details with confidence."
                ),
            )
        ]

        self.agent = None
        hf_token = os.environ.get("HUGGINGFACEHUB_API_TOKEN", "").strip()
        if hf_token:
            try:
                llm = HuggingFaceHub(
                    repo_id="mistralai/Mistral-7B-Instruct-v0.2",
                    model_kwargs={"temperature": 0.1, "max_new_tokens": 300},
                    huggingfacehub_api_token=hf_token,
                )
                self.agent = initialize_agent(
                    tools=self.tools,
                    llm=llm,
                    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
                    verbose=False,
                    agent_kwargs={"prefix": self.system_prompt},
                )
            except Exception:
                self.agent = None

    def _product_lookup_tool(self, _: str) -> str:
        if self._current_image is None:
            return json.dumps(
                {
                    "product_id": None,
                    "name": None,
                    "description": None,
                    "price": None,
                    "confidence_score": 0.0,
                    "message": "No image provided",
                }
            )

        matches = self.retriever.find_similar(self._current_image, top_k=3)
        if isinstance(matches, dict):
            return json.dumps(
                {
                    "product_id": None,
                    "name": None,
                    "description": None,
                    "price": None,
                    "confidence_score": 0.0,
                    "message": matches.get("message", "No confident match found"),
                }
            )

        top_match = matches[0]
        product_id = top_match["product_id"]
        product = get_product_by_id(product_id)

        if not product:
            return json.dumps(
                {
                    "product_id": product_id,
                    "name": top_match.get("name"),
                    "description": None,
                    "price": top_match.get("price"),
                    "confidence_score": top_match.get("confidence_score", 0.0),
                    "message": "Product found in index but missing in database",
                }
            )

        return json.dumps(
            {
                "product_id": product["product_id"],
                "name": product["name"],
                "description": product["description"],
                "price": product["price"],
                "confidence_score": top_match.get("confidence_score", 0.0),
                "message": "Match found",
            }
        )

    def _parse_json_response(self, raw_output: str) -> dict[str, Any]:
        try:
            return json.loads(raw_output)
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", raw_output, flags=re.DOTALL)
            if match:
                try:
                    return json.loads(match.group(0))
                except json.JSONDecodeError:
                    pass

        raise ValueError("Agent response is not valid JSON")

    def identify_product(self, image: Image.Image) -> dict[str, Any]:
        try:
            self._current_image = image.convert("RGB")

            # If no HF token is available, gracefully fallback to retrieval only.
            if self.agent is None:
                return json.loads(self._product_lookup_tool("fallback"))

            result = self.agent.invoke(
                {
                    "input": (
                        "A customer uploaded an image. "
                        "Use available tools and return only valid JSON with keys: "
                        "product_id, name, description, price, confidence_score, message."
                    )
                }
            )

            raw_output = result.get("output", "") if isinstance(result, dict) else str(result)
            return self._parse_json_response(raw_output)
        except Exception as exc:
            try:
                return json.loads(self._product_lookup_tool("fallback"))
            except Exception:
                pass

            return {
                "product_id": None,
                "name": None,
                "description": None,
                "price": None,
                "confidence_score": 0.0,
                "message": f"Failed to identify product: {exc}",
            }
