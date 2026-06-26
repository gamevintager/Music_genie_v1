import random


def generate_playlist(mood, songs, playlist_size=5):

    mood = mood.lower()

    if len(songs) == 0:
        return []

    playlist_size = min(
        playlist_size,
        len(songs)
    )

    # Songs with known duration
    known = [
        song for song in songs
        if song["duration"] != "Unknown"
    ]

    if len(known) == 0:
        return random.sample(
            songs,
            playlist_size
        )

    # --------------------------
    # Workout
    # --------------------------

    if mood == "workout":

        return random.sample(
            songs,
            playlist_size
        )

    # --------------------------
    # Study
    # --------------------------

    elif mood == "study":

        sorted_songs = sorted(
            known,
            key=lambda x: x["duration"]
        )

        candidates = sorted_songs[
            :max(
                playlist_size * 3,
                len(sorted_songs) // 2
            )
        ]

        return random.sample(
            candidates,
            min(
                playlist_size,
                len(candidates)
            )
        )

    # --------------------------
    # Relax
    # --------------------------

    elif mood == "relax":

        sorted_songs = sorted(
            known,
            key=lambda x: x["duration"],
            reverse=True
        )

        candidates = sorted_songs[
            :max(
                playlist_size * 3,
                len(sorted_songs) // 2
            )
        ]

        return random.sample(
            candidates,
            min(
                playlist_size,
                len(candidates)
            )
        )

    # --------------------------
    # Default
    # --------------------------

    return random.sample(
        songs,
        playlist_size
    )