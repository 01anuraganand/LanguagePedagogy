from django.db import models

# Create your models here.
class AudioModel(models.Model):
    audio = models.FileField(db_index=True, upload_to='audio')
    