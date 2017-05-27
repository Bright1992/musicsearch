from .models import *
import re, os


def eval_list(string):  #只能处理字符串列表，处理'boy'z'这种情况
    ret=[]
    cur=''
    state=0
    idx=-1
    for c in string:
        idx+=1
        if state==0:    #在引号外
            if c!="'":
                continue
            state=1
        elif state==1:  #在引号内
            if c!="'":
                cur+=c
            else:
                idx2=idx+1
                while idx2<len(string) and string[idx2]==' ':
                    idx2+=1
                if idx2==len(string) or string[idx2]==']' or string[idx2]==',':
                    ret.append(cur)
                    cur=''
                    state=0
                else:
                    cur+=c
    return ret


def import_artists(path):
    # id_ptn=re.compile(r"'id'\s*:\s*(\d+)")
    # name_ptn=re.compile(r"'name'\s*:\s*'(.*?)'")
    # alias_ptn=re.compile(r"'alias'\s*:\s*\[(.*?)\]")
    path = os.path.join(path, "meta_data", "artists")
    if os.path.exists(path) and os.path.isdir(path):
        os.chdir(path)
    else:
        raise NotADirectoryError

    for a in os.listdir(path):
        if os.path.isfile(a):
            print("Inserting artist id {}".format(a))
            if Artist.objects.filter(artist_id=int(a)).count() > 0:
                print("Artist id {} has been added to the database".format(a))
                continue
            with open(a, 'r') as f:
                s = eval(f.read())
                # id_mch=id_ptn.findall(s)
                # name_mch=name_ptn.findall(s)
                # alias_mch=alias_ptn.findall(s)
                try:
                    name = s['name']
                except Exception as e:
                    print("Warning: artist id {} has no name!".format(a))
                try:
                    alias = s['alias']
                except Exception as e:
                    alias = ''
                if len(alias) > 0:
                    alias = alias[0].strip(' ').strip("'")
                else:
                    alias = ''
                Artist(artist_id=int(a), name=name, alias=alias).save()
        else:
            raise IsADirectoryError


def import_albums(path):
    path = os.path.join(path, "meta_data", "albums")
    if os.path.exists(path) and os.path.isdir(path):
        os.chdir(path)
    else:
        raise NotADirectoryError
    for a in os.listdir(path):
        if os.path.isfile(a):
            print("Inserting album id {}".format(a))
            if Album.objects.filter(album_id=int(a)).count() > 0:
                print("Album id {} has been added to the database".format(a))
                continue
            with open(a, 'r') as f:
                s = eval(f.read())
                try:
                    name = s['name']
                except:
                    print("Warning: album id {} has no name!".format(a))
                try:
                    pic_url = s['picUrl']
                except:
                    print("Warning: album id {} has no pic!".format(a))
                try:
                    publist_time = s['publishTime']
                except:
                    print("Warning: album id {} has no publish time!".format(a))
                Album(album_id=int(a), name=name, pic_url=pic_url, publish_time=publist_time).save()
        else:
            raise IsADirectoryError


def import_songs(path):
    path = os.path.join(path, "meta_data", "songs")
    if os.path.exists(path) and os.path.isdir(path):
        os.chdir(path)
    else:
        raise NotADirectoryError
    for a in os.listdir(path):
        if os.path.isfile(a):
            print("Inserting song id {}".format(a))
            with open(a, 'r') as f:
                name = None
                artist_id = None
                artist_name = None
                album_id = None
                popularity = None
                for s in f.readlines():
                    if s.startswith("song_name:"):
                        name = s.strip('\n')[s.find(':') + 2:]
                    if s.startswith("artist_id:"):
                        artist_id = eval(s.strip('\n')[s.find(':') + 2:])
                    if s.startswith("album_id:"):
                        album_id = int(s.strip('\n')[s.find(':') + 2:])
                    if s.startswith("popularity:"):
                        popularity = float(s.strip('\n')[s.find(':') + 2:])
                    if s.startswith("artist_name:"):
                        artist_name = eval_list(s.strip('\n')[s.find(':') + 2:])
                if name is None:
                    print("Warning: song id {} has no name!".format(a))
                    name = ''
                if artist_id is None:
                    print("Warning: song id {} has no artist!".format(a))
                if album_id is None:
                    print("Warning: song id {} has no album!".format(a))
                if popularity is None:
                    print("Warning: song id {} has no popularity!".format(a))
                    popularity = 1
                s_inst = Song(song_id=int(a), name=name, popularity=popularity)
                s_inst.save()
                if artist_id is not None:
                    idx = 0
                    for aid in artist_id:
                        art = Artist.objects.filter(artist_id=aid)
                        if art.count() == 0:
                            print("Warning: artist id {} does not exist, creating it...".format(aid))
                            art = Artist(artist_id=int(aid), name=artist_name[idx])
                            art.save()
                            s_inst.artists.add(art)
                            art_d = {'id': aid, 'name': artist_name[idx]}
                            with open("../artists/{}".format(aid),'w') as art_f:
                                art_f.write(art_d.__str__())
                            idx += 1
                            continue
                        idx += 1
                        s_inst.artists.add(art.get())
                if album_id is not None:
                    alb = Album.objects.filter(album_id=album_id)
                    if alb.count() == 0:
                        print("Warning: artist id {} does not exist!".format(album_id))
                        continue
                    s_inst.album = alb.get()
                s_inst.save()


def do_import_data(path):
    import_artists(path)
    import_albums(path)
    import_songs(path)
