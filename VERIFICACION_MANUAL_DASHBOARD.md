# 🎯 GUÍA DE VERIFICACIÓN MANUAL - Dashboard Unificado

## Paso 1: Verificar que el Backend genera las métricas

En una terminal con venv activado:
```bash
cd c:\Users\luisfer\Documents\Visual-Code\sistema-graduacion
python manage.py shell
```

Dentro del shell:
```python
from reportes.services import dashboard_general
result = dashboard_general()
print(f"Tasa Aprobación: {result['tasa_aprobacion']}%")
print(f"Promedio Procesamiento: {result['promedio_procesamiento_dias']} días")
print(f"Satisfacción: {result['satisfaccion_score']}/10")
print(f"Proyección Mes: {result['proyeccion_mes_porcentaje']}%")
```

**Esperado:**
```
Tasa Aprobación: 0.0%
Promedio Procesamiento: 0.0 días
Satisfacción: 0.0/10
Proyección Mes: 0.0%
```

✅ Todas las métricas presentes (0 es correcto para sistema nuevo)

---

## Paso 2: Abrir Dashboard en el Navegador

1. Abre: http://localhost:5173/dashboard
2. Abre F12 (DevTools)
3. Ve a la pestaña NETWORK
4. Actualiza la página (F5)
5. Busca en Network por `dashboard-general`

**Esperado:**
```
Status: 200 OK
Response Headers: Content-Type: application/json
Response Body: {
  "total_postulantes": 0,
  "tasa_aprobacion": 0.0,
  "promedio_procesamiento_dias": 0.0,
  "satisfaccion_score": 0.0,
  "proyeccion_mes_porcentaje": 0.0
  ...
}
```

✅ Endpoint respondiendo con status 200

---

## Paso 3: Verificar que el Dashboard muestra las métricas

En la misma página, mira el panel "Resumen de Métricas" (derecha inferior)

**ANTES (❌ Hardcoded):**
- Tasa Completación: **87%**
- Promedio Procesamiento: **4.2 días**
- Satisfacción: **9.1/10**
- Proyección Mes: **+24%**

**DESPUÉS (✅ Del Backend):**
- Tasa de Aprobación: **0%** (o el valor real si hay postulaciones)
- Promedio Procesamiento: **0 días**
- Satisfacción: **0/10**
- Proyección Mes: **0%**

---

## Paso 4: Verificar en Console (F12)

En DevTools → Console, deberías ver logs como:

```
📊 [METRICS] CARGANDO MÉTRICAS DEL BACKEND
✅ [METRICS] Datos recibidos del backend:
   - tasa_aprobacion: 0
   - promedio_procesamiento_dias: 0
   - satisfaccion_score: 0
   - proyeccion_mes_porcentaje: 0
✅ [METRICS] Métricas actualizadas en el componente
```

✅ Frontend cargando y mostrando métricas correctamente

---

## Resumen de Validación

| Punto de Verificación | Estado | Si Falla |
|----------------------|--------|----------|
| Backend genera 4 métricas | ✅ | Revisar `reportes/services.py` |
| Frontend carga estado `metrics` | ✅ | Revisar `Charts.jsx` - states |
| Endpoint retorna datos | ✅ | Revisar logs en `docker logs sistema_backend` |
| Dashboard muestra valores | ✅ | Abrir F12 Console y revisar logs |
| Valores son 0 (no hardcoded) | ✅ | Comparar con valores anteriores (87%, 4.2, etc.) |

---

## 🎉 Conclusión

✅ **Dashboard completamente unificado**
✅ **Cero hardcoded values**
✅ **Todas las métricas vienen del backend**
✅ **Listo para data real**

