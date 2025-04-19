from rest_framework import serializers
from django.contrib.auth.hashers import make_password, check_password
from .models import User, Room, Message

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'name', 'avatar', 'bio', 'created_at']
        read_only_fields = ['id', 'created_at']

class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['username', 'name', 'password', 'avatar', 'bio']
    
    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

class RoomSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)
    has_password = serializers.SerializerMethodField()
    
    class Meta:
        model = Room
        fields = ['id', 'name', 'password', 'has_password', 'created_by', 'created_at']
        read_only_fields = ['id', 'created_by', 'created_at']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def get_has_password(self, obj):
        if isinstance(obj, dict):
            return bool(obj.get('password'))
        return bool(obj.password)

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        room = Room.objects.create(**validated_data)
        if password:
            room.set_password(password)
            room.save()
        return room

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance

class MessageSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Message
        fields = ['id', 'room', 'user', 'content', 'created_at']
        read_only_fields = ['id', 'user', 'created_at'] 