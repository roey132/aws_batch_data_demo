#!/bin/bash

# Exit if any command fails
set -e

echo "🔧 Creating build directory..."
rm -rf lambda_transform_build
mkdir lambda_transform_build

echo "📦 Installing dependencies..."
pip install pandas pyarrow -t lambda_transform_build/

echo "📁 Copying transform.py..."
cp ingestion/transform.py lambda_transform_build/

echo "🗜️ Zipping Lambda package..."
cd lambda_transform_build
zip -r ../transform_lambda.zip .
cd ..

echo "✅ Build complete: transform_lambda.zip"
