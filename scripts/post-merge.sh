#!/bin/bash
set -e

echo "=== Post-merge setup ==="

# Sync Python dependencies from pyproject.toml
echo "Installing Python dependencies..."
uv sync --frozen 2>/dev/null || uv sync

echo "=== Post-merge complete ==="
