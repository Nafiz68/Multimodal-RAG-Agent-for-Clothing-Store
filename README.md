# Multimodal RAG Agent for Clothing Store

A multimodal Retrieval-Augmented Generation (RAG) API that matches customer clothing images against a local product catalog using CLIP embeddings + ChromaDB, then returns product details as JSON.

## Project Structure

- `app.py` - FastAPI entry point with a simple HTML test UI
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

Start the app (FastAPI + simple HTML UI):

```bash
python app.py
```

Alternative command:

```bash
uvicorn app:app --host 0.0.0.0 --port 7860
```

Run it through ngrok so you can test it from a public URL:

```bash
# 1. Start the app
python app.py

# 2. In a second terminal, expose port 7860
ngrok http 7860
```

ngrok will print a public forwarding URL such as `https://xxxx.ngrok-free.app`. Open that URL in your browser and use the homepage or `/identify` endpoint.

Available endpoints:

- `GET /health`
- `POST /identify` (multipart form-data field name: `file`)
- `POST /reload-index`

## 5. Deploy to Hugging Face Spaces

### Prerequisites
- HuggingFace account and Space created at: https://huggingface.co/spaces/Nafizk368/Multimodal-RAG-Agent-for-Clothing-Store
- Git installed locally
- HuggingFace CLI authenticated: `huggingface-cli login`

### Steps

1. **Clone your Space repository** (replace with your Space URL):
```bash
git clone https://huggingface.co/spaces/Nafizk368/Multimodal-RAG-Agent-for-Clothing-Store
cd Multimodal-RAG-Agent-for-Clothing-Store
```

2. **Add your project files**:
```bash
# Copy all project files into the cloned Space directory
cp -r /path/to/local/project/* .
```

3. **Add your product images** (required):
```bash
# Create the images directory and add your product photos
mkdir -p data/product_images
cp /path/to/your/images/* data/product_images/
```

4. **Add to git and commit**:
```bash
git add .
git commit -m "Add clothing store RAG agent"
git push
```

5. **Set the HuggingFace API Secret** in Space UI:
   - Go to your Space settings → **Secrets**
   - Add: `HUGGINGFACEHUB_API_TOKEN` with your HuggingFace API key

6. **Monitor deployment**:
   - Space will automatically restart and install dependencies from `requirements.txt`
   - Check the logs in the Space's **Logs** tab
   - Once running, access at: `https://huggingface.co/spaces/Nafizk368/Multimodal-RAG-Agent-for-Clothing-Store`

### Important Notes for Spaces

- **Disk space**: Free tier has 50GB; the Chroma index and SQLite DB are created fresh on each restart
- **Product images** must be included in the git repository (stored in `data/product_images/`)
- **Data persistence**: The vector index rebuilds on startup if missing
- **Hardware**: Free tier uses CPU; GPU is available on paid tiers
- **Cold start**: First load may take 30-60 seconds while dependencies are installed and index is built

## 6. n8n Integration

Use an **HTTP Request** node:

- Method: `POST`
- URL: `https://your-space.hf.space/identify` or `https://your-ngrok.dev/identify`
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
