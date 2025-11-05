@echo off
REM Docker management script for Image Metadata API
REM Developer: Matheus Martins da Silva
REM Creation Date: 11/2025
REM docker.bat start
REM docker.bat stop
REM docker.bat restart
REM docker.bat logs
REM docker.bat build
REM docker.bat status
REM docker.bat clean
REM docker.bat usage
REM docker.bat end

if "%1"=="" goto usage

if "%1"=="start" goto start
if "%1"=="stop" goto stop
if "%1"=="restart" goto restart
if "%1"=="logs" goto logs
if "%1"=="build" goto build
if "%1"=="status" goto status
if "%1"=="clean" goto clean
goto usage

:start
echo [+] Starting Image Metadata API...
if not exist .env (
    echo [!] No .env found. Available: .env.dev, .env.homol, .env.prod
    echo [!] Copy one to .env or create from .env.dev
    if exist .env.dev (
        copy .env.dev .env
        echo [✓] Created .env from .env.dev
    ) else (
        echo [X] Error: No .env.dev found
        goto end
    )
)
docker-compose up -d
echo [✓] Container started successfully
echo [i] Use 'docker.bat logs' to view logs
goto end

:stop
echo [+] Stopping Image Metadata API...
docker-compose down
echo [✓] Container stopped successfully
goto end

:restart
echo [+] Restarting Image Metadata API...
docker-compose restart
echo [✓] Container restarted successfully
goto end

:logs
echo [+] Showing logs (Ctrl+C to exit)...
docker-compose logs -f
goto end

:build
echo [+] Building Image Metadata API...
docker-compose build --no-cache
echo [✓] Build completed successfully
goto end

:status
echo [+] Container status:
docker-compose ps
echo.
echo [+] Docker images:
docker images | findstr "ai-regression-api"
goto end

:clean
echo [+] Cleaning up containers, images and volumes...
docker-compose down -v
docker rmi ai-regression-api_api 2>nul
echo [✓] Cleanup completed
goto end

:usage
echo.
echo Docker Management Script - Image Metadata API
echo.
echo Usage: docker.bat [command]
echo.
echo Commands:
echo   start    - Start containers
echo   stop     - Stop containers
echo   restart  - Restart containers
echo   logs     - Show container logs
echo   build    - Rebuild containers
echo   status   - Show container status
echo   clean    - Remove containers, images and volumes
echo.
goto end

:end

