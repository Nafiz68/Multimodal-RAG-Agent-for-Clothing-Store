# HuggingFace Spaces Deployment Guide

## Quick Setup (5 minutes)

### 1. Clone Your Space Repository
```bash
git clone https://huggingface.co/spaces/Nafizk368/Multimodal-RAG-Agent-for-Clothing-Store
cd Multimodal-RAG-Agent-for-Clothing-Store
```

### 2. Add Project Files
Copy all files from your local project into the Space directory:
```bash
# Copy Python files
cp /path/to/local/project/*.py .
cp /path/to/local/project/requirements.txt .
cp /path/to/local/project/.gitignore .
cp /path/to/local/project/.env.example .

# Copy product images (IMPORTANT)
mkdir -p data/product_images
cp /path/to/local/project/data/product_images/* data/product_images/

# Copy database if needed (optional, will rebuild on startup)
# cp /path/to/local/project/data/products.db data/
```

### 3. Update database.py for Spaces
The database and index are auto-generated, so add product metadata directly in your seed function if needed.

### 4. Commit and Push
```bash
git add .
git commit -m "Add Multimodal RAG Agent for Clothing Store"
git push
```

### 5. Add HuggingFace API Secret
In your Space dashboard:
- Settings → **Secrets and variables** → **New secret**
- Name: `HUGGINGFACEHUB_API_TOKEN`
- Value: Your HuggingFace API token (get from https://huggingface.co/settings/tokens)

### 6. Deploy
- Space will auto-restart after the push
- First boot takes 30-60 seconds (dependencies install + index builds)
- Once ready, access at: `https://huggingface.co/spaces/Nafizk368/Multimodal-RAG-Agent-for-Clothing-Store`

---

## Troubleshooting

### Logs Not Visible?
- Check the **Logs** tab in your Space settings

### Agent Returning Null?
- Ensure your product images are in `data/product_images/`
- Verify images are readable (JPEG/PNG)
- Check the confidence threshold in `retriever.py` (currently set to 30.0)

### Out of Disk Space?
- HF Spaces free tier: 50GB limit
- Consider resizing images or upgrading to a paid tier

### App Won't Start?
- Check requirements.txt for missing dependencies
- Ensure `app.py` is executable: `chmod +x app.py`
- Review Space logs for error messages

---

## Manual Testing

### Upload a Test Image
1. Go to your Space URL
2. Use the Gradio interface to upload a product image
3. Click submit to see matching product details

### Via API (Advanced)
```bash
curl -X POST "https://huggingface.co/spaces/Nafizk368/Multimodal-RAG-Agent-for-Clothing-Store/api/identify" \
  -F "file=@/path/to/image.jpg"
```

---

## Adding More Products

1. **Locally**: Add images to `data/product_images/`
2. Update `database.py` seed data with new product metadata
3. Commit and push to Space
4. Space will rebuild the index on restart

Or use the API:
```bash
POST /reload-index
```
This will re-index all images in `data/product_images/`.

---

## Performance Tips

- **Images**: Keep product photos under 2MB each (reduces indexing time)
- **Cold Start**: First request after restart takes ~30s (index builds)
- **Subsequent Requests**: ~500ms per identification (CLIP + retrieval)

---

## Support

- HF Spaces Docs: https://huggingface.co/docs/hub/spaces
- Issue Tracker: Add issues to your GitHub repo or Space discussions
