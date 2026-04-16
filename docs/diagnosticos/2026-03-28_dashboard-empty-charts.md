# 🔍 DIAGNÓSTICO PUNTUAL: GRÁFICOS VACÍOS EN DASHBOARD

**Fecha**: 28 de Marzo 2026  
**Status**: ✅ DIAGNÓSTICO COMPLETADO - SIN CÓDIGOS MODIFICADOS

---

## 📊 RESUMEN EJECUTIVO

Los dos gráficos vacíos en el dashboard:
- ✅ **"Postulantes & Documentos por Semana"** → `barChartData`
- ✅ **"Progreso General (6 Meses)"** → `lineChartData`

**CAUSA RAÍZ**: No faltan datos en la BD. El problema es una **query/mapeo defectuoso en el backend** que **excluye el mes actual (Marzo)** de los datos retornados.

---

## 1️⃣ ENDPOINT IDENTIFICADO

### Url exacta que alimenta ambos gráficos:
```
GET /api/reportes/dashboard-chart-data/?meses=6
```

### Ubicación en código:
- **Backend**: `reportes/views.py` → `DashboardChartDataView.get()`
- **Función**: `reportes/services.py` → `get_dashboard_chart_data(meses=6)`

### JSON Esperado por Frontend:
El componente `Charts.jsx` espera esta estructura:

```javascript
{
  "barChartData": [
    { "semana": string, "postulantes": int, "documentos": int },
    ...
  ],
  "lineChartData": [
    { "mes": string, "graduados": int, "pendientes": int, "aprobados": int },
    ...
  ],
  "pieChartData": [...]
}
```

---

## 2️⃣ JSON REAL DEVUELTO POR BACKEND

> **Comando ejecutado**: `docker exec sistema_backend python manage.py shell` + diagnóstico

```json
{
  "lineChartData": [
    {"mes": "Sep", "graduados": 0, "pendientes": 0, "aprobados": 0},
    {"mes": "Oct", "graduados": 0, "pendientes": 0, "aprobados": 0},
    {"mes": "Nov", "graduados": 0, "pendientes": 0, "aprobados": 0},
    {"mes": "Dec", "graduados": 0, "pendientes": 0, "aprobados": 0},
    {"mes": "Jan", "graduados": 0, "pendientes": 0, "aprobados": 0},
    {"mes": "Feb", "graduados": 0, "pendientes": 0, "aprobados": 0}
  ],
  "barChartData": [
    {"semana": "Sem 1", "postulantes": 0, "documentos": 0},
    {"semana": "Sem 2", "postulantes": 0, "documentos": 0},
    {"semana": "Sem 3", "postulantes": 0, "documentos": 0},
    {"semana": "Sem 4", "postulantes": 0, "documentos": 0},
    {"semana": "Sem 5", "postulantes": 0, "documentos": 0},
    {"semana": "Sem 6", "postulantes": 0, "documentos": 0}
  ],
  "pieChartData": [
    {"name": "En Proceso", "value": 1, "color": "#f59e0b"},
    {"name": "Completado", "value": 1, "color": "#10b981"}
  ],
  "error": null
}
```

**CRÍTICO**: Los arrays NO están vacíos, están LLENOS pero con TODOS los valores = 0.

---

## 3️⃣ ESTADO DE LA BASE DE DATOS

### Datos de existencia:
```
Total Postulantes:   21
Total Postulaciones: 2
Total Documentos:    1
```

### Ubicación exacta de datos:
```
📋 TODAS LAS POSTULACIONES:
   1. ID 3: 2026-03-28 16:03:20 UTC | Estado: EN_PROCESO
   2. ID 2: 2026-03-28 15:55:22 UTC | Estado: TITULADO

📋 TODOS LOS DOCUMENTOS:
   1. ID 1: 2026-03-28 15:55:22 UTC | Estado: aprobado
```

---

## 4️⃣ CAMPOS DE FECHA UTILIZADOS

El backend usa estos campos para agrupar:

### Para Postulaciones:
```python
Postulacion.objects.filter(
    fecha_postulacion__gte=fecha_inicio,
    fecha_postulacion__lte=fecha_fin
).annotate(mes=TruncMonth('fecha_postulacion'))
```
**Campo**: `Postulacion.fecha_postulacion`

### Para Documentos:
```python
DocumentoPostulacion.objects.filter(
    fecha_subida__gte=fecha_inicio,
    fecha_subida__lte=fecha_fin
).annotate(mes=TruncMonth('fecha_subida'))
```
**Campo**: `DocumentoPostulacion.fecha_subida`

---

## 5️⃣ CAUSA RAÍZ EXACTA

### El Bug: Rango de 6 meses excluye el mes actual

**Código problemático** en `get_dashboard_chart_data()`:

```python
meses = 6
fecha_fin = timezone.now()      # 2026-03-28 23:54:33
fecha_inicio = fecha_fin - relativedelta(months=6)  # 2025-09-28 23:54:33

# Loop que SÓLO itera 6 veces:
for i in range(meses):  # i = 0, 1, 2, 3, 4, 5
    fecha = fecha_inicio + relativedelta(months=i)
    # Genera: Sep, Oct, Nov, Dec, Jan, Feb
    # ¿MARZO? NO - recién sería i=6, que está FUERA del loop
```

### Visualización del problema:

```
Semana 0 (i=0): 2025-09-28 → busca datos en TruncMonth(2025-09-01)
Semana 1 (i=1): 2025-10-28 → busca datos en TruncMonth(2025-10-01)
Semana 2 (i=2): 2025-11-28 → busca datos en TruncMonth(2025-11-01)
Semana 3 (i=3): 2025-12-28 → busca datos en TruncMonth(2025-12-01)
Semana 4 (i=4): 2026-01-28 → busca datos en TruncMonth(2026-01-01)
Semana 5 (i=5): 2026-02-28 → busca datos en TruncMonth(2026-02-01)

❌ MARZO (2026-03-01): NO INCLUIDO - sería i=6, loop termina en i=5
```

### Datos QuerySet EN MARZO (fuera del mapeo):

```
Query para MARZO:
   2026-03-01: postulantes=2  ✅ LOS DATOS EXISTEN
               documentos=1   ✅ LOS DATOS EXISTEN

Pero el loop SÓLOitera i=0 hasta i=5 (febrero)
Resultado: Todos los campos quedan en 0
```

---

## 6️⃣ CONFIRMACIÓN: Propiedades Frontend vs Backend

### Lo que Frontend espera (Charts.jsx):

```javascript
// Para barChartData
if (data.barChartData && data.barChartData.length > 0) {
  setBarChartData(data.barChartData);
}
// Propiedades esperadas: "semana", "postulantes", "documentos"

// Para lineChartData
if (data.lineChartData && data.lineChartData.length > 0) {
  setLineChartData(data.lineChartData);
}
// Propiedades esperadas: "mes", "graduados", "pendientes", "aprobados"
```

### Lo que Backend envía:

✅ **Propiedades correctas** (coinciden con frontend)  
✅ **Estructura correcta** (arrays con 6 elementos)  
❌ **Valores TODOS = 0** (porque mes de marzo no está en el rango)

---

## 7️⃣ TIPO DE PROBLEMA

```
┌─────────────────────────────────────────────────────────┐
│ ❌ ¿Falta real de datos?                                │
│    NO - Existen 2 postulaciones y 1 documento           │
│                                                          │
│ ❌ ¿Query backend?                                       │
│    La query SÍ obtiene los datos (marzo sí está en BD)   │
│                                                          │
│ ❌ ¿Serialización?                                       │
│    La serialización es correcta (propiedades correctas)  │
│                                                          │
│ ✅ ✅ ✅ ¿MAPEO Frontend/Backend?                        │
│    PARCIALMENTE - El backend mapea SÓLO 6 meses         │
│    cuando debería mapear "últimos 6 meses COMPLETOS"    │
│    incluyendo el mes actual                             │
│                                                          │
│ ✅ ✅ ✅ CLASE: BUG DE LÓGICA EN BACKEND                │
│    El rango de fechas excluye el mes actual             │
└─────────────────────────────────────────────────────────┘
```

---

## 📋 RESUMEN PARA ARREGLAR (referencia, no implementado)

| Aspecto | Valor |
|---------|-------|
| **Endpoint** | `/api/reportes/dashboard-chart-data/?meses=6` |
| **Función Backend** | `reportes/services.py:get_dashboard_chart_data()` |
| **Campo Postulaciones** | `Postulacion.fecha_postulacion` |
| **Campo Documentos** | `DocumentoPostulacion.fecha_subida` |
| **Problema** | Rango hace_6_meses...ahora excluye mes actual en iteración |
| **Causa** | `for i in range(meses)` genera 0...5, datos en i=6 |
| **Solución Potencial** | Cambiar lógica: `for i in range(-meses, 0)` o usar `fecha_fin - relativedelta(months=meses-1)` |
| **Verificado con** | Docker exec + Django shell + queryset real |

---

## ✅ CONCLUSIÓN

**El dashboard muestra gráficos "vacíos" porque el backend deliberadamente excluye el mes actual (Marzo) del rango de 6 meses solicitado.**

Los datos SÍ existen en la BD, la serialización es correcta, el mapeo de propiedades es correcto. El problema es una **lógica de iteración off-by-one en el cálculo de rango temporal**.

