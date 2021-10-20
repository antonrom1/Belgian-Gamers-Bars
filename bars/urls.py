"""BelgianGamersBars API URL Configuration
"""
from django.urls import path
from .views import index, AboutView, BarDetail

app_name = 'bars'

router = routers.SimpleRouter()
router.register(r'bars', BarApi)

urlpatterns = [
    path('', index, name="home"),
    path('about/', AboutView.as_view(), name="about"),
    path('bars/<pk>', BarDetail.as_view(), name="bar-detail"),
    path('api/', include((router.urls, app_name), namespace="api"))
]