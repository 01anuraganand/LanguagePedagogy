from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('', views.index, name= 'translate'),
    path('result/', views.text_translate_render, name = 'result'),
    path('speech/', views.text_speech_render, name = 'speech' ),
    path('pronunciation/', views.pronunciation_page, name = 'pronunciation_page'),
    path('pronunciationresult/', views.pronunciationresult, name = 'pronunciationresult'),
]