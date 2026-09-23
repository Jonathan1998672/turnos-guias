# Turnos y Salas — Museo Universitario de Ciencias

Aplicación para armar el **rol** de guías del museo: repartir a los guías entre
las salas a lo largo del turno, asignarles hora de comida, validar que no se
rompan las reglas y exportar el resultado en `.xlsx`, `.csv`, `.pdf` o imagen
para mandarlo al grupo de WhatsApp.

Sustituye el proceso de papel y lápiz, que además exigía recordar de memoria qué
guía puede dar qué función y qué código tiene cada sala.

## Stack

| Capa     | Tecnología                                        |
| -------- | ------------------------------------------------- |
| Backend  | FastAPI, SQLAlchemy 2.0, Alembic, PostgreSQL (Supabase) |
| Frontend | React 19, Vite, Tailwind CSS v4, React Router      |
| Export   | openpyxl (xlsx), csv (stdlib), ReportLab (pdf), PyMuPDF (png/jpg) |

El solver y los exportadores viven en el backend. El frontend solo consume la
API y renderiza.

## Reglas de negocio

### Salas

| Código | Nombre                | Es función | Comida por defecto |
| ------ | --------------------- | ---------- | ------------------ |
| H-20   | Súper Guía            | No         | 13:30              |
| H-21   | Planetario            | Sí         | 13:30              |
| H-22   | Come bien, juega bien | No         | 13:30              |
| H-23   | Física y astronomía   | No         | 14:00              |
| H-25   | Jardín de la ciencia  | No         | 13:30              |
| H-26   | MI-YO                 | No         | 14:00              |
| H-27   | Plasma                | Sí         | 14:00              |

H-20 es exclusiva del Súper Guía. Las salas marcadas como función exigen que el
guía esté certificado para ellas.

### Las cuatro reglas

1. Un guía no puede repetir sala a lo largo del turno. La única excepción es el
   Súper Guía, que permanece en H-20 los tres bloques.
2. Los guías de H-21/H-27, H-22/H-23 y H-25/H-26 no pueden empalmar la hora de
   comida dentro de cada pareja.
3. Las horas de comida son únicamente 13:30 y 14:00, de 30 minutos.
4. No siempre asisten todos los guías: el rol se genera con los presentes y las
   reglas anteriores se siguen cumpliendo.

Cuando falta personal certificado, el solver relaja la regla 1 solo para las
salas de función y lo reporta como advertencia, en vez de fallar. El detalle
está en [docs/reglas-de-negocio.md](docs/reglas-de-negocio.md).

### Turnos

El alcance actual es el **turno de fin de semana**: un solo turno con tres
bloques (10:00-12:30, 12:30-15:00, 15:00-17:00). Los turnos matutino y
vespertino de entre semana ya están modelados en la base de datos, pero todavía
no tienen interfaz.

## Estructura del repositorio

```
turnos-guias/
├── backend/          API FastAPI
├── frontend/         SPA de React
├── docs/             reglas de negocio y modelo de datos
├── legacy/           el prototipo original de un solo archivo HTML
└── README.md
```

### Backend

```
backend/app/
├── main.py           crea la app, monta CORS y el api_router
├── dependencies.py   get_db y factories de servicios
├── core/             configuración, motor de base de datos, excepciones
├── models/           tablas de SQLAlchemy
├── schemas/          contratos de la API en Pydantic v2
├── repositories/     único lugar que toca la sesión de base de datos
├── services/         orquestación y reglas de aplicación
├── scheduling/       el solver, Python puro sin base de datos
├── exporters/        xlsx, csv, pdf e imagen
└── routers/          endpoints bajo /api/v1
```

`scheduling/` no importa SQLAlchemy ni FastAPI: recibe dataclasses y devuelve
dataclasses, así que se prueba con `pytest` sin levantar base de datos.

### Frontend

```
frontend/src/
├── main.jsx          punto de entrada
├── App.jsx           layout y rutas
├── api/              una función por endpoint; la única carpeta con URLs
├── pages/            una pantalla por ruta
├── components/       ui/ genéricos y carpetas por dominio
├── hooks/            toda la lógica con estado y efectos
├── context/          el borrador del rol compartido
└── lib/              constantes y formateo
```

Tres convenciones: los componentes de `ui/` nunca llaman a la API, la lógica con
estado vive en `hooks/`, y las URLs solo aparecen en `api/`.

## Puesta en marcha

### 1. Base de datos en Supabase

Crea un proyecto en [supabase.com](https://supabase.com) y copia la cadena de
conexión desde *Project Settings → Database → Connection string → URI*.

Para desarrollo usa la **conexión directa** (puerto 5432). Si usas el pooler en
modo transacción (puerto 6543), el backend ya lo detecta y desactiva los
prepared statements automáticamente, que es lo que rompe a psycopg3 contra
PgBouncer.

### 2. Backend

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1          # en Linux/Mac: source .venv/bin/activate
pip install -r requirements-dev.txt

copy .env.example .env                 # y edita DATABASE_URL
alembic upgrade head
python -m scripts.seed
uvicorn app.main:app --reload
```

La API queda en `http://localhost:8000` y la documentación interactiva en
`http://localhost:8000/docs`.

### 3. Frontend

```powershell
cd frontend
npm install
copy .env.example .env
npm run dev
```

La app queda en `http://localhost:5173`.

## Variables de entorno

### `backend/.env`

| Variable       | Descripción                                          |
| -------------- | ---------------------------------------------------- |
| `DATABASE_URL` | Cadena de conexión de PostgreSQL de Supabase         |
| `CORS_ORIGINS` | Orígenes permitidos, separados por coma              |
| `DEBUG`        | `true` activa el log de SQL                          |

### `frontend/.env`

| Variable       | Descripción                                          |
| -------------- | ---------------------------------------------------- |
| `VITE_API_URL` | Base de la API, por defecto `http://localhost:8000/api/v1` |

## Endpoints

Todo cuelga de `/api/v1`.

| Método | Ruta                            | Descripción                                   |
| ------ | ------------------------------- | --------------------------------------------- |
| GET    | `/salas`                        | Catálogo de salas                              |
| POST   | `/salas`                        | Alta de sala                                   |
| PATCH  | `/salas/{id}`                   | Edición de sala                                |
| GET    | `/salas/pares-comida`           | Parejas que no pueden empalmar comida          |
| GET    | `/guias`                        | Catálogo de guías con sus certificaciones      |
| POST   | `/guias`                        | Alta de guía                                   |
| PATCH  | `/guias/{id}`                   | Edición de guía                                |
| DELETE | `/guias/{id}`                   | Baja lógica                                    |
| PUT    | `/guias/{id}/certificaciones`   | Reemplaza las salas de función que puede dar   |
| GET    | `/turnos`                       | Turnos disponibles                             |
| GET    | `/turnos/{id}/bloques`          | Bloques horarios de un turno                   |
| POST   | `/roles/generar`                | Genera un borrador sin guardarlo               |
| POST   | `/roles/validar`                | Valida un borrador editado, sin tocar la BD    |
| POST   | `/roles/exportar`               | Exporta un borrador sin guardarlo              |
| POST   | `/roles`                        | Guarda el rol                                  |
| GET    | `/roles`                        | Lista de roles, filtrable por fecha            |
| GET    | `/roles/{id}`                   | Detalle de un rol guardado                     |
| PATCH  | `/roles/{id}`                   | Reemplaza asignaciones y comidas               |
| DELETE | `/roles/{id}`                   | Borra un rol                                   |
| GET    | `/roles/{id}/exportar`          | Descarga en `xlsx`, `csv`, `pdf`, `png` o `jpg`|

## Pruebas

```powershell
cd backend
pytest
```

Las pruebas del solver y de la validación no necesitan base de datos.

## Roadmap

- Turnos matutino y vespertino de entre semana.
- Autenticación con Supabase Auth.
- Histórico de roles con búsqueda por guía.
- Envío directo del rol al grupo de WhatsApp.
