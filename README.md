# FinanzasNica

API REST para gestionar gastos compartidos por equipos: cuentas, categorías, presupuestos, créditos y facturas.

Stack: **Django 6.1**, **Django Ninja**, **PostgreSQL**.

## Requisitos

- Python 3.12+
- PostgreSQL

## Instalación

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Crea un archivo `.env` en la raíz del proyecto:

```env
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
DB_USER=
DB_PASSWORD=
DB_HOST=
DB_PORT=5432
```

Aplica migraciones y crea un usuario:

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## URLs

| Recurso | URL |
|---|---|
| Admin | http://127.0.0.1:8000/admin/ |
| API | http://127.0.0.1:8000/api/ |
| Docs (Swagger) | http://127.0.0.1:8000/api/docs |
| OpenAPI JSON | http://127.0.0.1:8000/api/openapi.json |

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

La lógica vive en `gastosapi/` (`models`, `api`, `routers`, `schemas`, `auth`). El proyecto Django está en `finanzasnica/`.
