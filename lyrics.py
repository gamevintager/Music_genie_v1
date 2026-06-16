import requests


def get_lyrics(title, artist=""):
    
    try:

        params = {
            "track_name": title,
            "artist_name": artist
        }

        response = requests.get(
            "https://lrclib.net/api/search",
            params=params,
            timeout=10
        )

        print("STATUS:", response.status_code)

        if response.status_code == 200:

            results = response.json()

            print("RESULTS:", len(results))

            if results:

                song = results[0]

                print(song)

                if song.get("plainLyrics"):
                    return song["plainLyrics"]

        return "Lyrics not found."

    except Exception as e:

        print("ERROR:", e)

        return "Unable to fetch lyrics."