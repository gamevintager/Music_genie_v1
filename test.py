from youtube_player import get_audio_stream
from player_controller import play_song

song = get_audio_stream(
    "husn anuv jain"
)

print(song["title"])

play_song(
    song["stream_url"]
)

input("Press Enter...")
