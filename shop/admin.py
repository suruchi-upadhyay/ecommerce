from django.contrib import admin

# Register your models here.
from .models import Product,Category, Contact, Order,OrderItem,Cart,CartItem,Wishlist,WishlistItem

admin.site.register(Product)
admin.site.register(Category)

admin.site.register(Contact)

admin.site.register(Order)
admin.site.register(OrderItem)



admin.site.register(Wishlist)
admin.site.register(WishlistItem)


admin.site.register(Cart)
admin.site.register(CartItem)


