# Core-Nexus

Proyecto integrador: suite de administración y monitoreo de bases de datos.

Core-Nexus es una suite propia para gestionar y monitorear instancias de SQL Server. Toma como referencia funcional la plataforma comercial AI-DBA y se construye como una solución original. El esquema de una Agencia de Viajes es solo un conjunto de datos de prueba: la aplicación se conecta a cualquier base de la instancia.

## Propósito

Desarrollar una solución que permita gestionar, monitorear y optimizar entornos de bases de datos, aplicando los conocimientos del curso de Administración de Bases de Datos.

## Objetivos

- Llevar a la práctica los conceptos de las unidades de Administración de Bases de Datos.
- Conectar, administrar y automatizar un SGBD real (SQL Server 2025) desde código. El esquema de la Agencia de Viajes puede usarse como entorno de pruebas.
- Aplicar control de versiones, diseño modular, manejo de errores y documentación técnica.
- Analizar herramientas comerciales y proponer una solución equivalente y propia.

## Tecnologías

- SGBD: Microsoft SQL Server 2025
- Control de versiones: Git y GitHub
- Backend: Python 3.11+ con FastAPI y pyodbc
- Interfaz: React, TypeScript y Vite

## Requisitos

- Python 3.11 o superior
- Node.js 20 o superior
- SQL Server
- [ODBC Driver 18 for SQL Server](https://learn.microsoft.com/sql/connect/odbc/download-odbc-driver-for-sql-server)

## Instalación y uso

Clona el repositorio:

```bash
git clone https://github.com/Thenavarro09/Core-Nexus.git
cd Core-Nexus
```

Copia la configuración de ejemplo y ajústala a tu instancia.

En Windows (PowerShell o cmd):

```powershell
copy config.example.env config.env
```

En macOS o Linux:

```bash
cp config.example.env config.env
```

Los scripts opcionales de prueba, como el de la Agencia de Viajes, van en [`database/`](database/). No son necesarios para arrancar la suite.

Backend, desde `backend/`:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

En macOS o Linux activa el entorno con `source .venv/bin/activate`.

La API queda en `http://127.0.0.1:8000`. La documentación interactiva está en `http://127.0.0.1:8000/docs`.

Frontend, desde `frontend/`, en otra terminal:

```bash
npm install
npm run dev
```

Abre la dirección que muestra Vite, normalmente `http://127.0.0.1:5173`. El servidor de desarrollo reenvía `/api` al backend.

## Estructura

- `backend/` — API modular: salud, prueba de conexión, listado de bases y routers reservados para monitoreo y administración.
- `frontend/` — interfaz con las secciones Conexiones, Monitoreo y Administración.
- `database/` — scripts SQL de prueba, independientes del núcleo de la aplicación.
- `config.example.env` — plantilla de conexión para `GET /api/databases`.

Desarrollado como proyecto integrador para la asignatura de Administración de Bases de Datos.
