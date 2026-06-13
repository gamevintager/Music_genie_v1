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
            "duration": entry.get("duration", "Unknown")
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

        return {
            "title": entry["title"],
            "stream_url": entry["url"]
        }