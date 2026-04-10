#!/usr/bin/env python3
"""
Download embedding models for local deployment using Qdrant FastEmbed.

This script downloads both dense and sparse models to the 'models' directory
for offline use in Docker deployment.

Dense Model: nomic-ai/nomic-embed-text-v1.5 (768 dimensions, MRL-trained, ~547MB)
Sparse Model: Qdrant/bm25 (BM25-based sparse embeddings)

Usage:
    pip install fastembed
    python download_models.py

The models will be saved to ./models/ in FastEmbed cache format (ONNX).
"""

import os
import sys
import shutil

# Models directory - this will be the FastEmbed cache directory
MODELS_DIR = os.environ.get('MODELS_DIR', 'models')

# Model names - using full precision model for best accuracy
DENSE_MODEL_NAME = os.environ.get('DENSE_MODEL_NAME', 'nomic-ai/nomic-embed-text-v1.5')
SPARSE_MODEL_NAME = os.environ.get('SPARSE_MODEL_NAME', 'Qdrant/bm25')


def clean_old_models():
    """Remove old sentence-transformers format models if they exist."""
    old_dirs = ['dense', 'sparse']
    for d in old_dirs:
        old_path = os.path.join(MODELS_DIR, d)
        if os.path.exists(old_path):
            # Check if it's old format (has .safetensors)
            has_safetensors = any(f.endswith('.safetensors') for f in os.listdir(old_path) if os.path.isfile(os.path.join(old_path, f)))
            if has_safetensors:
                print(f"  Removing old sentence-transformers model: {old_path}")
                shutil.rmtree(old_path)


def download_models():
    """Download both dense and sparse embedding models using FastEmbed."""
    from fastembed import TextEmbedding, SparseTextEmbedding
    
    # Create the models directory
    os.makedirs(MODELS_DIR, exist_ok=True)
    abs_models_dir = os.path.abspath(MODELS_DIR)
    
    print(f"\n[1/2] Downloading dense model: {DENSE_MODEL_NAME}")
    print("  (nomic-embed-text with MRL support, ONNX format)")
    print("  (768-dimensional vectors, truncatable to 256)")
    
    # Download dense model - FastEmbed will cache it in MODELS_DIR
    dense = TextEmbedding(
        model_name=DENSE_MODEL_NAME,
        cache_dir=abs_models_dir,
    )
    
    # Test embedding to verify model works
    test_emb = list(dense.embed(["test query"]))[0]
    dense_dim = len(test_emb)
    print(f"  SUCCESS: Dense model loaded ({dense_dim} dimensions)")
    
    print(f"\n[2/2] Downloading sparse model: {SPARSE_MODEL_NAME}")
    print("  (BM25-based sparse embeddings for keyword matching)")
    
    # Download sparse model
    sparse = SparseTextEmbedding(
        model_name=SPARSE_MODEL_NAME,
        cache_dir=abs_models_dir,
    )
    
    # Test embedding to verify model works
    test_sparse = list(sparse.embed(["test query for BM25"]))[0]
    print(f"  SUCCESS: Sparse model loaded ({len(test_sparse.indices)} test indices)")
    
    return dense_dim


def list_downloaded_files():
    """List the downloaded model files."""
    print(f"\nDownloaded files in {MODELS_DIR}/:")
    for root, dirs, files in os.walk(MODELS_DIR):
        level = root.replace(MODELS_DIR, '').count(os.sep)
        indent = '  ' * level
        print(f"{indent}{os.path.basename(root)}/")
        sub_indent = '  ' * (level + 1)
        for file in files[:10]:  # Limit files shown
            filepath = os.path.join(root, file)
            size = os.path.getsize(filepath)
            size_str = f"{size / 1024 / 1024:.1f}MB" if size > 1024*1024 else f"{size / 1024:.1f}KB"
            print(f"{sub_indent}{file} ({size_str})")
        if len(files) > 10:
            print(f"{sub_indent}... and {len(files) - 10} more files")


def main():
    print("=" * 70)
    print("CBP Training Assistant - Embedding Models Downloader")
    print("=" * 70)
    
    try:
        # List supported models if requested
        if '--list' in sys.argv:
            from fastembed import TextEmbedding, SparseTextEmbedding
            print("\n--- Supported Dense Models (nomic) ---")
            for model in TextEmbedding.list_supported_models():
                if 'nomic' in model['model'].lower():
                    print(f"  {model['model']} (dim: {model.get('dim', 'N/A')}, size: {model.get('size_in_GB', 'N/A')}GB)")
            print("\n--- Supported Sparse Models ---")
            for model in SparseTextEmbedding.list_supported_models():
                print(f"  {model['model']}")
            return
        
        print(f"\nTarget directory: {os.path.abspath(MODELS_DIR)}/")
        print("-" * 50)
        
        # Clean old format models
        print("\nChecking for old model formats...")
        clean_old_models()
        
        # Download models
        dense_dim = download_models()
        
        # Show downloaded files
        list_downloaded_files()
        
        print("\n" + "=" * 70)
        print("SUCCESS! All models downloaded in FastEmbed/ONNX format.")
        print("=" * 70)
        print(f"\nConfiguration:")
        print(f"  MODELS_DIR: {os.path.abspath(MODELS_DIR)}")
        print(f"  Dense:  {DENSE_MODEL_NAME} ({dense_dim}d -> 256d MRL)")
        print(f"  Sparse: {SPARSE_MODEL_NAME}")
        print(f"\nNext steps:")
        print(f"  1. Run: docker compose up -d --build")
        print(f"  2. Access the app at: http://localhost:8080")
        
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
