import json
from django.contrib.auth import authenticate
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from .serializers import RegistrationSerializer

# --- Existing RegistrationView (Do not delete) ---
class RegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"detail": "User created successfully!"},
                status=status.HTTP_201_CREATED
            )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# --- New Login View (Matches documentation exactly) ---
@csrf_exempt
def login_view(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            username = data.get("username")
            password = data.get("password")

            user = authenticate(request, username=username, password=password)

            if user is not None:
                # Generate real JWT tokens using SimpleJWT
                refresh = RefreshToken.for_user(user)
                access_token = str(refresh.access_token)

                # Construct the JSON response structure
                response_data = {
                    "detail": "Login successfully!",
                    "user": {
                        "id": user.id,
                        "username": user.username,
                        "email": user.email
                    }
                }

                response = JsonResponse(response_data, status=200)

                # Set tokens as HttpOnly cookies
                response.set_cookie(
                    key='access_token',
                    value=access_token,
                    httponly=True,
                    samesite='Lax',
                    secure=False  # Set to True in production
                )
                
                response.set_cookie(
                    key='refresh_token',
                    value=str(refresh),
                    httponly=True,
                    samesite='Lax',
                    secure=False
                )

                return response
            
            else:
                # 401 Error message matching the documentation
                return JsonResponse({"detail": "Ungültige Anmeldedaten."}, status=401)

        except json.JSONDecodeError:
            return JsonResponse({"detail": "Invalid JSON"}, status=400)
    
    return JsonResponse({"detail": "Method not allowed"}, status=405)

# --- Logout View ---
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            # Retrieve refresh token from cookie
            refresh_token = request.COOKIES.get('refresh_token')
            
            # If cookie is missing, optionally check body (fallback)
            if not refresh_token:
                refresh_token = request.data.get('refresh')
            
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()  # Blacklist the token
        except (TokenError, Exception):
            # Ignore errors (e.g. token already invalid), perform logout anyway
            pass

        response = Response(
            {"detail": "Log-Out successfully! All Tokens will be deleted. Refresh token is now invalid."},
            status=status.HTTP_200_OK
        )

        # Remove cookies
        response.delete_cookie('access_token')
        response.delete_cookie('refresh_token')
        
        return response