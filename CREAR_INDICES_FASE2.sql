-- ÍNDICES PostgreSQL RECOMENDADOS - FASE 2
-- Sistema de Graduación
-- Fecha: Enero 2025
--
-- INSTRUCCIONES:
-- 1. Backup de base de datos ANTES de ejecutar
-- 2. Ejecutar en ambiente staging PRIMERO
-- 3. Medir tiempo de creación (puede tomar 2-5 minutos en datos grandes)
-- 4. Verificar con: SELECT * FROM pg_indexes WHERE tablename LIKE 'postulantes%';
--
-- IMPACTO ESPERADO:
-- - Dashboard: 1400ms → 350ms (75% mejora)
-- - List views: 2100ms → 50ms (97% mejora)
-- - Reports: 5100ms → 100ms (98% mejora)
-- ============================================================================

BEGIN TRANSACTION;

-- ============================================================================
-- TABLA: postulantes_postulante
-- Impacto: Búsquedas por carrera, nombre, código de estudiante
-- ============================================================================

-- Índice 1: CRÍTICO - Filtros por carrera (usado en reportes)
CREATE INDEX CONCURRENTLY idx_postulante_carrera_v1 
    ON postulantes_postulante(carrera) 
    WHERE carrera IS NOT NULL AND carrera != '';

-- Índice 2: MEDIA - Búsquedas por nombre y apellido combinados
CREATE INDEX CONCURRENTLY idx_postulante_apellido_nombre_v1
    ON postulantes_postulante(apellido, nombre);

-- Índice 3: MEDIA - Búsquedas por usuario_id (para filtros de permisos)
CREATE INDEX CONCURRENTLY idx_postulante_usuario_v1
    ON postulantes_postulante(usuario_id);

-- ============================================================================
-- TABLA: postulantes_postulacion
-- Impacto: CRÍTICA - Usada en casi TODAS las queries de dashboard/reportes
-- ============================================================================

-- Índice 1: CRÍTICO - dashboard_general() - contar por estado
CREATE INDEX CONCURRENTLY idx_postulacion_estado_general_v1
    ON postulantes_postulacion(estado_general);

-- Índice 2: CRÍTICO - dashboard_general() - filtrar TITULADO
CREATE INDEX CONCURRENTLY idx_postulacion_estado_general_titulado_v1
    ON postulantes_postulacion(estado_general)
    WHERE estado_general = 'TITULADO';

-- Índice 3: CRÍTICO - estadísticas por gestión + estado (aggregate)
CREATE INDEX CONCURRENTLY idx_postulacion_gestion_estado_general_v1
    ON postulantes_postulacion(gestion, estado_general);

-- Índice 4: CRÍTICO - reportes de tutores (filter + values('tutor'))
CREATE INDEX CONCURRENTLY idx_postulacion_tutor_v1
    ON postulantes_postulacion(tutor)
    WHERE tutor IS NOT NULL AND tutor != '';

-- Índice 5: ALTA - Filtros por postulante + estado (para la vista del usuario)
CREATE INDEX CONCURRENTLY idx_postulacion_postulante_estado_v1
    ON postulantes_postulacion(postulante_id, estado_general);

-- Índice 6: MEDIA - Ordenamiento por fecha en reportes (time-range filters)
CREATE INDEX CONCURRENTLY idx_postulacion_fecha_postulacion_desc_v1
    ON postulantes_postulacion(fecha_postulacion DESC);

-- Índice 7: MEDIA - Filtros por fecha + estado combinados (reporte.py line 445)
CREATE INDEX CONCURRENTLY idx_postulacion_fecha_estado_v1
    ON postulantes_postulacion(fecha_postulacion DESC, estado_general);

-- ============================================================================
-- TABLA: documentos_documentopostulacion
-- Impacto: ALTA - Usada en dashboard para contar documentos
-- ============================================================================

-- Índice 1: CRÍTICO - dashboard_general() - contar pendientes + rechazados
CREATE INDEX CONCURRENTLY idx_documento_estado_v1
    ON documentos_documentopostulacion(estado);

-- Índice 2: CRÍTICO - Filtros pendientes por estado
CREATE INDEX CONCURRENTLY idx_documento_estado_pendiente_v1
    ON documentos_documentopostulacion(estado)
    WHERE estado = 'pendiente';

-- Índice 3: CRÍTICO - Filtros rechazados por estado
CREATE INDEX CONCURRENTLY idx_documento_estado_rechazado_v1
    ON documentos_documentopostulacion(estado)
    WHERE estado = 'rechazado';

-- Índice 4: ALTA - Búsquedas de documentos por postulación + estado
CREATE INDEX CONCURRENTLY idx_documento_postulacion_estado_v1
    ON documentos_documentopostulacion(postulacion_id, estado);

-- Índice 5: MEDIA - Documentos ordenados por fecha de subida (hay ordering en modelo)
CREATE INDEX CONCURRENTLY idx_documento_fecha_subida_desc_v1
    ON documentos_documentopostulacion(fecha_subida DESC);

-- Índice 6: MEDIA - Documentos revisados por usuario
CREATE INDEX CONCURRENTLY idx_documento_revisado_por_v1
    ON documentos_documentopostulacion(revisado_por_id)
    WHERE revisado_por_id IS NOT NULL;

-- Índice 7: BAJA - Búsquedas de documentos por tipo + estado
CREATE INDEX CONCURRENTLY idx_documento_tipo_estado_v1
    ON documentos_documentopostulacion(tipo_documento_id, estado);

-- ============================================================================
-- TABLA: postulantes_notificacion
-- Impacto: MEDIA - Usada para obtener notificaciones sin leer
-- ============================================================================

-- Índice 1: CRÍTICO - Obtener notificaciones sin leer de un usuario
CREATE INDEX CONCURRENTLY idx_notificacion_usuario_leida_v1
    ON postulantes_notificacion(usuario_id, leida);

-- Índice 2: MEDIA - Notificaciones sin leer (para badge de UI)
CREATE INDEX CONCURRENTLY idx_notificacion_usuario_leida_true_v1
    ON postulantes_notificacion(usuario_id)
    WHERE leida = false;

-- Índice 3: MEDIA - Ordenamiento por fecha en notificaciones
CREATE INDEX CONCURRENTLY idx_notificacion_fecha_creacion_desc_v1
    ON postulantes_notificacion(fecha_creacion DESC);

-- Índice 4: BAJA - Limpieza de notificaciones antiguas
CREATE INDEX CONCURRENTLY idx_notificacion_usuario_fecha_v1
    ON postulantes_notificacion(usuario_id, fecha_creacion DESC);

-- ============================================================================
-- TABLA: modalidades_modalidad
-- Impacto: MEDIA - Filtros por activa=True
-- ============================================================================

-- Índice 1: MEDIA - Filtros de modalidades activas (dashboard)
CREATE INDEX CONCURRENTLY idx_modalidad_activa_v1
    ON modalidades_modalidad(activa)
    WHERE activa = true;

-- ============================================================================
-- TABLA: modalidades_etapa
-- Impacto: BAJA - Relaciones con TipoDocumento
-- ============================================================================

-- Índice 1: BAJA - Búsquedas de etapas por modalidad
CREATE INDEX CONCURRENTLY idx_etapa_modalidad_v1
    ON modalidades_etapa(modalidad_id, orden);

-- ============================================================================
-- TABLA: documentos_tipodocumento
-- Impacto: BAJA - Filtros por etapa en formularios
-- ============================================================================

-- Índice 1: BAJA - Documentos por etapa
CREATE INDEX CONCURRENTLY idx_tipodocumento_etapa_v1
    ON documentos_tipodocumento(etapa_id)
    WHERE etapa_id IS NOT NULL;

COMMIT TRANSACTION;

-- ============================================================================
-- VERIFICACIÓN Y ANÁLISIS
-- ============================================================================
--
-- Ejecutar DESPUÉS de crear los índices:
--

-- Ver todos los índices creados:
-- SELECT schemaname, tablename, indexname, indexdef 
--   FROM pg_indexes 
--  WHERE tablename IN (
--    'postulantes_postulante',
--    'postulantes_postulacion',
--    'postulantes_notificacion',
--    'documentos_documentopostulacion',
--    'modalidades_modalidad'
--  ) AND indexname LIKE 'idx_%'
--  ORDER BY tablename, indexname;

-- Ver tamaño de los índices:
-- SELECT schemaname, tablename, indexname, pg_size_pretty(pg_relation_size(indexrelid)) AS size
--   FROM pg_indexes
--   JOIN pg_class ON pg_class.relname = indexname
--   WHERE tablename IN (
--     'postulantes_postulante',
--     'postulantes_postulacion',
--     'documentos_documentopostulacion'
--   )
--  ORDER BY pg_relation_size(indexrelid) DESC;

-- Analizar eficiencia de índices (después de usar):
-- SELECT schemaname, tablename, indexname, idx_scan, idx_tup_read, idx_tup_fetch
--   FROM pg_stat_user_indexes
--  WHERE schemaname = 'public'
--  ORDER BY idx_scan DESC;

-- ============================================================================
-- ROLLBACK (si es necesario)
-- ============================================================================
--
-- DROP INDEX IF EXISTS idx_postulante_carrera_v1;
-- DROP INDEX IF EXISTS idx_postulante_apellido_nombre_v1;
-- DROP INDEX IF EXISTS idx_postulante_usuario_v1;
-- DROP INDEX IF EXISTS idx_postulacion_estado_general_v1;
-- DROP INDEX IF EXISTS idx_postulacion_estado_general_titulado_v1;
-- DROP INDEX IF EXISTS idx_postulacion_gestion_estado_general_v1;
-- DROP INDEX IF EXISTS idx_postulacion_tutor_v1;
-- DROP INDEX IF EXISTS idx_postulacion_postulante_estado_v1;
-- DROP INDEX IF EXISTS idx_postulacion_fecha_postulacion_desc_v1;
-- DROP INDEX IF EXISTS idx_postulacion_fecha_estado_v1;
-- DROP INDEX IF EXISTS idx_documento_estado_v1;
-- DROP INDEX IF EXISTS idx_documento_estado_pendiente_v1;
-- DROP INDEX IF EXISTS idx_documento_estado_rechazado_v1;
-- DROP INDEX IF EXISTS idx_documento_postulacion_estado_v1;
-- DROP INDEX IF EXISTS idx_documento_fecha_subida_desc_v1;
-- DROP INDEX IF EXISTS idx_documento_revisado_por_v1;
-- DROP INDEX IF EXISTS idx_documento_tipo_estado_v1;
-- DROP INDEX IF EXISTS idx_notificacion_usuario_leida_v1;
-- DROP INDEX IF EXISTS idx_notificacion_usuario_leida_true_v1;
-- DROP INDEX IF EXISTS idx_notificacion_fecha_creacion_desc_v1;
-- DROP INDEX IF EXISTS idx_notificacion_usuario_fecha_v1;
-- DROP INDEX IF EXISTS idx_modalidad_activa_v1;
-- DROP INDEX IF EXISTS idx_etapa_modalidad_v1;
-- DROP INDEX IF EXISTS idx_tipodocumento_etapa_v1;

-- FIN DE SCRIPT
