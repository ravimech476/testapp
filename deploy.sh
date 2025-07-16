#!/bin/bash

# Automobile Safety Management System - Ubuntu Deployment Script
echo "🚀 Starting deployment of Automobile Safety Management System..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Create virtual environment
echo -e "${YELLOW}📦 Creating virtual environment...${NC}"
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo -e "${YELLOW}📥 Installing dependencies...${NC}"
pip install --upgrade pip
pip install -r requirements.txt

# Create necessary directories
echo -e "${YELLOW}📁 Creating directories...${NC}"
mkdir -p uploads logs

# Set permissions
chmod 755 uploads
chmod 755 logs

# Test the application
echo -e "${YELLOW}🧪 Testing application...${NC}"
python -c "from main import app; print('✅ Application imports successful')"

# Install PM2 if not exists
if ! command -v pm2 &> /dev/null; then
    echo -e "${YELLOW}📦 Installing PM2...${NC}"
    npm install -g pm2
fi

echo -e "${GREEN}✅ Setup complete! Ready to deploy with PM2${NC}"
echo -e "${GREEN}Run: pm2 start ecosystem.config.js${NC}"
echo -e "${GREEN}Then: pm2 save && pm2 startup${NC}"
