#!/bin/bash
# Quick Start Script for Product Importer

echo "🚀 Product Importer - Quick Start"
echo "=================================="
echo ""

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first:"
    echo "   https://docs.docker.com/get-docker/"
    exit 1
fi

echo "✅ Docker found"

# Check Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first:"
    echo "   https://docs.docker.com/compose/install/"
    exit 1
fi

echo "✅ Docker Compose found"
echo ""

# Start services
echo "Starting services with Docker Compose..."
docker-compose up -d

echo ""
echo "⏳ Waiting for services to start (30 seconds)..."
sleep 30

# Check if services are running
echo ""
echo "Checking services..."

if ! docker-compose ps | grep -q "postgres.*healthy"; then
    echo "⚠️  PostgreSQL still starting, waiting 30 more seconds..."
    sleep 30
fi

if ! docker-compose ps | grep -q "redis.*healthy"; then
    echo "⚠️  Redis still starting, waiting 30 more seconds..."
    sleep 30
fi

echo ""
echo "✅ Services started successfully!"
echo ""
echo "📍 Access the application:"
echo "   Web UI:      http://localhost:8000/static/index.html"
echo "   API Docs:    http://localhost:8000/docs"
echo "   Health:      http://localhost:8000/health"
echo ""
echo "📊 Services running:"
echo "   API (FastAPI):  http://localhost:8000"
echo "   Database:       postgres://localhost:5432"
echo "   Redis:          redis://localhost:6379"
echo ""
echo "📖 View logs:"
echo "   docker-compose logs -f api       # API server"
echo "   docker-compose logs -f celery    # Background worker"
echo "   docker-compose logs -f postgres  # Database"
echo ""
echo "🛑 Stop services:"
echo "   docker-compose down"
echo ""
echo "🗑️  Remove all data:"
echo "   docker-compose down -v"
echo ""
