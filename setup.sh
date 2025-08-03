#!/bin/bash

echo "🚀 Setting up Code Review Analyzer..."

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Check for security vulnerabilities in dependencies
echo "🔍 Scanning for security vulnerabilities..."
pip install pip-audit
pip-audit --desc

# Copy environment file
if [ ! -f .env ]; then
    echo "⚙️ Creating .env file from template..."
    cp .env.example .env
    echo "✏️ Please edit .env file with your configuration"
fi

# Create temp directory
echo "📁 Creating temporary directories..."
mkdir -p /tmp/code_analyzer

echo "✅ Setup complete!"
echo ""
echo "🔧 Optional development setup:"
echo "  pip install -r requirements-dev.txt"
echo "  pre-commit install"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your configuration"
echo "2. Start Redis: docker-compose up -d redis"
echo "3. Run the server: ./run_dev.py"
echo ""
echo "📊 Endpoints:"
echo "  API: http://localhost:8000"
echo "  Docs: http://localhost:8000/docs"
echo "  Health: http://localhost:8000/health"
