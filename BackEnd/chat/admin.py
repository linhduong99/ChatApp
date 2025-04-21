from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Room, Message, User

class CustomUserAdmin(UserAdmin):
    list_display = ('id', 'username', 'name', 'email', 'is_staff', 'is_superuser', 'get_groups')
    list_filter = ('is_staff', 'is_superuser', 'groups')
    search_fields = ('username', 'name', 'email')
    ordering = ('username',)

    def get_groups(self, obj):
        return ", ".join([group.name for group in obj.groups.all()])
    get_groups.short_description = 'Groups'

class RoomAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'created_by', 'created_at', 'has_password', 'message_count')
    list_filter = ('created_at', 'created_by')
    search_fields = ('name', 'created_by__username')
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)
    
    def has_password(self, obj):
        return bool(obj.password)
    has_password.boolean = True
    has_password.short_description = 'Password Protected'
    
    def message_count(self, obj):
        return obj.messages.count()
    message_count.short_description = 'Messages'

class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'content_preview', 'user', 'room', 'created_at')
    list_filter = ('created_at', 'room', 'user')
    search_fields = ('content', 'user__username', 'room__name')
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)
    
    def content_preview(self, obj):
        return obj.content[:50] + ('...' if len(obj.content) > 50 else '')
    content_preview.short_description = 'Content'

admin.site.register(User, CustomUserAdmin)
admin.site.register(Room, RoomAdmin)
admin.site.register(Message, MessageAdmin) 