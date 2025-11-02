from django.urls import path,include
from . import views

urlpatterns = [
    path("Logout",views.logout_view,name="logout"),
    path("Login/",views.Login,name="login"),
    path("Signup/",views.signup,name="signup"),
    path("",views.home,name="home"),
    path("detail/<int:id>/",views.detail,name="detail"),
    path("search/",views.search,name="search"),
    path("view/",views.view,name="views"),
    path("WatchList/",views.save,name="save"),
    path("fetch_mangas",views.fetch_mangas, name="fetchmanga"),
    path("manga",include("manga.urls")),
]
