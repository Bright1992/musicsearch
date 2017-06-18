from django.shortcuts import render
from .models import *
from .query import query, update_info
from django.http import HttpResponse, HttpResponseRedirect
import copy, os

# Create your views here.

alpha = 2  # parameter deciding weight of clicked_num and listened_num
beta = 2


def index(request):
    if request.method == "GET":
        search_text = request.GET.get("search_text")
        search_type = request.GET.get("search_type")
        if search_text is not None and search_text != '':
            return HttpResponseRedirect("/results.html?search_type={}&search_text={}".format(search_type, search_text))

        if search_type == "Lyric":
            opt1 = ''
            opt2 = 'checked="true"'
        else:
            opt1 = 'checked="true"'
            opt2 = ""
        ctx = {"option1": opt1,
               "option2": opt2}

        return HttpResponse(render(request, "index.html", context=ctx))


def show_results(request):
    search_type = request.GET.get("search_type")
    search_text = request.GET.get("search_text")

    results = None

    # conduct querying.....
    if search_type == "Lyric":
        opt1 = ''
        opt2 = 'checked="true"'
        if search_text is not None and search_text != '':
            results = query(search_text, "Lyric")
    else:
        opt1 = 'checked="true"'
        opt2 = ""
        if search_text is not None and search_text != '':
            results = query(search_text, "Music")

    ctx = {"option1": opt1,
           "option2": opt2}
    ctx["songs"] = []
    ctx["search_text"] = ""
    if results is not None:
        hits = results['hits']

        for i in range(hits):
            try:
                ctx["songs"].append(copy.deepcopy(results["songs"][i]))  # need deepcopy!
                ctx["songs"][-1]['num'] = i + 1

                song_obj = Song.objects.get(song_id=ctx["songs"][-1]['id'])

                ctx["songs"][-1]["artists"] = [{"name": artist_name, } for artist_name in
                                               results["songs"][i]["artists"]]
                for a in ctx["songs"][-1]["artists"]:
                    try:  # artists with same name is not considered..
                        a["id"] = song_obj.artists.filter(
                            name=a["name"].replace("<font color=\"#FF0000\">", "").replace("</font>",
                                                                                           "")).first().artist_id
                        # print(a)
                        if a["id"] == 0:  # due to bugs in models...
                            ctx["songs"][-1]["artists"].remove(a)
                    except Exception as e:
                        print(e)

                ctx["songs"][-1]["last_artist"] = {"name": results["songs"][i]["artists"][-1],
                                                   "id": song_obj.artists.last().artist_id}
                ctx["songs"][-1]["artists"] = ctx["songs"][-1]["artists"][:-1]

                ctx["songs"][-1]["album"] = {"id": song_obj.album.album_id,
                                             "name": song_obj.album.name}
            except Exception as e:
                print(e)
                print(ctx["songs"][-1]["artists"])
                # HttpResponseRedirect("error.html")

        ctx['search_text'] = search_text
    else:
        artist_id = request.GET.get('artist_id')
        if artist_id is not None:
            # try:
            artist_id = int(artist_id)
            ctx["songs"] = []
            i = 0
            songs = []
            for s in Artist.objects.get(artist_id=artist_id).song_set.all():
                i = i + 1
                songs.append({
                    "id": s.song_id,
                    # "num": i,
                    "name": s.name,
                    "artists": [{
                        "id": a.artist_id,
                        "name": a.name
                    } for a in s.artists.all()],
                    "last_artist": {
                        "id": s.artists.last().artist_id,
                        "name": s.artists.last().name
                    },
                    "album": {
                        "id": s.album.album_id,
                        "name": s.album.name
                    },
                    "publish_time": s.album.publish_time,
                    "clicked_num": s.clicked_num,
                    "listened_num": s.listened_num,
                    "popularity": s.popularity,
                })
                for a in songs[-1]["artists"]:
                    if a["id"] == 0:
                        songs[-1]["artists"].remove(a)
                songs[-1]["artists"] = songs[-1]["artists"][:-1]
            songs.sort(key=lambda song: song["popularity"] + beta * (
                song["clicked_num"] + alpha * song["listened_num"]), reverse=True)
            i = 0
            for s in songs:
                i += 1
                s["num"] = i
            ctx["songs"] = songs

            # except Exception as e:
            #     print(e)
        else:
            album_id = request.GET.get('album_id')
            if album_id is not None:
                try:
                    album_id = int(album_id)
                    ctx["songs"] = []
                    i = 0
                    songs = []
                    for s in Song.objects.filter(album_id=album_id).all():
                        i = i + 1
                        songs.append({
                            "id": s.song_id,
                            # "num": i,
                            "name": s.name,
                            "artists": [{
                                "id": a.artist_id,
                                "name": a.name
                            } for a in s.artists.all()],
                            "last_artist": {
                                "id": s.artists.last().artist_id,
                                "name": s.artists.last().name
                            },
                            "album": {
                                "id": s.album.album_id,
                                "name": s.album.name
                            },
                            "publish_time": Album.objects.get(album_id=album_id).publish_time,
                            "clicked_num": s.clicked_num,
                            "listened_num": s.listened_num,
                            "popularity": s.popularity,
                        })
                        for a in songs[-1]["artists"]:
                            if a["id"] == 0:
                                songs[-1]["artists"].remove(a)
                        songs[-1]["artists"] = songs[-1]["artists"][:-1]
                    songs.sort(key=lambda song: song["popularity"] + beta * (
                        song["clicked_num"] + alpha * song["listened_num"]), reverse=True)
                    ctx["songs"] = songs
                    i = 0
                    for s in songs:
                        i += 1
                        s["num"] = i
                except Exception as e:
                    print(e)
    return HttpResponse(render(request, "results.html", context=ctx))


def show_details(request):
    ctx = {}
    id = request.GET.get("id")
    try:
        id = int(id)
    except Exception as e:
        print(e)
        return HttpResponseRedirect("error.html")

    try:
        song_obj = Song.objects.get(song_id=id)
        song_obj.clicked_num += 1
        song_obj.save()
        update_info(id, song_obj.clicked_num + alpha * song_obj.listened_num)
        pic_url = song_obj.album.pic_url
        ctx['id'] = id
        ctx['pic_url'] = pic_url
        ctx['name'] = song_obj.name
        ctx['artists'] = [a.name for a in song_obj.artists.all()]
        ctx['album'] = song_obj.album.name
        ctx['click_num'] = song_obj.clicked_num
        ctx['download_num'] = song_obj.listened_num
        ctx['popularity'] = song_obj.popularity
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        print(BASE_DIR)
        with open(os.path.join(BASE_DIR,"..","data","lyrics","{}.lrc".format(id)),'r') as f:
            ctx['lrc'] = f.readlines()
    except Exception as e:
        print(e)
        return HttpResponseRedirect("error.html")

    return HttpResponse(render(request, "single.html", context=ctx))


def download_mp3(request):
    id = request.GET.get("id")
    try:
        id = int(id)
        song_obj = Song.objects.get(song_id=id)
        song_obj.listened_num += 1
        song_obj.save()
        update_info(id, song_obj.clicked_num + alpha * song_obj.listened_num)
        return HttpResponseRedirect("/static/{}.mp3".format(id))
    except Exception as e:
        print(e)
        return HttpResponseRedirect("error.html")


def error_proc(request):
    return HttpResponse(render(request, "error.html"))
