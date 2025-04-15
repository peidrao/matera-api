#!/bin/sh

echo "Aplicando migrations..."
python manage.py migrate

echo "Populando banco de dados"
python manage.py seed


echo "Iniciando servidor..."
exec "$@"