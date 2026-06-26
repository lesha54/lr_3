from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('api/tracks/', views.tracks_api, name='tracks_api'),
    path('track/<str:track_id>/', views.track_detail, name='track_detail'),
    path('track/<str:track_id>/vote/', views.vote, name='vote'),
    path('add/', views.add_track, name='add_track'),
    path('logout/', views.logout_view, name='logout'),
]
