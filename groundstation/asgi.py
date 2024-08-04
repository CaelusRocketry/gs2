import os

from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from django.urls import path

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'groundstation.settings')
django_asgi_app = get_asgi_application()

from groundstation.dashboard.consumers import GroundConsumer

application = ProtocolTypeRouter({
    'http': django_asgi_app,
    'websocket': URLRouter([
        path('data/', GroundConsumer.as_asgi())
    ])
})