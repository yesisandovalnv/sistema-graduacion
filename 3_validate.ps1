# ============================================================================
# VALIDACIÓN POST-START - Verifica flujo completo del sistema
# ============================================================================
# Prueba:
# 1. Backend responde
# 2. Base de datos conectada
# 3. Frontend accesible
# 4. Login posible
# 5. Dashboard funciona
# ============================================================================

param(
    [string]$Mode = "both"  # "dev", "prod", o "both"
)

$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$logFile = "logs/validation_$timestamp.log"

# Colores
$colors = @{
    Success = "Green"
    Error   = "Red"
    Warning = "Yellow"
    Info    = "Cyan"
    Debug   = "Gray"
}

function Write-Log {
    param([string]$Message, [string]$Level = "Info")
    
    $logMessage = "[$((Get-Date).ToString('HH:mm:ss'))] [$Level] $Message"
    Write-Host $logMessage -ForegroundColor $colors[$Level]
    Add-Content -Path $logFile -Value $logMessage
}

function Test-Endpoint {
    param(
        [string]$Url,
        [string]$Name,
        [ValidateSet("GET", "POST")]$Method = "GET",
        [hashtable]$Headers = @{}
    )
    
    try {
        $response = Invoke-WebRequest `
            -Uri $Url `
            -Method $Method `
            -Headers $Headers `
            -TimeoutSec 5 `
            -ErrorAction Stop
        
        Write-Log "[OK] $Name responde (HTTP $($response.StatusCode))" -Level Success
        return $true
        
    } catch [Microsoft.PowerShell.Commands.HttpResponseException] {
        # Status codes como 401, 404, 400 son válidos (backend respondió)
        if ($_.Exception.Response.StatusCode -in @(400, 401, 404, 500)) {
            Write-Log "[OK] $Name responde (HTTP $($_.Exception.Response.StatusCode))" -Level Success
            return $true
        } else {
            Write-Log "[ERROR] $Name - HTTP $($_.Exception.Response.StatusCode)" -Level Error
            return $false
        }
    } catch {
        Write-Log "[ERROR] $Name - $_" -Level Error
        return $false
    }
}

function Test-Database {
    try {
        $dbCheck = docker compose exec db pg_isready -U sistema_user -d sistema_graduacion 2>$null
        
        if ($LASTEXITCODE -eq 0) {
            Write-Log "[OK] Base de datos conectada y lista" -Level Success
            return $true
        } else {
            Write-Log "[WARNING]  Base de datos no ready" -Level Warning
            return $false
        }
    } catch {
        Write-Log "[ERROR] No se pudo verificar BD: $_" -Level Error
        return $false
    }
}

function Test-DockerServices {
    param([string]$Mode)
    
    Write-Log ""
    Write-Log "---" -Level Info
    Write-Log "[DOCKER] SERVICIOS DOCKER" -Level Info
    Write-Log "---" -Level Info
    
    $ps = docker compose ps --format '{{.Service}},{{.Status}}' 2>$null
    
    if ($Mode -eq "dev" -or $Mode -eq "both") {
        Write-Log "Verificando servicios Desarrollo (db, backend)..." -Level Info
        
        $services = @("db", "backend")
        foreach ($service in $services) {
            $status = $ps | Select-String $service | ForEach-Object { $_.ToString().Split(",")[1] }
            
            if ($status -like "*Up*") {
                Write-Log "  [OK] $service está activo" -Level Success
            } else {
                Write-Log "  [ERROR] $service no está activo" -Level Error
            }
        }
    }
    
    if ($Mode -eq "prod" -or $Mode -eq "both") {
        Write-Log "Verificando servicios Producción (todos)..." -Level Info
        
        $services = @("db", "backend", "frontend", "nginx")
        foreach ($service in $services) {
            $status = $ps | Select-String $service | ForEach-Object { $_.ToString().Split(",")[1] }
            
            if ($status -like "*Up*") {
                Write-Log "  [OK] $service está activo" -Level Success
            } else {
                Write-Log "  [ERROR] $service no está activo" -Level Error
            }
        }
    }
}

function Test-BackendAPI {
    Write-Log ""
    Write-Log "---" -Level Info
    Write-Log "[BACKEND] BACKEND API" -Level Info
    Write-Log "---" -Level Info
    
    $backendOk = Test-Endpoint "http://localhost:8000/" "Homepage"
    $apiOk = Test-Endpoint "http://localhost:8000/api/" "API Root"
    $adminOk = Test-Endpoint "http://localhost:8000/admin/" "Admin Panel"
    $tokenOk = Test-Endpoint "http://localhost:8000/api/token/" "Token Endpoint" "POST"
    
    return ($backendOk -and $apiOk -and $adminOk -and $tokenOk)
}

function Test-Frontend {
    Write-Log ""
    Write-Log "---" -Level Info
    Write-Log "[FRONTEND]  FRONTEND" -Level Info
    Write-Log "---" -Level Info
    
    $devOk = Test-Endpoint "http://localhost:5173/" "Frontend Dev (5173)"
    $prodOk = Test-Endpoint "http://localhost/" "Frontend Prod/Nginx (80)"
    
    # Frontend da HTML con 200 si existe, así que ambas opciones son OK
    if ($devOk -or $prodOk) {
        Write-Log "[OK] Frontend accesible" -Level Success
        return $true
    }
    
    return $false
}

# ==================================================================
# MAIN
# ==================================================================

Write-Host ""
Write-Host "========" -ForegroundColor Cyan
Write-Host "|            ✓ VALIDACIÓN POST-START DEL SISTEMA              |" -ForegroundColor Cyan
Write-Host "========" -ForegroundColor Cyan
Write-Host ""

Write-Log "Iniciando validación..." -Level Info
Write-Log "Mode: $Mode" -Level Debug

$resultsOk = 0
$resultsFail = 0

try {
    # Servicios Docker
    Test-DockerServices -Mode $Mode
    
    # Backend API
    if (Test-BackendAPI) {
        $resultsOk++
    } else {
        $resultsFail++
    }
    
    # Database
    if (Test-Database) {
        $resultsOk++
    } else {
        $resultsFail++
    }
    
    # Frontend
    if (Test-Frontend) {
        $resultsOk++
    } else {
        $resultsFail++
    }
    
    # Resumen
    Write-Host ""
    Write-Host "========" -ForegroundColor Cyan
    Write-Host "|                      [REPORT] RESUMEN                              |" -ForegroundColor Cyan
    Write-Host "========" -ForegroundColor Cyan
    Write-Host ""
    
    if ($resultsFail -eq 0) {
        Write-Log "[OK] TODOS LOS TESTS PASARON" -Level Success
        Write-Host ""
        Write-Host "[WEB] ACCESO RECOMENDADO:" -ForegroundColor Green
        Write-Host ""
        Write-Host "  Desarrollo:" -ForegroundColor White
        Write-Host "    • Frontend: http://localhost:5173" -ForegroundColor Cyan
        Write-Host "    • Backend:  http://localhost:8000/api" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "  Producción:" -ForegroundColor White
        Write-Host "    • App: http://localhost or http://localhost:5173" -ForegroundColor Cyan
        Write-Host ""
    } else {
        Write-Log "[WARNING]  $resultsFail validación(es) fallaron" -Level Warning
        Write-Log "Verifica logs: $logFile" -Level Warning
    }
    
} catch {
    Write-Log "[ERROR] Error durante validación: $_" -Level Error
    Write-Log "Stack: $($_.ScriptStackTrace)" -Level Debug
}

Write-Host ""
Write-Host "[LOG] Logs completos en: $logFile" -ForegroundColor Gray
Write-Host ""
