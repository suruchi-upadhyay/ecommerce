from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
#from __future__ import unicode_literals

from django.db import models
from django.core.validators import RegexValidator
import hashlib
from django.core.validators import *
from django.core.exceptions import ValidationError


# Create your models here.
class SignUp(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.CharField(max_length=70, default="")
    phone = models.CharField(max_length=70, default="")
    password = models.CharField(max_length=70, default="")


class Product(models.Model):
    product_id = models.AutoField
    product_name = models.CharField(max_length=50)
    category = models.CharField(max_length=50, default="")
    subcategory = models.CharField(max_length=50, default="")
    price = models.IntegerField(default=0)
    desc = models.CharField(max_length=300)
    pub_date = models.DateField()
    image = models.ImageField(upload_to='shop/images', default="")

    def __str__(self):
        return self.product_name


class Vendor(models.Model):
    email = models.EmailField(primary_key=True)
    username = models.CharField(max_length=50)
    password = models.CharField(max_length=100)
    name = models.CharField(max_length=200)
    address = models.TextField()
    city = models.CharField(max_length=100, null=True)
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$',
                                 message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")  # look into regex
    phone = models.CharField(
        validators=[phone_regex], max_length=15, blank=True)
    is_authorized = models.BooleanField()

    def make_password(self, password):
        assert password
        hashedpassword = hashlib.md5(password.encode('utf-8')).hexdigest()
        return hashedpassword

    def check_password(self, password):
        assert password
        hashed = hashlib.md5(password.encode('utf-8')).hexdigest()
        return self.password == hashed

    def set_password(self, password):
        self.password = password

    def __str__(self):
        return self.name


class Customer(models.Model):
    email = models.EmailField(primary_key=True)
    password = models.CharField(max_length=100)
    name = models.CharField(max_length=200)
    address = models.TextField()
    city = models.CharField(max_length=100, null=True)
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$',
                                 message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")  # look into regex
    phone = models.CharField(
        validators=[phone_regex], max_length=15, blank=True)

    def make_password(self, password):
        assert password
        hashedpassword = hashlib.md5(password.encode('utf-8')).hexdigest()
        return hashedpassword

    def check_password(self, password):
        assert password
        hashed = hashlib.md5(password.encode('utf-8')).hexdigest()
        return self.password == hashed

    def set_password(self, password):
        self.password = password

    def __str__(self):
        return self.name


class Contact(models.Model):
    msg_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    email = models.CharField(max_length=70, default="")
    phone = models.CharField(max_length=70, default="")
    desc = models.CharField(max_length=500, default="")

    def __str__(self):
        return self.name


class Orders(models.Model):
    order_id = models.AutoField(primary_key=True)
    items_json = models.CharField(max_length=5000)
    amount = models.IntegerField(default=0)
    name = models.CharField(max_length=90)
    email = models.CharField(max_length=111)
    address = models.CharField(max_length=111)
    city = models.CharField(max_length=111)
    state = models.CharField(max_length=111)
    zip_code = models.CharField(max_length=111)
    phone = models.CharField(max_length=111, default="")

    def __str__(self):
        return self.name+phone


class OrderUpdate(models.Model):
    update_id = models.AutoField(primary_key=True)
    order_id = models.IntegerField(default="")
    update_desc = models.CharField(max_length=5000)
    timestamp = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.update_desc[0:7] + "..."
