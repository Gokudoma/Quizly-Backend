from django.urls import path
from .views import RegistrationView, login_view, LogoutView, CookieTokenRefreshView

urlpatterns = [
    path('register/', RegistrationView.as_view(), name='registration'),
    path('login/', login_view, name='login'),
    path('refresh/', CookieTokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', LogoutView.as_view(), name='logout'),
]