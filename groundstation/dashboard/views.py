from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, StreamingHttpResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_POST
from .models import Test

def index(request):
    ctx: dict = {
        "sensors": {
            "pressure": ["PT-1", "PT-2", "PT-3", "PT-4"],
            "load": ["LC-1", "LC-2", "LC-3"],
            "thermocouple": ["TC-1"]
        }
    }
    return render(request, "home.html", ctx)

@ensure_csrf_cookie
def tests(request):
    tests = Test.objects.all()
    ctx: dict = {
        "test_list": tests
    }
    return render(request, "tests.html", ctx)

@require_POST
def delete_test(request, pk):
    test = get_object_or_404(Test, pk=pk)
    test.delete()    
    return JsonResponse({"success": True})

def export_test(request, pk):
    test = get_object_or_404(Test, pk=pk)

    def stream():
        yield "Caelus Rocketry Ground Software\n"
        yield f"Test #{pk}, ran on {test.created_at}\n---\n"
        for packet in test.packets.all():
            yield f"{packet.values}\n"

    response = StreamingHttpResponse(stream(), content_type="text/plain")
    response["Content-Disposition"] = "attachment; filename=\"test_{}_{}.txt\"".format(pk, test.created_at.strftime("%d_%b_%y"))

    return response