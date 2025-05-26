#!/bin/bash

set -e  # Exit immediately if a command exits with a non-zero status

echo "Setting up Conda env for FairFare..."

# Make sure conda is available
if ! command -v conda &> /dev/null; then
    echo "conda command not found. Please initialize Conda first."
    exit 1
fi

# Source conda into this shell session
eval "$(conda shell.bash hook)"

# Create env only if it doesn't exist
if conda info --envs | grep -q "^fairfare"; then
    echo "Conda env 'fairfare' already exists. Skipping creation."
else
    conda env create -f environment.yml
fi

# Activate the environment
conda activate fairfare

echo "Installing dependencies with Poetry..."
poetry install

echo "Installing pre-commit hooks..."
pre-commit install

echo "✅ FairFare environment and pre-commit hooks setup complete."
