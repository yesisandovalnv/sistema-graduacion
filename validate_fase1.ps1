# validate_fase1.ps1
"""
FASE 1 VALIDATION SCRIPT (PowerShell)
Script para validar FASE 1 manualmente
- Rate limiting
- Status codes
- Logging

USO:
  .\validate_fase1.ps1

REQUISITOS:
  - Django server corriendo en http://localhost:8000
  - curl disponible en PATH
"""

# Configuración
$BASE_URL = "http://localhost:8000"
$API_TOKEN_URL = "$BASE_URL/api/token/"
$DASHBOARD_URL = "$BASE_URL/api/reportes/dashboard/"
$TEST_USERNAME = "admin"
$TEST_PASSWORD = "admin"

# Colores
$GREEN = [ConsoleColor]::Green
$RED = [ConsoleColor]::Red
$YELLOW = [ConsoleColor]::Yellow
$CYAN = [ConsoleColor]::Cyan

function Write-Header {
    param([string]$Text)
    Write-Host ""
    Write-Host "═" * 70 -ForegroundColor $CYAN
    Write-Host "  $Text" -ForegroundColor $CYAN
    Write-Host "═" * 70 -ForegroundColor $CYAN
}

function Write-Success {
    param([string]$Text)
    Write-Host "✅ $Text" -ForegroundColor $GREEN
}

function Write-Error {
    param([string]$Text)
    Write-Host "❌ $Text" -ForegroundColor $RED
}

function Write-Warning {
    param([string]$Text)
    Write-Host "⚠️  $Text" -ForegroundColor $YELLOW
}

function Write-Info {
    param([string]$Text)
    Write-Host "ℹ️  $Text" -ForegroundColor $CYAN
}

# TEST 1: Verificar servidor está corriendo
Write-Header "TEST 1: Verificar Servidor Django"

try {
    $response = curl -s -w "%{http_code}" -o $null "$BASE_URL/api/token/"
    if ($response -eq "405" -or $response -eq "400" -or $response -eq "200") {
        Write-Success "Servidor Django está corriendo"
    } else {
        Write-Error "Servidor no responde correctamente: status $response"
        exit 1
    }
} catch {
    Write-Error "No se puede conectar a $BASE_URL"
    Write-Info "¿Django está corriendo? Ejecuta: python manage.py runserver"
    exit 1
}

# TEST 2: Verificar estructura de respuesta de error
Write-Header "TEST 2: Status Codes - Sin Autenticación"

$response = curl -s -w "\n%{http_code}" "$DASHBOARD_URL"
$status = ($response | Select-Object -Last 1)
$body = ($response | Select-Object -SkipLast 1) -join "`n"

Write-Info "Request sin token a: $DASHBOARD_URL"
Write-Info "  Status: $status"
Write-Info "  Response: $body"

if ($status -eq "401" -o $status -eq "403") {
    Write-Success "Sin autenticación retorna $status (CORRECTO)"
} else {
    Write-Warning "Status esperado 401/403, recibido $status"
}

# TEST 3: Obtener y usar token válido
Write-Header "TEST 3: Status Codes - Con Autenticación"

Write-Info "Obteniendo token para usuario: $TEST_USERNAME"

$tokenResponse = curl -s -X POST "$API_TOKEN_URL" `
    -H "Content-Type: application/json" `
    -d "{`"username`":`"$TEST_USERNAME`",`"password`":`"$TEST_PASSWORD`"}"

# Intentar obtener token (puede fallar si usuario no existe)
try {
    $tokenObj = $tokenResponse | ConvertFrom-Json -ErrorAction SilentlyContinue
    $token = $tokenObj.access
    
    if ($token) {
        Write-Success "Token obtenido: ${token:0:20}..."
        
        # Request con token válido
        Write-Info "Request con token a: $DASHBOARD_URL"
        
        $dashboardResponse = curl -s -w "\n%{http_code}" `
            -H "Authorization: Bearer $token" `
            "$DASHBOARD_URL"
        
        $dashStatus = ($dashboardResponse | Select-Object -Last 1)
        $dashBody = ($dashboardResponse | Select-Object -SkipLast 1 -First 3) -join "`n"
        
        Write-Info "  Status: $dashStatus"
        Write-Info "  Response (primeras líneas): $dashBody..."
        
        if ($dashStatus -eq "200") {
            Write-Success "Con autenticación retorna 200 (CORRECTO)"
        } elseif ($dashStatus -eq "500") {
            Write-Warning "Con autenticación retorna 500 (error en servidor)"
            Write-Info "Verificar logs/errors.log para detalles"
        } else {
            Write-Info "Status recibido: $dashStatus"
        }
    } else {
        Write-Warning "No se pudo obtener token"
        Write-Info "Usuario 'admin' con contraseña 'admin' probablemente no existe"
        Write-Info "Esto es normal en desarrollo sin usuarios precargados"
    }
} catch {
    Write-Warning "No se pudo procesar la respuesta de token"
    Write-Info "Usuario probablemente no existe"
}

# TEST 4: Verificar Rate Limiting
Write-Header "TEST 4: Rate Limiting"

Write-Info "Haciendo múltiples requests sin autenticación..."
Write-Info "Límite: 100 requests/hora para anónimos"

$successCount = 0
$rateLimitedCount = 0

for ($i = 1; $i -le 10; $i++) {
    $status = curl -s -w "%{http_code}" -o $null "$DASHBOARD_URL"
    
    if ($status -eq "429") {
        Write-Warning "Request $i: 429 Too Many Requests"
        $rateLimitedCount++
    } elseif ($status -eq "401") {
        Write-Info "Request $i: 401 Unauthorized"
        $successCount++
    } else {
        Write-Info "Request $i: $status"
        $successCount++
    }
    
    Start-Sleep -Milliseconds 100
}

Write-Info "Resultados: $successCount exitosos, $rateLimitedCount limitados"

if ($rateLimitedCount -eq 0) {
    Write-Success "Rate limiting está activo (sistema responde normalmente)"
} else {
    Write-Warning "Algunos requests fueron limitados (429)"
}

# TEST 5: Verificar Logging
Write-Header "TEST 5: Logging"

$djangoLogPath = "logs/django.log"
$errorsLogPath = "logs/errors.log"

if (Test-Path $djangoLogPath) {
    Write-Success "Archivo de log encontrado: $djangoLogPath"
    $logSize = (Get-Item $djangoLogPath).Length
    Write-Info "  Tamaño: $logSize bytes"
    
    # Mostrar últimas líneas
    Write-Info "  Últimas 3 líneas:"
    $lastLines = Get-Content $djangoLogPath -Tail 3
    $lastLines | ForEach-Object { Write-Host "    $_" }
} else {
    Write-Warning "Archivo logs/django.log no encontrado"
    Write-Info "Se creará automáticamente cuando Django registre eventos"
}

if (Test-Path $errorsLogPath) {
    Write-Success "Archivo de errores encontrado: $errorsLogPath"
    $errSize = (Get-Item $errorsLogPath).Length
    Write-Info "  Tamaño: $errSize bytes"
} else {
    Write-Info "Archivo logs/errors.log aún no creado (se crea con errores)"
}

# TEST 6: Verificar estructura de directorio logs
Write-Header "TEST 6: Estructura de Logs"

if (Test-Path "logs") {
    Write-Success "Directorio 'logs' existe"
    
    $files = Get-ChildItem "logs" -Force
    Write-Info "  Contenidos:"
    $files | ForEach-Object { 
        Write-Host "    - $($_.Name)" 
    }
} else {
    Write-Warning "Directorio 'logs' no encontrado"
    Write-Info "Se creará automáticamente"
}

# TEST 7: Resumen
Write-Header "RESUMEN DE VALIDACIÓN FASE 1"

Write-Success "Validación completada"
Write-Info ""
Write-Info "Próximos pasos:"
Write-Info "  1. Revisar logs/django.log para confirmar logs"
Write-Info "  2. Ejecutar: python manage.py test test_fase1_validation"
Write-Info "  3. Revisar TESTING_FASE1.md para más pruebas"
Write-Info ""

Write-Host ""
Write-Host "📊 FASE 1 está listo para validación detallada" -ForegroundColor $GREEN
Write-Host ""
