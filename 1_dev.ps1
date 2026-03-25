# ============================================================================
# MODO 1: DESARROLLO - BD + Backend en Docker, Frontend Local
# ============================================================================

Write-Host ""
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "         MODO 1: DESARROLLO (Local + Docker)" -ForegroundColor Cyan
Write-Host "   Backend: Docker | BD: Docker | Frontend: Tu maquina" -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""

try {
    # Verificar .env
    Write-Host "[*] Verificando configuracion..." -ForegroundColor Yellow
    if (!(Test-Path ".env")) {
        if (Test-Path ".env.example") {
            Write-Host "  Creando .env desde .env.example..." -ForegroundColor Yellow
            Copy-Item ".env.example" ".env"
            Write-Host "  OK - .env creado" -ForegroundColor Green
        } else {
            throw ".env.example no encontrado"
        }
    } else {
        Write-Host "  OK - .env existe" -ForegroundColor Green
    }
    
    # Detener previos
    Write-Host ""
    Write-Host "[*] Limpiando contenedores previos..." -ForegroundColor Yellow
    docker compose down --quiet 2>$null
    Start-Sleep -Seconds 1
    
    # Levantar BD y Backend
    Write-Host ""
    Write-Host "[*] Levantando PostgreSQL + Backend..." -ForegroundColor Cyan
    docker compose up db backend
    
} catch {
    Write-Host ""
    Write-Host "[ERROR] $_" -ForegroundColor Red
    docker compose down --quiet 2>$null
    exit 1
}

Write-Host ""
Write-Host "[*] Backend detenido" -ForegroundColor Yellow
Write-Host ""
Write-Host "Para continuar, abre otra terminal y ejecuta:" -ForegroundColor Yellow
Write-Host "  cd frontend && npm install && npm run dev" -ForegroundColor White
Write-Host ""

