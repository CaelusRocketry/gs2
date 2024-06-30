from groundstation import settings
from django.shortcuts import render

def index_view(request):
    ctx: dict = {
        "sensors": settings.CONFIG["sensors"]
    }
    return render(request, "home.html", ctx)