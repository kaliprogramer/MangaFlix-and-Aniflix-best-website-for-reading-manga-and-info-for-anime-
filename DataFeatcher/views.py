import requests
from django.http import HttpResponse
from .models import Anime
from django.db import transaction

@transaction.atomic
def fetch_and_save_anime(request):
    imported_count = 0
    for page in range(1, 500):  # 4 pages x 25 = 100 anime
        url = f"https://api.jikan.moe/v4/top/anime?limit=25&page={page}"
        res = requests.get(url)
        if res.status_code == 200:
            for item in res.json().get('data', []):
                anime, created = Anime.objects.update_or_create(
                    mal_id=item['mal_id'],
                    defaults={
                        'title': item['title'],
                        'synopsis': item.get('synopsis', ''),
                        'image_url': item['images']['jpg']['large_image_url'],
                        'score': item.get('score', 0),
                        'episodes': item.get('episodes', 0),
                        'status': item.get('status', ''),
                        'genres': ', '.join([g['name'] for g in item.get('genres', [])]),
                        'video_url' : item.get("embed_url"),
                        'trailer_thumbnail' : item.get("images", {}).get("maximun_image_url"),
                    }
                )
                if created:
                    imported_count += 1

    return HttpResponse(f"✅ Imported {imported_count} anime successfully.")
from django.shortcuts import render

# Create your views here.
