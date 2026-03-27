# 🚀 GUÍA VISUAL: Cómo Ejecutar el Sistema

## 📍 TÚ ESTÁS AQUÍ → `c:\Users\luisfer\Documents\Visual-Code\sistema-graduacion`

---

## ⚡ FORMA MÁS FÁCIL: El Menú Interactivo 

### **PASO 1: Abre PowerShell en la carpeta del proyecto**

Si estás en VS Code:
1. Terminal → New Terminal (Ctrl + `)
2. Asegúrate que estés en la carpeta raíz del proyecto
   ```
   C:\Users\luisfer\Documents\Visual-Code\sistema-graduacion>
   ```

### **PASO 2: Ejecuta el script de inicio**

Copia y pega esto:
```powershell
.\start.ps1
```

### **PASO 3: Elige tu opción**

```
╔════════════════════════════════════════════════════════════════╗
║              🎓 SISTEMA DE GRADUACIÓN - LAUNCHER            ║
╚════════════════════════════════════════════════════════════════╝

¿En qué modo quieres ejecutar el sistema?

  [1] 💻  MODO DESARROLLO
      - Frontend en tu máquina con hot-reload
      - Backend + BD en Docker
      - ⚡ Mejor para programar

  [2] 🐳 MODO FULL DOCKER (Producción)
      - TODO en contenedores
      - Frontend compilado + Nginx
      - 📦 Mejor para demostración/producción

  [3] 📖 VER GUÍA COMPLETA

Elige opción [1/2/3]:
```

---

## 💻 OPCIÓN 1: MODO DESARROLLO (Recomendado para programar)

### Si elegiste `[1]`

El script automáticamente:
1. ✅ Verifica que `.env` existe
2. ✅ Levanta PostgreSQL en Docker
3. ✅ Levanta Backend (Django) en Docker
4. ✅ Te muestra en pantalla dónde está Backend

### **Esperas a ver esto:**
```
----- Backend LISTO -----
✓ Sistema en puerto 8000
✓ Conectado a PostgreSQL
```

### **PUIS ABRE OTRA TERMINAL (Ctrl + Shift + `):**

```powershell
cd frontend
npm install    # Solo primera vez
npm run dev
```

### **Esperas a ver:**
```
VITE v5.x.x  ready in XXX ms

➜  Local:   http://localhost:5173/
➜  press h + enter to show help
```

### **🎉 YA LO TIENES TODO LISTO!**

Abre en tu navegador:
- **Frontend:** http://localhost:5173 ← **AQUÍ PROGRAMAS** ⭐
- **Backend:** http://localhost:8000
- **Admin:** http://localhost:8000/admin

---

## 🐳 OPCIÓN 2: MODO FULL DOCKER (Producción)

### Si elegiste `[2]`

El script automáticamente:
1. ✅ Limpia contenedores viejos
2. ✅ Construye imágenes (Frontend + Backend)
3. ✅ Levanta TODO: DB + Backend + Frontend + Nginx

### **Esperas a ver (30-60 segundos):**
```
╔════════════════════════════════════════════════════════════════╗
║                    ✅ SISTEMA LISTO                          ║
╚════════════════════════════════════════════════════════════════╝

🌐 ACCESO:
  • Frontend: http://localhost:5173
  • Backend (Nginx): http://localhost:80
  • Backend (directo): http://localhost:8000
  • Admin Django: http://localhost:8000/admin
```

### **🎉 YA LO TIENES TODO LISTO!**

Abre en tu navegador:
- **Frontend:** http://localhost:5173
- **Nginx:** http://localhost:80 (proxy inverso)

---

## 📖 OPCIÓN 3: Ver Guía Completa

Si elegiste `[3]`, se abre automáticamente:
- **[MODOS_EJECUCION.md](MODOS_EJECUCION.md)** - Guía 100% completa con troubleshooting

---

## 🔄 Cambiar entre Modos

### De Modo 1 → Modo 2

**Terminal 1 (Backend en Docker):** Presiona `Ctrl + C`

**Luego ejecuta:**
```powershell
.\run_modo2_prod.ps1
```

### De Modo 2 → Modo 1

**Presiona `Ctrl + C` en la terminal principal**

**Luego ejecuta:**
```powershell
.\run_modo1_dev.ps1
# En otra terminal:
cd frontend && npm run dev
```

---

## 🛑 Detener Todo

### **Opción 1: Presionar Ctrl + C** (más sencillo)
En la terminal donde corre el sistema, presiona `Ctrl + C`

### **Opción 2: Script de Parada**
```powershell
.\stop_sistema.ps1
```

---

## 🔍 Verificar que Todo Esté Correcto

### ✅ Docker está corriendo
```powershell
docker ps
```
Debe mostrar contenedores en ejecución

### ✅ Backend está en línea
En tu navegador: **http://localhost:8000**
Debe mostrar la página de Django

### ✅ Frontend está en línea
En tu navegador: **http://localhost:5173**
Debe mostrar la aplicación React

### ✅ Base de datos está conectada
En el navegador: **http://localhost:8000/admin**
Si puedes acceder, la BD funciona

---

## ⚠️ Problemas Comunes

### ❌ "No puedo ejecutar scripts"
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
# Luego responde: Y (yes)
```

### ❌ Puerto 5173 o 8000 ocupado
```powershell
# Ve qué usa el puerto:
netstat -ano | findstr :8000
# Entonces mata ese proceso:
taskkill /PID <numero> /F
```

### ❌ Docker no está corriendo
- Abre Docker Desktop desde Windows
- O reinicia Docker desde sistema

### ❌ Frontend no se conecta a Backend
1. Verifica que backend esté en docker:
   ```powershell
   docker compose ps backend
   ```
2. Verifica que frontend/.env.development tiene:
   ```
   VITE_API_URL=http://localhost:8000/api
   ```

---

## 📚 Referencias Rápidas

### Carpeta Proyecto
```
c:\Users\luisfer\Documents\Visual-Code\sistema-graduacion
├── run_modo1_dev.ps1         ← Script Modo 1
├── run_modo2_prod.ps1        ← Script Modo 2  
├── start.ps1                 ← Menú (COMIENZA AQUÍ)
├── stop_sistema.ps1          ← Detener todo
├── MODOS_EJECUCION.md        ← Guía completa
├── docker-compose.yml        ← Configuración Docker
├── .env                       ← Variables globales
└── frontend/
    ├── .env.development      ← Variables Modo 1
    ├── .env.production       ← Variables Modo 2
    └── src/
```

### Comandos útiles (Si necesitas terminal)
```powershell
# Ver logs del backend
docker compose logs -f backend

# Ver logs del frontend
docker compose logs -f frontend

# Acceder a base de datos
docker compose exec db psql -U sistema_user -d sistema_graduacion

# Reiniciar solo backend
docker compose restart backend

# Limpiar TODO (¡cuidado! borra BD)
docker compose down -v
```

---

## 🎯 Resumen

| Necesitas | Comando |
|-----------|---------|
| Empezar rápido | `.\start.ps1` |
| Modo Desarrollo | `.\run_modo1_dev.ps1` |
| Modo Producción | `.\run_modo2_prod.ps1` |
| Detener todo | `.\stop_sistema.ps1` |
| Ver guía completa | Ver `MODOS_EJECUCION.md` |

---

**Created:** 2026-03-24 | **Last Updated:** 2026-03-24

¡Ahora está listo para usarlo! Cualquier duda, consulta [MODOS_EJECUCION.md](MODOS_EJECUCION.md) 🚀
