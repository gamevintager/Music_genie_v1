import os

def create_playlist(name, songs, music_folder):

    playlist_folder = os.path.join(
        music_folder,
        "MusicGenie",
        "Playlists"
    )

    os.makedirs(
        playlist_folder,
        exist_ok=True
    )

    filename = os.path.join(
        playlist_folder,
        f"{name}.m3u"
    )

    with open(
        filename,
        "w",
        encoding="utf-8"
    ) as f:

        f.write("#EXTM3U\n")

        for song in songs:
            f.write(song["path"] + "\n")

    return filename