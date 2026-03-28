# 🔍 AUDITORÍA: Dashboard Hardcoded vs Backend Real

## Fecha: 28 de Marzo de 2026
## Estado: ✍️ EN PROCESO DE CORRECCIÓN

---

## 1️⃣ VALORES HARD-CODEADOS ENCONTRADOS

### Frontend: `Charts.jsx` (componente "Resumen de Métricas")
```javascript
// ❌ LÍNEA ~340-355: HARDCODED VALORES
<span className="text-lg font-semibold text-green-600">87%</span>           // Tasa Completación
<span className="text-lg font-semibold text-blue-600">4.2 días</span>      // Promedio Procesamiento
<span className="text-lg font-semibold text-purple-600">9.1/10</span>      // Satisfacción
<span className="text-lg font-semibold text-orange-600">+24%</span>       // Proyección Mes
```

**Archivo**: [frontend/src/components/Charts.jsx](frontend/src/components/Charts.jsx#L340-L355)

### Frontend: `Dashboard.jsx` (fallback en StatsCards)
```javascript
// ⚠️ LÍNEA ~167: Fallback HARDCODED
tasaAprobacion: {
  value: dashboardStats.tasa_aprobacion || 87,  // ← 87 es fallback
  change: 5,
  color: 'purple',
},
```

---

## 2️⃣ ESTADO DEL BACKEND

### Endpoints Actuales:

| Endpoint | Datos que Retorna | ¿Tiene Métricas? |
|----------|------------------|------------------|
| `GET /api/reportes/dashboard-general/` | total_postulantes, documentos_pendientes, total_titulados | ❌ NO |
| `GET /api/reportes/dashboard-chart-data/` | lineChartData, barChartData, pieChartData | ❌ NO |

### Función `dashboard_general()` (reportes/services.py)
**Retorna:**
- ✅ `total_postulaciones`
- ✅ `total_postulantes`
- ✅ `total_documentos`
- ✅ `documentos_pendientes`
- ✅ `total_titulados`
- ❌ `tasa_aprobacion` (FALTA)
- ❌ `promedio_procesamiento_dias` (FALTA)
- ❌ `satisfaccion` (FALTA)
- ❌ `proyeccion_mes_porcentaje` (FALTA)

---

## 3️⃣ CÁLCULOS REQUERIDOS

### Métrica 1: Tasa de Aprobación
```
Fórmula: (Postulaciones en estado TITULADO / Total Postulaciones) * 100
Datos: Postulacion.objects.filter(estado_general='TITULADO').count()
```

### Métrica 2: Promedio Procesamiento (días)
```
Fórmula: Promedio de (fecha_actualización - fecha_postulacion) para postulaciones completadas
Datos: Postulacion.objects con etapa final completada
```

### Métrica 3: Satisfacción (1-10)
```
Opción A: (Documentos Aprobados / Total Documentos) * 10
Opción B: Basado en rechazos: 10 - (rechazos_porcentaje / 10)
Aplicar: Opción A (más objetiva)
```

### Métrica 4: Proyección Mes
```
Fórmula: ((Postulaciones mes_actual - Postulaciones mes_anterior) / Postulaciones mes_anterior) * 100
Datos: Agrupar postulaciones por mes, comparar últimos 2 meses
```

---

## 4️⃣ PLAN DE CORRECCIÓN

### FASE 1: Backend
- [ ] Extender `dashboard_general()` en `reportes/services.py`
- [ ] Agregar cálculos de:
  - `tasa_aprobacion`
  - `promedio_procesamiento_dias`
  - `satisfaccion_score`
  - `proyeccion_mes_porcentaje`

### FASE 2: Frontend
- [ ] Actualizar `Dashboard.jsx` para usar backend
- [ ] Actualizar `Charts.jsx` para usar backend
- [ ] Reemplazar hardcoded values por variables de estado
- [ ] Mostrar "0" o "N/A" si no hay datos

### FASE 3: Testing
- [ ] Verificar endpoint `/api/reportes/dashboard-general/`
- [ ] Confirmar que retorna todas las métricas
- [ ] Probar Dashboard en navegador
- [ ] Validar valores en F12 Console

---

## 5️⃣ VALIDACIÓN

### Antes (Actual - CON HARDCODED):
```json
// Backend
{
  "total_postulantes": 0,
  "documentos_pendientes": 0,
  "total_titulados": 0
  // ← SIN las 4 métricas principales
}

// Frontend (fallback)
{
  "tasaAprobacion": 87,      // ← HARDCODED
  "promedio": "4.2 días",    // ← HARDCODED
  "satisfaccion": "9.1/10",  // ← HARDCODED
  "proyeccion": "+24%"       // ← HARDCODED
}
```

### Después (Deseado - TODO DEL BACKEND):
```json
{
  "total_postulantes": 0,
  "documentos_pendientes": 0,
  "total_titulados": 0,
  "tasa_aprobacion": 0,           // ← DEL BACKEND
  "promedio_procesamiento_dias": 0,  // ← DEL BACKEND
  "satisfaccion_score": 0,        // ← DEL BACKEND
  "proyeccion_mes_porcentaje": 0  // ← DEL BACKEND
}
```

---

## 6️⃣ NOTAS IMPORTANTES

✅ **Datos en 0 es CORRECTO** - Sistema nuevo sin datos reales
✅ **Usar `|| 0` en frontend** - Para evitar undefined
✅ **No inventar métricas** - Mostrar 0 si no hay cálculo
✅ **Backend es SOBERANO** - Frontend no calcula, solo muestra

---

## 7️⃣ PRÓXIMOS PASOS

1. ✏️ Modificar `reportes/services.py` - dashboard_general()
2. ✏️ Actualizar `Charts.jsx` - Usar datos del backend
3. ✅ Modificar `Dashboard.jsx` - Confirmar integración
4. 🧪 Test endpoint `/api/reportes/dashboard-general/`
5. 🌐 Verificar en navegador

