from django.urls import path
from . import views

urlpatterns = [
    path("", views.manga_home, name="manga"),
    path("/mangasearch", views.mangasearch, name="mangasearch"),
    path("/mangaview", views.mangaview, name="mangaview"),
    path("/mangadetail/<uuid:manga_id>/", views.mangadetail, name="mangadetail"),
    path("/manga_reading/<uuid:manga_id>/chapter/<int:chapter_index>/", views.chapter_reading, name="chapter_reading"),
    path("/get_chapter/<str:chapter_id>/", views.get_chapter, name="get_chapter"),
    path("/save_bookmark/<uuid:manga_id>", views.save_bookmark, name="save_bookmark"),
    path("/Bookmark",views.bookmark_list, name="bookmark_list"),
]
