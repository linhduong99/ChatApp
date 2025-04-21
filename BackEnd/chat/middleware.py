import logging
from django.utils.deprecation import MiddlewareMixin
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
import jwt
from django.conf import settings
from django.http import JsonResponse
from rest_framework import status
from .models import User
from django.contrib.auth.models import AnonymousUser

logger = logging.getLogger(__name__)

class AuthenticationLoggingMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # List of paths that don't require authentication
        PUBLIC_PATHS = [
            '/api/users/login/',
            '/api/token/refresh/',
            '/admin',
            '/favicon.ico',
            '/static/',
            '/media/',
        ]

        # Skip validation for OPTIONS requests
        if request.method == 'OPTIONS':
            request._user = AnonymousUser()
            return None

        # Get the full path
        full_path = request.get_full_path()
        logger.info(f"Processing request to path: {full_path}")

        # Skip validation for public paths
        if any(full_path.startswith(path) for path in PUBLIC_PATHS):
            logger.info(f"Skipping authentication for public path: {full_path}")
            request._user = AnonymousUser()
            return None

        # Get the authorization header
        auth_header = request.headers.get('Authorization', '')
        
        # Log the request details
        logger.info(f"Request to {full_path} with method {request.method}, auth_header: {auth_header}")
        
        if not auth_header.startswith('Bearer '):
            logger.warning(f"No token provided for request to {full_path}")
            request._user = AnonymousUser()
            return JsonResponse(
                {'error': 'Authentication credentials were not provided.'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )

        token = auth_header.split(' ')[1]
        try:
            # Try to validate the token
            access_token = AccessToken(token)
            # Log token details
            decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            logger.info(f"Valid token for request to {full_path}. Token details: {decoded_token}")
            
            # Get user from token and set it in request
            user_id = decoded_token.get('user_id')
            try:
                user = User.objects.get(id=user_id)
                request._user = user
                logger.info(f"User {user.username} authenticated for request to {full_path}")
            except User.DoesNotExist:
                logger.warning(f"User with id {user_id} not found")
                request._user = AnonymousUser()
                return JsonResponse(
                    {'error': 'User not found.'}, 
                    status=status.HTTP_401_UNAUTHORIZED
                )
                
            return None
        except (InvalidToken, TokenError) as e:
            logger.warning(f"Invalid token for request to {full_path}: {str(e)}")
            request._user = AnonymousUser()
            return JsonResponse(
                {'error': 'Invalid token.'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        except jwt.InvalidTokenError as e:
            logger.warning(f"JWT decode error for request to {full_path}: {str(e)}")
            request._user = AnonymousUser()
            return JsonResponse(
                {'error': 'Invalid token format.'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )

class CorsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.method == "OPTIONS":
            response = self.get_response(request)
            response["Access-Control-Allow-Origin"] = "http://localhost:4000"
            response["Access-Control-Allow-Methods"] = "GET, POST, PUT, PATCH, DELETE, OPTIONS"
            response["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-Requested-With"
            response["Access-Control-Allow-Credentials"] = "true"
            return response

        response = self.get_response(request)
        response["Access-Control-Allow-Origin"] = "http://localhost:4000"
        response["Access-Control-Allow-Methods"] = "GET, POST, PUT, PATCH, DELETE, OPTIONS"
        response["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-Requested-With"
        response["Access-Control-Allow-Credentials"] = "true"
        return response 