# 🔍 DIAGNÓSTICO PRECISO: PIE CHART DEL DASHBOARD

## 1. DE DÓNDE SALEN LOS DATOS ACTUALMENTE

### Opción A: PIE CHART MUESTRA 45%, 30%, 15%, 10% (MOCK)

**Línea exacta donde se define:**
[Charts.jsx línea 28-32](frontend/src/components/Charts.jsx#L28)

```javascript
const mockPieChartData = [
  { name: 'Completado', value: 45, color: '#10b981' },    // ← 45%
  { name: 'En Proceso', value: 30, color: '#f59e0b' },    // ← 30%
  { name: 'Por Revisar', value: 15, color: '#3b82f6' },   // ← 15%
  { name: 'Rechazado', value: 10, color: '#ef4444' },     // ← 10%
];
```

**Inicialización:**
[Charts.jsx línea 41](frontend/src/components/Charts.jsx#L41)

```javascript
const [pieChartData, setPieChartData] = useState(mockPieChartData);
```

**¿Por qué se queda con estos valores fijos (45, 30, 15, 10)?**
Significa que `setPieChartData()` NO se llegó a llamar en el useEffect.

---

### Opción B: PIE CHART MUESTRA 30%, 30%, 24%, 16% (REAL)

**Línea exacta donde se asignan los datos reales:**
[Charts.jsx línea 81-92](frontend/src/components/Charts.jsx#L81)

```javascript
if (data.pieChartData) {  // ← LÍNEA 81: Verifica si backend devuelve datos
  console.log('✅ [STATE] setPieChartData from backend (raw counts):', data.pieChartData);
  
  // Transform counts to percentages (Línea 85-89)
  const total = data.pieChartData.reduce((sum, item) => sum + (item.value || 0), 0);
  const pieDataWithPercentages = data.pieChartData.map(item => ({
    ...item,
    value: total > 0 ? Math.round((item.value / total) * 100 * 10) / 10 : 0
  }));
  
  console.log('✅ [STATE] setPieChartData with percentages:', pieDataWithPercentages);
  setPieChartData(pieDataWithPercentages);  // ← LÍNEA 92: Se EJECUTA SI backend tiene datos
}
```

---

## 2. ¿ESTÁ HARDCODEADO? ANÁLISIS

### ❌ VALORES HARDCODEADOS ENCONTRADOS:
- **Línea 28-32**: mockPieChartData = [45, 30, 15, 10] ← VALORES FIJOS

### ✅ VALORES QUE VIENEN DEL BACKEND:
- **Línea 81**: if (data.pieChartData) ← Verifica si backend devuelve (depende del backend, no del código)
- **Línea 85-92**: Transforma counts del backend a porcentajes (código dinámico)

---

## 3. ¿SE USA CHARTDATA DEL BACKEND EN PIE CHART?

### Flujo Esperado:

```
1. useEffect (línea 43-100) ejecuta
   ├─ Línea 45: const token = localStorage.getItem('access_token')
   │  └─ SI NO HAY TOKEN: retorna (line 47-48) ⚠️
   │
   ├─ Línea 51: fetch('/api/reportes/dashboard-chart-data/?meses=6')
   │
   ├─ Línea 58: if (response.ok) { ... }
   │  └─ SI response NO ES 200: no ejecuta (line 101) ⚠️
   │
   ├─ Línea 81: if (data.pieChartData) { 
   │  └─ SI backend NO devuelve pieChartData: no ejecuta ⚠️
   │
   └─ Línea 92: setPieChartData(pieDataWithPercentages)
      └─ SI LLEGA AQUI: pie chart ACTUALIZA con datos del backend ✅
```

### Datos del Backend (cuando funciona):

Backend devuelve:
```python
{
  "pieChartData": [
    {"name": "Rechazado", "value": 15, "color": "#ef4444"},
    {"name": "Completado", "value": 15, "color": "#10b981"},
    {"name": "En Proceso", "value": 12, "color": "#f59e0b"},
    {"name": "Por Revisar", "value": 8, "color": "#3b82f6"},
  ]
}
```

Frontend transforma a:
```javascript
[
  {"name": "Rechazado", "value": 30.0, ...},      // 15/50*100
  {"name": "Completado", "value": 30.0, ...},    // 15/50*100
  {"name": "En Proceso", "value": 24.0, ...},    // 12/50*100
  {"name": "Por Revisar", "value": 16.0, ...},   // 8/50*100
]
```

---

## 4. LÍNEA EXACTA DONDE SE DEFINE PIEDATA

**mockPieData** (valores fijos):
[frontend/src/components/Charts.jsx línea 28-32](frontend/src/components/Charts.jsx#L28)

```javascript
const mockPieChartData = [
  { name: 'Completado', value: 45, color: '#10b981' },
  { name: 'En Proceso', value: 30, color: '#f59e0b' },
  { name: 'Por Revisar', value: 15, color: '#3b82f6' },
  { name: 'Rechazado', value: 10, color: '#ef4444' },
];
```

**pieChartData state** (lo que realmente renderiza):
[frontend/src/components/Charts.jsx línea 41](frontend/src/components/Charts.jsx#L41)

```javascript
const [pieChartData, setPieChartData] = useState(mockPieChartData);
```

**Actualización desde backend**:
[frontend/src/components/Charts.jsx línea 92](frontend/src/components/Charts.jsx#L92)

```javascript
setPieChartData(pieDataWithPercentages);
```

---

## 5. ¿VALORES FIJOS O BACKEND?

### Si pieChartData usa:

| Escenario | Condición | Resultado |
|-----------|-----------|-----------|
| ❌ Valores Fijos | `setPieChartData` NO se ejecuta | Muestra 45%, 30%, 15%, 10% (mock) |
| ✅ Backend | `setPieChartData` SÍ se ejecuta | Muestra 30%, 30%, 24%, 16% (real) |

### Checklist para verificar cuál es el caso:

```
1. Abre F12 → Console
2. Busca logs que empiezan con "✅ [STATE]"
   
   SI VES:
   ✅ [STATE] setPieChartData from backend (raw counts): [...]
   ✅ [STATE] setPieChartData with percentages: [...]
   → BACKEND SE ESTÁ USANDO ✅
   
   SI NO VES estos logs:
   → BACKEND NO SE ESTÁ USANDO ❌
   → Pie chart mostrado MOCKDATA ❌

3. Alterna logs a buscar:
   ❌ [DEBUG] No token available, using mock data
   ❌ [DEBUG] Backend returned non-200 status
   ❌ [DEBUG] Chart data fetch error
   
   SI VES alguno → EXPLICA por qué useEffect se detiene
```

---

## 📊 CONCLUSIÓN

| Parte del Código | Estado |
|------------------|--------|
| ✅ mockPieChartData (hardcoded) | En línea 28-32 |
| ✅ useState(mockPieChartData) | En línea 41 |
| ✅ useEffect fetch | En línea 43-100 |
| ✅ Transformación backend→porcentajes | En línea 85-92 |
| ✅ setPieChartData call | En línea 92 |
| ✅ Pie chart (renderiza pieChartData) | En línea 221 |

**EL CÓDIGO ESTÁ CORRECTO** para usar datos del backend.

**El problema está en la EJECUCIÓN del useEffect** (una de las 5 causas mencionadas).

---

## 🔧 Para Verificar Exactamente Qué Está Pasando

1. **Abre dashboard**: http://localhost:5173/dashboard
2. **F12 → Console**
3. **Busca uno de estos patrones**:

   ```
   ❌ "No token available"         → Agrega token a localStorage
   ❌ "Backend returned non-200"   → Backend tiene error
   ❌ "Chart data fetch error"     → Error en fetch
   ✅ "with percentages: [30, 30, 24, 16]" → TODO FUNCIONA
   ```

4. **Si ves valores en console**:
   ```
   [30.0, 30.0, 24.0, 16.0]  → Pie chart DEBE mostrar estos (no 45, 30, 15, 10)
   [45, 30, 15, 10]          → Pie chart muestra MOCK
   ```

---

**Status**: Diagnóstico completado. Código está bien, falta ejecutancia.

