# Multimodal RAG Agent for Clothing Store

A multimodal Retrieval-Augmented Generation (RAG) API that matches customer clothing images against a local product catalog using CLIP embeddings + ChromaDB, then returns product details as JSON.

## Project Structure

- `app.py` - FastAPI + Gradio entry point
- `indexer.py` - One-time (or on-demand) image indexing into ChromaDB
- `retriever.py` - Image query encoding + similarity search
- `agent.py` - LangChain agent wrapper with `product_lookup` tool
- `database.py` - SQLite schema + CRUD + sample seed data
- `requirements.txt` - pinned dependencies (CPU-only torch)
- `.env.example` - environment variable template
- `.env` - local secret file, not committed
- `data/products.db` - SQLite DB file
- `data/chroma_store/` - persistent ChromaDB vector store
- `data/product_images/` - product images used for matching

Generated files such as `data/products.db`, `data/chroma_store/`, `.env`, and the virtual environment are excluded by `.gitignore`.

## 1. Setup

1. Clone the repository.
2. Create and activate a Python 3.10+ virtual environment.
3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Create your env file from template:

```bash
cp .env.example .env
```

5. Set your Hugging Face token in `.env`:

```env
HUGGINGFACEHUB_API_TOKEN=your_real_token_here
```

## 2. Initialize Data

Run the database bootstrap to create the schema and seed sample products:

```bash
python database.py
```

Add your product images to `data/product_images/`.

Build the vector index:

```bash
python indexer.py
```

## 3. How to Add Products

1. Add the image file into `data/product_images/`.
2. Insert product metadata with `database.insert_product(...)`.
3. Rebuild vectors by running:

```bash
python indexer.py
```

Or call the API endpoint:

```bash
POST /reload-index
```

## 4. Run Locally

Start the app (FastAPI + mounted Gradio UI):

```bash
python app.py
```

Alternative command:

```bash
uvicorn app:app --host 0.0.0.0 --port 7860
```

Available endpoints:

- `GET /health`
- `POST /identify` (multipart form-data field name: `file`)
- `POST /reload-index`

## 5. Deploy to Hugging Face Spaces

1. Create a new Space using **Gradio SDK**.
2. Add secret `HUGGINGFACEHUB_API_TOKEN` in Space settings.
3. Push project files to the Space repository.
4. Space will install `requirements.txt` and serve the app.

## 6. n8n Integration

Use an **HTTP Request** node:

- Method: `POST`
- URL: `https://your-space.hf.space/identify`
- Body type: `form-data`
- Field name: `file` (attach image binary)

Then parse response JSON fields such as:

- `product_id`
- `name`
- `price`
- `confidence_score`
- `message`

## Notes

- Uses CPU-only PyTorch to stay compatible with free Hugging Face Spaces.
- ChromaDB uses `PersistentClient` so embeddings survive restarts.
- API responses are JSON-friendly dictionaries.
