from django.contrib import admin
from .models import *
# Register your models here.

class SongAdmin(admin.ModelAdmin):
    list_display =('song_id','name','album','popularity','clicked_num')

class AlbumAdmin(admin.ModelAdmin):
    list_display = ('album_id','name','publish_time')

class ArtistAdmin(admin.ModelAdmin):
    list_display = ('artist_id','name','alias')

admin.site.register(Artist,ArtistAdmin)
admin.site.register(Album,AlbumAdmin)
admin.site.register(Song,SongAdmin)