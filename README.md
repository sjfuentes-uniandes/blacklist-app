# Microservicio Blacklist

API REST en Flask que gestiona una lista negra global de correos. En local usa PostgreSQL vía **Docker Compose**; el despliegue previsto es **AWS Elastic Beanstalk**.

## Documentación del API

- **Postman Documenter:** [https://documenter.getpostman.com/view/22595946/2sBXitBSSc](https://documenter.getpostman.com/view/22595946/2sBXitBSSc)
- **Colección Postman (repo):** [Blacklist_API.postman_collection.json](Blacklist_API.postman_collection.json) — importar en Postman para ejecutar todos los escenarios de prueba.

## Requisitos

- [Docker](https://docs.docker.com/get-docker/) y Docker Compose v2
- Python **3.8–3.11** (recomendado por las versiones fijadas en `requirements.txt`)

## Paso a paso: levantar el servicio

### 1. Variables de entorno

En la raíz del repositorio:

```bash
cp .env.example .env
```

Edita `.env` si cambias usuario, contraseña o base de datos. **Importante:** `DATABASE_URL` debe coincidir con `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB` y con el puerto publicado por Docker (por defecto `5432`).

Docker Compose lee `POSTGRES_*` desde ese `.env` al arrancar el contenedor.

### 2. Base de datos con Docker Compose

```bash
docker compose up -d
```

Comprueba que el servicio esté en marcha (y opcionalmente *healthy*):

```bash
docker compose ps
docker compose logs -f db
```

### 3. Entorno Python e instalación de dependencias

```bash
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

La aplicación carga automáticamente el archivo `.env` gracias a `python-dotenv` en `config.py`.

### 4. Arrancar la API

Con el virtualenv activado y desde la raíz del proyecto:

```bash
python application.py
```

Por defecto el servidor escucha en **http://127.0.0.1:5000**. En el primer arranque se crean las tablas necesarias (`db.create_all()`).

---

## Pruebas manuales

Todas las rutas protegidas exigen el header:

`Authorization: Bearer <STATIC_TOKEN>`

(el valor de `STATIC_TOKEN` en tu `.env`, por defecto `my-static-bearer-token`).

### Con `curl`



**POST — agregar email (201):**

```bash
curl -s -w "\nHTTP: %{http_code}\n" -X POST http://127.0.0.1:5000/blacklists \
  -H "Authorization: Bearer my-static-bearer-token" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "usuario@ejemplo.com",
    "app_uuid": "550e8400-e29b-41d4-a716-446655440000",
    "blocked_reason": "Spam reiterado"
  }'
```

`blocked_reason` es opcional.

**GET — consultar si un email está listado (200):**

```bash
curl -s -H "Authorization: Bearer my-static-bearer-token" \
  "http://127.0.0.1:5000/blacklists/usuario@ejemplo.com"
```

**Sin token (401):**

```bash
curl -s -X POST http://127.0.0.1:5000/blacklists \
  -H "Content-Type: application/json" \
  -d '{"email":"otro@ejemplo.com","app_uuid":"550e8400-e29b-41d4-a716-446655440000"}'
```

**Email inválido (400):** repite el POST con `"email": "no-es-email"`.

**Duplicado (409):** ejecuta dos veces el mismo POST con el mismo `email`.

### Con Postman o cliente HTTP similar

| Paso | Método | URL | Headers | Body |
|------|--------|-----|---------|------|
| Alta | POST | `http://127.0.0.1:5000/blacklists` | `Authorization: Bearer …`, `Content-Type: application/json` | JSON con `email`, `app_uuid` y opcionalmente `blocked_reason` |
| Consulta | GET | `http://127.0.0.1:5000/blacklists/{email}` | `Authorization: Bearer …` | — |

Sustituye `{email}` por el correo (por ejemplo `usuario@ejemplo.com`).

---

## Comandos útiles de Docker

| Acción | Comando |
|--------|---------|
| Parar contenedores | `docker compose stop` |
| Parar y eliminar contenedores (conserva el volumen de datos) | `docker compose down` |
| Eliminar también los datos de PostgreSQL | `docker compose down -v` |

## Guía de Despliegue en AWS Elastic Beanstalk

Descripción del despliegue paso a paso del servicio en AWS Beanstalk

---

## **PARTE 1: CONFIGURACIÓN DE RDS (Base de Datos)**


### Paso 1.1: Crear Nueva Instancia RDS

1. Crear base de datos desde AWS RDS.
2. Seleccionar:
   - **Engine type**: PostgreSQL
   - **Version**: PostgreSQL 16.1 (o superior)
   - **Templates**: Development (para desarrollo)

**Selector de engine:** PostgreSQL

# Settings:
- **DB instance identifier**: `blacklist-db`
- **Master username**: `postgres`
- **Master password**: `password`

# DB instance class:
- **db.t3.micro** (elegible para capa gratuita si tienes)
- **Storage**: 20 GB

---

### Paso 1.2: Conectividad

1. En la sección **Connectivity**:
   - **VPC**: Default VPC
   - **DB Subnet Group**: default
   - **Public Access**: **NO**
   - **VPC security group**: Default

2. En la sección **Additional configuration**:
   - **Initial database name**: `blacklist_db`
   - **Enable automated backups**: ✓ Sí
   - **Backup retention period**: 7 días

3. Crear instancia de base de datos.

---

### Paso 1.3: Obtener Endpoint de RDS

Una vez que el estado cambie a **Available**:

1. **Copiar el endpoint** de la instancia RDS

---

## **PARTE 2: PREPARAR LA APLICACIÓN PARA ELASTIC BEANSTALK**

### Paso 2.1: Verificar estructura de archivos

El proyecto debe tener esta estructura:

```
blacklist-app/
├── application.py          ← Punto de entrada (WSGI)
├── config.py               ← Configuración
├── requirements.txt        ← Dependencias Python
├── .ebextensions/          ← Configuración EB (IMPORTANTE)
│   ├── 01_flask.config
│   ├── 02_packages.config
│   ├── 03_healthcheck.config
│   ├── 04_environment.config
│   └── 05_db_init.config
├── models/
│   ├── __init__.py
│   └── blacklist_entry.py
├── resources/
│   ├── __init__.py
│   └── blacklist.py
└── schemas/
    ├── __init__.py
    └── blacklist_schema.py
```

---

### Paso 2.2: Actualizar requirements.txt (si es necesario)

Verifica que tenga todas las dependencias:

```
Flask==1.1.4
Flask-RESTful==0.3.9
Flask-SQLAlchemy==2.5.1
flask-marshmallow==0.14.0
marshmallow-sqlalchemy==0.26.1
Werkzeug==1.0.1
psycopg2-binary==2.9.5
python-dotenv==0.21.0
SQLAlchemy>=1.3.0,<2.0
marshmallow>=3.0.0,<4.0.0
MarkupSafe>=1.1.1,<2.1.0
```

---

## **PARTE 3: CREAR Y CONFIGURAR ELASTIC BEANSTALK**

### Paso 3.1: Acceder a Elastic Beanstalk Console

1. Inicia sesión en AWS Console
2. Busca **Elastic Beanstalk**
3. Acceder a **Elastic Beanstalk** → **Applications**

---

### Paso 3.2: Crear Nueva Aplicación

1. Acceder en **Create application**
2. Completar:
   - **Application name**: `blacklist-app`
   - **Platform**: Python
   - **Platform branch**: Python 3.9 running on 64bit Amazon Linux 2
   - **Application code**: Upload your code
     - **Source code origin**: Local file
     - Carga un ZIP del proyecto

---

### Paso 3.3: Configurar Ambiente

En la consola EB después de crear la aplicación:

1. Ir a **Environments** → Al ambiente (ej: `blacklist-env`)
2. Hacer clic en **Configuration**
3. Buscar **Software** y hacer clic en **Edit**

---

### Paso 3.4: Configurar Variables de Entorno

En el editor de Software → **Environment properties**:

Agregar estas variables con los valores de tu RDS:

```
DATABASE_URL = postgresql://postgres:password@blacklist-db.c61e8q6aqwiu.us-east-1.rds.amazonaws.com:5432/blacklist_db
JWT_SECRET_KEY = super-secret-static-key
STATIC_TOKEN = my-static-bearer-token
```

---

### Paso 3.5: Configurar Security Group para acceder a RDS

En EC2 Console:

1. Ir a **Security Groups**
2. Buscar el security group de RDS (`blacklist-db-sg`)
3. Abrir **Edit inbound rules**
4. Agregar una regla:
   - **Type**: PostgreSQL
   - **Port**: 5432
   - **Source**: Security Group de EB
   - Hacer click en **Save rules**

---

## **PARTE 4: DESPLEGAR LA APLICACIÓN**

1. Ir a Elastic Beanstalk → Acceder aplicación
2. Hacer clic en **Upload and Deploy**
3. Cargar el ZIP del proyecto
4. Haz clic en **Deploy**
5. **Esperar 5-10 minutos** a que se despliegue


---

## Problemas frecuentes

- **Puerto 5432 ocupado:** cambia en `docker-compose.yml` el mapeo a `"5433:5432"` y actualiza el puerto en `DATABASE_URL` dentro de `.env`.
- **Error de conexión a la base:** asegúrate de que `docker compose up -d` haya terminado y que `DATABASE_URL` apunte a `localhost` con el puerto correcto.
- **401 en todas las peticiones:** el token en `Authorization: Bearer` debe ser exactamente el valor de `STATIC_TOKEN` en `.env`.

---
