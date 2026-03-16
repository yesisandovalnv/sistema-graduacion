# monitor_logs_fase1.ps1
"""
MONITOR LOGS - FASE 1
Script para monitorear logs en tiempo real

USO:
  .\monitor_logs_fase1.ps1

Este script mostrará en tiempo real:
  - Logs del sistema (logs/django.log)
  - Errores (logs/errors.log)
  - Eventos de rate limiting
"""

param(
    [string]$LogType = "general",  # general, errors, all
    [int]$RefreshSeconds = 2,       # Actualizar cada X segundos
    [int]$TailLines = 20            # Mostrar últimas X líneas
)

# Configuración
$DJANGO_LOG = "logs/django.log"
$ERRORS_LOG = "logs/errors.log"

# Colores
$INFO_COLOR = [ConsoleColor]::Cyan
$ERROR_COLOR = [ConsoleColor]::Red
$SUCCESS_COLOR = [ConsoleColor]::Green
$WARNING_COLOR = [ConsoleColor]::Yellow

function Write-LogHeader {
    param([string]$Text)
    Write-Host "`n" + "="*70 -ForegroundColor $INFO_COLOR
    Write-Host "  $Text" -ForegroundColor $INFO_COLOR
    Write-Host "="*70 -ForegroundColor $INFO_COLOR
}

function Show-GeneralLogs {
    Write-LogHeader "📜 DJANGO LOGS (Generales)"
    
    if (Test-Path $DJANGO_LOG) {
        $content = Get-Content $DJANGO_LOG -Tail $TailLines -ErrorAction SilentlyContinue
        
        if ($content) {
            $content | ForEach-Object {
                if ($_ -match "ERROR") {
                    Write-Host $_ -ForegroundColor $ERROR_COLOR
                } elseif ($_ -match "WARNING") {
                    Write-Host $_ -ForegroundColor $WARNING_COLOR
                } elseif ($_ -match "INFO") {
                    Write-Host $_ -ForegroundColor $SUCCESS_COLOR
                } else {
                    Write-Host $_
                }
            }
        } else {
            Write-Host "  (sin logs aún)" -ForegroundColor $WARNING_COLOR
        }
    } else {
        Write-Host "  ⚠️  Archivo no encontrado: $DJANGO_LOG" -ForegroundColor $WARNING_COLOR
        Write-Host "  Se creará cuando Django comience a registrar eventos" -ForegroundColor $INFO_COLOR
    }
}

function Show-ErrorLogs {
    Write-LogHeader "🔴 ERROR LOGS (Solo Errores)"
    
    if (Test-Path $ERRORS_LOG) {
        $content = Get-Content $ERRORS_LOG -Tail $TailLines -ErrorAction SilentlyContinue
        
        if ($content) {
            $content | ForEach-Object {
                Write-Host $_ -ForegroundColor $ERROR_COLOR
            }
        } else {
            Write-Host "  ✅ Sin errores registrados" -ForegroundColor $SUCCESS_COLOR
        }
    } else {
        Write-Host "  ✅ Archivo no existe (aún sin errores)" -ForegroundColor $SUCCESS_COLOR
    }
}

function Show-AllLogs {
    Write-LogHeader "📊 TODOS LOS LOGS"
    
    Show-GeneralLogs
    Show-ErrorLogs
}

function Show-RateLimitInfo {
    Write-LogHeader "⚡ INFORMACIÓN DE RATE LIMITING"
    
    Write-Host ""
    Write-Host "Configuración actual:" -ForegroundColor $INFO_COLOR
    Write-Host "  ├─ Usuarios anónimos: 100 requests/hora" -ForegroundColor $SUCCESS_COLOR
    Write-Host "  ├─ Usuarios autenticados: 1000 requests/hora" -ForegroundColor $SUCCESS_COLOR
    Write-Host "  └─ Response cuando se excede: 429 Too Many Requests" -ForegroundColor $SUCCESS_COLOR
    
    Write-Host ""
    Write-Host "Búsqueda en logs:" -ForegroundColor $INFO_COLOR
    
    if (Test-Path $ERRORS_LOG) {
        $rateLimitHits = Get-Content $ERRORS_LOG -ErrorAction SilentlyContinue | 
            Where-Object { $_ -match "429|rate.*limit|throttle" } | 
            Measure-Object | Select-Object -ExpandProperty Count
        
        if ($rateLimitHits -gt 0) {
            Write-Host "  🔴 Detections de rate limiting: $rateLimitHits" -ForegroundColor $WARNING_COLOR
        } else {
            Write-Host "  ✅ Sin detecciones de rate limiting" -ForegroundColor $SUCCESS_COLOR
        }
    }
}

function Show-StatusCodeStats {
    Write-LogHeader "📈 ESTADÍSTICAS DE STATUS CODES"
    
    if (Test-Path $DJANGO_LOG) {
        Write-Host ""
        Write-Host "Búsqueda de status codes en logs:" -ForegroundColor $INFO_COLOR
        
        $statusCounts = @{}
        Get-Content $DJANGO_LOG -ErrorAction SilentlyContinue | 
            Select-String -Pattern "\b([245]\d{2})\b" -AllMatches | 
            ForEach-Object {
                $_.Matches | ForEach-Object {
                    $code = $_.Value
                    $statusCounts[$code]++
                }
            }
        
        if ($statusCounts.Count -gt 0) {
            $statusCounts.GetEnumerator() | Sort-Object Name | ForEach-Object {
                $code = $_.Key
                $count = $_.Value
                
                if ($code -like "2*") {
                    Write-Host "  ✅ $code: $count ocurrencias" -ForegroundColor $SUCCESS_COLOR
                } elseif ($code -like "4*") {
                    Write-Host "  ⚠️  $code: $count ocurrencias" -ForegroundColor $WARNING_COLOR
                } else {
                    Write-Host "  ❌ $code: $count ocurrencias" -ForegroundColor $ERROR_COLOR
                }
            }
        } else {
            Write-Host "  (sin status codes específicos encontrados)" -ForegroundColor $INFO_COLOR
        }
    }
}

function Show-LoggingStats {
    Write-LogHeader "📊 ESTADÍSTICAS DE LOGGING"
    
    Write-Host ""
    Write-Host "Archivos de log:" -ForegroundColor $INFO_COLOR
    
    if (Test-Path $DJANGO_LOG) {
        $djangoSize = (Get-Item $DJANGO_LOG).Length
        $djangoLines = (Get-Content $DJANGO_LOG -ErrorAction SilentlyContinue | Measure-Object -Line).Lines
        Write-Host "  📄 django.log: $djangoLines líneas (~$([math]::Round($djangoSize/1KB))KB)" -ForegroundColor $SUCCESS_COLOR
    } else {
        Write-Host "  📄 django.log: No encontrado" -ForegroundColor $WARNING_COLOR
    }
    
    if (Test-Path $ERRORS_LOG) {
        $errorsSize = (Get-Item $ERRORS_LOG).Length
        $errorsLines = (Get-Content $ERRORS_LOG -ErrorAction SilentlyContinue | Measure-Object -Line).Lines
        Write-Host "  🔴 errors.log: $errorsLines líneas (~$([math]::Round($errorsSize/1KB))KB)" -ForegroundColor $SUCCESS_COLOR
    } else {
        Write-Host "  🔴 errors.log: No encontrado (aún sin errores)" -ForegroundColor $WARNING_COLOR
    }
    
    Write-Host ""
    Write-Host "Niveles de log detectados:" -ForegroundColor $INFO_COLOR
    
    if (Test-Path $DJANGO_LOG) {
        $logContent = Get-Content $DJANGO_LOG -ErrorAction SilentlyContinue
        
        $infoCount = ($logContent | Where-Object { $_ -match "INFO" } | Measure-Object).Count
        $warningCount = ($logContent | Where-Object { $_ -match "WARNING" } | Measure-Object).Count
        $errorCount = ($logContent | Where-Object { $_ -match "ERROR" } | Measure-Object).Count
        $debugCount = ($logContent | Where-Object { $_ -match "DEBUG" } | Measure-Object).Count
        
        Write-Host "  ✅ INFO: $infoCount" -ForegroundColor $SUCCESS_COLOR
        Write-Host "  ⚠️  WARNING: $warningCount" -ForegroundColor $WARNING_COLOR
        Write-Host "  ❌ ERROR: $errorCount" -ForegroundColor $ERROR_COLOR
        Write-Host "  🔍 DEBUG: $debugCount" -ForegroundColor $INFO_COLOR
    }
}

function Show-Menu {
    Write-Host ""
    Write-Host "═"*70 -ForegroundColor $INFO_COLOR
    Write-Host "  OPCIONES DE MONITOREO" -ForegroundColor $INFO_COLOR
    Write-Host "═"*70 -ForegroundColor $INFO_COLOR
    Write-Host ""
    Write-Host "  g - Mostrar logs generales" -ForegroundColor $SUCCESS_COLOR
    Write-Host "  e - Mostrar solo errores" -ForegroundColor $ERROR_COLOR
    Write-Host "  a - Mostrar todos los logs" -ForegroundColor $INFO_COLOR
    Write-Host "  r - Ver info de rate limiting" -ForegroundColor $WARNING_COLOR
    Write-Host "  s - Ver estadísticas de status codes" -ForegroundColor $INFO_COLOR
    Write-Host "  l - Ver estadísticas de logging" -ForegroundColor $INFO_COLOR
    Write-Host "  f - Mostrar contenido completo de archivos" -ForegroundColor $INFO_COLOR
    Write-Host "  c - Limpiar pantalla" -ForegroundColor $INFO_COLOR
    Write-Host "  q - Salir" -ForegroundColor $ERROR_COLOR
    Write-Host ""
}

# Main loop
$running = $true

Write-Host ""
Write-Host "╔═══════════════════════════════════════════════════════════════════╗" -ForegroundColor $INFO_COLOR
Write-Host "║         🔍 MONITOR DE LOGS - FASE 1 VALIDATION                  ║" -ForegroundColor $INFO_COLOR
Write-Host "╚═══════════════════════════════════════════════════════════════════╝" -ForegroundColor $INFO_COLOR
Write-Host ""
Write-Host "Este script monitorea los logs de FASE 1 en tiempo real" -ForegroundColor $INFO_COLOR
Write-Host "Presiona 'h' para ayuda" -ForegroundColor $INFO_COLOR
Write-Host ""

# Mostrar vista inicial
Show-GeneralLogs

while ($running) {
    Write-Host ""
    $choice = Read-Host "Opción [g/e/a/r/s/l/f/c/h/q]"
    
    switch ($choice.ToLower()) {
        'g' {
            Clear-Host
            Show-GeneralLogs
        }
        'e' {
            Clear-Host
            Show-ErrorLogs
        }
        'a' {
            Clear-Host
            Show-AllLogs
        }
        'r' {
            Clear-Host
            Show-RateLimitInfo
        }
        's' {
            Clear-Host
            Show-StatusCodeStats
        }
        'l' {
            Clear-Host
            Show-LoggingStats
        }
        'f' {
            Clear-Host
            Write-LogHeader "📄 CONTENIDO COMPLETO - DJANGO.LOG"
            if (Test-Path $DJANGO_LOG) {
                Get-Content $DJANGO_LOG
            } else {
                Write-Host "Archivo no encontrado" -ForegroundColor $WARNING_COLOR
            }
            
            Write-LogHeader "📄 CONTENIDO COMPLETO - ERRORS.LOG"
            if (Test-Path $ERRORS_LOG) {
                Get-Content $ERRORS_LOG
            } else {
                Write-Host "Archivo no encontrado" -ForegroundColor $WARNING_COLOR
            }
        }
        'c' {
            Clear-Host
        }
        'h' {
            Show-Menu
        }
        'q' {
            $running = $false
        }
        default {
            Show-Menu
        }
    }
}

Write-Host ""
Write-Host "✅ Monitor finalizado" -ForegroundColor $SUCCESS_COLOR
Write-Host ""
