# ============================================================================
# SCRIPT AUXILIAR: Detener el sistema completamente
# ============================================================================

Write-Host "🛑 Deteniendo sistema..." -ForegroundColor Yellow
Write-Host ""

docker compose down --volumes

Write-Host ""
Write-Host "✅ Sistema detenido" -ForegroundColor Green
Write-Host ""
Write-Host "Para volver a iniciar:" -ForegroundColor Yellow
Write-Host "  • Modo 1 (Desarrollo):  .\run_modo1_dev.ps1" -ForegroundColor White
Write-Host "  • Modo 2 (Producción):  .\run_modo2_prod.ps1" -ForegroundColor White
