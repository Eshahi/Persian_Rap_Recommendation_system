from django.db import models

class Song(models.Model):
    artist = models.CharField(max_length=100)
    title = models.CharField(max_length=100)
    # path to local MP3, or a URL in real usage
    audio_path = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f"{self.artist} - {self.title}"

class SongEmbedding(models.Model):
    """
    Storing each song's 2D embedding (ensc_x, ensc_y), or any extra info.
    """
    song = models.OneToOneField(Song, on_delete=models.CASCADE)
    ensc_x = models.FloatField()
    ensc_y = models.FloatField()

    def __str__(self):
        return f"Embedding for {self.song}"
