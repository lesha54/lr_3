import pymongo
from django.conf import settings


client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["music_chart_db"]


tracks_collection = db["tracks"]
votes_collection = db["votes"]
