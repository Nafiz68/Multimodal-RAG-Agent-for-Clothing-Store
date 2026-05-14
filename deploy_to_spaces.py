#!/usr/bin/env python3
"""
Deploy the Multimodal RAG Agent to HuggingFace Spaces.

Usage:
    python deploy_to_spaces.py <space_repo_path>

Example:
    python deploy_to_spaces.py ~/hf-spaces/Multimodal-RAG-Agent-for-Clothing-Store
"""

import sys
import shutil
from pathlib import Path
import subprocess

def deploy(space_dir: str) -> None:
    """Copy project files to Space repository and prepare for push."""
    space_path = Path(space_dir).resolve()
    
    if not space_path.exists():
        print(f"❌ Space directory not found: {space_path}")
        print(f"   Run: git clone https://huggingface.co/spaces/Nafizk368/Multimodal-RAG-Agent-for-Clothing-Store")
        return
    
    project_root = Path(__file__).parent.resolve()
    
    # Files to copy
    files_to_copy = [
        "app.py",
        "agent.py",
        "retriever.py",
        "indexer.py",
        "database.py",
        "requirements.txt",
        ".env.example",
        ".gitignore",
        "README.md",
        "DEPLOYMENT_GUIDE.md",
    ]
    
    print(f"📦 Deploying from: {project_root}")
    print(f"📍 Pushing to Space: {space_path}\n")
    
    # Copy files
    for filename in files_to_copy:
        src = project_root / filename
        dst = space_path / filename
        if src.exists():
            shutil.copy2(src, dst)
            print(f"✅ Copied {filename}")
        else:
            print(f"⚠️  Skipped {filename} (not found)")
    
    # Copy product images
    images_src = project_root / "data" / "product_images"
    images_dst = space_path / "data" / "product_images"
    if images_src.exists():
        images_dst.parent.mkdir(parents=True, exist_ok=True)
        for img in images_src.glob("*"):
            if img.is_file():
                shutil.copy2(img, images_dst / img.name)
        print(f"✅ Copied product images ({len(list(images_src.glob('*')))} files)")
    else:
        print(f"⚠️  No product images found in {images_src}")
    
    print("\n📤 Ready to push. Execute:\n")
    print(f"   cd {space_path}")
    print(f"   git add .")
    print(f"   git commit -m 'Deploy Multimodal RAG Agent'")
    print(f"   git push\n")
    print("🚀 Space will deploy automatically after push.")
    print("   Monitor progress in Space → Logs tab")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python deploy_to_spaces.py <space_repo_path>")
        print("\nExample:")
        print("  python deploy_to_spaces.py ~/hf-spaces/Multimodal-RAG-Agent-for-Clothing-Store")
        sys.exit(1)
    
    deploy(sys.argv[1])
