from django.shortcuts import render, get_object_or_404
from django.http import Http404, JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
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

def delete_test(request, pk):
    if request.method == "POST":
        test = get_object_or_404(Test, pk=pk)
        test.delete()    
        return JsonResponse({"success": True})
    raise Http404