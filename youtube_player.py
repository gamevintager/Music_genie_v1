from yt_dlp import YoutubeDL


def search_youtube(query):

    ydl_opts = {
        "quiet": True,
        "default_search": "ytsearch1"
    }

    with YoutubeDL(ydl_opts) as ydl:

        info = ydl.extract_info(
            query,
            download=False
        )

        entry = info["entries"][0]

        return {
            "title": entry["title"],
            "url": entry["webpage_url"],
            "duration": entry.get(
                "duration",
                "Unknown"
            ),
            "thumbnail": entry.get(
                "thumbnail"
            )
        }


def get_audio_stream(query):

    ydl_opts = {
        "quiet": True,
        "format": "bestaudio",
        "default_search": "ytsearch1"
    }

    with YoutubeDL(ydl_opts) as ydl:

        info = ydl.extract_info(
            query,
            download=False
        )

        entry = info["entries"][0]

        def clean_title(title):

            remove_words = [
                "(Official Audio)",
                "(Official Video)",
                "[Official Audio]",
                "[Official Video]",
                "(Lyrics)",
                "[Lyrics]",
                "(Visualizer)",
                "[Visualizer]",
                "Official Audio",
                "Official Video",
                "Lyrical Video",
                "HD Video"
            ]

            for word in remove_words:
                title = title.replace(word, "")

            title = title.split("|")[0].strip()

            return title

        title = clean_title(entry["title"])

        return {
            "title": title,
            "stream_url": entry["url"],
            "thumbnail": entry.get(
                "thumbnail"
            ),
            "duration": entry.get(
                "duration",
                "Unknown"
            )
        }