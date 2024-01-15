import os

from channels.routing import ProtocolTypeRouter, URLRouter, ChannelNameRouter
from django.core.asgi import get_asgi_application
from django.urls import path

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "groundstation.settings")

from groundstation.dal.gndconsumer import GroundConsumer
from groundstation.dal.fsbridge import FSBridge

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": URLRouter([
        path("data/", GroundConsumer.as_asgi())
    ]),
    "channel": ChannelNameRouter({
        "flight-software": FSBridge.as_asgi()
    })
})