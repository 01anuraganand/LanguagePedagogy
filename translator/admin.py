from django.contrib import admin
from django.db import models
from . models import AudioModel
# Register your models here.

@admin.register(AudioModel)
class AudioAdmin(admin.ModelAdmin):
    list_display = ['audio']