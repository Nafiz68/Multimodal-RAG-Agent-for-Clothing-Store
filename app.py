import io
import os

from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from PIL import Image

from agent import ClothingAgent

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

agent = ClothingAgent()


@app.get("/health")
def health():
    return {"status": "ok", "space": "clothing-rag-agent"}


@app.post("/identify")
async def identify(file: UploadFile = File(...)):
    contents = await file.read()
    image = Image.open(io.BytesIO(contents)).convert("RGB")
    result = agent.identify_product(image)
    return result


@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <!doctype html>
    <html lang="en">
    <head>
        <meta charset="utf-8"/>
        <title>Clothing RAG Agent</title>
        <style>
            body { font-family: Arial, sans-serif; background: #f5f7fb; margin: 0; color: #111827; }
            .wrap { max-width: 680px; margin: 48px auto; padding: 24px; }
            .card { background: #fff; border: 1px solid #e5e7eb; border-radius: 16px; padding: 32px; }
            h1 { margin: 0 0 8px; font-size: 26px; }
            p { color: #6b7280; line-height: 1.6; }
            input[type=file] { margin: 16px 0; display: block; }
            button { background: #2563eb; color: #fff; border: none; padding: 10px 24px; border-radius: 8px; cursor: pointer; font-size: 15px; }
            button:hover { background: #1d4ed8; }
            pre { background: #f3f4f6; padding: 16px; border-radius: 8px; font-size: 13px; overflow-x: auto; margin-top: 20px; min-height: 60px; }
            .label { font-size: 13px; font-weight: 600; color: #374151; margin-bottom: 4px; }
        </style>
    </head>
    <body>
        <div class="wrap">
            <div class="card">
                <h1>Clothing Store — Product Identifier</h1>
                <p>Upload a photo of a clothing item to identify the matching product.</p>
                <div class="label">Select image</div>
                <input type="file" id="img-input" accept="image/*"/>
                <button onclick="identify()">Identify Product</button>
                <div class="label" style="margin-top:20px">Result</div>
                <pre id="result">Result will appear here...</pre>
            </div>
        </div>
        <script>
            async function identify() {
                const input = document.getElementById('img-input');
                const result = document.getElementById('result');
                if (!input.files.length) {
                    result.textContent = 'Please select an image first.';
                    return;
                }
                result.textContent = 'Identifying...';
                const form = new FormData();
                form.append('file', input.files[0]);
                try {
                    const res = await fetch('/identify', { method: 'POST', body: form });
                    const data = await res.json();
                    result.textContent = JSON.stringify(data, null, 2);
                } catch (e) {
                    result.textContent = 'Error: ' + e.message;
                }
            }
        </script>
    </body>
    </html>
    """


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 7860))
    uvicorn.run(app, host="0.0.0.0", port=port)