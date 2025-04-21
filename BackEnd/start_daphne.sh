#!/bin/bash

# Wait for Django to be ready
echo "Waiting for Django service..."
until nc -z django 8002; do
  sleep 2
  echo "Still waiting for Django..."
done
echo "Django is available!"

# Start Daphne server
daphne -b 0.0.0.0 -p 8003 chat_project.asgi:application 