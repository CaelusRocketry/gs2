from datetime import timedelta
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseForbidden, JsonResponse, StreamingHttpResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_POST
from .models import Test
from django.shortcuts import redirect
from django.conf import settings
import json

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
    if not test.completed:
        return HttpResponseForbidden()
    test.delete()    
    return JsonResponse({"success": True})

def export_test(request, pk):
    test = get_object_or_404(Test, pk=pk)
    
    if not test.completed:
        return HttpResponseForbidden()
    

    def stream():
        yield "Caelus Rocketry Ground Software\n"
        yield f"Test #{pk}, ran on {test.created_at}\n---\n"
        for packet in test.packets.all():
            yield f"{test.created_at + timedelta(seconds=packet.timestamp)} ({packet.timestamp}): {packet.values}\n"

    response = StreamingHttpResponse(stream(), content_type="text/plain")
    response["Content-Disposition"] = "attachment; filename=\"test_{}_{}.txt\"".format(pk, test.created_at.strftime("%d_%b_%y"))

    return response

def zeroall(request): # edits the sensor calibration directly cuz thats easier to do
    result = request.GET.get('result', None) # gets reading
    result = json.loads(result)

    print(settings.SENSOR_CALIBRATION_MAPPING) # print old calibration values
    
    # assign new values based on what was sent from frontend
    settings.SENSOR_CALIBRATION_MAPPING['PT-1'] -= result['PT-1']
    settings.SENSOR_CALIBRATION_MAPPING['PT-2'] -= result['PT-2']
    settings.SENSOR_CALIBRATION_MAPPING['PT-3'] -= result['PT-3']
    settings.SENSOR_CALIBRATION_MAPPING['PT-4'] -= result['PT-4']

    print(settings.SENSOR_CALIBRATION_MAPPING) # print new calibration values

    return redirect('index') # redirect to the index page