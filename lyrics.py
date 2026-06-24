import requests
import time


def get_lyrics(title, artist=""):

    print("=" * 50)
    print("LYRICS REQUEST")
    print("TITLE:", title)
    print("ARTIST:", artist)

    params = {
        "track_name": title,
        "artist_name": artist
    }

    for attempt in range(3):

        try:

            response = requests.get(
                "https://lrclib.net/api/search",
                params=params,
                timeout=20
            )

            print("STATUS:", response.status_code)
            print("URL:", response.url)

            if response.status_code == 200:

                results = response.json()

                print("RESULTS:", len(results))

                if results:

                    song = results[0]

                    print(
                        "FOUND:",
                        song.get("trackName"),
                        "-",
                        song.get("artistName")
                    )

                    if song.get("plainLyrics"):

                        return song["plainLyrics"]

            return "Lyrics not found."

        except Exception as e:

            print(
                f"ATTEMPT {attempt + 1} FAILED:",
                e
            )

            if attempt < 2:

                print("RETRYING IN 2 SECONDS...")
                time.sleep(2)

            else:

                return "Unable to fetch lyrics."