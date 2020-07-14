from django.contrib.auth.models import AbstractUser
from django.db import models

# Stores ALL user credentials
class User(AbstractUser):
    def __str__(self):
        return f"{self.username} {self.password} {self.email}"

# Stores ALL listing and their active status
class auctionListing(models.Model):
    title = models.CharField(max_length=64, blank=False)
    description = models.TextField(blank=False)
    startingBid = models.IntegerField(blank=False)
    image = models.URLField(max_length=100000)
    date = models.DateTimeField(blank=False)
    listingOwner = models.ForeignKey(User, on_delete=models.CASCADE, related_name= 'listOwner')
    activeStatus = models.BooleanField(blank=False)

    class Category(models.TextChoices):
        Fashion = 'Fashion'
        Toys = 'Toys'
        Electronics = 'Electronics'
        Home = 'Home'

    category = models.CharField(max_length=30, blank=False, choices=Category.choices)

    def __str__(self):
        return f"{self.title} {self.description} {self.startingBid} {self.image} {self.date} {self.listingOwner} {self.activeStatus} {self.category}"


# Stores ALL bid for each listing
class auctionBid(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bidder")
    listing = models.ForeignKey(auctionListing, on_delete=models.CASCADE, related_name='listing')
    amount = models.IntegerField()

    def __str__(self):
        return f"{self.user} {self.listing} {self.amount}"

# Stores ALL comments for each listing
class listingComment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name= 'userComment')
    listing = models.ForeignKey(auctionListing, on_delete=models.CASCADE, related_name='listingComment')
    comments = models.CharField(max_length=100, blank=False)

    def __str__(self):
        return f"{self.user} {self.listing} {self.comments}"

# Stores ALL watched Listing for each User
class watchList(models.Model):
    Watcher = models.ManyToManyField(User)
    listing = models.ForeignKey(auctionListing, on_delete=models.CASCADE, related_name='watchedListing')

    def __str__(self):
        return f"{self.Watcher} {self.listing}"


