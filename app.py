from __future__ import annotations

from io import BytesIO

import gradio as gr
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from PIL import Image, UnidentifiedImageError

from agent import ClothingAgent
from indexer import build_index

app = FastAPI(title="Clothing Store Product Identifier API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

agent = ClothingAgent()


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok", "model": "CLIP + Mistral-7B"}


@app.post("/identify")
async def identify(file: UploadFile = File(...)) -> dict:
    try:
        image_bytes = await file.read()
        image = Image.open(BytesIO(image_bytes)).convert("RGB")
    except UnidentifiedImageError:
        return JSONResponse(
            status_code=400,
            content={
                "product_id": None,
                "name": None,
                "description": None,
                "price": None,
                "confidence_score": 0.0,
                "message": "Unsupported or unreadable image file",
            },
        )
    except Exception as exc:
        return JSONResponse(
            status_code=400,
            content={
                "product_id": None,
                "name": None,
                "description": None,
                "price": None,
                "confidence_score": 0.0,
                "message": f"Failed to read image: {exc}",
            },
        )

    result = agent.identify_product(image)
    return result


@app.post("/reload-index")
def reload_index() -> dict[str, str]:
    build_index()
    return {"status": "ok", "message": "Index reloaded"}


def gradio_identify(image: Image.Image) -> dict:
    return agent.identify_product(image)


gradio_ui = gr.Interface(
    fn=gradio_identify,
    inputs=gr.Image(type="pil", label="Upload customer photo"),
    outputs=gr.JSON(label="Matched Product"),
    title="Clothing Store Product Identifier",
    description="Upload a photo of a clothing item to find the matching product.",
)

app = gr.mount_gradio_app(app, gradio_ui, path="/")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", host="0.0.0.0", port=7860, reload=False)
