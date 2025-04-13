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
        user = self.instance  
        if CustomUser.objects.filter(email=value).exclude(pk=user.pk if user else None).exists():
            raise serializers.ValidationError("Email already in use.")
        return value

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = CustomUser(**validated_data)
        print("Password recibida antes del set_password:", password)
        user.set_password(password)  
        print("Password después del set_password:", user.password) 
        user.save()
        return user
    
    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.set_password(password)

        instance.save()
        return instance
