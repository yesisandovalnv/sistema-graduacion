# ============================================================================
# MODO 2: PRODUCCIÓN FULL DOCKER
# ============================================================================
# Este script levanta TODO en contenedores:
# - PostgreSQL
# - Backend Django
# - Frontend React (compilado)
# - Nginx (proxy inverso)
# ============================================================================

Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Magenta
Write-Host "║           MODO 2: FULL DOCKER (Producción)                  ║" -ForegroundColor Magenta
Write-Host "║  BD: Docker | Backend: Docker | Frontend: Docker | Nginx    ║" -ForegroundColor Magenta
Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Magenta
Write-Host ""

# Paso 1: Verificar .env existe
Write-Host "📋 Verificando configuración..." -ForegroundColor Yellow
if (!(Test-Path ".env")) {
    if (Test-Path ".env.example") {
        Write-Host "  ⚠️  .env no encontrado, creando desde .env.example..." -ForegroundColor Yellow
        Copy-Item ".env.example" ".env"
        Write-Host "  ✅ .env creado" -ForegroundColor Green
    } else {
        Write-Host "  ❌ ERROR: .env.example no encontrado" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "  ✅ .env existe" -ForegroundColor Green
}

# Paso 2: Detener y eliminar contenedores previos
Write-Host ""
Write-Host "🛑 Limpiando contenedores previos..." -ForegroundColor Yellow
docker compose down --volumes --quiet 2>$null

# Paso 3: Construir imágenes (frontend + backend)
Write-Host ""
Write-Host "🔨 Construyendo imágenes Docker..." -ForegroundColor Cyan
Write-Host "  (Frontend + Backend)" -ForegroundColor Cyan
docker compose build --no-cache 2>&1 | Select-String -Pattern "Successfully|error|Error"

if ($LASTEXITCODE -ne 0) {
    Write-Host "  ❌ Error construyendo imágenes" -ForegroundColor Red
    exit 1
}
Write-Host "  ✅ Imágenes construidas" -ForegroundColor Green

# Paso 4: Levantar todo con profile prod
Write-Host ""
Write-Host "🚀 Levantando sistema completo (DB + Backend + Frontend + Nginx)..." -ForegroundColor Cyan
Write-Host "  Esto puede tomar 30-60 segundos..." -ForegroundColor Cyan
Write-Host ""

docker compose --profile prod up --wait

Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║                    ✅ SISTEMA LISTO                          ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""
Write-Host "🌐 ACCESO:" -ForegroundColor Green
Write-Host "  • Frontend: http://localhost:5173" -ForegroundColor White
Write-Host "  • Backend (Nginx): http://localhost:80" -ForegroundColor White
Write-Host "  • Backend (directo): http://localhost:8000" -ForegroundColor White
Write-Host "  • Admin Django: http://localhost:8000/admin" -ForegroundColor White
Write-Host ""
Write-Host "📊 MONITOREO:" -ForegroundColor Yellow
Write-Host "  Ver logs Backend:  docker compose logs -f backend" -ForegroundColor White
Write-Host "  Ver logs Nginx:    docker compose logs -f nginx" -ForegroundColor White
Write-Host "  Ver logs Frontend: docker compose logs -f frontend" -ForegroundColor White
Write-Host ""
Write-Host "🛑 DETENER:" -ForegroundColor Yellow
Write-Host "  Presiona Ctrl+C aquí, o ejecuta: docker compose down" -ForegroundColor White
Write-Host ""
