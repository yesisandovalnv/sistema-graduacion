#!/bin/bash
# OPERATIVO 3: Backup y Restauración de Base de Datos

echo "=============================================================="
echo " OPERATIVO 3: BACKUP Y RESTAURACIÓN DE BASE DE DATOS"
echo "=============================================================="

DB_NAME="sistema_graduacion"
DB_USER="sistema_user"
DB_PASSWORD="sistema_pass"
DB_HOST="localhost"
BACKUP_FILE="backup_test_$(date +%Y%m%d_%H%M%S).sql"

echo ""
echo "🔄 Paso 1: Crear backup de la BD..."

# Backup completo
PGPASSWORD="$DB_PASSWORD" pg_dump -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" > "/tmp/$BACKUP_FILE"

if [ -f "/tmp/$BACKUP_FILE" ]; then
    SIZE=$(du -h "/tmp/$BACKUP_FILE" | cut -f1)
    echo "   ✓ Backup creado: $BACKUP_FILE ($SIZE)"
else
    echo "   ❌ Error creando backup"
    exit 1
fi

# Contar tablas en backup
TABLE_COUNT=$(grep -c "CREATE TABLE" "/tmp/$BACKUP_FILE")
echo "   ✓ Tablas en backup: $TABLE_COUNT"

echo ""
echo "🔄 Paso 2: Verificar integridad del backup..."

# Intentar restaurar en una BD de prueba
TEST_DB="${DB_NAME}_test_restore"
CHECK_DB=$(PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -U "$DB_USER" -d "postgres" -tc "SELECT 1 FROM pg_database WHERE datname = '$TEST_DB'" | grep -q 1; echo $?)

if [ $CHECK_DB -eq 0 ]; then
    echo "   ✓ BD de prueba existe, eliminando..."
    PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -U "$DB_USER" -d "postgres" -c "DROP DATABASE $TEST_DB;" > /dev/null 2>&1
fi

# Crear BD de prueba
PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -U "$DB_USER" -d "postgres" -c "CREATE DATABASE $TEST_DB;" > /dev/null 2>&1

if [ $? -ne 0 ]; then
    echo "   ❌ Error creando BD de prueba"
    exit 1
fi

echo "   ✓ BD de prueba creada"

# Restaurar backup en BD de prueba
PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -U "$DB_USER" -d "$TEST_DB" < "/tmp/$BACKUP_FILE" > /dev/null 2>&1

if [ $? -eq 0 ]; then
    echo "   ✓ Backup restaurado exitosamente"
    
    # Contar registros en tabla usuarios
    USUARIOS=$(PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -U "$DB_USER" -d "$TEST_DB" -tc "SELECT COUNT(*) FROM usuarios_customuser;" | tr -d ' ')
    echo "   ✓ Usuarios en BD restaurada: $USUARIOS"
else
    echo "   ❌ Error restaurando backup"
    exit 1
fi

echo ""
echo "🔄 Paso 3: Limpiar BD de prueba..."

PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -U "$DB_USER" -d "postgres" -c "DROP DATABASE $TEST_DB;" > /dev/null 2>&1

if [ $? -eq 0 ]; then
    echo "   ✓ BD de prueba eliminada"
else
    echo "   ⚠️ Advertencia: No se pudo eliminar BD de prueba"
fi

echo ""
echo "=============================================================="
echo " OPERATIVO 3: OK - Backup/Restauración funcionando"
echo "=============================================================="
echo ""
