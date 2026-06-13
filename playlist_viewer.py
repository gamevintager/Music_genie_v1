import os

def get_playlists(music_folder):

    playlist_folder = os.path.join(
        music_folder,
        "MusicGenie",
        "Playlists"
    )

    if not os.path.exists(playlist_folder):
        return []

    playlists = []

    for file in os.listdir(playlist_folder):

        if file.endswith(".m3u"):

            playlists.append(file)

    return playlists