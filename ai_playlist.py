import random

def generate_playlist(mood, songs, playlist_size=5):

    mood = mood.lower()

    if len(songs) == 0:
        return []

    playlist_size = min(
        playlist_size,
        len(songs)
    )

    if mood == "workout":

        return random.sample(
            songs,
            playlist_size
        )

    elif mood == "study":

        sorted_songs = sorted(
            songs,
            key=lambda x:
            x["duration"]
            if x["duration"] != "Unknown"
            else 0
        )

        return sorted_songs[:playlist_size]

    elif mood == "relax":

        sorted_songs = sorted(
            songs,
            key=lambda x:
            x["duration"]
            if x["duration"] != "Unknown"
            else 0,
            reverse=True
        )

        return sorted_songs[:playlist_size]

    return random.sample(
        songs,
        playlist_size
    )