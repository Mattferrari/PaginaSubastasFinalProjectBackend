from django.shortcuts import render
from django.db.models import Q 
from rest_framework.exceptions import ValidationError, NotFound
from rest_framework.response import Response
from datetime import datetime
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.views import APIView
from django.utils import timezone 



from .permissions import IsOwnerOrAdmin, IsAuthorOrAdmin
from rest_framework import generics, status, permissions
from .models import Category, Auction, Bid, Rating, Comentario
from .serializers import (
    CategoryListCreateSerializer, 
    CategoryDetailSerializer, 
    AuctionListCreateSerializer, 
    AuctionDetailSerializer, 
    BidSerializer,
    RatingSerializer,
    ComentarioSerializer,
    AuctionUnautenticatedDetailSerializer
)

class ComentarioListCreateView(generics.ListCreateAPIView):
    serializer_class = ComentarioSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return Comentario.objects.filter(
            subasta_id=self.kwargs['subasta_id']
        ).order_by('-creado_en')

    def perform_create(self, serializer):
        serializer.save(
            autor=self.request.user,
            subasta_id=self.kwargs['subasta_id']
        )

class ComentarioRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ComentarioSerializer
    queryset = Comentario.objects.all()
    permission_classes = [IsAuthorOrAdmin]

    def perform_update(self, serializer):
        serializer.save()

    def perform_destroy(self, instance):
        instance.delete()

class MyComments(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        comentarios = Comentario.objects.filter(autor=user)
        serializer = ComentarioSerializer(comentarios, many=True)
        return Response({"value":serializer.data}, status=200)

class BidListCreate(generics.ListCreateAPIView):
    serializer_class = BidSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_auction(self):
        try:
            return Auction.objects.get(pk=self.kwargs['id_subasta'])
        except Auction.DoesNotExist:
            raise NotFound("Auction not found.")

    def get_queryset(self):
        auction = self.get_auction()
        return Bid.objects.filter(auction=auction)

    def perform_create(self, serializer):
        auction = self.get_auction()
        
        if auction.closing_date < timezone.now():
            raise ValidationError({"detail": "La subasta ya ha cerrado."})
        
        serializer.save(auction=auction, bidder=self.request.user.username)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['auction'] = self.get_auction()
        return context

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
        low_rating = params.get('low_rating', None)
        is_open = params.get('is_open', None)


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
        
        if low_rating:
            try:
                low_rating = float(low_rating)
            except ValueError:
                raise ValidationError(
                    {"low_rating": "Invalid value. Must be a number"},
                    code=status.HTTP_400_BAD_REQUEST
                )
    
        if low_rating:
            queryset = queryset.filter(rating__gte=max(0,min(5,low_rating)))

        if is_open:
            queryset = queryset.filter(closing_date__gt=timezone.now())

        return queryset
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class AuctionRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView): 
    queryset = Auction.objects.all() 
    serializer_class = AuctionDetailSerializer
    permission_classes = [IsOwnerOrAdmin]


    def perform_destroy(self, instance):
        instance.delete()

class AuctionDetailView(generics.RetrieveAPIView):
    permission_classes = [permissions.AllowAny]
    queryset = Auction.objects.all()
    serializer_class = AuctionUnautenticatedDetailSerializer

class AuctionByUserList(generics.ListAPIView):
    serializer_class = AuctionListCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Auction.objects.filter(user=self.request.user)
    

class PublicRatingsListView(generics.ListAPIView):
    queryset = Rating.objects.all()
    serializer_class = RatingSerializer
    permission_classes = [permissions.AllowAny]
    
class RateAuctionView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        try:
            auction = Auction.objects.get(pk=pk)
        except Auction.DoesNotExist:
            return Response({'error': 'Auction not found'}, status=status.HTTP_404_NOT_FOUND)

        data = request.data.copy()
        data['auction'] = auction.id  # asignar el id manualmente
        serializer = RatingSerializer(data=data, context={'request': request})

        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Rating saved'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
   
class DeleteRatingView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, auction_id):
        try:
            rating = Rating.objects.get(user=request.user, auction_id=auction_id)
            rating.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Rating.DoesNotExist:
            return Response({'detail': 'Valoración no encontrada.'}, status=status.HTTP_404_NOT_FOUND)

class UserRatingView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, auction_id):
        user = request.user  
        rating = Rating.objects.filter(user=user, auction_id=auction_id).first()

        if rating:
            return Response({"value": rating.value}, status=200)
        return Response({"value": None}, status=404)
    
class MyRatingsView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        ratings =  Rating.objects.filter(user=user)
        serializer = RatingSerializer(ratings, many=True)
        return Response({"value": serializer.data}, status=200)