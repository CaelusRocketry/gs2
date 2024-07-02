from django.shortcuts import render

def index_view(request):
    ctx: dict = {
        "sensors": {
            "pressure": ["PT-1", "PT-2", "PT-3", "PT-4"],
            "load": ["LC-1", "LC-2", "LC-3"],
            "thermocouple": ["TC-1"]
        }
    }
    return render(request, "home.html", ctx)