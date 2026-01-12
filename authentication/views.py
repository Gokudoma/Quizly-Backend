import json
from django.contrib.auth import authenticate
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
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