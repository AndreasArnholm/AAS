from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    #re_path('ws/', websocket_view),
    re_path('ws/', consumers.UpdateConsumer.as_asgi()),
    re_path('stream/', consumers.StreamConsumer.as_asgi()),
]