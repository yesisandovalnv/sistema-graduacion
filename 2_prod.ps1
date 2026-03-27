# ============================================================================
# MODO 2: PRODUCCIÓN - Docker Backend + Nginx (Frontend con npm run dev)
# ============================================================================

Write-Host ""
Write-Host "========================================================" -ForegroundColor Magenta
Write-Host "  [DOCKER] MODO 2: PRODUCCIÓN" -ForegroundColor Magenta
Write-Host "  DB + Backend + Nginx (Frontend en npm run dev)" -ForegroundColor Magenta
Write-Host "========================================================" -ForegroundColor Magenta
Write-Host ""

try {
    # Verificar .env
    Write-Host "[LOG] Verificando configuración..." -ForegroundColor Yellow
    if (!(Test-Path ".env")) {
        if (Test-Path ".env.example") {
            Write-Host "  [WARNING] .env no encontrado, creando desde .env.example..." -ForegroundColor Yellow
            Copy-Item ".env.example" ".env"
            Write-Host "  [OK] .env creado" -ForegroundColor Green
        } else {
            throw ".env.example no encontrado"
        }
    } else {
        Write-Host "  [OK] .env existe" -ForegroundColor Green
    }
    
    # Detener contenedores SIN borrar datos
    Write-Host ""
    Write-Host "[LOG] Deteniendo contenedores (sin borrar datos)..." -ForegroundColor Yellow
    docker compose down --quiet 2>$null
    Start-Sleep -Seconds 1
    
    # Reconstruir SOLO backend
    Write-Host ""
    Write-Host "[LOG] Reconstruyendo imagen backend..." -ForegroundColor Cyan
    docker compose build --no-cache backend 2>&1
    
    if ($LASTEXITCODE -ne 0) {
        throw "Build falló"
    }
    
    # Levantar todos los servicios en segundo plano
    Write-Host ""
    Write-Host "[LOG] Levantando servicios (DB, Backend, Nginx)..." -ForegroundColor Cyan
    docker compose up -d --quiet
    Start-Sleep -Seconds 2
    
    # Mostrar estado
    Write-Host ""
    Write-Host "[LOG] Estado de servicios:" -ForegroundColor Cyan
    docker compose ps
    
    Write-Host ""
    Write-Host "[OK] Sistema en producción listo" -ForegroundColor Green
    Write-Host "  Frontend: npm run dev (en local, puerto 5173)" -ForegroundColor Gray
    Write-Host "  Backend:  http://localhost:8000" -ForegroundColor Gray
    Write-Host "  Nginx:    http://localhost (puerto 80)" -ForegroundColor Gray
    Write-Host ""
    
} catch {
    Write-Host ""
    Write-Host "[ERROR] $_" -ForegroundColor Red
    docker compose down --quiet 2>$null
    exit 1
}

Write-Host "[LOG] Próximos pasos:" -ForegroundColor Cyan
Write-Host "  1. npm run dev   (en carpeta frontend/ con otra terminal)" -ForegroundColor Gray
Write-Host "  2. Acceder a: http://localhost:5173 o http://localhost:80" -ForegroundColor Gray
Write-Host ""

