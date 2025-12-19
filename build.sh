#!/usr/bin/env bash
set -euo pipefail

echo "Starting build..."

# Load environment variables safely
if [ -f ".env" ]; then
  echo "Loading environment variables from .env"
  set -a
  . ./.env
  set +a
fi

echo "Using Python:"
python --version

echo "Installing Python dependencies..."
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

echo "Making migrations..."
python manage.py makemigrations --noinput || true

echo "Running database migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Creating superuser if not exists..."
python manage.py shell <<'EOF'
from django.contrib.auth import get_user_model
import os

User = get_user_model()

username = os.getenv("DJANGO_SUPERUSER_USERNAME")
email = os.getenv("DJANGO_SUPERUSER_EMAIL")
password = os.getenv("DJANGO_SUPERUSER_PASSWORD")

if not (username and email and password):
    print("Missing DJANGO_SUPERUSER_* variables, skipping superuser creation.")
else:
    if not User.objects.filter(username=username).exists():
        User.objects.create_superuser(username, email, password)
        print(f"Superuser '{username}' created.")
    else:
        print(f"Superuser '{username}' already exists.")
EOF

echo "Build complete!"
