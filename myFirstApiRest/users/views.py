from django.shortcuts import render
from rest_framework.generics import RetrieveUpdateAPIView

# Create your views here.
from rest_framework import status, generics, permissions
from rest_framework.response import Response 
from rest_framework_simplejwt.tokens import RefreshToken 
from rest_framework.views import APIView 

from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from django.contrib.auth import authenticate

from .models import CustomUser 
from .serializers import UserSerializer
 
class UserRegisterView(generics.CreateAPIView): 
    permission_classes = [AllowAny]
    queryset = CustomUser.objects.all() 
    serializer_class = UserSerializer 
 
    def create(self, request, *args, **kwargs): 
        serializer = self.get_serializer(data=request.data) 
        if serializer.is_valid():
            user = serializer.save() 
            refresh = RefreshToken.for_user(user) 
            return Response({ 
                'user': serializer.data, 
                'access': str(refresh.access_token), 
                'refresh': str(refresh), 
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, 
status=status.HTTP_400_BAD_REQUEST) 
 
class UserListView(generics.ListAPIView): 
    permission_classes = [IsAdminUser]
    serializer_class = UserSerializer 
    queryset = CustomUser.objects.all() 
 
class UserRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView): 
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer 
    queryset = CustomUser.objects.all()

class LogoutView(APIView): 
    permission_classes = [IsAuthenticated]
    def post(self, request): 
        """Realiza el logout eliminando el RefreshToken (revocar)""" 
        try: 
            # Obtenemos el RefreshToken del request  
     #Se esperan que esté en el header Authorization 
            refresh_token = request.data.get('refresh', None) 
            if not refresh_token: 
                return Response({"detail": "No refresh token provided."}, 
status=status.HTTP_400_BAD_REQUEST) 
 
            # Revocar el RefreshToken 
            token = RefreshToken(refresh_token) 
            token.blacklist()   
            return Response({"detail": "Logout successful"}, 
status=status.HTTP_205_RESET_CONTENT) 
 
        except Exception as e: 
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
class UserMeView(generics.RetrieveUpdateAPIView):
    """
    Endpoint para obtener los datos del usuario autenticado.
    """
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user
    def update(self, request, *args, **kwargs):
        user = self.get_object()
        if "password" in request.data:
            user.set_password(request.data["password"])
            user.save()
            return Response({"detail": "Contraseña actualizada correctamente."})
        return super().update(request, *args, **kwargs)
