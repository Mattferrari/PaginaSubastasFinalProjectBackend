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
    ComentarioRetrieveUpdateDestroyView,
    UserRatingView,
    MyComments,
    MyRatingsView
)

app_name = "auctions"

urlpatterns = [
    # Categorías
    # returns a list of all categories allowing to create new ones
    path('subastas/categorias/', CategoryListCreate.as_view(), name='category-list-create'), 
    # modifies or deletes a given category
    path('subastas/categoria/<int:pk>/', CategoryRetrieveUpdateDestroy.as_view(), name='category-detail'),


    # auctions
    # returns a list of all auctions allowing to create new ones
    path('subastas/', AuctionListCreate.as_view(), name='auction-list-create'),
    # modifies or deletes a given auction
    path('subastas/<int:pk>/', AuctionRetrieveUpdateDestroy.as_view(), name='auction-detail'),
    # returns a list of all auctions filtered by user
    path('subastas/mis-subastas/', AuctionByUserList.as_view(), name='auction-by-user'),


    # returns a list of all bids filtered by user
    path('subastas/mis-pujas/', BidByUserList.as_view(), name='bid-by-user'),
    # returns a list of all bids filtered by auction
    path('subastas/<int:id_subasta>/pujas/', BidListCreate.as_view(), name='bid-list-create'),
    # modifies or deletes a given bid (designated by auction and bid id)
    path('subastas/<int:id_subasta>/pujas/<int:idPuja>/', BidRetrieveUpdateDestroy.as_view(), name='bid-detail'),


    # Ratings
    # returns the list of all ratings
    path('subastas/<int:pk>/ratings/', PublicRatingsListView.as_view(), name='ratings-list'),
    # returns the rating of a person in a auction
    path('subastas/<int:auction_id>/user/rate/', UserRatingView.as_view(), name='rate-user-auction'),
    # allows to create or modify a rating for a given product
    path('subastas/<int:pk>/rate/', RateAuctionView.as_view(), name='rate-auction'),
    # deletes a given rating
    path('subastas/<int:auction_id>/rate/delete/', DeleteRatingView.as_view(), name='delete_rating'),
    # returns a list of user's ratings
    path('subastas/rate/user/', MyRatingsView.as_view(), name='mis-ratings'),

    # Comentarios
    # returns a list  of all comments allowing to create new ones
    path('subastas/<int:subasta_id>/comentarios/', ComentarioListCreateView.as_view(), name='comentarios-list-create'),
    # modifies or deletes a given comment
    path('subastas/<int:subasta_id>/comentarios/<int:pk>/', ComentarioRetrieveUpdateDestroyView.as_view(), name='comentario-detail'),
    # returns al list of user's comments
    path('subastas/comentarios/user/', MyComments.as_view(), name='mis-comentarios'),

]
