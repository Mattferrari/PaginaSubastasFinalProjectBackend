# auctions/models.py
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings
from django.db.models import Avg


class Category(models.Model): 
    name = models.CharField(max_length=50, blank=False, unique=True) 
 
    class Meta:  
        ordering = ('id',)  
 
    def __str__(self): 
        return self.name 
 
class Auction(models.Model): 
    title = models.CharField(max_length=150) 
    description = models.TextField() 
    price = models.DecimalField(max_digits=10, decimal_places=2) 

    stock = models.IntegerField(validators=[MinValueValidator(1)]) 
    brand = models.CharField(max_length=100) 
    category = models.ForeignKey(Category, related_name='auctions', on_delete=models.CASCADE) 
    thumbnail = models.URLField() 
    creation_date = models.DateTimeField(auto_now_add=True)      
    closing_date = models.DateTimeField()
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='auctions',
        null=True
    )
 
    class Meta:  
        ordering = ('id',)  
 
    def __str__(self): 
        return self.title
    
    @property
    def average_rating(self):
        avg = self.ratings.aggregate(Avg('value'))['value__avg']
        return round(avg, 2) if avg is not None else 1.0
    
class Bid(models.Model):
    auction = models.ForeignKey(Auction, related_name='bids', on_delete=models.CASCADE)
    bidder = models.CharField(max_length=150)
    price = models.DecimalField(
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    bid_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-bid_time'] 

    def __str__(self):
        return f"{self.bidder} - {self.price}€ en {self.auction.title}"


class Rating(models.Model):
    value = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='ratings'
    )
    auction = models.ForeignKey(
        Auction,
        on_delete=models.CASCADE,
        related_name='ratings'
    )

    class Meta:
        unique_together = ('user', 'auction')  # Un usuario no puede valorar una subasta más de una vez

    def __str__(self):
        return f'{self.user.username} - {self.value} en {self.auction.title}'
    

class Comentario(models.Model):
    titulo = models.CharField(max_length=100)
    cuerpo = models.TextField()
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    autor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='comentarios')
    subasta = models.ForeignKey(Auction, on_delete=models.CASCADE, related_name='comentarios')

    def __str__(self):
        return f"{self.titulo} - {self.autor.username}"