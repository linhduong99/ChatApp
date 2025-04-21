from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Room, Message, User
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .serializers import RoomSerializer, MessageSerializer, UserSerializer, UserCreateSerializer
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth.hashers import check_password
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import Group
import logging

logger = logging.getLogger(__name__)

class IsAdminOrSelf(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Allow admin users to do anything
        if request.user.is_staff:
            return True
        # Allow users to modify their own data
        return obj == request.user

@login_required
def chat_room(request, room_name):
    room, created = Room.objects.get_or_create(name=room_name)
    messages = Message.objects.filter(room=room).order_by('timestamp')
    return render(request, 'chat/room.html', {
        'room_name': room_name,
        'messages': messages,
        'username': request.user.username
    })

@login_required
def index(request):
    rooms = Room.objects.all()
    return render(request, 'chat/index.html', {
        'rooms': rooms
    })

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    def get_permissions(self):
        if self.action in ['create', 'login']:
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer

    def create(self, request, *args, **kwargs):
        logger.info(f"Attempting to create user with username: {request.data.get('username')}")
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            logger.info(f"User created successfully: {user.username}")
            return Response({
                'user': serializer.data,
                'tokens': {
                    'access': str(refresh.access_token),
                    'refresh': str(refresh),
                }
            }, status=status.HTTP_201_CREATED)
        logger.error(f"User creation failed: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def login(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        
        if not username or not password:
            return Response({'error': 'Please provide both username and password'}, status=400)
            
        # Try to get user directly from database
        try:
            user = User.objects.get(username=username)
            if user.check_password(password):
                refresh = RefreshToken.for_user(user)
                return Response({
                    'user': UserSerializer(user).data,
                    'tokens': {
                        'access': str(refresh.access_token),
                        'refresh': str(refresh)
                    }
                })
        except User.DoesNotExist:
            pass
            
        return Response({'error': 'Invalid credentials'}, status=401)

    @action(detail=False, methods=['post'])
    def logout(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            logger.info("User logged out successfully")
            return Response({'message': 'Logged out successfully'})
        except Exception as e:
            logger.error(f"Logout failed: {str(e)}")
            return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def me(self, request):
        logger.info(f"Fetching current user info for: {request.user.username}")
        return Response(UserSerializer(request.user).data)

    @action(detail=True, methods=['delete'])
    def delete_account(self, request, pk=None):
        user = self.get_object()
        if user == request.user or request.user.is_staff:
            user.delete()
            return Response({'message': 'Account deleted successfully'})
        return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

    @action(detail=True, methods=['put'])
    def change_info(self, request, pk=None):
        user = self.get_object()
        if user != request.user and not request.user.is_staff:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

        data = request.data.copy()
        if 'password' in data:
            current_password = data.pop('current_password', None)
            if not current_password or not user.check_password(current_password):
                return Response({'error': 'Current password is incorrect'}, status=status.HTTP_400_BAD_REQUEST)
            user.set_password(data.pop('password'))

        serializer = UserSerializer(user, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def change_password(self, request, pk=None):
        user = self.get_object()
        if user != request.user and not request.user.is_staff:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

        current_password = request.data.get('current_password')
        new_password = request.data.get('new_password')

        if not current_password or not new_password:
            return Response({'error': 'Current password and new password are required'}, 
                          status=status.HTTP_400_BAD_REQUEST)

        if not user.check_password(current_password):
            return Response({'error': 'Current password is incorrect'}, 
                          status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()
        return Response({'message': 'Password changed successfully'})

class RoomViewSet(viewsets.ModelViewSet):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['post'])
    def check_password(self, request, pk=None):
        room = self.get_object()
        password = request.data.get('password')
        if room.check_password(password):
            return Response({'success': True})
        return Response({'success': False}, status=status.HTTP_400_BAD_REQUEST)

class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        queryset = Message.objects.all()
        room_id = self.request.query_params.get('room_id', None)
        if room_id is not None:
            queryset = queryset.filter(room_id=room_id)
        return queryset.order_by('created_at') 