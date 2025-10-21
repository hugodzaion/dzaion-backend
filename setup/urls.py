from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

# DZAION-AUTH: Importação da nossa nova view customizada
from accounts.views import GoogleLoginView

# URLS V1
url_v1_patterns = [    # DZAION-AUTH: Rota de login do Google agora usa nossa view customizada
    path('accounts/auth/google/', GoogleLoginView.as_view(), name='google_login'),
    path('accounts/', include('accounts.urls')),
    path('tenants/', include('tenants.urls')),
    path('products/', include('products.urls')),
    path('activities/', include('activities.urls')),
    path('finances/', include('finances.urls')),
    path('locations/', include('locations.urls')),
    path('contacts/', include('contacts.urls')),
    path('tenants/<uuid:tenant_pk>/subscriptions/', include('entitlements.urls')),
    # URLS dos módulos
    path('crm/', include('crm.urls')),
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
