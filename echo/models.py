from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.


class Books(models.Model):
    name = models.CharField(max_length=200)
    author = models.CharField(max_length=100)
    price = models.FloatField(default=0)

    def __str__(self):
        return f"{self.name} by {self.author}"


class User(AbstractUser):
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=[
        ('user', 'Regular User'),
        ('admin', 'Administrator')
    ], default='user')

    class Meta:
        swappable = 'AUTH_USER_MODEL'

    # Login, passwd, name is included in AbstractUser

    def __str__(self):
        return f"{self.username} ({self.role})"


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    total_price = models.FloatField(default=0)

    def __str__(self):
        return f"Order #{self.id} by {self.user.username} on {self.created_at}"


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name='items')
    book_name = models.CharField(max_length=200)
    book_author = models.CharField(max_length=100)
    price = models.FloatField()
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.quantity} x {self.book_name} in Order #{self.order.id}"
