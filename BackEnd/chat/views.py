from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Room, Message, User
from django.contrib.auth import authenticate, login, logout
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .serializers import RoomSerializer, MessageSerializer, UserSerializer, UserCreateSerializer
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth.hashers import check_password

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

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer

    @action(detail=False, methods=['post'])
    def login(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        
        try:
            user = User.objects.get(username=username)
            if user.check_password(password):
                login(request, user)
                return Response(UserSerializer(user).data)
            return Response({'error': 'Invalid password'}, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['post'])
    def logout(self, request):
        logout(request)
        return Response({'message': 'Logged out successfully'})

    @action(detail=True, methods=['delete'])
    def delete_account(self, request, pk=None):
        user = self.get_object()
        if user == request.user:
            user.delete()
            return Response({'message': 'Account deleted successfully'})
        return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

    @action(detail=True, methods=['put'])
    def change_info(self, request, pk=None):
        user = self.get_object()
        if user != request.user:
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
        if user != request.user:
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
    permission_classes = [permissions.AllowAny]

    def perform_create(self, serializer):
        user_id = self.request.data.get('user_id')
        if user_id:
            try:
                user = User.objects.get(id=user_id)
                serializer.save(created_by=user)
            except User.DoesNotExist:
                pass

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
    permission_classes = [permissions.AllowAny]

    def perform_create(self, serializer):
        user_id = self.request.data.get('user_id')
        if user_id:
            try:
                user = User.objects.get(id=user_id)
                serializer.save(user=user)
            except User.DoesNotExist:
                pass

    def get_queryset(self):
        queryset = Message.objects.all()
        room = self.request.query_params.get('room', None)
        if room is not None:
            queryset = queryset.filter(room=room)
        return queryset 