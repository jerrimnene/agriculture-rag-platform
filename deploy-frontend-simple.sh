#!/bin/bash

# Simple Frontend Deployment Script
# This deploys ONLY the frontend to Vercel (backend stays local)

echo "🚀 Deploying Hupfumi.Africa Frontend..."
echo ""

cd frontend

# Check if vercel is installed
if ! command -v vercel &> /dev/null; then
    echo "❌ Vercel CLI not found. Installing..."
    npm install -g vercel
fi

echo "📦 Deploying to Vercel..."
vercel --prod

echo ""
echo "✅ Frontend deployed!"
echo ""
echo "⚠️  IMPORTANT: Your backend is still running locally on http://localhost:8000"
echo "    Update API_BASE in your HTML files if you want to connect to a different backend."
echo ""
echo "📱 Access your site at the URL shown above"
