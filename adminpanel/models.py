from django.db import models

# Create your models here.

class UserModel(models.Model):
    name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    
    ROLE_CHOICES =(
        ('admin','Admin'),
        ('staff','Staff'),
    )
    
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    
    def __str__(self):
        return self.name