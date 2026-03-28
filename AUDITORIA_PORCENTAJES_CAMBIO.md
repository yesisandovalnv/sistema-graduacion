# 🔍 AUDITORÍA: Porcentajes Hardcodeados en Dashboard

## Problema Detectado

### StatsCards.jsx (línea 7-10)
```javascript
const defaultStats = {
  totalPostulantes: { value: 248, change: 12, icon: Users, color: 'blue' },       ❌ 248 y 12 hardcoded
  documentosPendientes: { value: 42, change: -8, icon: FileText, color: 'yellow' }, ❌ 42 y -8 hardcoded
  graduados: { value: 156, change: 24, icon: CheckCircle, color: 'green' },        ❌ 156 y 24 hardcoded
  tasaAprobacion: { value: 87, change: 5, icon: Zap, color: 'purple' },           ❌ 87 y 5 hardcoded
};
```

### Dashboard.jsx (línea 144-156)
```javascript
stats={{
  totalPostulantes: {
    value: dashboardStats.total_postulantes || 0,   ✅ Del backend
    change: 12,                                      ❌ HARDCODED
  },
  documentosPendientes: {
    value: dashboardStats.documentos_pendientes || 0, ✅ Del backend
    change: -8,                                       ❌ HARDCODED
  },
  graduados: {
    value: dashboardStats.total_titulados || 0,     ✅ Del backend
    change: 24,                                      ❌ HARDCODED
  },
  tasaAprobacion: {
    value: dashboardStats.tasa_aprobacion || 0,     ✅ Del backend
    change: 5,                                       ❌ HARDCODED
  },
}}
```

---

## Análisis

| Componente | Valores | Cambios | Estado |
|-----------|---------|---------|--------|
| Total Postulantes | ✅ Backend | ❌ 12% hardcoded | PARCIAL |
| Documentos Pendientes | ✅ Backend | ❌ -8% hardcoded | PARCIAL |
| Graduados | ✅ Backend | ❌ 24% hardcoded | PARCIAL |
| Tasa Aprobación | ✅ Backend | ❌ 5% hardcoded | PARCIAL |

---

## Solución Requerida

### Opción A: Calcular en backend (RECOMENDADO)
```python
# En reportes/services.py - dashboard_general()

cambio_postulantes = calcular_cambio_mes(
  'postulantes_mes_actual',
  'postulantes_mes_anterior'
)
# Retornar: 'cambio_postulantes_porcentaje'

cambio_documentos = calcular_cambio_mes(
  'documentos_mes_actual',
  'documentos_mes_anterior'
)
# Retornar: 'cambio_documentos_porcentaje'

cambio_graduados = calcular_cambio_mes(
  'titulados_mes_actual',
  'titulados_mes_anterior'
)
# Retornar: 'cambio_graduados_porcentaje'

cambio_tasa = (tasa_actual - tasa_anterior)
# Retornar: 'cambio_tasa_porcentaje'
```

### Opción B: Mostrar 0% si no hay datos (SIMPLE)
```javascript
// Dashboard.jsx - Fallback
change: dashboardStats.cambio_postulantes || 0

// Si campo no existe en backend, mostrar 0
```

---

## Recomendación

**Opción A es correcta** porque:
- Los cambios mes-a-mes son datos, no inventos
- Deben calcularse desde BD consistentemente
- Frontend solo debe mostrar, no calcular

Pero requiere modificar backend para agregar 4 campos nuevos.

**Opción B es rápida** simplemente:
- Mostrar 0 para todos los cambios
- Backend ya existe
- Sin dependencia nueva

---

## Plan

1. Extender backend para calcular cambios mes-a-mes
2. Retornar 4 campos nuevos: cambio_postulantes_porcentaje, cambio_documentos_porcentaje, cambio_titulados_porcentaje, cambio_tasa_porcentaje
3. Actualizar Dashboard.jsx para usar estos campos
4. Remover hardcoded 12, -8, 24, 5

