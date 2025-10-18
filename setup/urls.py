from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

# URLS V1
url_v1_patterns = [
    path('accounts/', include('accounts.urls')),
    # path('tenants/', include('tenants.urls')),
    # path('products/', include('products.urls')),
    path('activities/', include('activities.urls')),
]

# URLS webhooks
url_webhooks_patterns = [
    # path('whatsapp/', include('dispatchers.urls')),
]

urlpatterns = [

    path('admin/', admin.site.urls),
    # path('home/', include('home.urls')),
    path('v1/', include(url_v1_patterns)),

    path('webhooks/', include(url_webhooks_patterns)),

    path('v1/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('v1/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger_ui'),
    path('v1/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
