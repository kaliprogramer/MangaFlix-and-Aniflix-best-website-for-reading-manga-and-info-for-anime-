
from django.db import models
from django.contrib.auth.models import User
class Manga(models.Model):
    manga_id = models.CharField(max_length=100, unique=True)  # MangaDex ID
    title = models.CharField(max_length=300)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=50, blank=True, null=True)
    genres = models.CharField(max_length=500, blank=True, null=True)
    image_url = models.URLField(max_length=500, blank=True, null=True)
    rating = models.FloatField(blank=True, null=True)  # MangaDex may have average rating
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title



