from django.urls import path
from . import views
urlpatterns = [
    path("", views.fetch_and_save_anime, name="index"),
]