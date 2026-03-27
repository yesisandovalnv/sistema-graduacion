# ============================================================================
# MENÚ PRINCIPAL - Sistema de Graduación
# ============================================================================

Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║              🎓 SISTEMA DE GRADUACIÓN - LAUNCHER            ║" -ForegroundColor Cyan
Write-Host "║                   v1.0 - Producción Ready                     ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

Write-Host "¿Qué deseas hacer?" -ForegroundColor Yellow
Write-Host ""
Write-Host "  [1] 💻  MODO DESARROLLO" -ForegroundColor Green
Write-Host "      Frontend con hot-reload | Backend en Docker | BD en Docker" -ForegroundColor Gray
Write-Host "      → Mejor para programar" -ForegroundColor Gray
Write-Host ""
Write-Host "  [2] 🐳 MODO PRODUCCIÓN" -ForegroundColor Magenta
Write-Host "      TODO en Docker (Frontend + Backend + BD + Nginx)" -ForegroundColor Gray
Write-Host "      → Mejor para testing/demostración" -ForegroundColor Gray
Write-Host ""
Write-Host "  [3] ✓  VALIDAR SISTEMA" -ForegroundColor Cyan
Write-Host "      Prueba todos los endpoints y servicios" -ForegroundColor Gray
Write-Host "      → Usar después de iniciar cualquier modo" -ForegroundColor Gray
Write-Host ""
Write-Host "  [4] 🛑 DETENER TODO" -ForegroundColor Red
Write-Host "      Apaga todos los contenedores" -ForegroundColor Gray
Write-Host ""
Write-Host "  [5] 📖 VER DOCUMENTACIÓN" -ForegroundColor Blue
Write-Host "      Guías detalladas y troubleshooting" -ForegroundColor Gray
Write-Host ""

$choice = Read-Host "Elige opción [1-5]"

switch ($choice) {
    "1" {
        Write-Host ""
        Write-Host "▶️  Iniciando MODO DESARROLLO..." -ForegroundColor Green
        Write-Host ""
        & ".\1_dev.ps1"
    }
    "2" {
        Write-Host ""
        Write-Host "▶️  Iniciando MODO PRODUCCIÓN..." -ForegroundColor Magenta
        Write-Host ""
        & ".\2_prod.ps1"
    }
    "3" {
        Write-Host ""
        Write-Host "▶️  Validando sistema..." -ForegroundColor Cyan
        Write-Host ""
        & ".\3_validate.ps1" -Mode "both"
    }
    "4" {
        Write-Host ""
        Write-Host "▶️  Deteniendo sistema..." -ForegroundColor Red
        Write-Host ""
        docker compose down --volumes
        Write-Host ""
        Write-Host "✅ Sistema detenido" -ForegroundColor Green
    }
    "5" {
        Write-Host ""
        Write-Host "📖 Documentación disponible:" -ForegroundColor Blue
        Write-Host ""
        Write-Host "  • MODOS_EJECUCION.md      - Guía completa" -ForegroundColor White
        Write-Host "  • GUIA_RAPIDA_VISUAL.md   - Tutorial visual" -ForegroundColor White
        Write-Host "  • COMIENZA_AQUI.txt       - Quick start" -ForegroundColor White
        Write-Host ""
        $openDocs = Read-Host "¿Deseas abrir MODOS_EJECUCION.md? (S/N)"
        
        if ($openDocs -eq "S" -or $openDocs -eq "s") {
            Start-Process "notepad" "$PWD\MODOS_EJECUCION.md"
        }
    }
    default {
        Write-Host ""
        Write-Host "❌ Opción inválida. Intenta de nuevo." -ForegroundColor Red
    }
}

