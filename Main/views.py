from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from DataFeatcher.models import Anime, Banner, WatchList
from django.db.models import Q
from django.core.paginator import Paginator
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login ,logout
import requests
from .models import Manga
from django.contrib.auth import logout
import re
def logout_view(request):
    logout(request)
    return redirect('home')

def signup(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        print("Data received:", first_name, last_name, username)

        # 🔐 Validation
        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, 'signup.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken.")
            return render(request, 'signup.html')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
            return render(request, 'signup.html')

        # ✅ Create user
        user = User.objects.create_user(
            username=username,
            password=password,
            email=email,
            first_name=first_name,
            last_name=last_name
        )
        user.save()

        # ✅ Log in the user
        login(request, user)
        return redirect('home')

    return render(request, 'signup.html')



def Login(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')  # success
        else:
            return redirect("signup")


    return render(request, 'login.html')

@login_required


def home(request):

    anime = Anime.objects.all()
    banners = Banner.objects.filter(
        type__icontains="anime"

    )

    return render(request, 'home.html', {
        'animes': anime,
        'banners': banners,

    })




@login_required
def detail(request, id):
    # Fetch anime safely
    anime = get_object_or_404(Anime, id=id)

    # Clean genres
    genres = [g.strip() for g in anime.genres.split(",") if g.strip()]

    # Step 1: Match ALL genres (AND logic)
    related_all = Anime.objects.exclude(id=anime.id)
    for genre in genres:
        related_all = related_all.filter(genres__icontains=genre)

    related = list(related_all.distinct()[:3])

    # Step 2: If less than 3, fallback to ANY (OR logic)
    if len(related) < 3 and genres:
        extra_needed = 3 - len(related)

        # Build a safe OR filter using Q objects
        q_filter = Q()
        for genre in genres:
            q_filter |= Q(genres__icontains=genre)

        related_any = (
            Anime.objects.filter(q_filter)
            .exclude(id=anime.id)
            .exclude(id__in=[a.id for a in related])
            .distinct()[:extra_needed]
        )

        related += list(related_any)

    return render(
        request,
        "videostreaming.html",
        {"anime": anime, "related": related}
    )
@login_required

def search(request):
    query = request.GET.get("q")  # one param only
    search_type = request.GET.get("type", "manga")  # default to manga
    results = []
    paged_results = []

    if query:
        keywords = query.split()
        q_objects = Q()
        for word in keywords:
            q_objects |= Q(title__icontains=word) | Q(genres__icontains=word)

        if search_type == "anime":
            results = Anime.objects.filter(q_objects).distinct()
        else:
            results = Manga.objects.filter(q_objects).distinct()

        paginator = Paginator(results, 30)
        page = request.GET.get("page")
        paged_results = paginator.get_page(page)

    return render(request, "search.html", {
        "results": paged_results,
        "query": query,
        "type": search_type
    })


@login_required
def view(request):
    query = request.GET.get('q')
    if query == "recent":
        result = Anime.objects.filter(status__icontains="Currently Airing")
    else:
        result = Anime.objects.filter(genres__icontains=query)
    paginator = Paginator(result, 50)
    page = request.GET.get('page')
    page_obj = paginator.get_page(page)
    return render(request,'views.html', {'results': page_obj,"query":query})

@login_required
def save(request):
    anime_id = request.GET.get('anime_id')

    if anime_id:
        anime_id = int(anime_id)
        try:
            anime = Anime.objects.get(id=anime_id)
        except Anime.DoesNotExist:
            messages.error(request, "Anime not found.")
            return redirect("WatchListView")

        # Check if this anime is already saved by this user
        if WatchList.objects.filter(user=request.user, anime_id=anime.id).exists():
            messages.warning(request, "Already saved to your watchlist.")
        else:
            WatchList.objects.create(
                user=request.user,
                title=anime.title,
                anime_id=anime.id,
                score=anime.score,
                status=anime.status,
                episodes=anime.episodes,
                image_url=anime.image_url
            )
            messages.success(request, "Anime added to your watchlist.")

    # Show only the current user's watchlist
    watchlist = WatchList.objects.filter(user=request.user)
    paginator = Paginator(watchlist, 10)
    page = request.GET.get('page')
    page_obj = paginator.get_page(page)

    return render(request, "saved.html", {'results': page_obj})



























import requests
from django.shortcuts import render
from django.http import HttpResponse
from .models import Manga

def fetch_mangas(request):
    MANGADEX_API = "https://api.mangadex.org/manga"

    params = {
        "limit": 100,  # Top 20
        "contentRating[]": ["pornographic"],  # 18+ only
        "order[followedCount]": "desc",  # Popularity
    }

    response = requests.get(MANGADEX_API, params=params)
    if response.status_code != 200:
        return render(request, 'error.html', {'error': 'Failed to fetch hentai manga data'})

    mangas_data = response.json().get("data", [])

    saved_count = 0
    for item in mangas_data:
        manga_id = item.get("id")



        attributes = item.get("attributes", {})
        title_dict = attributes.get("title", {})
        title = title_dict.get("en") or list(title_dict.values())[0]
        image = attributes.get("image", {})
        description = attributes.get("description", {}).get("en", "")
        status = attributes.get("status", "")

        # Check if manga has at least 1 chapter
        chapters_resp = requests.get(f"https://api.mangadex.org/chapter", params={
            "manga": manga_id,
            "limit": 1
        })
        chapters_data = chapters_resp.json().get("data", [])
        if not chapters_data:
            print(f"No chapters: {title}")
            continue

        # Genres
        tags = attributes.get("tags", [])
        genres = [tag["attributes"]["name"].get("en", "") for tag in tags]

        # Save
        Manga.objects.create(
            manga_id=manga_id,
            title=title,
            description=description,
            image_url=image,
            status=status,
            genres=", ".join(genres)
        )
        print(f"Saved: {title}")
        saved_count += 1

    return HttpResponse(f"✅ Finished. Total saved: {saved_count}")

