# FinanzasNica

API REST para gestionar gastos compartidos por equipos: cuentas, categorías, presupuestos, créditos y facturas.

Stack: **Django 6.1**, **Django Ninja**, **PostgreSQL**, **Docker + Nginx**.

## Requisitos

- Docker y Docker Compose (recomendado), o
- Python 3.12+ y PostgreSQL

## Opción A: Docker (recomendado)

El stack levanta dos contenedores:

| Contenedor | Función |
|---|---|
| `django_api` | Gunicorn sirviendo la API (puerto interno 8000) |
| `nginx_proxy` | Publica el puerto 80, sirve `/static/` y `/media/` y proxea el resto a Django |

```bash
cp .env.example .env    # completa DB_*, SECRET_KEY, ALLOWED_HOSTS y TRUSTED_ORIGINS
docker compose up -d --build
```

Al arrancar, el contenedor de Django aplica las migraciones (`migrate`) y genera los
estáticos (`collectstatic`) antes de iniciar Gunicorn.

- API: http://localhost/api/
- Admin: http://localhost/admin/
- Docs (Swagger): http://localhost/api/docs

Los archivos estáticos y los subidos por los usuarios se guardan en los volúmenes
`static_data` y `media_data`, compartidos con Nginx (que los monta en solo lectura).
El código vive en `api/`, por lo que los comandos locales se ejecutan desde ahí.

Comandos útiles:

```bash
docker compose logs -f django     # logs de la aplicación
docker compose exec django python manage.py createsuperuser
docker compose exec django python manage.py migrate
docker compose down               # detener el stack
docker compose down -v            # detener y borrar volúmenes (¡elimina media y static!)
```

## Opción B: Local

```bash
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r api/requirements.txt
```

Crea un archivo `.env` en la raíz del proyecto (ver `.env.example`):

```env
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
DB_USER=
DB_PASSWORD=
DB_HOST=
DB_PORT=5432
SECRET_KEY=
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
TRUSTED_ORIGINS=http://localhost,http://127.0.0.1
```

Aplica migraciones y crea un usuario:

```bash
cd api
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## URLs

| Recurso | URL (Docker) | URL (local) |
|---|---|---|
| Admin | http://localhost/admin/ | http://127.0.0.1:8000/admin/ |
| API | http://localhost/api/ | http://127.0.0.1:8000/api/ |
| Docs (Swagger) | http://localhost/api/docs | http://127.0.0.1:8000/api/docs |
| OpenAPI JSON | http://localhost/api/openapi.json | http://127.0.0.1:8000/api/openapi.json |

## Autenticación

1. `POST /api/auth/login` con `{ "username": "...", "password": "..." }`
2. Usar el token en cada petición:

```
Authorization: Bearer <token>
```

Otros endpoints de auth:

- `POST /api/auth/logout` — invalida el token actual
- `GET /api/auth/me` — usuario autenticado

Los datos se filtran por equipos donde el usuario es miembro. `created_by` se asigna con el usuario del token.

## Endpoints

CRUD (list, create, get, patch, delete) en:

| Recurso | Ruta |
|---|---|
| Equipos | `/api/teams/` |
| Miembros | `/api/team-members/` |
| Categorías | `/api/categories/` |
| Cuentas | `/api/accounts/` |
| Movimientos | `/api/account-movements/` |
| Presupuestos | `/api/budgets/` |
| Créditos | `/api/credits/` |
| Cuotas | `/api/credit-installments/` |
| Gastos | `/api/expenses/` |
| Facturas | `/api/expense-invoices/` |

Listados paginados. Filtro opcional `team_id` (o `account_id` / `credit_id` / `expense_id` según el recurso).

Al crear un equipo, el usuario queda como dueño. Subida de facturas: `POST /api/expense-invoices/?expense_id=<id>` (multipart, campo `file`).

Campos calculados en lectura:

- `Account.balance`
- `Credit.is_paid`

## Modelos

- **Team / TeamMember** — equipos y membresías
- **Category** — ingreso (`IN`) o gasto (`OUT`)
- **Account / AccountMovement** — cuentas y movimientos
- **Budget** — presupuestos por periodo
- **Credit / CreditInstallment** — créditos y cuotas
- **Expense / ExpenseInvoice** — gastos y archivos
- **AuthToken** — tokens de API

Al crear un gasto se genera un movimiento de cuenta. Si está ligado a una cuota, también actualiza el pago.

## App

La lógica vive en `api/gastosapi/` (`models`, `api`, `routers`, `schemas`, `auth`). El proyecto Django está en `api/finanzasnica/` y `api/manage.py` es el punto de entrada.

Los archivos de facturas se guardan en `MEDIA_ROOT` (`/app/media` en Docker) y se sirven en `/media/`; los estáticos de Django se recolectan en `/app/static` y se sirven en `/static/`.
