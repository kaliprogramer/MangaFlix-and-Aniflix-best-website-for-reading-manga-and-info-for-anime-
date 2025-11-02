from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from DataFeatcher.models import Anime, Banner, WatchList
from django.db.models import Q
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login ,logout
import requests
from .models import Bookmark
from Main.models import Manga
from django.contrib.auth import logout
import re
# Create your views here.



@login_required
def mangaview(request):
    query = request.GET.get('q')
    if query == "recent":
        result = Manga.objects.filter(status__icontains="Currently Airing")
    else:
        result = Manga.objects.filter(genres__icontains=query)
    paginator = Paginator(result, 50)
    page = request.GET.get('page')
    page_obj = paginator.get_page(page)
    return render(request,'views.html', {'results': page_obj,"query":query})




@login_required
def mangasearch(request):
    query = request.GET.get('m') or request.GET.get('q')

    results = []
    paged_results = []

    if query:
        keywords = query.split()
        q_objects = Q()
        for word in keywords:
            q_objects |= Q(title__icontains=word) | Q(genres__icontains=word)

        results = Manga.objects.filter(q_objects).distinct()
        paginator = Paginator(results, 30)
        page = request.GET.get('page')
        paged_results = paginator.get_page(page)

    return render(request, 'mangasearch.html', {
        'results': paged_results,
        'query': query,
        'type': 'manga'
    })
def mangadetail(request, manga_id):
    MANGA_ID = manga_id

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    }

    limit = 100
    offset = 0
    all_chapters = []

    while True:
        url = f"https://api.mangadex.org/chapter?manga={MANGA_ID}&limit={limit}&offset={offset}&translatedLanguage[]=en&order[chapter]=asc"
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            print("Failed to fetch chapters. Status code:", response.status_code)
            break

        data = response.json()
        chapters = data.get('data', [])
        if not chapters:
            break

        all_chapters.extend(chapters)
        offset += limit

    chapters_list = []
    for chapter in all_chapters:
        attributes = chapter.get('attributes', {})
        chapters_list.append({
            'id': chapter['id'],
            'chapter': attributes.get('chapter', 'No number'),
            'title': attributes.get('title', 'No Title')
        })

    total_chapters = len(chapters_list)  # total chapters

    result = Manga.objects.get(manga_id=manga_id)
    genres_list = result.genres.split(', ') if result.genres else []

    return render(request, 'mangadetail.html', {
        'result': result,
        'genres_list': genres_list,
        'chapters_list': chapters_list,
        'total_chapters': total_chapters,
        'manga_id':manga_id
    })


def manga_home(request):
    mangas = Manga.objects.filter(
        genres__icontains="Action"

    )[:40]
    banners = Banner.objects.filter(
        type__icontains="manga"

    )

    return render(request, 'manga_home.html', {"mangas": mangas,'banners': banners})
def chapter_reading(request, manga_id, chapter_index=0):
    headers = {"User-Agent": "Mozilla/5.0"}
    limit = 100
    offset = 0
    all_chapters = []

    while True:
        url = f"https://api.mangadex.org/chapter?manga={manga_id}&limit={limit}&offset={offset}&translatedLanguage[]=en&order[chapter]=asc"
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            break
        data = response.json()
        chapters = data.get('data', [])
        if not chapters:
            break
        all_chapters.extend(chapters)
        offset += limit

    if chapter_index >= len(all_chapters):
        return JsonResponse({"error": "No more chapters"}, status=404)

    chapter_id = all_chapters[chapter_index]['id']

    chapter_url = f"https://api.mangadex.org/at-home/server/{chapter_id}"
    response = requests.get(chapter_url, headers=headers)
    if response.status_code != 200:
        return JsonResponse({"error": "Failed to fetch chapter"}, status=500)

    data = response.json()
    base_url = data['baseUrl']
    chapter_data = data['chapter']

    if request.GET.get("ajax"):
        # Return JSON for JS
        return JsonResponse({
            "baseUrl": base_url,
            "chapter": {
                "hash": chapter_data['hash'],
                "dataSaver": chapter_data.get('dataSaver', chapter_data.get('data', []))
            }
        })

    # For normal page load
    chapter_list = [chap['id'] for chap in all_chapters]
    return render(request, 'chapter_reading.html', {
        'chapter_index': chapter_index,
        'manga_id': manga_id,
        'chapter_list': chapter_list,
        'current_index': chapter_index,
    })

def get_chapter(request, chapter_id):
    MANGADEX_API = "https://api.mangadex.org"
    url = f"{MANGADEX_API}/at-home/server/{chapter_id}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        return JsonResponse(data, safe=False)  # return chapter details
    else:
        return JsonResponse({
            "error": "Failed to fetch chapter",
            "status": response.status_code,
            "message": response.text
        }, status=response.status_code)



@login_required
def save_bookmark(request,manga_id):
    manga_id = manga_id

    if manga_id:
        try:
            manga = Manga.objects.get(manga_id=manga_id)
        except Manga.DoesNotExist:
            messages.error(request, "Manga not found.")
            return redirect("bookmark_list")

        # Check if already saved
        if Bookmark.objects.filter(user=request.user, manga_id=manga_id).exists():
            messages.warning(request, "Already saved to your bookmarks.")
        else:
            Bookmark.objects.create(
                user=request.user,
                manga_id=manga_id,
                title=manga.title,
                image_url=manga.image_url
            )
            messages.success(request, "Manga added to your bookmarks.")

    # Show only bookmarks of the logged-in user
    bookmarks = Bookmark.objects.filter(user=request.user).order_by("-created_at")
    paginator = Paginator(bookmarks, 10)
    page = request.GET.get("page")
    page_obj = paginator.get_page(page)

    return render(request, "Bookmark.html", {"results": page_obj})

def bookmark_list(request):
    results = Bookmark.objects.filter(user=request.user).order_by("-created_at")
    return render(request, "Bookmark.html",{"results": results})