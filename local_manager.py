from mutagen import File
import os

def scan_music(folder):

    songs = []

    for root, dirs, files in os.walk(folder):

        for file in files:

            if file.lower().endswith(".mp3"):

                path = os.path.join(root, file)

                try:

                    audio = File(path)

                    duration = round(
                        audio.info.length
                    )

                    songs.append({
                        "title": file,
                        "duration": duration,
                        "path": path
                    })

                except:

                    songs.append({
                        "title": file,
                        "duration": "Unknown",
                        "path": path
                    })

    return songs