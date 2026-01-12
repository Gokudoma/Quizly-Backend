from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # 1. Fixes the 404 error: Makes the endpoint available at /api/createQuiz/
    path('api/', include('quiz_management.urls')),

    # 2. Standard Auth URLs (e.g., /api/login/, /api/logout/)
    path('api/', include('authentication.urls')),

    # 3. Legacy support: Keeps /api/token/refresh/ working to avoid breaking existing clients
    path('api/token/', include('authentication.urls')),
]