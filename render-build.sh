#!/usr/bin/env bash
# Exit on error
set -o errexit

# Build Frontend
echo "Building Frontend..."
cd laptop-matchmaker/frontend
npm install
npm run build
cd ../..

# Install Backend Dependencies
echo "Installing Backend Dependencies..."
cd laptop-matchmaker/backend
pip install -r requirements.txt
cd ../..

echo "Build Complete!"
