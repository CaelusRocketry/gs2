import os

from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from django.urls import path

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "groundstation.settings")

from groundstation.dashboard.consumers import GroundConsumer

application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),
        "websocket": URLRouter([path("gnd/", GroundConsumer.as_asgi())]),
    }
)
