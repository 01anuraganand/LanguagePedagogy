from django.urls import path
from . import views


urlpatterns = [
    path('', views.index_home, name='indexhome'),
    path('image_text_extract/', views.render_upload_photo_extract_text, name='extract_image_text'),
    path('postagging/', views.get_text_for_pos, name='pos_tagging_url'), 
    path('fileformaterror/', views.fileformaterror, name='fileformaterror'),
] 