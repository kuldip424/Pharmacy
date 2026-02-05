from django.contrib import admin
from .models import RegistrationModel,CategoryModel,ProductModel,ProductDetailModel,CartModel,OrderModel
# Register your models here.

class RegistrationModel_(admin.ModelAdmin):
    list_display = ['id','name','email','mobile']

admin.site.register(RegistrationModel,RegistrationModel_)

class ProductModel_(admin.ModelAdmin):
    list_display = ['id','name','image','price','stock','categories']
    
admin.site.register(ProductModel,ProductModel_)   


class CategoryModel_(admin.ModelAdmin):
    list_display = ['id','name']
admin.site.register(CategoryModel,CategoryModel_)

class ProductDetailModel_(admin.ModelAdmin):
    list_display = ['id','product']
admin.site.register(ProductDetailModel,ProductDetailModel_)

class CartModel_(admin.ModelAdmin):
    list_display = ['id','user','product','qty','total_price','order_id']
admin.site.register(CartModel,CartModel_)

class OrderModel_(admin.ModelAdmin):
    list_display=['id','user','product','qty','total_price','payment_mode','status','datetime']
admin.site.register(OrderModel,OrderModel_)