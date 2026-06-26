
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
from bson.objectid import ObjectId
from .db import tracks_collection, votes_collection
from django.contrib.auth import logout as django_logout

def home(request):
    return render(request, 'chart/home.html')

def tracks_api(request):
    page = int(request.GET.get('page', 1))
    limit = 5
    skip = (page - 1) * limit
    
    tracks_cursor = tracks_collection.find().sort("rating", -1).skip(skip).limit(limit)
    
    tracks_list = []
    for track in tracks_cursor:
        tracks_list.append({
            "id": str(track["_id"]),
            "artist": track.get("artist"),
            "title": track.get("title"),
            "genre": track.get("genre"),
            "year": track.get("year"),
            "rating": track.get("rating", 0.0),
            "votes_count": track.get("votes_count", 0),
            "avatar": track.get("avatar", "")
        })
    return JsonResponse({"tracks": tracks_list})

def track_detail(request, track_id):
    track = tracks_collection.find_one({"_id": ObjectId(track_id)})
    if not track:
        return redirect('home')
    
    track['id'] = str(track['_id'])
    
    already_voted = False
    if request.user.is_authenticated:
        vote = votes_collection.find_one({
            "user_id": request.user.id,
            "track_id": track_id
        })
        if vote:
            already_voted = True

    return render(request, 'chart/track_detail.html', {'track': track, 'already_voted': already_voted})

@login_required
def add_track(request):
    if request.method == "POST":
        artist = request.POST.get('artist')
        title = request.POST.get('title')
        genre = request.POST.get('genre')
        year = request.POST.get('year')
        artist_info = request.POST.get('artist_info')
        lyrics = request.POST.get('lyrics')
        
        avatar_url = ""
        if request.FILES.get('avatar'):
            avatar_file = request.FILES['avatar']
            fs = FileSystemStorage()
            filename = fs.save(avatar_file.name, avatar_file)
            avatar_url = fs.url(filename)

        new_track = {
            "artist": artist,
            "title": title,
            "genre": genre,
            "year": int(year),
            "artist_info": artist_info,
            "lyrics": lyrics,
            "avatar": avatar_url,
            "rating": 0.0,
            "votes_count": 0,
            "total_score": 0
        }
        tracks_collection.insert_one(new_track)
        return redirect('home')
        
    return render(request, 'chart/add_track.html')

@login_required
def vote(request, track_id):
    if request.method == "POST":
        score = int(request.POST.get('score', 0))
        if 1 <= score <= 10:
            user_id = request.user.id
            
            existing_vote = votes_collection.find_one({"user_id": user_id, "track_id": track_id})
            if not existing_vote:
                votes_collection.insert_one({"user_id": user_id, "track_id": track_id, "score": score})

                track = tracks_collection.find_one({"_id": ObjectId(track_id)})
                new_votes_count = track.get("votes_count", 0) + 1
                new_total_score = track.get("total_score", 0) + score
                new_rating = new_total_score / new_votes_count
                
                tracks_collection.update_one(
                    {"_id": ObjectId(track_id)},
                    {"$set": {
                        "votes_count": new_votes_count,
                        "total_score": new_total_score,
                        "rating": new_rating
                    }}
                )
    return redirect('track_detail', track_id=track_id)

def logout_view(request):
    django_logout(request)
    return redirect('home')

