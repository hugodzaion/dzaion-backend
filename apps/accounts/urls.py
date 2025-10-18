from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from apps.accounts.views import CustomTokenObtainPairView
from apps.accounts import views as UserViews


urlpatterns = [
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('me/', UserViews.MeView.as_view()),
    path('register/', UserViews.RegisterView.as_view()),
]
