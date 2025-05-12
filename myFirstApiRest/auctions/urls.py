from django.urls import path
from .views import (
    CategoryListCreate,
    CategoryRetrieveUpdateDestroy,
    AuctionListCreate,
    AuctionRetrieveUpdateDestroy,
    BidListCreate,
    BidRetrieveUpdateDestroy,
    AuctionByUserList,
    BidByUserList,
    DeleteRatingView,
    RateAuctionView,
    PublicRatingsListView,
    ComentarioListCreateView,
    ComentarioRetrieveUpdateDestroyView
)

app_name = "auctions"

urlpatterns = [
    # Categorías
    path('subastas/categorias/', CategoryListCreate.as_view(), name='category-list-create'),
    path('subastas/categoria/<int:pk>/', CategoryRetrieveUpdateDestroy.as_view(), name='category-detail'),

    path('subastas/', AuctionListCreate.as_view(), name='auction-list-create'),
    path('subastas/<int:pk>/', AuctionRetrieveUpdateDestroy.as_view(), name='auction-detail'),
    path('subastas/mis-subastas/', AuctionByUserList.as_view(), name='auction-by-user'),

    path('subastas/mis-pujas/', BidByUserList.as_view(), name='bid-by-user'),
    path('subastas/<int:id_subasta>/pujas/', BidListCreate.as_view(), name='bid-list-create'),
    path('subastas/<int:id_subasta>/pujas/<int:idPuja>/', BidRetrieveUpdateDestroy.as_view(), name='bid-detail'),

    path('subastas/<int:pk>/ratings/', PublicRatingsListView.as_view(), name='ratings-list'),
    path('subastas/<int:pk>/rate/', RateAuctionView.as_view(), name='rate-auction'),
    path('subastas/<int:auction_id>/rate/delete/', DeleteRatingView.as_view(), name='delete_rating'),

    path('subastas/<int:subasta_id>/comentarios/', ComentarioListCreateView.as_view(), name='comentarios-list-create'),
    path('subastas/<int:subasta_id>/comentarios/<int:pk>/', ComentarioRetrieveUpdateDestroyView.as_view(), name='comentario-detail'),

]
