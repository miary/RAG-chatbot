#!/usr/bin/env python3
"""
Download embedding models for local deployment using Qdrant FastEmbed.

This script downloads both dense and sparse models to the 'models' directory
for offline use in Docker deployment.

Dense Model: nomic-ai/nomic-embed-text-v1.5 (768 dimensions, MRL-trained, truncated to 256)
Sparse Model: Qdrant/bm25 (BM25-based sparse embeddings)

Usage:
    pip install fastembed
    python download_models.py

The models will be saved to:
    - models/  (FastEmbed cache structure)
"""

import os
import sys

# Models directory - this will be the FastEmbed cache directory
MODELS_DIR = os.environ.get('MODELS_DIR', 'models')

# Model names - using the standard (non-quantized) version for better compatibility
DENSE_MODEL_NAME = os.environ.get('DENSE_MODEL_NAME', 'nomic-ai/nomic-embed-text-v1.5')
SPARSE_MODEL_NAME = os.environ.get('SPARSE_MODEL_NAME', 'Qdrant/bm25')


def download_models():
    """Download both dense and sparse embedding models using FastEmbed."""
    from fastembed import TextEmbedding, SparseTextEmbedding
    
    # Create the models directory
    os.makedirs(MODELS_DIR, exist_ok=True)
    
    print(f"Downloading dense model: {DENSE_MODEL_NAME}")
    print("  (nomic-embed-text with MRL support)")
    print("  (768-dimensional vectors, truncatable to 256)")
    
    # Download dense model - FastEmbed will cache it in MODELS_DIR
    dense = TextEmbedding(
        model_name=DENSE_MODEL_NAME,
        cache_dir=MODELS_DIR,
    )
    
    # Test embedding to verify model works
    test_emb = list(dense.embed(["test"]))[0]
    dense_dim = len(test_emb)
    print(f"  Dense model loaded: {dense_dim} dimensions")
    
    print(f"\nDownloading sparse model: {SPARSE_MODEL_NAME}")
    print("  (BM25-based sparse embeddings for keyword matching)")
    
    # Download sparse model
    sparse = SparseTextEmbedding(
        model_name=SPARSE_MODEL_NAME,
        cache_dir=MODELS_DIR,
    )
    
    # Test embedding to verify model works
    test_sparse = list(sparse.embed(["test query"]))[0]
    print(f"  Sparse model loaded: {len(test_sparse.indices)} test indices")
    
    return dense_dim


def list_supported_models():
    """List all supported models in FastEmbed."""
    from fastembed import TextEmbedding, SparseTextEmbedding
    
    print("\n--- Supported Dense Models ---")
    for model in TextEmbedding.list_supported_models():
        if 'nomic' in model['model'].lower():
            print(f"  {model['model']} (dim: {model.get('dim', 'N/A')}, size: {model.get('size_in_GB', 'N/A')}GB)")
    
    print("\n--- Supported Sparse Models ---")
    for model in SparseTextEmbedding.list_supported_models():
        print(f"  {model['model']}")


def main():
    print("=" * 70)
    print("CBP Training Assistant - Embedding Models Downloader")
    print("=" * 70)
    
    try:
        # Optionally list supported models
        if '--list' in sys.argv:
            list_supported_models()
            return
        
        # Download models
        print(f"\nDownloading models to: {os.path.abspath(MODELS_DIR)}/")
        print("-" * 50)
        dense_dim = download_models()
        
        print("\n" + "=" * 70)
        print("SUCCESS! All models downloaded.")
        print("=" * 70)
        print(f"\nModel locations:")
        print(f"  Cache directory: {os.path.abspath(MODELS_DIR)}/")
        print(f"  Dense:  {DENSE_MODEL_NAME} ({dense_dim}d -> 256d MRL)")
        print(f"  Sparse: {SPARSE_MODEL_NAME}")
        print(f"\nMatryoshka Representation Learning (MRL):")
        print(f"  - nomic-embed-text is trained with MRL")
        print(f"  - Full dimension: {dense_dim}")
        print(f"  - Truncated to: 256 (first 256 dims preserve semantics)")
        print(f"\nBM25 Sparse Embeddings:")
        print(f"  - Fast keyword-based matching")
        print(f"  - Hybrid search with dense vectors for best results")
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
