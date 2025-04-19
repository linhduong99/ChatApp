# Real-time Chat Application

A full-stack real-time chat application built with Next.js, Django, and WebSocket.

## Features

- Real-time messaging using WebSocket
- User authentication (login/register)
- Private and public chat rooms
- Password-protected rooms
- User profiles with avatars
- Responsive design
- Modern UI with Tailwind CSS

## Tech Stack

### Frontend
- Next.js 14
- TypeScript
- Tailwind CSS
- WebSocket API

### Backend
- Django 4.2
- Django REST Framework
- Django Channels (WebSocket)
- JWT Authentication
- PostgreSQL

## Prerequisites

- Node.js 18+ and npm
- Python 3.9+
- PostgreSQL

## Installation

### Backend Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/chat-app.git
cd chat-app/django-chat-app
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Run migrations:
```bash
python manage.py migrate
```

6. Start the development server:
```bash
python manage.py runserver
```

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd ../nextjs-chat-app
```

2. Install dependencies:
```bash
npm install
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. Start the development server:
```bash
npm run dev
```

## Environment Variables

### Backend (.env)
```
DEBUG=True
SECRET_KEY=your_secret_key
DATABASE_URL=postgres://user:password@localhost:5432/chat_app
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:3000
```

### Frontend (.env)
```
NEXT_PUBLIC_API_URL=http://localhost:8002
NEXT_PUBLIC_WS_URL=ws://localhost:8003
```

## API Endpoints

### Authentication
- `POST /api/token/` - Login
- `POST /api/users/` - Register
- `GET /api/current-user/` - Get current user info

### Rooms
- `GET /api/rooms/` - List rooms
- `POST /api/rooms/` - Create room
- `POST /api/rooms/{id}/join/` - Join room
- `POST /api/rooms/{id}/verify-password/` - Verify room password

### Messages
- `GET /api/rooms/{id}/messages/` - Get room messages
- `POST /api/rooms/{id}/messages/` - Send message

## WebSocket Events

### Connection
- `ws://localhost:8003/ws/chat/{room_name}/` - Connect to room

### Message Format
```json
{
  "message": "Hello!",
  "token": "jwt_token"
}
```

## Acknowledgments

- [Next.js](https://nextjs.org/)
- [Django](https://www.djangoproject.com/)
- [Django Channels](https://channels.readthedocs.io/)
- [Tailwind CSS](https://tailwindcss.com/) 