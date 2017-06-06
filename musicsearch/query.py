import socket
import threading


def parse_query(search_text):
    search_text.replace(",", " ")
    search_text.replace(":", " ")
    while search_text.find("  ") >= 0:
        search_text = search_text.replace("  ", " ")
    # keywords = search_text.split(" ")
    # qlist = ["all:{}".format(k) for k in keywords]
    return "all:{}".format(search_text)


# def res_intersector(results):
#     if results is not None and len(results) > 0:
#         return results[0]
#
#     else:
#         return None


def res_formatter(results):
    formatted_res = {}
    if results is None:
        formatted_res['hits'] = 0
        return formatted_res
    res_list = results.split("\r\n\r\n")
    formatted_res['hits'] = int(res_list[0][6:])  # "hits: "
    songs = []
    try:
        for res in res_list[1:]:
            song = {}
            song_info = res.split("\r\n")
            song["id"] = int(song_info[0][4:])  # "id: "
            song["name"] = song_info[1][6:]  # "song: "
            artists = song_info[2][8:].split(",")  # "singer: "
            for i in range(len(artists)):
                artists[i] = artists[i].strip(" ")
                artists[i] = artists[i].strip("'")
            song["artists"] = artists
            if len(song_info)>3:
                song["lyric"] = song_info[3][5:]  # "lrc: "
            else:
                song["lyric"] = ""
            songs.append(song)
    except Exception as e:
        print(e)
        print(song_info[0])
    formatted_res['songs'] = songs
    return formatted_res


PORT = 8080


def query(search_text, search_type):
    if search_type == "Music":
        q = parse_query(search_text)
    elif search_type == "Title":
        q = "song:{}".format(search_text)
    elif search_type == "Artist":
        q = "singer:{}".format(search_type)
    elif search_type == "Lyric":
        q = "lrc:{}".format(search_text)
    else:
        q = parse_query(search_text)

    print(q)
    conn = socket.socket()
    results = []
    try:
        print("connecting to 8080...")
        conn.connect(("127.0.0.1", PORT))
        print("8080 connected")

        conn.send((q + "\r\n\r\n").encode('utf-8'))
        print("sent {}".format(q))
        results = conn.recv(202400).decode('utf-8')
        # print(results)
    except Exception as e:
        print(e)
        results = None
    finally:
        conn.close()

    return res_formatter(results)


def update_info(id, value):
    conn = socket.socket()
    q = "update: {} {}".format(id, value)
    try:
        print("connecting to 8080...")
        conn.connect(("127.0.0.1", PORT))
        print("8080 connected")

        conn.send((q + "\r\n\r\n").encode('utf-8'))
        print("sent {}".format(q))
        results = conn.recv(202400).decode('utf-8')
        # print(results)
    except Exception as e:
        print(e)
        print("update clicked num for {} failed!".format(id))
    finally:
        conn.close()
