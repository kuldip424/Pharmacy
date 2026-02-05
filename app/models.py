from django.db import models
from django.utils import timezone
# Create your models here.
class RegistrationModel(models.Model):
    name = models.CharField(max_length=30)
    email = models.EmailField(unique=True)
    mobile = models.CharField(max_length=10)
    password = models.CharField(max_length=15)
    otp = models.CharField(max_length=6, blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    def __str__(self):
        return self.name
    
class CategoryModel(models.Model):
    name = models.CharField(max_length=20)
    
    def __str__(self):
        return self.name

class ProductModel(models.Model):
    name = models.CharField(max_length=20)
    image = models.ImageField(upload_to='product_image')
    price = models.IntegerField()
    stock = models.IntegerField()
    description = models.TextField()
    categories = models.ForeignKey(CategoryModel,on_delete=models.CASCADE)
    
    manufacture_date = models.DateField()
    expiry_date = models.DateField()
    def __str__(self):
        return self.name
    
class ProductDetailModel(models.Model):
    moredescription = models.TextField()
    product = models.ForeignKey(ProductModel,on_delete=models.CASCADE)
    
    def __str__(self):
        return self.product
    
    
class CartModel(models.Model):
    user = models.ForeignKey(RegistrationModel, on_delete=models.CASCADE)
    product = models.ForeignKey(ProductModel,on_delete=models.CASCADE)
    qty = models.IntegerField()
    total_price = models.IntegerField()
    order_id = models.IntegerField(default=0)
    
    def __str__(self):
        return self.product.name
    
class OrderModel(models.Model):
    user = models.ForeignKey(RegistrationModel,on_delete=models.CASCADE)
    product = models.ForeignKey(ProductModel,on_delete=models.CASCADE,null=True,
        blank=True)
    qty = models.IntegerField(blank=True, null=True)
    total_price = models.IntegerField()
    name = models.CharField(max_length=50)
    mobile = models.CharField(max_length=10)
    address = models.TextField()
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    zipcode = models.CharField(max_length=6)
    payment_mode = models.CharField(max_length=20)
    transaction = models.TextField(blank=True,null=True)
    datetime = models.DateTimeField(auto_now=True)
    status = models.CharField(default='PLACED')
    
    def __str__(self):
        return self.user.name
