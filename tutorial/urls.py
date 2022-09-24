from django.urls import path

from .quickstart import views



urlpatterns = [
    path('parser/', views.parse),
]
