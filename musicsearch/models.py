from django.db import models


# Create your models here.

class Artist(models.Model):
    artist_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=150)
    alias = models.CharField(max_length=150, default='')


class Album(models.Model):
    album_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=150)
    pic_url = models.CharField(max_length=1024)
    publish_time = models.IntegerField(default=1)


class Song(models.Model):
    song_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    artists = models.ManyToManyField(Artist, blank=True, null=True)
    album = models.ForeignKey(Album, on_delete=models.SET_NULL, null=True, blank=True)
    popularity = models.FloatField()
    clicked_num = models.IntegerField(default=0)
    listened_num = models.IntegerField(default=0)
