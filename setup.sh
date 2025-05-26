#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

echo "Setting up FairFare project with Poetry..."

# Step 1: Install dependencies using Poetry
# This command reads the pyproject.toml file and installs all the dependencies
# including the main and development dependencies.
echo "Installing dependencies with Poetry..."
poetry install

# Step 2: Install pre-commit hooks
# This command installs the pre-commit hooks defined in the .pre-commit-config.yaml file
# into the Git repository's .git/hooks directory. This ensures that the hooks
# run automatically before each commit.
echo "Installing pre-commit hooks..."
pre-commit install

echo "FairFare environment and pre-commit hooks setup complete."
