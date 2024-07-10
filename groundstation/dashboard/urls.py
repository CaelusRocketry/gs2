from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("tests", views.tests, name="tests"),
    path("delete_test/<int:pk>", views.delete_test, name="delete_test")
]