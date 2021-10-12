"""BelgianGamersBars API URL Configuration
"""
from django.urls import path
from .views import about

app_name = 'info'
urlpatterns = [
    path('', about, name="about"),
]