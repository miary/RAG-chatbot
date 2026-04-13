#!/usr/bin/env python3
"""
Download Ollama models for local deployment.

This script downloads the specified Ollama model to the 'models/ollama' directory
for offline use in Docker deployment.

Default Model: gemma3:4b

Usage:
    # Download default model (gemma3:4b)
    python download_ollama_model.py

    # Download specific model
    python download_ollama_model.py llama3.1:8b

    # List available models
    python download_ollama_model.py --list

Requirements:
    - Ollama must be installed locally: https://ollama.ai
    - Or run via Docker: docker run -d -v ./models/ollama:/root/.ollama -p 11434:11434 ollama/ollama
"""

import os
import sys
import subprocess
import shutil
import json
import urllib.request
import urllib.error

# Default model
DEFAULT_MODEL = os.environ.get('OLLAMA_MODEL', 'gemma3:4b')

# Ollama host (local or Docker)
OLLAMA_HOST = os.environ.get('OLLAMA_HOST', 'http://localhost:11434')

# Models directory
MODELS_DIR = os.environ.get('MODELS_DIR', 'models')
OLLAMA_MODELS_DIR = os.path.join(MODELS_DIR, 'ollama')


def check_ollama_running():
    """Check if Ollama server is running."""
    try:
        req = urllib.request.Request(f"{OLLAMA_HOST}/api/tags")
        with urllib.request.urlopen(req, timeout=5) as response:
            return response.status == 200
    except (urllib.error.URLError, urllib.error.HTTPError):
        return False


def start_ollama_docker():
    """Start Ollama via Docker if not running."""
    print(f"Starting Ollama via Docker...")
    os.makedirs(OLLAMA_MODELS_DIR, exist_ok=True)
    
    # Check if container already exists
    result = subprocess.run(
        ["docker", "ps", "-a", "--filter", "name=ollama-download", "--format", "{{.Names}}"],
        capture_output=True, text=True
    )
    
    if "ollama-download" in result.stdout:
        # Remove existing container
        subprocess.run(["docker", "rm", "-f", "ollama-download"], capture_output=True)
    
    # Start new container
    abs_models_dir = os.path.abspath(OLLAMA_MODELS_DIR)
    subprocess.run([
        "docker", "run", "-d",
        "--name", "ollama-download",
        "-v", f"{abs_models_dir}:/root/.ollama",
        "-p", "11434:11434",
        "ollama/ollama"
    ], check=True)
    
    print("  Waiting for Ollama to start...")
    import time
    for _ in range(30):
        if check_ollama_running():
            print("  Ollama is ready.")
            return True
        time.sleep(1)
    
    print("  ERROR: Ollama failed to start")
    return False


def pull_model(model_name):
    """Pull a model using Ollama API."""
    print(f"\nPulling model: {model_name}")
    print("  This may take several minutes depending on model size...")
    
    # Use the Ollama API to pull
    data = json.dumps({"name": model_name}).encode('utf-8')
    req = urllib.request.Request(
        f"{OLLAMA_HOST}/api/pull",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    
    try:
        with urllib.request.urlopen(req, timeout=3600) as response:
            # Stream the response
            for line in response:
                try:
                    status = json.loads(line.decode('utf-8'))
                    if 'status' in status:
                        if 'completed' in status and 'total' in status:
                            pct = (status['completed'] / status['total']) * 100
                            print(f"\r  {status['status']}: {pct:.1f}%", end='', flush=True)
                        else:
                            print(f"\r  {status['status']}", end='', flush=True)
                except json.JSONDecodeError:
                    pass
            print()  # New line after progress
        return True
    except Exception as e:
        print(f"\n  ERROR: Failed to pull model: {e}")
        return False


def list_models():
    """List available models from Ollama."""
    try:
        req = urllib.request.Request(f"{OLLAMA_HOST}/api/tags")
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            models = data.get('models', [])
            if models:
                print("\nInstalled models:")
                for model in models:
                    size_gb = model.get('size', 0) / (1024**3)
                    print(f"  - {model['name']} ({size_gb:.2f} GB)")
            else:
                print("\nNo models installed yet.")
            return models
    except Exception as e:
        print(f"ERROR: Could not list models: {e}")
        return []


def cleanup_docker():
    """Stop and remove the download container."""
    subprocess.run(["docker", "rm", "-f", "ollama-download"], capture_output=True)


def main():
    print("=" * 70)
    print("CBP Training Assistant - Ollama Model Downloader")
    print("=" * 70)
    
    # Parse arguments
    if '--list' in sys.argv:
        if not check_ollama_running():
            print("Ollama is not running. Starting via Docker...")
            if not start_ollama_docker():
                sys.exit(1)
        list_models()
        return
    
    if '--help' in sys.argv or '-h' in sys.argv:
        print(__doc__)
        return
    
    # Get model name from args or use default
    model_name = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith('-') else DEFAULT_MODEL
    
    print(f"\nModel to download: {model_name}")
    print(f"Models directory:  {os.path.abspath(OLLAMA_MODELS_DIR)}")
    print("-" * 50)
    
    # Create models directory
    os.makedirs(OLLAMA_MODELS_DIR, exist_ok=True)
    
    # Check if Ollama is running
    use_docker = False
    if not check_ollama_running():
        print("\nOllama is not running locally.")
        print("Attempting to start via Docker...")
        if not start_ollama_docker():
            print("\nERROR: Could not start Ollama.")
            print("Please install Ollama from https://ollama.ai or ensure Docker is running.")
            sys.exit(1)
        use_docker = True
    else:
        print("\nOllama server detected at", OLLAMA_HOST)
    
    # Pull the model
    success = pull_model(model_name)
    
    # List installed models
    list_models()
    
    # Cleanup if we started Docker
    if use_docker:
        print("\nStopping temporary Docker container...")
        cleanup_docker()
    
    if success:
        print("\n" + "=" * 70)
        print("SUCCESS! Model downloaded.")
        print("=" * 70)
        print(f"\nModel location: {os.path.abspath(OLLAMA_MODELS_DIR)}/")
        print(f"\nThe model will be automatically loaded when you run:")
        print("  docker compose up -d --build")
    else:
        print("\n" + "=" * 70)
        print("FAILED to download model.")
        print("=" * 70)
        sys.exit(1)


if __name__ == '__main__':
    main()
