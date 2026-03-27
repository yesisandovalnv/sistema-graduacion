# ============================================================================
# MODO 1: DESARROLLO (BD + Backend en Docker, Frontend local con hot-reload)
# ============================================================================
# Este script levanta PostgreSQL y Backend en Docker
# El Frontend se ejecuta localmente con "npm run dev"
# ============================================================================

Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║           MODO 1: DESARROLLO (Local + Docker)               ║" -ForegroundColor Cyan
Write-Host "║  Backend: Docker | BD: Docker | Frontend: Tu máquina        ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Paso 1: Verificar .env existe
Write-Host "📋 Verificando configuración..." -ForegroundColor Yellow
if (!(Test-Path ".env")) {
    if (Test-Path ".env.example") {
        Write-Host "  ⚠️  .env no encontrado, creando desde .env.example..." -ForegroundColor Yellow
        Copy-Item ".env.example" ".env"
        Write-Host "  ✅ .env creado" -ForegroundColor Green
    } else {
        Write-Host "  ❌ ERROR: .env.example no encontrado en $(Get-Location)" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "  ✅ .env existe" -ForegroundColor Green
}

# Paso 2: Detener contenedores previos
Write-Host ""
Write-Host "🛑 Deteniendo contenedores previos..." -ForegroundColor Yellow
docker compose down --quiet 2>$null

# Paso 3: Levantar DB y Backend
Write-Host ""
Write-Host "🚀 Levantando PostgreSQL + Backend..." -ForegroundColor Cyan
docker compose up db backend

# Si el usuario presiona Ctrl+C
Write-Host ""
Write-Host "⚠️  Backend detenido" -ForegroundColor Yellow
Write-Host ""
Write-Host "Para detener completamente, ejecuta:" -ForegroundColor Yellow
Write-Host "  docker compose down" -ForegroundColor White
Write-Host ""
Write-Host "Para iniciar el Frontend en otra terminal, ejecuta:" -ForegroundColor Yellow
Write-Host "  cd frontend && npm install && npm run dev" -ForegroundColor White
