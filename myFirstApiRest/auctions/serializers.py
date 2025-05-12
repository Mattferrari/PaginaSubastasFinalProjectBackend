from rest_framework import serializers 
from .models import Category, Auction, Bid, Rating, Comentario
from django.utils import timezone 
from drf_spectacular.utils import extend_schema_field 
from django.db.models import Avg


class ComentarioSerializer(serializers.ModelSerializer):
    autor_username = serializers.CharField(source='autor.username', read_only=True)

    class Meta:
        model = Comentario
        fields = ['id', 'titulo', 'cuerpo', 'creado_en', 'actualizado_en', 'autor', 'autor_username', 'subasta']
        read_only_fields = ['autor', 'creado_en', 'actualizado_en', 'subasta', 'id']


class BidSerializer(serializers.ModelSerializer):
    bid_time = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%SZ", read_only=True)

    class Meta:
        model = Bid
        fields = ['id', 'auction', 'bidder', 'price', 'bid_time']
        read_only_fields = ['id', 'bid_time', 'auction']

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("El precio debe ser positivo.")
        
        auction = self.context.get('auction')
        if not auction:
            raise serializers.ValidationError("No se ha proporcionado subasta.")

        highest_bid = auction.bids.order_by('-price').first()
        if highest_bid and value <= highest_bid.price:
            raise serializers.ValidationError("La puja debe superar la puja más alta.")
        if value <= auction.price:
            raise serializers.ValidationError("La puja debe superar el precio inicial.")
        return value

class CategoryListCreateSerializer(serializers.ModelSerializer): 
    class Meta: 
        model = Category 
        fields = ['id', 'name'] 

class CategoryDetailSerializer(serializers.ModelSerializer): 
    class Meta: 
        model = Category 
        fields = '__all__' 

class AuctionListCreateSerializer(serializers.ModelSerializer): 
    creation_date = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%SZ", read_only=True) 
    closing_date = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%SZ") 
    isOpen = serializers.SerializerMethodField(read_only=True)

    class Meta: 
        model = Auction 
        fields = '__all__'
        read_only_fields = ('id', 'user', 'creation_date')  # <-- user marcado como read-only

    def validate_closing_date(self, value): 
        if value <= timezone.now(): 
            raise serializers.ValidationError("Closing date must be greater than now.") 
        elif (value - timezone.now()).days < 15:
            raise serializers.ValidationError("Closing date must be 15 or more days after now.") 
        return value

    @extend_schema_field(serializers.BooleanField()) 
    def get_isOpen(self, obj): 
        return obj.closing_date > timezone.now()
    

class AuctionDetailSerializer(serializers.ModelSerializer): 
    creation_date = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%SZ", read_only=True) 
    closing_date = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%SZ")
    isOpen = serializers.SerializerMethodField(read_only=True) 
    average_rating = serializers.SerializerMethodField(read_only=True) 

    class Meta: 
        model = Auction 
        fields = '__all__'
        read_only_fields = ('id', 'user', 'creation_date')

    @extend_schema_field(serializers.BooleanField())
    def get_isOpen(self, obj): 
        return obj.closing_date > timezone.now()

    def validate_closing_date(self, value): 
        if value <= timezone.now(): 
            raise serializers.ValidationError("Closing date must be greater than now.") 
        elif (value - timezone.now()).days < 15:
            raise serializers.ValidationError("Closing date must be 15 or more days after now.") 
        return value

    @extend_schema_field(serializers.FloatField())
    def get_average_rating(self, obj):
        avg = obj.ratings.aggregate(Avg('value'))['value__avg']
        return avg if avg is not None else 1.0

class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = ['value', 'auction']  # 'user' se infiere del request, no hace falta enviarlo

    def create(self, validated_data):
        user = self.context['request'].user
        auction = validated_data['auction']
        value = validated_data['value']

        # Update si ya existe, o crea si no existe
        instance, _ = Rating.objects.update_or_create(
            user=user,
            auction=auction,
            defaults={'value': value}
        )
        return instance


    
