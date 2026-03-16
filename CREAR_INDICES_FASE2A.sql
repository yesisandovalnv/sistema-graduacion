-- FASE 2A: CREAR 5 ÍNDICES CRÍTICOS
-- Sistema de Graduación - Marzo 2026
-- 
-- Alcance limitado: Solo 5 índices críticos
-- Impacto esperado: -40% en queries dashboard/reportes
-- Tiempo: ~30 segundos en tabla con 10k registros

BEGIN TRANSACTION;

-- ============================================================================
-- ÍNDICE 1: Filtros por tutor (reportes de tutores)
-- ============================================================================
CREATE INDEX CONCURRENTLY idx_postulacion_tutor_fase2a
    ON postulantes_postulacion(tutor)
    WHERE tutor IS NOT NULL AND tutor != '';

-- ============================================================================
-- ÍNDICE 2: Filtros por estado_general (dashboard counts)
-- CRÍTICO: Usado en 6 queries diferentes en dashboard_general()
-- ============================================================================
CREATE INDEX CONCURRENTLY idx_postulacion_estado_general_fase2a
    ON postulantes_postulacion(estado_general);

-- ============================================================================
-- ÍNDICE 3: Estado de documentos (agregaciones en dashboard)
-- ============================================================================
CREATE INDEX CONCURRENTLY idx_documento_estado_fase2a
    ON documentos_documentopostulacion(estado);

-- ============================================================================
-- ÍNDICE 4: Carrera para reportes y filtros
-- ============================================================================
CREATE INDEX CONCURRENTLY idx_postulante_carrera_fase2a
    ON postulantes_postulante(carrera)
    WHERE carrera IS NOT NULL AND carrera != '';

-- ============================================================================
-- ÍNDICE 5: Notificaciones sin leer (UI badge)
-- ============================================================================
CREATE INDEX CONCURRENTLY idx_notificacion_usuario_leida_fase2a
    ON postulantes_notificacion(usuario_id, leida)
    WHERE leida = false;

COMMIT TRANSACTION;

-- ============================================================================
-- VALIDACIÓN POST-CREACIÓN
-- ============================================================================
-- Ejecutar después de crear índices:
--
-- SELECT schemaname, tablename, indexname
--   FROM pg_indexes
--  WHERE indexname LIKE 'idx_%_fase2a'
--  ORDER BY tablename, indexname;
--
-- Resultado esperado: 5 índices listados
--
-- ============================================================================
-- ROLLBACK (si es necesario)
-- ============================================================================
-- DROP INDEX CONCURRENTLY IF EXISTS idx_postulacion_tutor_fase2a;
-- DROP INDEX CONCURRENTLY IF EXISTS idx_postulacion_estado_general_fase2a;
-- DROP INDEX CONCURRENTLY IF EXISTS idx_documento_estado_fase2a;
-- DROP INDEX CONCURRENTLY IF EXISTS idx_postulante_carrera_fase2a;
-- DROP INDEX CONCURRENTLY IF EXISTS idx_notificacion_usuario_leida_fase2a;
