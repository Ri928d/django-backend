from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from rest_framework import routers
from todo.views import InventoryItemView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

router = routers.DefaultRouter()
router.register(r'items', InventoryItemView, basename='item')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/auth/', include('authentication.urls')),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema')),
    path('', lambda request: HttpResponse('backend running')),
]

#done