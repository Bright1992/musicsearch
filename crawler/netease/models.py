# -*- coding: utf-8 -*-

"""
netease-dl.models
~~~~~~~~~~~~~~~~~

ORM for database in the future.
"""


class Song(object):
    def __init__(self, song_id, song_name, **kwargs):
        self.song_id = song_id
        self.song_name = song_name
        self.artist_id = None if not 'artist_id' in kwargs.keys() else kwargs['artist_id']
        self.artist_name = None if not 'artist_name' in kwargs.keys() else kwargs['artist_name']
        self.album_id = None if not 'album_id' in kwargs.keys() else kwargs['album_id']
        self.album_name = None if not 'album_name' in kwargs.keys() else kwargs['album_name']
        self.album = None if not 'album' in kwargs.keys() else kwargs['album']

        self.year = None if not 'year' in kwargs.keys() else kwargs['year']
        self.popularity = None if not 'popularity' in kwargs.keys() else kwargs['popularity']

        self.hot_comments = [] if not 'hot_comments' in kwargs.keys() else kwargs['hot_comments']
        self.comment_count = 0 if not 'comment_count' in kwargs.keys() else kwargs['comment_count']
        self.song_lyric = None if not 'song_lyric' in kwargs.keys() else kwargs['song_lyric']
        self.song_url = None if not 'song_url' in kwargs.keys() else kwargs['song_url']
        self.duration = 0 if not 'duration' in kwargs.keys() else kwargs['duration']
        self.artists = None


class Comment(object):
    def __init__(self, comment_id, content, like_count, created_time,
                 user_id=None):
        self.comment_id = comment_id
        self.content = content
        self.like_count = like_count
        self.created_time = created_time
        self.user_id = user_id


class Album(object):
    def __init__(self, album_id, album_name, artist_id=None,
                 songs=None, hot_comments=None):
        self.album_id = album_id
        self.album_name = album_name
        self.artist_id = artist_id
        self.songs = [] if songs is None else songs
        self.hot_comments = [] if hot_comments is None else hot_comments

    def add_song(self, song):
        self.songs.append(song)


class Artist(object):
    def __init__(self, artist_id, artist_name, hot_songs=None):
        self.artist_id = artist_id
        self.artist_name = artist_name
        self.hot_songs = [] if hot_songs is None else hot_songs

    def add_song(self, song):
        self.hot_songs.append(song)


class Playlist(object):
    def __init__(self, playlist_id, playlist_name, user_id=None,
                 songs=None, hot_comments=None):
        self.playlist_id = playlist_id
        self.playlist_name = playlist_name
        self.user_id = user_id
        self.songs = [] if songs is None else songs
        self.hot_comments = [] if hot_comments is None else hot_comments

    def add_song(self, song):
        self.songs.append(song)


class User(object):
    def __init__(self, user_id, user_name, songs=None, hot_comments=None):
        self.user_id = user_id
        self.user_name = user_name
        self.songs = [] if songs is None else songs
        self.hot_comments = [] if hot_comments is None else hot_comments

    def add_song(self, song):
        self.songs.append(song)
