from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("accounts/login/", views.login_view, name="login"),
    path("accounts/logout/", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create", views.create, name="create"),
    path("category", views.category, name="category"),
    path('<str:category>', views.categoryList, name="categoryList"),
    path('listing/AddBid', views.AddBid, name="AddBid"),
    path('listing/Comments', views.Comments, name="Comments"),
    path('listing/closeListing', views.closeListing, name="closeListing"),
    path('listing/listingWon', views.listingWon, name="listingWon"),
    path('listing/AddWatchList', views.addWatchList, name="addWatchlist"),
    path('listing/watchlist', views.watchlist, name="watchlist"),
    path('listing/<str:itemName>', views.item, name="item"),
    path('listing/deleteWatchlist/', views.deleteWishlist, name="deleteWatchlist"),
]
