"""BelgianGamersBars API URL Configuration
"""
from django.urls import path
from .views import index, AboutView, BarDetail

app_name = 'bars'
urlpatterns = [
    path('', index, name="home"),
    path('about/', AboutView.as_view(), name="about"),
    path('bars/<pk>', BarDetail.as_view(), name="bar-detail"),
]