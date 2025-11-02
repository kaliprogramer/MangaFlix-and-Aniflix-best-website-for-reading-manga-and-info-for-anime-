from django.db import models
from django.contrib.auth.models import User

class Bookmark(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    image_url = models.URLField(max_length=300,null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    manga_id = models.CharField(max_length=100)
    title = models.CharField(max_length=300)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'manga_id')

    def __str__(self):
        return f"{self.user.username} - {self.title}"
