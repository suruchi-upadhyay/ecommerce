from django.urls import path
from . import views

from django.contrib.auth.views import LoginView
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path("", views.index, name="ShopHome"),
    path("about/", views.about, name="AboutUs"),
    path("contact/", views.contact, name="ContactUs"),
    path("tracker/", views.tracker, name="TrackingStatus"),
    path("search/", views.search, name="Search"),
    path('login/', LoginView.as_view(template_name="shop/login.html"), name="login"),

    path("logout",LogoutView.as_view(), name='logout'),
    path("signup/", views.signup, name="SignUp"),
    # path('signup/', views.SignUp.as_view(), name='SignUp'),

    

    path("products/<int:myid>", views.productView, name="ProductView"),
    path("checkout/", views.checkout, name="Checkout"),
    path("handlerequest/", views.handlerequest, name="HandleRequest"),
    # path("vendorprofile/<int:pk>",views.UserUpdate.as_view(),name='vendorprofile'),
    path("profile/",views.vendor, name='vendorprofile'),

]