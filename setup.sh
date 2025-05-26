#!/bin/bash

echo "Setting up Conda env for FairFare..."

conda env create -f environment.yml
conda activate fairfare

echo "Installing dependencies with Poetry..."
poetry install

echo "Installing pre-commit hooks..."
pre-commit install

echo "FairFare environment and pre-commit hooks setup complete."
