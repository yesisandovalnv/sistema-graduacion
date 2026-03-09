# 📊 ANÁLISIS TÉCNICO DETALLADO - MODELOS Y FLUJOS

**Documento complementario al diagnóstico arquitectónico**

---

## **1. ESQUEMA DE BASE DE DATOS**

### **1.1 Tabla: usuarios_customuser**

```sql
│ Field           │ Type               │ Constraints        │
├─────────────────┼────────────────────┼────────────────────┤
│ id              │ BIGINT PK          │ Primary Key        │
│ username        │ VARCHAR(150)       │ UNIQUE, NOT NULL   │
│ password        │ VARCHAR(128)       │ NOT NULL (hashed)  │
│ first_name      │ VARCHAR(150)       │                    │
│ last_name       │ VARCHAR(150)       │                    │
│ email           │ VARCHAR(254)       │ UNIQUE             │
│ role            │ VARCHAR(20)        │ admin, administ,   │
│                 │                    │ estudiante         │
│ is_active       │ BOOLEAN            │ DEFAULT: True      │
│ is_staff        │ BOOLEAN            │ DEFAULT: False     │
│ is_superuser    │ BOOLEAN            │ DEFAULT: False     │
│ date_joined     │ TIMESTAMP          │ AUTO               │
│ last_login      │ TIMESTAMP          │ NULL allowed       │
```

**Índices:**
```
- PK: id
- UNIQUE: username
- UNIQUE: email
- INDEX: role
```

**¿De dónde vienen?**
- Creados en Django Admin (/admin/usuarios/customuser/add/)
- O vía API: POST /api/usuarios/ (si existe endpoint)

---

### **1.2 Tabla: postulantes_postulante**

```sql
│ Field              │ Type          │ Relaciones        │
├────────────────────┼───────────────┼───────────────────┤
│ id                 │ BIGINT PK     │                   │
│ usuario_id         │ BIGINT FK     │ → usuarios_customuser │
│ nombre             │ VARCHAR(100)  │                   │
│ apellido           │ VARCHAR(100)  │                   │
│ carrera_id         │ BIGINT FK     │ → ??? (no veo)    │
│ cedula             │ VARCHAR(20)   │ UNIQUE            │
│ telefono           │ VARCHAR(20)   │                   │
│ codigo_estudiante  │ VARCHAR(50)   │ UNIQUE            │
│ fecha_ingreso      │ DATE          │                   │
│ estado             │ VARCHAR(20)   │ activo, inactivo  │
│ created_at         │ TIMESTAMP     │ AUTO              │
│ updated_at         │ TIMESTAMP     │ AUTO              │
```

**Relaciones:**
```
PostulanteModel (1) ──→ (1) CustomUser
PostulanteModel (1) ──→ (N) PostulacionModel
PostulanteModel (1) ──→ (N) DocumentoPostulacion
```

---

### **1.3 Tabla: postulantes_postulacion**

```sql
│ Field              │ Type          │ Relaciones        │
├────────────────────┼───────────────┼───────────────────┤
│ id                 │ BIGINT PK     │                   │
│ postulante_id      │ BIGINT FK     │ → postulantes_postulante │
│ modalidad_id       │ BIGINT FK     │ → modalidades_modalidad │
│ estado             │ VARCHAR(50)   │ (ver abajo)       │
│ etapa_actual_id    │ BIGINT FK     │ → modalidades_etapa │
│ tutor_asignado_id  │ BIGINT FK     │ → usuarios_customuser │
│ observaciones      │ TEXT          │ NULL allowed      │
│ fecha_creacion     │ TIMESTAMP     │ AUTO              │
│ fecha_actualizacion│ TIMESTAMP     │ AUTO              │
│ fecha_aprobacion   │ TIMESTAMP     │ NULL allowed      │
│ resultado_privada  │ VARCHAR(20)   │ NULL allowed      │
│ resultado_publica  │ VARCHAR(20)   │ NULL allowed      │
```

**Estados válidos:**
```
EN_PROCESO
PERFIL_APROBADO
PRIVADA_APROBADA
PUBLICA_APROBADA
TITULADO
```

---

### **1.4 Tabla: documentos_documentopostulacion**

```sql
│ Field               │ Type          │ Relaciones        │
├─────────────────────┼───────────────┼───────────────────┤
│ id                  │ BIGINT PK     │                   │
│ postulacion_id      │ BIGINT FK     │ → postulantes_postulacion │
│ tipo_documento_id   │ BIGINT FK     │ → documentos_tipodocumento │
│ archivo             │ FILE          │ uploaded files/   │
│ estado              │ VARCHAR(50)   │ PENDIENTE, APROB, REC │
│ fecha_subida        │ TIMESTAMP     │ AUTO              │
│ fecha_aprobacion    │ TIMESTAMP     │ NULL allowed      │
│ evaluador_id        │ BIGINT FK     │ → usuarios_customuser │
│ comentario_rechazo  │ TEXT          │ NULL allowed      │
│ version             │ INT           │ DEFAULT: 1        │
│ archivo_anterior_id │ BIGINT FK     │ → self (para control version) │
```

**Estados:**
```
PENDIENTE_REVISION
APROBADO
RECHAZADO
```

---

### **1.5 Tabla: documentos_tipodocumento**

```sql
│ Field          │ Type       │ Descripción            │
├────────────────┼────────────┼────────────────────────┤
│ id             │ BIGINT PK  │                        │
│ nombre         │ VARCHAR    │ Ej: "Tesis", "Formato" │
│ descripcion    │ TEXT       │                        │
│ requerido      │ BOOLEAN    │ Required en postulación│
│ activo         │ BOOLEAN    │ DEFAULT: True          │
│ modalidades    │ MANY2MANY  │ Qué modalidades usan   │
```

---

### **1.6 Tabla: modalidades_modalidad**

```sql
│ Field          │ Type       │ Descripción            │
├────────────────┼────────────┼────────────────────────┤
│ id             │ BIGINT PK  │                        │
│ nombre         │ VARCHAR    │ Ej: "Tesis", "Trabajo" │
│ descripcion    │ TEXT       │                        │
│ documentos_req │ TEXT       │ Documentos requeridos  │
│ activo         │ BOOLEAN    │ DEFAULT: True          │
│ created_at     │ TIMESTAMP  │ AUTO                   │
│ updated_at     │ TIMESTAMP  │ AUTO                   │
```

---

### **1.7 Tabla: modalidades_etapa**

```sql
│ Field          │ Type       │ Descripción            │
├────────────────┼────────────┼────────────────────────┤
│ id             │ BIGINT PK  │                        │
│ modalidad_id   │ BIGINT FK  │ → modalidades_modalidad│
│ nombre         │ VARCHAR    │ Ej: "Aprobación perfil"│
│ descripcion    │ TEXT       │                        │
│ orden          │ INT        │ Orden secuencial       │
│ es_final       │ BOOLEAN    │ ¿Es la última etapa?   │
```

**Ejemplo de etapas:**
```
Modalidad: Tesis
├─ Etapa 1: Revisión de Perfil (orden=1)
├─ Etapa 2: Defensa Privada (orden=2)
├─ Etapa 3: Defensa Pública (orden=3, es_final=True)
```

---

### **1.8 Tabla: auditoria_auditorialog**

```sql
│ Field          │ Type       │ Descripción            │
├────────────────┼────────────┼────────────────────────┤
│ id             │ BIGINT PK  │                        │
│ usuario_id     │ BIGINT FK  │ → usuarios_customuser  │
│ accion         │ VARCHAR    │ CREATE, UPDATE, DELETE │
│ tabla          │ VARCHAR    │ Tabla modificada       │
│ registro_id    │ INT        │ ID del registro        │
│ cambios_antes  │ JSONB      │ Valores anteriores     │
│ cambios_despues│ JSONB      │ Valores nuevos         │
│ ip_address     │ VARCHAR    │ IP del usuario         │
│ timestamp      │ TIMESTAMP  │ Cuándo ocurrió         │
```

---

## **2. DIAGRAMA DE RELACIONES (ER Diagram)**

```
┌──────────────────────┐
│  CustomUser          │
├──────────────────────┤
│ id (PK)              │
│ username (UNIQUE)    │
│ email (UNIQUE)       │
│ password (hashed)    │◄─────────────────┐
│ role                 │                  │
│ is_active            │                  │
└──────────────────────┘                  │
    ▲                                     │
    │                    ┌────────────────┼──────────────┐
    │                    │                │              │
    │                    │                │              │
    └─── (1)            (N)              (N)            (N)
         is_user         is_staff       is_tutor    is_evaluador
         of              for            of           for
         │               │              │            │
    ┌────┴──────────────┐  ┌───────────┴────────┐  ┌──────────────┐
    │Postulante         │  │Postulacion         │  │DocumentoPost │
    ├───────────────────┤  ├────────────────────┤  ├──────────────┤
    │id (PK)            │  │id (PK)             │  │id (PK)       │
    │usuario_id (FK)    │  │postulante_id (FK)  │  │postulacion… │
    │nombre             │  │modalidad_id (FK)   │  │tipo_doc_id   │
    │apellido           │  │estado              │  │archivo       │
    │cedula (UNIQUE)    │  │etapa_actual_id(FK) │  │estado        │
    │codigo_estudiante  │  │tutor_asignado_id   │  │evaluador_id  │
    │                   │  │(FK→CustomUser)     │  │              │
    └─────────┬─────────┘  └────────┬───────────┘  └──────────────┘
              │                     │
              └──────────(1)───(N)──┘

┌──────────────────────┐  ┌──────────────────────┐
│ Modalidad            │  │ Etapa                │
├──────────────────────┤  ├──────────────────────┤
│ id (PK)              │  │ id (PK)              │
│ nombre               │  │ modalidad_id (FK)    │
│ descripcion          │  │ nombre               │
│ documentos_req       │  │ orden                │
│ activo               │  │ es_final             │
└──────────┬───────────┘  └──────────────────────┘
           │
           │ (M2M)
           │
       TipoDocumento
       {id, nombre, descripcion}
```

---

## **3. FLUJOS DE NEGOCIO PRINCIPALES**

### **3.1 Flujo: Registro de Nuevo Estudiante**

```
┌────────────────────────────────────────────┐
│ 1. ADMIN CREA USUARIO EN DJANGO ADMIN      │
├────────────────────────────────────────────┤
│ • Va a /admin/usuarios/customuser/add/     │
│ • Ingresa username, password, email        │
│ • Asigna role = "estudiante"               │
│ • GUARDA → Nuevo CustomUser creado         │
└────────────────────────┬───────────────────┘
                         │
                         ▼
┌────────────────────────────────────────────┐
│ 2. ESTUDIANTE CREA PERFIL POSTULANTE       │
├────────────────────────────────────────────┤
│ • Accede a /admin/postulantes/postulante   │
│ • Completa: nombre, apellido, carrera      │
│ • Ingresa: cedula, código_estudiante       │
│ • GUARDA → Nuevo Postulante creado         │
└────────────────────────┬───────────────────┘
                         │
                         ▼
┌────────────────────────────────────────────┐
│ 3. ESTUDIANTE INICIA POSTULACIÓN           │
├────────────────────────────────────────────┤
│ • Va a /admin/postulaciones/postulacion    │
│ • Selecciona: postulante, modalidad        │
│ • Estado inicial: EN_PROCESO                │
│ • Etapa actual: Primera etapa              │
│ • GUARDA → Postulación creada              │
└────────────────────────┬───────────────────┘
                         │
                         ▼
┌────────────────────────────────────────────┐
│ 4. ESTUDIANTE SUBE DOCUMENTOS              │
├────────────────────────────────────────────┤
│ • POST /api/documentos/ (multipart/form)   │
│ • Selecciona: tipo de documento            │
│ • Sube: archivo PDF/imagen                 │
│ • Estado: PENDIENTE_REVISION               │
│ • GUARDA → DocumentoPostulacion creado     │
└────────────────────────┬───────────────────┘
                         │
                         ▼
┌────────────────────────────────────────────┐
│ 5. ADMINISTRATIVO REVISA DOCUMENTOS        │
├────────────────────────────────────────────┤
│ • Va a /admin/documentos/               │
│ • Ve todos los documentos pendientes       │
│ • Descarga PDF para revisar                │
│ • Decide: APROBADO o RECHAZADO            │
│ • Si rechaza: ingresa comentario           │
│ • GUARDA → Estado actualizado              │
└────────────────────────┬───────────────────┘
                         │
                    ┌────┴────┐
                    │          │
               APROBADO    RECHAZADO
                    │          │
                    ▼          ▼
            ┌──────────┐   ┌──────────┐
            │ Avanza   │   │ Requiere │
            │ a étapa  │   │ nueva    │
            │ siguiente│   │ versión  │
            │Estado:   │   │ del doc. │
            │PERFIL_   │   │          │
            │APROBADO  │   │Vuelve a  │
            │          │   │paso 4    │
            └──────────┘   └──────────┘
```

---

### **3.2 Flujo: Evaluación de Defensa**

```
┌────────────────────────────────────────────┐
│ 1. POSTULACIÓN EN ETAPA "DEFENSA PRIVADA"  │
├────────────────────────────────────────────┤
│ • Estado: EN_PROCESO                       │
│ • Etapa actual: "Defensa Privada"          │
│ • Tribunal de jurado asignado               │
│ • Fecha de defensa: 2024-03-15             │
└────────────────────────┬───────────────────┘
                         │
                         ▼
┌────────────────────────────────────────────┐
│ 2. JURADO REALIZA DEFENSA                  │
├────────────────────────────────────────────┤
│ • Estudiante presenta trabajo              │
│ • Jurado hace preguntas                    │
│ • Jurado vota: Aprobado/Rechazado          │
└────────────────────────┬───────────────────┘
                         │
                         ▼
┌────────────────────────────────────────────┐
│ 3. ADMINISTRATIVO REGISTRA RESULTADO       │
├────────────────────────────────────────────┤
│ • Va a /admin/postulaciones/postulacion    │
│ • Campo: resultado_privada = "APROBADO"    │
│ • Estado → "PRIVADA_APROBADA"              │
│ • Etapa actual → "Defensa Pública"         │
│ • GUARDA → Postulación actualizada         │
└────────────────────────┬───────────────────┘
                         │
                         ▼
┌────────────────────────────────────────────┐
│ 4. PROCESO REPITE PARA DEFENSA PÚBLICA     │
├────────────────────────────────────────────┤
│ • Defensa pública con asistencia            │
│ • Jurado nuevo vota nuevamente             │
│ • Resultado: resultado_publica             │
│ • Si aprobado → TITULADO                   │
└────────────────────────────────────────────┘
```

---

### **3.3 Flujo: Generación de Reportes**

```
┌──────────────────────────────────────────────────┐
│ ADMIN SOLICITA REPORTE VÍA API                   │
├──────────────────────────────────────────────────┤
│ GET /api/reportes/dashboard-general/             │
│ Headers: Authorization: Bearer {access_token}    │
└──────────────────────┬───────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────┐
│ BACKEND PROCESA REQUEST                          │
├──────────────────────────────────────────────────┤
│ • Django valida JWT token                        │
│ • Verifica permisos (admin?)                    │
│ • Ejecuta queries en PostgreSQL                 │
│                                                  │
│ SELECT COUNT(*) FROM postulantes_postulante;    │
│ SELECT COUNT(*) FROM postulantes_postulacion;   │
│ SELECT COUNT(*) FROM documentos_..;             │
│ SELECT COUNT(*) WHERE estado='TITULADO';        │
│                                                  │
│ • Genera JSON con resultados                    │
└──────────────────────┬───────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────┐
│ CLIENT RECIBE JSON                               │
├──────────────────────────────────────────────────┤
│ {                                                │
│   "total_postulantes": 145,                      │
│   "total_postulaciones": 142,                    │
│   "total_documentos": 568,                       │
│   "titulados": 89,                               │
│   "en_proceso": 53,                              │
│   "por_modalidad": {...}                         │
│ }                                                │
└──────────────────────────────────────────────────┘
```

---

## **4. FLUJOS DE API REST**

### **4.1 POST /api/auth/login/ (Obtener Tokens)**

```
REQUEST:
POST /api/auth/login/
Content-Type: application/json

{
  "username": "juan_perez",
  "password": "contraseña123"
}

VALIDACIÓN:
1. ¿Usuario existe en CustomUser?
2. ¿Contraseña es correcta? (Django compara hash)
3. ¿Usuario está activo (is_active=True)?

RESPONSE (200 OK):
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ..."
}

ERROR (401 Unauthorized):
{
  "detail": "No active account found with the given credentials"
}
```

*Después de esto, usar en cada request:*
```
Authorization: Bearer <access_token>
```

---

### **4.2 GET /api/postulantes/ (Listar Postulantes)**

```
REQUEST:
GET /api/postulantes/?search=juan&ordering=-created_at
Headers: Authorization: Bearer {token}

VALIDACIÓN:
1. Token JWT válido?
2. Usuario tiene permisos?

RESPONSE (200 OK):
{
  "count": 145,
  "next": "http://api/postulantes/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "usuario": 5,
      "nombre": "Juan",
      "apellido": "Pérez",
      "cedula": "12345678",
      "codigo_estudiante": "ESI-001",
      "carrera": "Ingeniería de Sistemas",
      "estado": "activo",
      "created_at": "2024-01-15T10:30:00Z"
    },
    {...}
  ]
}

PARÁMETROS DISPONIBLES:
- search=    : Buscar en nombre, apellido, cedula
- ordering=  : Ordenar por campo (-para desc)
- page=      : Paginación (default: page_size=20)
- limit=     : Cambiar cantidad por página
```

---

### **4.3 POST /api/documentos/ (Subir Documento)**

```
REQUEST:
POST /api/documentos/
Content-Type: multipart/form-data
Headers: Authorization: Bearer {token}

Form Data:
- postulacion_id: 42
- tipo_documento_id: 7
- archivo: <binary file>
- comentario: "Documento de tesis V3"

VALIDACIÓN:
1. ¿Postulacion existe?
2. ¿Usuario puede subir a esta postulación?
3. ¿Archivo no es muy grande?
4. ¿Formato válido?

RESPONSE (201 Created):
{
  "id": 234,
  "postulacion": 42,
  "tipo_documento": 7,
  "archivo": "/media/documents/tesis_v3.pdf",
  "estado": "PENDIENTE_REVISION",
  "fecha_subida": "2024-03-08T14:45:00Z",
  "version": 3
}

ERROR (400 Bad Request):
{
  "archivo": ["File size exceeds 50MB"]
}
```

---

### **4.4 GET /api/reportes/estadisticas-tutores/**

```
REQUEST:
GET /api/reportes/estadisticas-tutores/
Headers: Authorization: Bearer {token}

RESPONSE (200 OK):
[
  {
    "tutor_id": 2,
    "tutor_nombre": "Dr. Carlos García",
    "total_alumnos": 12,
    "titulados": 10,
    "en_proceso": 2,
    "promedio_duracion_meses": 8.5,
    "tasa_aprobacion": 0.833
  },
  {
    "tutor_id": 4,
    "tutor_nombre": "Dra. María López",
    "total_alumnos": 8,
    "titulados": 7,
    "en_proceso": 1,
    "promedio_duracion_meses": 7.2,
    "tasa_aprobacion": 0.875
  }
]
```

---

### **4.5 GET /api/reportes/estadisticas-tutores/exportar/**

```
REQUEST:
GET /api/reportes/estadisticas-tutores/exportar/
Headers: Authorization: Bearer {token}

RESPONSE: (200 OK + Excel file)
Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet
Content-Disposition: attachment; filename="estadisticas_tutores_2024-03-08.xlsx"

[Binary Excel File]

CONTENIDO DEL EXCEL:
- Hoja 1: "Tutores"
  Columnas: ID | Nombre | Tot. Alumnos | Titulados | En Proceso | Prom. Duración | Tasa Aprobación
  
- Hoja 2: "Detalles por Alumno"
  Columnas: Tutor | Alumno | Modalidad | Estado | Fecha Inicio | Fecha Titulación
```

---

## **5. SEGURIDAD Y CONTROL DE ACCESO**

### **5.1 Matriz de Permisos (RBAC)**

| Endpoint | Admin ✓ | Administ ✓ | Estudiante ✓ | Anónimo |
|----------|--------|-----------|------------|---------|
| POST /auth/login/ | ✓ | ✓ | ✓ | ✓ |
| GET /postulantes/ | ✓ | ✓ | Solo propios | ✗ |
| POST /postulantes/ | ✓ | ✓ | ✗ | ✗ |
| GET /postulaciones/ | ✓ | ✓ | Solo propios | ✗ |
| POST /documentos/ | ✓ | ✓ | Solo propios | ✗ |
| GET /reportes/ | ✓ | Limitado | ✗ | ✗ |
| GET /admin/ | ✓ | Limitado | ✗ | ✗ |

### **5.2 Tokens JWT**

```
Access Token:
├─ Lifetime: 60 minutos
├─ Contiene: user_id, username, role, exp
├─ Usado en: Authorization: Bearer {token}
└─ Riesgo: Si se expone, atacante tiene 60 min

Refresh Token:
├─ Lifetime: 7 días
├─ Usado para: POST /api/auth/refresh/
├─ Genera nuevo: Access Token
└─ Riesgo: Si se expone, atacante tiene 7 días

```

---

## **6. CÁLCULOS Y MÉTRICAS**

### **6.1 Métrica: Tasa de Titulación por Carrera**

```
QUERY:
SELECT 
  carrera,
  COUNT(*) as total_postulantes,
  SUM(CASE WHEN estado='TITULADO' THEN 1 ELSE 0 END) as titulados,
  (SUM(CASE WHEN estado='TITULADO' THEN 1.0 ELSE 0 END) / COUNT(*)) * 100 as porcentaje
FROM postulantes p
JOIN postulaciones po ON p.id = po.postulante_id
GROUP BY carrera
ORDER BY porcentaje DESC;

RESULTADO ESPERADO:
Carrera              | Total | Titulados | % Titulación
─────────────────────┼───────┼───────────┼──────────────
Ingeniería Sistemas  | 45    | 38        | 84.4%
Administrativos      | 30    | 28        | 93.3%
Abogacía            | 25    | 18        | 72.0%
```

### **6.2 Métrica: Tiempo Promedio de Titulación**

```
QUERY:
SELECT 
  carrera,
  ROUND(AVG(EXTRACT(DAY FROM (DATE(fecha_titulacion) - DATE(fecha_creacion))))) as dias_promedio,
  ROUND(AVG(EXTRACT(DAY FROM (DATE(fecha_titulacion) - DATE(fecha_creacion)))) / 30.44, 1) as meses_promedio
FROM postulaciones
WHERE estado = 'TITULADO'
GROUP BY carrera;

RESULTADO ESPERADO:
Carrera              | Días | Meses
─────────────────────┼──────┼────────
Ingeniería Sistemas  | 245  | 8.0
Administrativos      | 210  | 6.9
Abogacía            | 280  | 9.2
```

---

## **7. PROBLEMAS POTENCIALES EN LOS MODELOS**

### **🔴 Problema #1: Falta de FK a Carrera**

**Observación:**
```
Postulante tiene campo "carrera_id" pero modelo Carrera no existe
```

**Impacto:**
```
INSERT INTO postulantes (usuario_id, nombre, carrera_id...)
↓
ERROR: Foreign key violation (carrera_id no existe)
```

**Solución:**
```python
# En postulantes/models.py
class Postulante(Model):
    carrera = ForeignKey(Carrera, on_delete=CASCADE)  # ← Agregar modelo
```

---

### **🔴 Problema #2: Control de Versiones de Documentos**

**Observación:**
```
Campo "version" existe pero no hay trigger automático
Si usuario sube versión 2, debe actualizar manualmente
```

**Impacto:**
```
VERSION CONTROL no es automático
User puede perder track de cambios
```

**Solución:**
```python
# En documentos/models.py
class DocumentoPostulacion(Model):
    def save(self, *args, **kwargs):
        if not self.pk:
            # Nuevo documento
            self.version = 1
        else:
            # Update existente - incrementar versión
            self.version = F('version') + 1
        super().save(*args, **kwargs)
```

---

### **🟡 Problema #3: Sin Control de Cambios de Estado**

**Observación:**
```
Campo "estado" en Postulacion puede cambiar a cualquier valor
No hay validación de transiciones válidas
```

**Impacto:**
```
Estado: EN_PROCESO → cambiar a TITULADO directamente (❌ inconsistenete)
Sin seguir las etapas intermedias
```

**Solución:**
```python
VALID_TRANSITIONS = {
    'EN_PROCESO': ['PERFIL_APROBADO', 'RECHAZADO'],
    'PERFIL_APROBADO': ['PRIVADA_APROBADA', 'RECHAZADO'],
    'PRIVADA_APROBADA': ['PUBLICA_APROBADA', 'RECHAZADO'],
    'PUBLICA_APROBADA': ['TITULADO'],
}

def cambiar_estado(self, nuevo_estado):
    if nuevo_estado not in VALID_TRANSITIONS.get(self.estado, []):
        raise ValidationError(f"Transición inválida: {self.estado} → {nuevo_estado}")
    self.estado = nuevo_estado
    self.save()
```

---

### **🟡 Problema #4: Sin Constraint de Integridad para Tutor**

**Observación:**
```
tutor_asignado_id puede apuntar a cualquier usuario
Sin validar que sea un usuario con role="docente"
```

**Impacto:**
```
Tutor puede ser "estudiante" (❌ inconsistente)
```

**Solución:**
```python
def clean(self):
    if self.tutor_asignado and self.tutor_asignado.role != 'docente':
        raise ValidationError("El tutor debe ser un usuario con rol 'docente'")
```

---

## **8. PENDIENTES DE VERIFICACIÓN**

- ❓ ¿Modelo Carrera existe en la BD?
- ❓ ¿Modelo Docente existe o es CustomUser con role='docente'?
- ❓ ¿Existe control de archivos duplicados en uploads?
- ❓ ¿Hay job/tarea de limpieza de archivos borrados?
- ❓ ¿PostgreSQL tiene backups automáticos?

---

**Fin del análisis técnico** • Última actualización: 9 de marzo de 2026
