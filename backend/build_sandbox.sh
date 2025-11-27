#!/bin/bash

# ArbiterAI Docker Sandbox - Build Script

set -e

echo "🐳 Building ArbiterAI Docker Sandbox Image..."

# Navigate to backend directory
cd "$(dirname "$0")"

# Build the sandbox image
docker build -f Dockerfile.sandbox -t arbiter-sandbox:latest .

echo "✅ Sandbox image built successfully!"
echo ""
echo "📊 Image details:"
docker images | grep arbiter-sandbox

echo ""
echo "🧪 Testing sandbox..."
docker run --rm arbiter-sandbox:latest python --version
docker run --rm arbiter-sandbox:latest node --version

echo ""
echo "✅ Sandbox is ready to use!"
echo ""
echo "To enable Docker sandbox in ArbiterAI:"
echo "  export USE_DOCKER_SANDBOX=true"
echo "  python websocket_server_v2.py"
