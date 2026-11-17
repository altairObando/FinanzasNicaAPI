#!/bin/sh
set -e

# Aplica migraciones pendientes contra la base de datos remota
python manage.py migrate --noinput

# Recolecta estáticos dentro del volumen montado en /app/static,
# para que nginx siempre sirva la versión generada por esta imagen.
python manage.py collectstatic --noinput

exec "$@"
