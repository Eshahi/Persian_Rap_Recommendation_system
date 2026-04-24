from django.urls import path
from . import views

urlpatterns = [
    path('songs/', views.song_list, name='song_list'),
    path('song-detail/', views.song_detail, name='song_detail'),
]
