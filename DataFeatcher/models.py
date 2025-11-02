from django.db import models
from django.contrib.auth.models import User
class Anime(models.Model):
    mal_id = models.IntegerField(unique=True)  # Unique MAL ID
    title = models.CharField(max_length=255)
    synopsis = models.TextField(blank=True, null=True)
    image_url = models.URLField()
    score = models.FloatField(blank=True, null=True)
    episodes = models.IntegerField(blank=True, null=True)
    status = models.CharField(max_length=100, blank=True, null=True)
    genres = models.CharField(max_length=255, blank=True, null=True)
    video_url = models.URLField(null=True, blank=True)
    trailer_thumbnail = models.URLField(null=True, blank=True)
    def __str__(self):
        return self.title

class Banner(models.Model):
    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to='banner/',null=True, blank=True)
    type = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.title
    



class WatchList(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    anime_id = models.IntegerField( null=True, blank=True)  # remove unique=True
    title = models.CharField(max_length=255, null=True, blank=True)
    image_url = models.URLField( null=True, blank=True)
    score = models.FloatField(blank=True, null=True)
    status = models.CharField(max_length=100, blank=True, null=True)
    episodes = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username if self.user else 'Anonymous'} - {self.title}"

