from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/music/', include('musicapp.urls')),  # /api/music/songs, etc.
]
