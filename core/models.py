from django.db import models

# Create your models here.
class Image(models.Model):
    id = models.BigAutoField(primary_key=True)
    photo = models.ImageField(upload_to = 'images')
    date = models.DateTimeField(auto_now_add=True)