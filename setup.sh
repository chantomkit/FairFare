#!/bin/bash

# This script sets up the development environment for the FairFare project.

# Step 1: Install the conda environment from environment.yml
# This command creates or updates a conda environment named "FairFare"
# using the dependencies specified in the environment.yml file.
conda env create -f environment.yml

# Step 2: Activate the conda environment
# This command activates the newly created or updated "FairFare" environment.
# It's important to activate the environment before installing pre-commit hooks
# to ensure the pre-commit tool is installed within the correct environment.
# Note: Depending on your conda setup, you might need to use `conda activate` directly.
# If the script is run non-interactively, you might need to source the conda initialization script first.
# For interactive use, 'conda activate' is usually sufficient after initialization.
source $(conda info --base)/etc/profile.d/conda.sh
conda activate FairFare

# Step 3: Install pre-commit hooks
# This command installs the pre-commit hooks defined in the .pre-commit-config.yaml file
# into the Git repository's .git/hooks directory. This ensures that the hooks
# run automatically before each commit.
pre-commit install

# Step 4: Deactivate the conda environment (optional but good practice)
# After installing the hooks, you can deactivate the environment if you are done
# with this script and don't need the environment active for other tasks.
# conda deactivate

echo "FairFare environment and pre-commit hooks setup complete."
