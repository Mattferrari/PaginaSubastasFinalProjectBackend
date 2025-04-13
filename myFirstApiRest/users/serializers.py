from rest_framework import serializers 
from .models import CustomUser 

class UserSerializer(serializers.ModelSerializer): 
    class Meta: 
        model = CustomUser 
        fields = ('id', 'first_name', 'last_name', 'username',
                    'email', 'birth_date', 'municipality', 'locality',
                    'password'
                ) 
        extra_kwargs = { 
            'password': {'write_only': True}, 
        } 

    def validate_email(self, value):
        user = self.instance  # Solo tiene valor cuando se está actualizando 
        if CustomUser.objects.filter(email=value).exclude(pk=user.pk if user else None).exists():
            raise serializers.ValidationError("Email already in use.")
        return value

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = CustomUser(**validated_data)
        print("Password recibida antes del set_password:", password)
        user.set_password(password)  # Este paso es crucial para encriptar la contraseña
        print("Password después del set_password:", user.password)  # Debería verse algo como "pbkdf2_sha256$..."
        user.save()
        return user
