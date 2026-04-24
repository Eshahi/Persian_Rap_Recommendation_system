from rest_framework import serializers
from .models import Song, SongEmbedding

class SongSerializer(serializers.ModelSerializer):
    class Meta:
        model = Song
        fields = '__all__'

class SongEmbeddingSerializer(serializers.ModelSerializer):
    # embed the related Song data, if needed
    song = SongSerializer()
    class Meta:
        model = SongEmbedding
        fields = '__all__'
