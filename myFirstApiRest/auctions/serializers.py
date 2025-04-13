from rest_framework import serializers 
from .models import Category, Auction, Bid
from django.utils import timezone 
from drf_spectacular.utils import extend_schema_field 

class BidSerializer(serializers.ModelSerializer):
    bidder_username = serializers.ReadOnlyField(source='bidder.username')  # opcional, para mostrar nombre del usuario
    bid_time = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%SZ", read_only=True)

    class Meta:
        model = Bid
        fields = ['id', 'auction', 'bidder', 'bidder_username', 'price', 'bid_time']
        read_only_fields = ['id', 'bid_time', 'bidder_username']

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("El precio de la puja debe ser un número positivo.")
        return value

    def validate_price(self, value):
        auction = self.context['auction']
        highest_bid = auction.bids.order_by('-price').first()
        if highest_bid and value <= highest_bid.price:
            raise serializers.ValidationError("The bid must be higher than the current highest bid.")
        if value <= auction.price:
            raise serializers.ValidationError("The bid must be higher than the starting price.")
        return value

    def create(self, validated_data):
        validated_data['auction'] = self.context['auction']
        validated_data['bidder'] = self.context['request'].user
        return super().create(validated_data)

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
