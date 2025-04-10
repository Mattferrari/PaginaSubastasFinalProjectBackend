# from django.urls import path 
# from .views import (CategoryListCreate, 
#                     CategoryRetrieveUpdateDestroy, 
#                     AuctionListCreate, 
#                     AuctionRetrieveUpdateDestroy, 
#                     BidListCreate, 
#                     BidRetrieveUpdateDestroy)

# app_name="auctions" 
# urlpatterns = [ 
#     path('categories/', CategoryListCreate.as_view(), name='category-list-create'), 
#     path('categories/<int:pk>/', CategoryRetrieveUpdateDestroy.as_view(), name='category-detail'), 
#     path('', AuctionListCreate.as_view(), name='auction-list-create'), 
#     path('<int:pk>/', AuctionRetrieveUpdateDestroy.as_view(), name='auction-detail'), 
#     path('<int:id_subasta>/pujas/', BidListCreate.as_view()),
#     path('<int:id_subasta>/pujas/<int:idPuja>/', BidRetrieveUpdateDestroy.as_view()),
# ] 


from django.urls import path
from .views import (
    CategoryListCreate,
    CategoryRetrieveUpdateDestroy,
    AuctionListCreate,
    AuctionRetrieveUpdateDestroy,
    BidListCreate,
    BidRetrieveUpdateDestroy
)

app_name = "auctions"

urlpatterns = [
    # Categorías
    path('subastas/categorias/', CategoryListCreate.as_view(), name='category-list-create'),
    path('subastas/categoria/<int:pk>/', CategoryRetrieveUpdateDestroy.as_view(), name='category-detail'),

    # Subastas
    path('subastas/', AuctionListCreate.as_view(), name='auction-list-create'),
    path('subastas/<int:pk>/', AuctionRetrieveUpdateDestroy.as_view(), name='auction-detail'),

    # Pujas
    path('subastas/<int:id_subasta>/pujas/', BidListCreate.as_view(), name='bid-list-create'),
    path('subastas/<int:id_subasta>/pujas/<int:idPuja>/', BidRetrieveUpdateDestroy.as_view(), name='bid-detail'),
]
