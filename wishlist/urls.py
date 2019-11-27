from . import views
from django.urls import path
app_name = "wishlist"
urlpatterns = [

    # url(r'^add/(?P<product_id>\d+)/$', views.wishlist_add, name='wishlist_add'),
    # url(r'^remove/(?P<product_id>\d+)/$', views.wishlist_remove, name='wishlist_remove'),
    # url(r'^$', views.wishlist_detail, name='wishlist_detail'),

    


    path("", views.wishlist_detail, name="wishlist_detail"),

    path("remove/<int:product_id>", views.wishlist_remove, name="wishlist_remove"),
    path("add/<int:product_id>", views.wishlist_add, name="wishlist_add"),

    
    # path("checkout/", views.checkout, name="Checkout"),
    # path("vendorprofile/<int:pk>",views.UserUpdate.as_view(),name='vendorprofile'),
    

]