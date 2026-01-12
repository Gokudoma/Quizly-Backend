from django.urls import path
from .views import RegistrationView, login_view
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('register/', RegistrationView.as_view(), name='registration'),
    path('login/', login_view, name='login'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]