from django.shortcuts import render
from django.db.models import Q 
from rest_framework.exceptions import ValidationError, NotFound
from rest_framework.response import Response
from datetime import datetime
from rest_framework.permissions import IsAuthenticatedOrReadOnly


from rest_framework import generics, status, permissions
from .models import Category, Auction, Bid
from .serializers import (
    CategoryListCreateSerializer, 
    CategoryDetailSerializer, 
    AuctionListCreateSerializer, 
    AuctionDetailSerializer, 
    BidSerializer
)


class BidListCreate(generics.ListCreateAPIView):
    serializer_class = BidSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def get_auction(self):
        try:
            return Auction.objects.get(pk=self.kwargs['id_subasta'])
        except Auction.DoesNotExist:
            raise NotFound("Auction not found.")

    def get_queryset(self):
        auction = self.get_auction()
        return Bid.objects.filter(auction=auction)

    def post(self, request, id_subasta):
        try:
            auction = Auction.objects.get(id=id_subasta)
        except Auction.DoesNotExist:
            return Response({"detail": "Subasta no encontrada."}, status=status.HTTP_404_NOT_FOUND)
        
        if auction.closing_date < datetime.now():
            return Response({"detail": "La subasta ya ha cerrado."}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = BidSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(auction=auction, bidder=request.user, bid_time=datetime.now())
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
class BidByUserList(generics.ListAPIView):
    """
    Endpoint para listar las pujas realizadas por el usuario autenticado.
    Se requiere enviar el token JWT en la cabecera (Authorization: Bearer <token>).
    """
    serializer_class = BidSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Filtra las pujas cuyo campo 'bidder' (string) concuerda con el username del usuario autenticado.
        return Bid.objects.filter(bidder=self.request.user.username)
    

class BidRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = BidSerializer
    lookup_url_kwarg = 'idPuja'

    def get_auction(self):
        try:
            return Auction.objects.get(pk=self.kwargs['id_subasta'])
        except Auction.DoesNotExist:
            raise NotFound("Auction not found.")

    def get_queryset(self):
        auction = self.get_auction()
        return Bid.objects.filter(auction=auction)

class CategoryListCreate(generics.ListCreateAPIView): 
    queryset = Category.objects.all() 
    serializer_class = CategoryListCreateSerializer 

class CategoryRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView): 
    queryset = Category.objects.all() 
    serializer_class = CategoryDetailSerializer 

class AuctionListCreate(generics.ListCreateAPIView): 
    queryset = Auction.objects.all() 
    serializer_class = AuctionListCreateSerializer 
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = Auction.objects.all()
        params = self.request.query_params

        search = params.get('texto', None)
        category = params.get('category', None)
        low_price = params.get('low_price', None)
        high_price = params.get('high_price', None)

        # Validación de búsqueda
        if search and len(search) < 3:
            raise ValidationError(
                {"search": "Search query must be at least 3 characters long."},
                code=status.HTTP_400_BAD_REQUEST
            )
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | Q(description__icontains=search)
            )

        # Validación de categoría
        if category and not Category.objects.filter(id=category).exists():
            raise ValidationError(
                {"category": "Category query ID must exist."},
                code=status.HTTP_400_BAD_REQUEST
            )
        if category:
            queryset = queryset.filter(category__id=category)

        # Validación de precios
        if low_price:
            try:
                low_price = float(low_price)
                if low_price <= 0.0:
                    raise ValidationError(
                        {"low_price": "Must be greater than 0."},
                        code=status.HTTP_400_BAD_REQUEST
                    )
            except ValueError:
                raise ValidationError(
                    {"low_price": "Invalid value. Must be a number."},
                    code=status.HTTP_400_BAD_REQUEST
                )

        if high_price:
            try:
                high_price = float(high_price)
            except ValueError:
                raise ValidationError(
                    {"high_price": "Invalid value. Must be a number."},
                    code=status.HTTP_400_BAD_REQUEST
                )

        if high_price and low_price and high_price < low_price:
            raise ValidationError(
                {"high_price": "Must be greater than low_price."},
                code=status.HTTP_400_BAD_REQUEST
            )

        # Aplicar filtros de precio
        if low_price:
            queryset = queryset.filter(price__gte=low_price)
        if high_price:
            queryset = queryset.filter(price__lte=high_price)

        return queryset
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class AuctionRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView): 
    queryset = Auction.objects.all() 
    serializer_class = AuctionDetailSerializer


class AuctionByUserList(generics.ListAPIView):
    serializer_class = AuctionListCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Auction.objects.filter(user=self.request.user)
    