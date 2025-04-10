from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User


# Create your models here.
class Category(models.Model): 
    name = models.CharField(max_length=50, blank=False, unique=True) 
 
    class Meta:  
        ordering=('id',)  
 
    def __str__(self): 
        return self.name 
 
class Auction(models.Model): 
    title = models.CharField(max_length=150) 
    description = models.TextField() 
    price = models.DecimalField(max_digits=10, 
                                decimal_places=2) 
    rating = models.DecimalField(max_digits=3, 
                                 decimal_places=2, 
                                 validators=[MaxValueValidator(5), MinValueValidator(1)]) 
    stock = models.IntegerField(validators=[MinValueValidator(1)]) 
    brand = models.CharField(max_length=100) 
    category = models.ForeignKey(Category, 
                                related_name='auctions', 
                                on_delete=models.CASCADE) 
    thumbnail = models.URLField() 
    creation_date = models.DateTimeField(auto_now_add=True)      
    closing_date = models.DateTimeField() 
 
    class Meta:  
        ordering=('id',)  
 
    def __str__(self): 
        return self.title
    
class Bid(models.Model):
    auction = models.ForeignKey(Auction, related_name='bids', on_delete=models.CASCADE)
    bidder = models.ForeignKey(User, related_name='bids', on_delete=models.CASCADE)  # Usuario que puja
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)])
    bid_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-bid_time'] 

    def __str__(self):
        return f"{self.bidder.username} - {self.amount}€ en {self.auction.title}"
