#!/usr/bin/env python3
"""
Download embedding models for local deployment.

This script downloads both dense and sparse models to the 'models' directory
for offline use in Docker deployment.

Dense Model: all-MiniLM-L6-v2 (384 dimensions, supports MRL truncation to 256)
Sparse Model: naver/splade-cocondenser-ensembledistil (for hybrid search)

Usage:
    python download_models.py

The models will be saved to:
    - models/dense/
    - models/sparse/
"""

import os
import sys

def download_dense_model():
    """Download the dense embedding model."""
    from sentence_transformers import SentenceTransformer
    
    model_name = os.environ.get('DENSE_MODEL_NAME', 'all-MiniLM-L6-v2')
    output_path = os.environ.get('DENSE_MODEL_PATH', 'models/dense')
    
    print(f"Downloading dense model: {model_name}")
    model = SentenceTransformer(model_name)
    
    print(f"Saving to: {output_path}")
    model.save(output_path)
    
    print(f"Dense model saved. Dimensions: {model.get_sentence_embedding_dimension()}")
    return model.get_sentence_embedding_dimension()


def download_sparse_model():
    """Download the sparse embedding model (SPLADE)."""
    from transformers import AutoModelForMaskedLM, AutoTokenizer
    
    model_name = os.environ.get('SPARSE_MODEL_NAME', 'naver/splade-cocondenser-ensembledistil')
    output_path = os.environ.get('SPARSE_MODEL_PATH', 'models/sparse')
    
    print(f"Downloading sparse model: {model_name}")
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForMaskedLM.from_pretrained(model_name)
    
    print(f"Saving to: {output_path}")
    tokenizer.save_pretrained(output_path)
    model.save_pretrained(output_path)
    
    print("Sparse model (SPLADE) saved successfully.")


def main():
    print("=" * 60)
    print("FRDS Embedding Models Downloader")
    print("=" * 60)
    
    # Create output directories
    os.makedirs('models/dense', exist_ok=True)
    os.makedirs('models/sparse', exist_ok=True)
    
    try:
        # Download dense model
        print("\n[1/2] Downloading Dense Embedding Model...")
        dense_dim = download_dense_model()
        
        # Download sparse model
        print("\n[2/2] Downloading Sparse Embedding Model (SPLADE)...")
        download_sparse_model()
        
        print("\n" + "=" * 60)
        print("SUCCESS! All models downloaded.")
        print("=" * 60)
        print(f"\nModel locations:")
        print(f"  Dense:  models/dense/  (dim: {dense_dim})")
        print(f"  Sparse: models/sparse/")
        print(f"\nNext steps:")
        print(f"  1. Copy 'models' directory to your deployment environment")
        print(f"  2. Set MODELS_DIR=/path/to/models in your environment")
        print(f"  3. Run docker-compose up")
        
    except Exception as e:
        print(f"\nERROR: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
