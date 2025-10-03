set -o errexit

echo "Starting build..."

if [ -f ".env" ]; then
  echo "Loading environment variables from .env"
  export $(grep -v '^#' .env | xargs)
fi

echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "Making migrations..."
python manage.py makemigrations --noinput || true

echo "Running database migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "👤 Creating superuser if not exists..."
python manage.py shell << END
from django.contrib.auth import get_user_model
import os
User = get_user_model()
username = os.getenv("DJANGO_SUPERUSER_USERNAME")
email = os.getenv("DJANGO_SUPERUSER_EMAIL")
password = os.getenv("DJANGO_SUPERUSER_PASSWORD")

if username and email and password:
    if not User.objects.filter(username=username).exists():
        User.objects.create_superuser(username, email, password)
        print(f"Superuser '{username}' created.")
    else:
        print(f"Superuser '{username}' already exists, skipping...")
else:
    print("⚠️ Missing DJANGO_SUPERUSER_* environment variables, skipping superuser creation.")
END

echo "✅ Build complete!"