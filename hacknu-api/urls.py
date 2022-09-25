from django.urls import path

from .parser import views

urlpatterns = [
    path('parser/', views.parse),
]
