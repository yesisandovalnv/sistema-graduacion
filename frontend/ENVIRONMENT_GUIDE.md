# Guía de Configuración de Variables de Entorno (Frontend)

## 📋 Resumen Rápido

| Modo | Comando | Archivo | VITE_API_URL |
|------|---------|---------|--------------|
| **Desarrollo Local** | `npm run dev` | `.env.development` | `http://localhost:8000/api` |
| **Producción (Docker)** | `docker build` | `.env.production` | `http://backend:8000/api` |

---

## 🔍 ¿Cómo Vite Carga Variables?

Vite carga automáticamente en este orden:

```
1. .env               (base, siempre)
2. .env.{mode}       (específico del modo)
3. Variables globales (solo las que comienzan con VITE_)
```

### Ejemplo

```bash
# Con npm run dev:
1. Lee .env.example (base)
2. Lee .env.development (sobrescribe)
3. Variables disponibles como: import.meta.env.VITE_API_URL

# Con npm run build (o docker build):
1. Lee .env.example (base)
2. Lee .env.production (sobrescribe)
3. Variables disponibles en el bundle como: import.meta.env.VITE_API_URL
```

---

## 🚀 Modo Desarrollo (npm run dev)

**Arquitectura:**
```
localhost:5173 (Frontend en Vite dev server)
     ↓
localhost:8000 (Backend en Docker - port mapping)
```

**Archivo: `.env.development`**
```
VITE_API_URL=http://localhost:8000/api
VITE_API_TIMEOUT=30000
```

**Por qué `localhost:8000`:**
- Frontend corre en tu máquina (npm run dev)
- Backend corre en Docker pero puerto está mapeado al host
- El navegador necesita acceder al host, no a la red Docker

**Uso en código:**
```javascript
import.meta.env.VITE_API_URL  // http://localhost:8000/api
```

---

## 🐳 Modo Producción (Docker Completo)

**Arquitectura:**
```
Frontend Container (puerto 5173 en Docker)
     ↓ (red interna Docker)
Backend Container (servicio "backend")
```

**Archivo: `.env.production`**
```
VITE_API_URL=http://backend:8000/api
VITE_API_TIMEOUT=30000
```

**Por qué `backend:8000` (no localhost):**
- Frontend está DENTRO de Docker
- Backend está DENTRO de Docker, en la misma red
- Docker DNS interno resuelve "backend" → IP del contenedor
- El navegador NO está involucrado (está en el servidor)

**Uso en código:**
```javascript
import.meta.env.VITE_API_URL  // http://backend:8000/api
```

---

## ⚠️ Errores Comunes

### ERROR 1: Usar `http://backend:8000` en desarrollo local

```
❌ INCORRECTO:
npm run dev
# Tienes .env.development con VITE_API_URL=http://backend:8000/api

ERROR: "backend" no se resuelve
Razón: Tu máquina host no sabe qué es "backend"
```

**Solución:** `.env.development` debe usar `http://localhost:8000/api`

---

### ERROR 2: Usar `http://localhost:8000` en Docker

```
❌ INCORRECTO:
docker compose --profile prod up
# Frontend container tiene VITE_API_URL=http://localhost:8000/api

ERROR: Frontend resuelve localhost → 127.0.0.1 (dentro del container)
       Backend NO está en 127.0.0.1 dentro del container
```

**Solución:** `.env.production` debe usar `http://backend:8000/api`

---

### ERROR 3: Archivo .gitignore excluye .env.development o .env.production

```
❌ INCORRECTO:
.gitignore contiene: .env*
# Esto excluye todo (incluyendo .env.development y .env.production)
```

**Solución:** Ser más específico en .gitignore:
```
.env           # Excluir solo .env base
.env.local     # Excluir archivos locales
# NO excluir:
# .env.development
# .env.production
```

O commitear archivos específicos:
```bash
git add -f frontend/.env.development
git add -f frontend/.env.production
```

---

## 🧪 Verificar Qué Variable Se Está Usando

### En navegador:

```javascript
// Abre DevTools Console (F12)
// Pega esto:
console.log(import.meta.env.VITE_API_URL)

// Resultado esperado:
// Desarrollo: http://localhost:8000/api
// Docker: http://backend:8000/api
```

### En terminal (durante build):

```bash
# Desarrollo
npm run dev
# Output: VITE app server running at: ...

# Producción
npm run build
# Output: ✓ built in 1.23s
```

---

## 📋 Checklist

- [ ] `.env.development` tiene `VITE_API_URL=http://localhost:8000/api`
- [ ] `.env.production` tiene `VITE_API_URL=http://backend:8000/api`
- [ ] `.env.example` es solo base (información general)
- [ ] Al hacer `npm run dev`, el API responde desde `http://localhost:8000`
- [ ] Al hacer `docker compose --profile prod up`, el API responde desde backend service
- [ ] No hay `console.log()` usando hardcodeado URLs
- [ ] Código usa `import.meta.env.VITE_API_URL`

---

## 🔗 Referencias

- [Vite Docs: Env Variables](https://vitejs.dev/guide/env-and-modes.html)
- [Vite Docs: API Endpoint](https://vitejs.dev/config/server-options.html)

