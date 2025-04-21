from django.urls import re_path
from . import consumers_new

websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<room_name>\w+)/$', consumers_new.ChatConsumer.as_asgi()),
] 