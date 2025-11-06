#!/bin/bash

set -e

# Get the project root directory (parent of scripts/)
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
echo "PROJECT_DIR:${PROJECT_DIR}"

# Extract mlflow version from pyproject.toml
MLFLOW_VERSION=$(grep -A 1 '\[project.optional-dependencies\]' "$PROJECT_DIR/pyproject.toml" | \
                 grep 'mlflow==' | \
                 sed -E 's/.*mlflow==([0-9.]+).*/\1/')

if [ -z "$MLFLOW_VERSION" ]; then
    echo "Failed to extract MLflow version from pyproject.toml"
    exit 1
fi

echo "Building Docker image with MLflow version: $MLFLOW_VERSION"

# Build the image
docker build \
    --build-arg MLFLOW_VERSION="$MLFLOW_VERSION" \
    -t mlflow_global_setup:latest \
    "$PROJECT_DIR"

echo "Image 'mlflow_global_setup:latest' built successfully with MLflow $MLFLOW_VERSION"
