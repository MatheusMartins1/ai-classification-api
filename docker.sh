#!/bin/bash
# Docker management script for Image Metadata API
# Developer: Matheus Martins da Silva
# Creation Date: 11/2025
# ./docker.sh start
# ./docker.sh stop
# ./docker.sh restart
# ./docker.sh logs
# ./docker.sh build
# ./docker.sh status
# ./docker.sh clean
# ./docker.sh usage
# ./docker.sh end

set -e

case "$1" in
    start)
        echo "[+] Starting Image Metadata API..."
        if [ ! -f .env ]; then
            echo "[!] No .env found. Available: .env.dev, .env.homol, .env.prod"
            echo "[!] Copy one to .env or create from .env.dev"
            if [ -f .env.dev ]; then
                cp .env.dev .env
                echo "[✓] Created .env from .env.dev"
            else
                echo "[X] Error: No .env.dev found"
                exit 1
            fi
        fi
        docker-compose up -d
        echo "[✓] Container started successfully"
        echo "[i] Use './docker.sh logs' to view logs"
        ;;
    
    stop)
        echo "[+] Stopping Image Metadata API..."
        docker-compose down
        echo "[✓] Container stopped successfully"
        ;;
    
    restart)
        echo "[+] Restarting Image Metadata API..."
        docker-compose restart
        echo "[✓] Container restarted successfully"
        ;;
    
    logs)
        echo "[+] Showing logs (Ctrl+C to exit)..."
        docker-compose logs -f
        ;;
    
    build)
        echo "[+] Building Image Metadata API..."
        docker-compose build --no-cache
        echo "[✓] Build completed successfully"
        ;;
    
    status)
        echo "[+] Container status:"
        docker-compose ps
        echo ""
        echo "[+] Docker images:"
        docker images | grep "ai-regression-api" || echo "No images found"
        ;;
    
    clean)
        echo "[+] Cleaning up containers, images and volumes..."
        docker-compose down -v
        docker rmi ai-regression-api_api 2>/dev/null || true
        echo "[✓] Cleanup completed"
        ;;
    
    *)
        echo ""
        echo "Docker Management Script - Image Metadata API"
        echo ""
        echo "./docker.sh [command]"
        echo ""
        echo "Commands:"
        echo "  start    - Start containers"
        echo "  stop     - Stop containers"
        echo "  restart  - Restart containers"
        echo "  logs     - Show container logs"
        echo "  build    - Rebuild containers"
        echo "  status   - Show container status"
        echo "  clean    - Remove containers, images and volumes"
        echo ""
        exit 1
        ;;
esac

