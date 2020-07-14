from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django import forms
from django.utils.safestring import mark_safe
import datetime
from .models import *

# This should have been stored in a Model for cleaner design
Categories = ['Fashion', 'Toys', 'Electronics', 'Home']

class CreateListingForm(forms.Form):
    title = forms.CharField(label="Title", max_length= 64, widget=forms.TextInput(attrs={'class' : 'myfieldclass'}))
    description = forms.CharField(label = "Description",widget=forms.Textarea(attrs={'class' : 'myfieldclass', "rows":50, "cols":50, 'style': 'height: 10em;'}))
    Bid = forms.IntegerField(label='Staring Bid')
    Image = forms.URLField(label='Image URL')

class CreateBidForm(forms.Form):
    Bid = forms.IntegerField(label='Bid Amount')

class CreateItemCommentsForm(forms.Form):
    comments = forms.CharField(label = "Description",widget=forms.Textarea(attrs={'class' : 'myfieldclass', "rows":50, "cols":50, 'style': 'height: 10em;'}))

def index(request):    
    # Filter by selecting ACTIVE ONLY auction listing
    listing = auctionListing.objects.filter(activeStatus=True) 
    if listing is not None:
            return render(request, "auctions/index.html", {
                "listing": listing
            })

    return render(request, "auctions/index.html")

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))

def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

@login_required
def create(request):
    Msg = ""
    if request.method == "POST":
        formData = CreateListingForm(request.POST)
        if(formData.is_valid()):
            newListTitle = formData.cleaned_data['title']
            newListDescription = formData.cleaned_data['description']
            newListBid = formData.cleaned_data['Bid']
            newListImage = formData.cleaned_data['Image']

            # Retrieve user data object from django's Model
            UserID = request.POST["username"]
            UserInstance = User.objects.get(username=UserID)

            Date = datetime.datetime.now()
            ActiveStatus = True
            Category = request.POST["category"]

            AuctionListing = auctionListing(title=newListTitle, description=newListDescription, 
                                            startingBid=newListBid, image=newListImage, date=Date, 
                                            listingOwner=UserInstance, activeStatus=ActiveStatus, category=Category)

            AuctionListing.save()
            Msg = f"Listing {newListTitle} was sucessfully added"

    print(Msg)       
    return render(request, "auctions/create.html", {
        "CreateForm": CreateListingForm(),
        "Categories": Categories,
        "createSucessMsg": Msg
    })

def category(request):
    return render(request, "auctions/category.html", {
        "categoryList": Categories
    })

def categoryList(request, category):
    # Use Category passed in to render all listing from auctionListing
    listing = auctionListing.objects.filter(category=category)
    if listing is not None:
            return render(request, "auctions/index.html", {
                "listing": listing
            })

def item(request, itemName):
    BiddingTextBox = CreateBidForm()
    Listing = auctionListing.objects.filter(title=itemName) 
    ListingComment = listingComment.objects.filter(listing=Listing[0])

    DeleteButton = False
    if Listing[0].listingOwner.username == request.user.username:
        DeleteButton = True

    print(Listing[0].listingOwner.username == request.user.username)

    if Listing is not None:
        return render(request, "auctions/listing.html", {
            "listing": Listing,
            "biddingBox": BiddingTextBox,
            "commentBox": CreateItemCommentsForm(),
            "comments": ListingComment,
            "deleteButton": DeleteButton
        })

@login_required
def addWatchList(request):
    if request.method == "POST":
        userID = request.POST["username"]
        itemName = request.POST["itemName"]
        # Grab Model object for current User
        UserInstance = User.objects.get(username=userID)
        # Grab Model object for current List Item
        ListItem = auctionListing.objects.get(title=itemName)

        WatchList = watchList(listing=ListItem)
        WatchList.save()
        WatchList.Watcher.add(UserInstance)

        return HttpResponseRedirect(reverse("item",args=[itemName]))

@login_required
def watchlist(request):
    UserID = request.user.username
    watchlist = watchList.objects.filter(Watcher=User.objects.get(username=UserID))
    
    return render(request, "auctions/watchlist.html", {
        "Item": watchlist
    })

@login_required
def deleteWishlist(request):
    if request.method == "POST":
        UserID = request.user.username
        itemName = request.POST["WatchlistItem"]
        # Grab Model object for current User
        UserInstance = User.objects.get(username=UserID)
        # Grab Model object for current List Item
        ListItem = auctionListing.objects.get(title=itemName)

        watchlist = watchList.objects.filter(Watcher=User.objects.get(username=UserID), listing=ListItem)
        watchlist.delete()
        return HttpResponseRedirect(reverse("watchlist"))

@login_required   
def AddBid(request):
    Msg = ""
    if request.method == "POST":
        itemName = request.POST["itemName"]
        NewBid = CreateBidForm(request.POST)
        if(NewBid.is_valid()):
            # Get new Bid Amt
            NewBidAmt = int(NewBid.cleaned_data["Bid"])
            # Check current Bid Amt
            item = auctionListing.objects.get(title=itemName)
            CurrBid = int(item.startingBid)

            if(NewBidAmt>CurrBid):
                # Update Listed Auction Item with the New Bid
                item.startingBid = NewBidAmt
                item.save()
                # Record the Bidding to auctionBid Model & the user that made the Bid
                AuctionBid = auctionBid(user=User.objects.get(username=request.user.username), listing=item, amount=NewBidAmt)
                AuctionBid.save()
                # Display Successful Bidding Message
                Msg = f"Your Bid of {NewBidAmt} has been placed sucessfully for {itemName}"
            else:
                Msg = f"You cannot offer a bid lower than the current ${CurrBid}"

            ListingComment = listingComment.objects.filter(listing=item)
            return render(request, "auctions/listing.html", {
                "listing": [item],
                "biddingBox": CreateBidForm(),
                "Message": Msg,
                "commentBox": CreateItemCommentsForm(),
                "comments": ListingComment
            })

@login_required
def Comments(request):
    if request.method == "POST":
        ItemComments = CreateItemCommentsForm(request.POST)
        if(ItemComments.is_valid()):
            comment = ItemComments.cleaned_data["comments"]
            itemName = request.POST["itemName"]
            # Grab Model object for current User
            UserInstance = User.objects.get(username=request.user.username)
            # Grab Model object for current List Item
            ListItem = auctionListing.objects.get(title=itemName)

            ListingComment = listingComment(user=UserInstance, listing=ListItem, comments=comment)
            ListingComment.save()

            return item(request, itemName)

@login_required
def closeListing(request):
    if request.method == "POST":
        itemName = request.POST["itemName"]
        item = auctionListing.objects.get(title=itemName)
        item.activeStatus = False
        item.save()

        return index(request)

@login_required
def listingWon(request):
    ListItemWonArray = []
    # Get all listing that have Active Status of FALSE (closed listing)
    AuctionListingArray = auctionListing.objects.filter(activeStatus=False)
    for listItem in AuctionListingArray:
        winningBid = listItem.startingBid
        # Get all Auction Bidder that have amount > or = to (closed listing) that current User has Bid
        ListItemWon = listItem.listing.filter(amount=winningBid, user=User.objects.get(username=request.user.username))
        if ListItemWon:
            ListItemWonArray.append(ListItemWon)

    print(ListItemWonArray[0][0].listing)
    return render(request, "auctions/winning.html", {
        "ItemWonArray": ListItemWonArray
    })
