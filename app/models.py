from django.db import models
from django.utils import timezone
# Create your models here.
class RegistrationModel(models.Model):
    name = models.CharField(max_length=30)
    email = models.EmailField(unique=True)
    mobile = models.CharField(max_length=10)
    password = models.CharField(max_length=128)
    otp = models.CharField(max_length=6, blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    def __str__(self):
        return self.name
    
class CategoryModel(models.Model):
    name = models.CharField(max_length=20)
    
    def __str__(self):
        return self.name

class SupplierModel(models.Model):
    name = models.CharField(max_length=100)
    contact_person = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True)
    mobile = models.CharField(max_length=15)
    address = models.TextField(blank=True)

    def __str__(self):
        return self.name

class ProductModel(models.Model):
    name = models.CharField(max_length=20)
    image = models.ImageField(upload_to='product_image')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    buy_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    stock = models.IntegerField()
    description = models.TextField()
    categories = models.ForeignKey(CategoryModel,on_delete=models.CASCADE)
    supplier = models.ForeignKey(SupplierModel, on_delete=models.SET_NULL, null=True, blank=True)
    
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
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    order_id = models.IntegerField(default=0)
    
    def __str__(self):
        return self.product.name
    
class OrderModel(models.Model):
    user = models.ForeignKey(RegistrationModel,on_delete=models.CASCADE)
    
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    name = models.CharField(max_length=50)
    mobile = models.CharField(max_length=10)
    address = models.TextField()
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    zipcode = models.CharField(max_length=6)
    payment_mode = models.CharField(max_length=20)
    transaction = models.TextField(blank=True,null=True)
    datetime = models.DateTimeField(auto_now=True)
    
    STATUS_CHOICES = (
        ('PLACED', 'Placed'),
        ('CONFIRMED', 'Confirmed'),
        ('DISPATCHED', 'Dispatched'),
        ('DELIVERED', 'Delivered'),
        ('CANCELLED', 'Cancelled'),
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PLACED')
    
    PAYMENT_STATUS_CHOICES = (
        ('PAID', 'Paid'),
        ('PENDING', 'Pending (Debtor)'),
    )
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='PAID')
    
    def __str__(self):
        return self.user.name
    
class orderItemModel(models.Model):
    order = models.ForeignKey(OrderModel,on_delete=models.CASCADE)
    product = models.ForeignKey(ProductModel,on_delete=models.CASCADE)
    qty = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return self.product.name
