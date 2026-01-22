#!/usr/bin/env bash
# exit on error
set -o errexit

# Check for required environment variables
if [ -z "$CONVEX_DEPLOY_KEY" ]; then
  echo "ERROR: CONVEX_DEPLOY_KEY is not set. Please add it to Render Environment Variables."
  echo "You can find it in Convex dashboard > Settings > Deployment Key."
  exit 1
fi

# --- 1. Install Root Dependencies ---
echo "Installing root dependencies..."
npm install
chmod -R +x node_modules/.bin || true

# --- 2. Build Vue Frontend ---
echo "Building Vue Frontend..."
cp .env web-frontend/.env || true
cd web-frontend
npm install
npm run build
cd ..

# --- 3. Setup Python Backend ---
echo "Installing Python dependencies..."
cd backend
pip install -r requirements.txt
cd ..

# --- 4. Deploy Convex Backend ---
echo "Deploying Convex schema and functions..."
npm run convex:deploy

echo "Build complete!"
