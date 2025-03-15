from django.db import models

# Create your models here.


class Books(models.Model):
    name = models.CharField(max_length=200)
    author = models.CharField(max_length=100)
    price = models.FloatField(default=0)

    def __str__(self):
        return f"{self.name} by {self.author}"
