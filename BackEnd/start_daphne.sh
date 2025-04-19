#!/bin/bash

# Wait for Django to be ready
echo "Waiting for Django to be ready..."
while ! nc -z django 8002; do
  sleep 0.1
done

echo "Django is ready!"

# Initialize Django
export DJANGO_SETTINGS_MODULE=chat_project.settings
python -c "import django; django.setup()"

# Run migrations
python manage.py migrate

# Create default room if not exists
python -c "
import django
django.setup()
from chat.models import Room
Room.objects.get_or_create(name='chat_12')
"

# Start Daphne
daphne -b 0.0.0.0 -p 8003 chat_project.asgi:application 