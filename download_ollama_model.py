#!/usr/bin/env python3
"""
Download Ollama models for local deployment.

This script downloads the specified Ollama model to the 'models/ollama' directory
for offline use in Docker deployment.

Default Model: gemma4:latest

Usage:
    # Download default model (gemma4:latest)
    python download_ollama_model.py

    # Download specific model
    python download_ollama_model.py llama3.1:8b

Requirements:
    - Docker must be installed and running
"""

import os
import sys
import subprocess
import time

# Default model
DEFAULT_MODEL = os.environ.get('OLLAMA_MODEL', 'gemma4:latest')

# Models directory
MODELS_DIR = os.environ.get('MODELS_DIR', 'models')
OLLAMA_MODELS_DIR = os.path.join(MODELS_DIR, 'ollama')

CONTAINER_NAME = "ollama-model-download"


def run_command(cmd, check=True, capture=False):
    """Run a shell command."""
    print(f"  Running: {' '.join(cmd)}")
    if capture:
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result
    else:
        result = subprocess.run(cmd)
        if check and result.returncode != 0:
            raise Exception(f"Command failed with code {result.returncode}")
        return result


def cleanup_container():
    """Remove existing download container if it exists."""
    subprocess.run(
        ["docker", "rm", "-f", CONTAINER_NAME],
        capture_output=True
    )


def start_ollama_container(models_path):
    """Start Ollama container with volume mount."""
    print(f"\nStarting Ollama container...")
    print(f"  Models will be saved to: {models_path}")
    
    cleanup_container()
    
    # Start Ollama container
    run_command([
        "docker", "run", "-d",
        "--name", CONTAINER_NAME,
        "-v", f"{models_path}:/root/.ollama",
        "ollama/ollama"
    ])
    
    # Wait for Ollama to be ready
    print("  Waiting for Ollama to start...")
    for i in range(60):
        result = subprocess.run(
            ["docker", "exec", CONTAINER_NAME, "ollama", "list"],
            capture_output=True
        )
        if result.returncode == 0:
            print("  Ollama is ready.")
            return True
        time.sleep(1)
        if i % 10 == 9:
            print(f"  Still waiting... ({i+1}s)")
    
    print("  ERROR: Ollama failed to start")
    return False


def pull_model(model_name):
    """Pull model using docker exec."""
    print(f"\nPulling model: {model_name}")
    print("  This may take several minutes depending on model size...")
    print("-" * 50)
    
    # Use docker exec to run ollama pull
    result = subprocess.run(
        ["docker", "exec", CONTAINER_NAME, "ollama", "pull", model_name],
    )
    
    return result.returncode == 0


def list_models():
    """List downloaded models."""
    print("\nInstalled models:")
    subprocess.run(
        ["docker", "exec", CONTAINER_NAME, "ollama", "list"],
    )


def verify_download(models_path):
    """Verify that model files were downloaded."""
    print(f"\nVerifying download in {models_path}...")
    
    # Check for model files
    blobs_path = os.path.join(models_path, "models", "blobs")
    manifests_path = os.path.join(models_path, "models", "manifests")
    
    has_blobs = os.path.exists(blobs_path) and os.listdir(blobs_path)
    has_manifests = os.path.exists(manifests_path)
    
    if has_blobs:
        blob_files = os.listdir(blobs_path)
        total_size = sum(
            os.path.getsize(os.path.join(blobs_path, f)) 
            for f in blob_files 
            if os.path.isfile(os.path.join(blobs_path, f))
        )
        print(f"  Found {len(blob_files)} blob files ({total_size / (1024**3):.2f} GB)")
        return True
    else:
        print("  WARNING: No model files found!")
        return False


def main():
    print("=" * 70)
    print("CBP Training Assistant - Ollama Model Downloader")
    print("=" * 70)
    
    # Parse arguments
    if '--help' in sys.argv or '-h' in sys.argv:
        print(__doc__)
        return
    
    # Get model name from args or use default
    model_name = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith('-') else DEFAULT_MODEL
    
    # Create absolute path for models directory
    abs_models_path = os.path.abspath(OLLAMA_MODELS_DIR)
    os.makedirs(abs_models_path, exist_ok=True)
    
    print(f"\nModel to download: {model_name}")
    print(f"Models directory:  {abs_models_path}")
    
    try:
        # Start Ollama container
        if not start_ollama_container(abs_models_path):
            print("\nERROR: Failed to start Ollama container")
            print("Make sure Docker is installed and running.")
            sys.exit(1)
        
        # Pull the model
        success = pull_model(model_name)
        
        if success:
            # List models to confirm
            list_models()
            
            # Verify files exist
            verify_download(abs_models_path)
            
            print("\n" + "=" * 70)
            print("SUCCESS! Model downloaded.")
            print("=" * 70)
            print(f"\nModel files saved to: {abs_models_path}/")
            print(f"\nTo use with Docker Compose:")
            print("  docker compose up -d --build")
        else:
            print("\n" + "=" * 70)
            print("FAILED to download model.")
            print("=" * 70)
            print("\nCheck if the model name is correct: " + model_name)
            print("You can browse available models at: https://ollama.com/library")
            sys.exit(1)
            
    finally:
        # Always cleanup
        print("\nCleaning up temporary container...")
        cleanup_container()


if __name__ == '__main__':
    main()
