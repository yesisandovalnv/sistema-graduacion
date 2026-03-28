# ✅ REVISIÓN: Métrica Satisfacción - N/A cuando sin datos

**Fecha:** 28 de Marzo de 2026  
**Problema Resuelto:** Satisfacción mostraba "0/10" cuando no había datos (interpretable como mala, no como ausencia)  
**Solución Implementada:** Mostrar "N/A" cuando no hay documentos  

---

## 📋 Problema Original

Cuando el sistema no tenía documentos:
- Backend retornaba: `satisfaccion_score: 0.0`
- Frontend mostraba: **"0/10"** ❌
- Interpretación: Mala satisfacción (cuando en realidad = sin datos)

---

## ✅ Solución Implementada

### 1. Backend: `reportes/services.py`

**CAMBIO 1: Asignar "N/A" cuando no hay documentos**

```python
# ANTES
satisfaccion_score = 0.0
try:
    if total_documentos > 0:
        satisfaccion_score = round((docs_aprobados / total_documentos) * 10, 2)
        satisfaccion_score = min(satisfaccion_score, 10.0)
    print(f"✅ Satisfacción: {satisfaccion_score}/10 ({docs_aprobados}/{total_documentos})")
except Exception as e:
    print(f"⚠️ Error calculando satisfaccion: {e}")
    satisfaccion_score = 0.0  # ❌ Devolvía 0.0

# DESPUÉS
satisfaccion_score = "N/A"
try:
    if total_documentos > 0:
        satisfaccion_score = round((docs_aprobados / total_documentos) * 10, 2)
        satisfaccion_score = min(satisfaccion_score, 10.0)
        print(f"✅ Satisfacción: {satisfaccion_score}/10 ({docs_aprobados}/{total_documentos})")
    else:
        print(f"ℹ️  Satisfacción: N/A (sin documentos para calcular)")  # ✅ Nuevo
except Exception as e:
    print(f"⚠️ Error calculando satisfaccion: {e}")
    satisfaccion_score = "N/A"  # ✅ Devuelve N/A en error
```

**CAMBIO 2: Actualizar response JSON**

```python
# En el return final del endpoint
return {
    ...
    'satisfaccion_score': satisfaccion_score,  # N/A si sin datos, número si con datos
    ...
}

# En el exception handler (safety net)
'satisfaccion_score': "N/A",  # N/A por defecto (sin datos)
```

### 2. Frontend: `Charts.jsx`

**CAMBIO 1: Actualizar estado de métricas**

```javascript
// ANTES
setMetrics({
  tasaAprobacion: metricsData.tasa_aprobacion || 0,
  promedioProcesamiento: metricsData.promedio_procesamiento_dias || 0,
  satisfaccion: metricsData.satisfaccion_score || 0,  // ❌ 0 por defecto
  proyeccionMes: metricsData.proyeccion_mes_porcentaje || 0,
});

// DESPUÉS
setMetrics({
  tasaAprobacion: metricsData.tasa_aprobacion || 0,
  promedioProcesamiento: metricsData.promedio_procesamiento_dias || 0,
  satisfaccion: metricsData.satisfaccion_score || "N/A",  // ✅ N/A por defecto
  proyeccionMes: metricsData.proyeccion_mes_porcentaje || 0,
});
```

**CAMBIO 2: Actualizar fallback en error**

```javascript
// ANTES
setMetrics({
  tasaAprobacion: 0,
  promedioProcesamiento: 0,
  satisfaccion: 0,  // ❌ 0 por defecto en error
  proyeccionMes: 0,
});

// DESPUÉS
setMetrics({
  tasaAprobacion: 0,
  promedioProcesamiento: 0,
  satisfaccion: "N/A",  // ✅ N/A por defecto en error
  proyeccionMes: 0,
});
```

**CAMBIO 3: Mostrar "N/A" en renderización**

```jsx
// ANTES
<span className="text-lg font-semibold text-purple-600 dark:text-purple-400">
  {metrics.satisfaccion || 0}/10   {/* ❌ Mostraba "0/10" */}
</span>

// DESPUÉS
<span className="text-lg font-semibold text-purple-600 dark:text-purple-400">
  {metrics.satisfaccion === "N/A" ? "N/A" : `${metrics.satisfaccion || 0}/10`}  {/* ✅ N/A o valor/10 */}
</span>
```

---

## ✅ Validación

Script ejecutado: `validar_satisfaccion_na.py`

### Resultados:
```
✅ Satisfacción (sin datos): N/A
   Tipo: <class 'str'>
   ¿Es 'N/A'? True

✅ ✅ ✅ CORRECTO: Satisfacción retorna 'N/A' cuando no hay datos
✅ Todos los 11 campos presentes en respuesta JSON
✅ Regla implementada: sin datos → N/A | con datos → valor/10
```

---

## 📊 Comportamiento Final

### Caso 1: Sistema sin datos (tabla Postulacion vacía)
```json
{
  "satisfaccion_score": "N/A"  ← String "N/A" en lugar de 0.0
}
```
**Frontend muestra:** `N/A` ✅

### Caso 2: Sistema con datos (ej: 8 docs aprobados de 10)
```json
{
  "satisfaccion_score": 8.0
}
```
**Frontend muestra:** `8.0/10` ✅

### Caso 3: Error en backend
```json
{
  "satisfaccion_score": "N/A"  ← Fallback seguro
}
```
**Frontend muestra:** `N/A` ✅

---

## 🎯 Regla Implementada

✅ **Con datos reales** → Mostrar `valor/10` (ej: `8.0/10`)  
✅ **Sin datos** → Mostrar `N/A` (no inventar 0)  
✅ **En error** → Fallback seguro a `N/A` (no crash)  

---

## 📁 Archivos Modificados

1. ✏️ `reportes/services.py` - Función `dashboard_general()`
   - Líneas 177-187: Cambio de 0.0 a "N/A"
   - Línea 366: Response dict actualizado (comentario)
   - Línea 396: Exception handler actualizado (comentario)

2. ✏️ `frontend/src/components/Charts.jsx`
   - Línea 148: `setMetrics()` con "N/A"
   - Línea 160: Fallback error con "N/A"
   - Línea 340: Renderización condicional para "N/A"

3. ✅ `validar_satisfaccion_na.py` - Script de validación (NUEVO)

---

## 🔗 Contexto

Este cambio es parte de la **Unificación del Dashboard** donde se elimina TODO hardcode visual. Ahora:
- ✅ Valores principales: Backend
- ✅ Cambios mes-a-mes: Backend
- ✅ Métricas secundarias: Backend
- ✅ Indicador de ausencia de datos: N/A (no inventados)

**Cuanto más clara la interfaz, mejor la UX. 0/10 confunde; N/A comunica realidad.**

