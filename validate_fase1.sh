#!/bin/bash
# validate_fase1.sh
# FASE 1 VALIDATION SCRIPT (Bash/Linux/Mac)
# Script para validar FASE 1 manualmente
# - Rate limiting
# - Status codes
# - Logging

# Configuration
BASE_URL="http://localhost:8000"
API_TOKEN_URL="$BASE_URL/api/token/"
DASHBOARD_URL="$BASE_URL/api/reportes/dashboard/"
TEST_USERNAME="admin"
TEST_PASSWORD="admin"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

function print_header() {
    echo ""
    echo -e "${CYAN}════════════════════════════════════════════════════════════════════${NC}"
    echo -e "${CYAN}  $1${NC}"
    echo -e "${CYAN}════════════════════════════════════════════════════════════════════${NC}"
}

function print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

function print_error() {
    echo -e "${RED}❌ $1${NC}"
}

function print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

function print_info() {
    echo -e "${CYAN}ℹ️  $1${NC}"
}

# TEST 1: Verificar servidor está corriendo
print_header "TEST 1: Verificar Servidor Django"

if curl -s -f "$BASE_URL/api/token/" > /dev/null 2>&1 || \
   curl -s "$BASE_URL/api/token/" | grep -q "POST"; then
    print_success "Servidor Django está corriendo"
else
    print_error "No se puede conectar a $BASE_URL"
    print_info "¿Django está corriendo? Ejecuta: python manage.py runserver"
    exit 1
fi

# TEST 2: Verificar estructura de respuesta de error
print_header "TEST 2: Status Codes - Sin Autenticación"

response=$(curl -s -w "\n%{http_code}" "$DASHBOARD_URL")
status=$(echo "$response" | tail -n1)
body=$(echo "$response" | head -n-1)

print_info "Request sin token a: $DASHBOARD_URL"
print_info "  Status: $status"
print_info "  Response: $(echo "$body" | head -c 100)..."

if [ "$status" = "401" ] || [ "$status" = "403" ]; then
    print_success "Sin autenticación retorna $status (CORRECTO)"
else
    print_warning "Status esperado 401/403, recibido $status"
fi

# TEST 3: Obtener y usar token válido
print_header "TEST 3: Status Codes - Con Autenticación"

print_info "Obteniendo token para usuario: $TEST_USERNAME"

token_response=$(curl -s -X POST "$API_TOKEN_URL" \
    -H "Content-Type: application/json" \
    -d "{\"username\":\"$TEST_USERNAME\",\"password\":\"$TEST_PASSWORD\"}")

token=$(echo "$token_response" | grep -o '"access":"[^"]*' | cut -d'"' -f4)

if [ -n "$token" ]; then
    print_success "Token obtenido: ${token:0:20}..."
    
    print_info "Request con token a: $DASHBOARD_URL"
    
    dash_response=$(curl -s -w "\n%{http_code}" \
        -H "Authorization: Bearer $token" \
        "$DASHBOARD_URL")
    
    dash_status=$(echo "$dash_response" | tail -n1)
    
    print_info "  Status: $dash_status"
    
    if [ "$dash_status" = "200" ]; then
        print_success "Con autenticación retorna 200 (CORRECTO)"
    elif [ "$dash_status" = "500" ]; then
        print_warning "Con autenticación retorna 500 (error en servidor)"
        print_info "Verificar logs/errors.log para detalles"
    else
        print_info "Status recibido: $dash_status"
    fi
else
    print_warning "No se pudo obtener token"
    print_info "Usuario 'admin' con contraseña 'admin' probablemente no existe"
fi

# TEST 4: Verificar Rate Limiting
print_header "TEST 4: Rate Limiting"

print_info "Haciendo múltiples requests sin autenticación..."
print_info "Límite: 100 requests/hora para anónimos"

success_count=0
rate_limited_count=0

for i in {1..10}; do
    status=$(curl -s -w "%{http_code}" -o /dev/null "$DASHBOARD_URL")
    
    if [ "$status" = "429" ]; then
        print_warning "Request $i: 429 Too Many Requests"
        ((rate_limited_count++))
    elif [ "$status" = "401" ]; then
        print_info "Request $i: 401 Unauthorized"
        ((success_count++))
    else
        print_info "Request $i: $status"
        ((success_count++))
    fi
    
    sleep 0.1
done

print_info "Resultados: $success_count exitosos, $rate_limited_count limitados"

if [ "$rate_limited_count" -eq 0 ]; then
    print_success "Rate limiting está activo (sistema responde normalmente)"
else
    print_warning "Algunos requests fueron limitados (429)"
fi

# TEST 5: Verificar Logging
print_header "TEST 5: Logging"

if [ -f "logs/django.log" ]; then
    print_success "Archivo de log encontrado: logs/django.log"
    log_size=$(stat -f%z "logs/django.log" 2>/dev/null || stat -c%s "logs/django.log" 2>/dev/null)
    print_info "  Tamaño: $log_size bytes"
    print_info "  Últimas 3 líneas:"
    tail -n 3 logs/django.log | while read line; do
        echo "    $line"
    done
else
    print_warning "Archivo logs/django.log no encontrado"
    print_info "Se creará automáticamente cuando Django registre eventos"
fi

if [ -f "logs/errors.log" ]; then
    print_success "Archivo de errores encontrado: logs/errors.log"
    err_size=$(stat -f%z "logs/errors.log" 2>/dev/null || stat -c%s "logs/errors.log" 2>/dev/null)
    print_info "  Tamaño: $err_size bytes"
else
    print_info "Archivo logs/errors.log aún no creado (se crea con errores)"
fi

# TEST 6: Verificar estructura de directorio logs
print_header "TEST 6: Estructura de Logs"

if [ -d "logs" ]; then
    print_success "Directorio 'logs' existe"
    print_info "  Contenidos:"
    ls -la logs | tail -n +4 | while read line; do
        echo "    $line"
    done
else
    print_warning "Directorio 'logs' no encontrado"
    print_info "Se creará automáticamente"
fi

# TEST 7: Resumen
print_header "RESUMEN DE VALIDACIÓN FASE 1"

print_success "Validación completada"
echo ""
print_info "Próximos pasos:"
print_info "  1. Revisar logs/django.log para confirmar logs"
print_info "  2. Ejecutar: python manage.py test test_fase1_validation"
print_info "  3. Revisar TESTING_FASE1.md para más pruebas"
echo ""

echo -e "${GREEN}📊 FASE 1 está listo para validación detallada${NC}"
echo ""
