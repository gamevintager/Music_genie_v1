import streamlit as st
import pandas as pd
import os
import random
import re
import html
import json
import time
from player_controller import (
    play_song,
    pause_song,
    stop_song,
    is_playing,
    song_finished,
    has_song_ended,
    get_current_time,
    get_duration
)
from lyrics import get_lyrics
from youtube_player import get_audio_stream
from mutagen.id3 import ID3
from mutagen import File
from streamlit_autorefresh import st_autorefresh
from PIL import Image
from io import BytesIO
from ai_assistant import (
    ask_music_genie,
    get_intent
)
from playlist_viewer import get_playlists
from local_manager import scan_music
from playlist_manager import create_playlist
from ai_playlist import generate_playlist


# ----------------------------------
# Page Configuration
# ----------------------------------

st.set_page_config(
    page_title="Music Genie",
    page_icon="🎵",
    layout="wide"
)

st.markdown("""
<style>

/* Main App */
.stApp{
    background:
    linear-gradient(
        135deg,
        #090012,
        #12001f,
        #1d0930
    );
}

/* Headers */
h1,h2,h3{
    color:white;
}

/* Buttons */
.stButton button{
    background:#241033;
    color:white;
    border:1px solid #ff4fd8;
    border-radius:18px;
    height:55px;
}

/* Hover */
.stButton button:hover{
    border-color:#ff7ce8;
    box-shadow:
    0 0 15px #ff4fd8;
}

/* Sidebar */
[data-testid="stSidebar"]{
    background:
    linear-gradient(
        180deg,
        #12001f,
        #1a0828
    );
}

</style>
""", unsafe_allow_html=True)



responses = [
    "Let's take a look at your library.",
    "Analyzing your collection...",
    "Music Genie is checking your songs..."
]

st.info(
    random.choice(responses)
)

@st.cache_data
def build_df(songs):
    return pd.DataFrame(songs)

# ----------------------------------
# Playlist loader
# ----------------------------------
def load_liked_songs():

    try:

        with open(
            "liked_songs.json",
            "r"
        ) as f:

            return json.load(f)

    except:

        return []

def format_time(seconds):

    minutes = int(seconds // 60)

    seconds = int(seconds % 60)

    return f"{minutes:02}:{seconds:02}"

def save_liked_songs(songs):

    with open(
        "liked_songs.json",
        "w"
    ) as f:

        json.dump(
            songs,
            f,
            indent=4
        )

def load_m3u_playlist(
    music_folder,
    playlist_file
):

    playlist_path = os.path.join(
        music_folder,
        "MusicGenie",
        "Playlists",
        playlist_file
    )

    playlist = []

    if not os.path.exists(
        playlist_path
    ):
        return playlist

    with open(
        playlist_path,
        "r",
        encoding="utf-8"
    ) as f:

        for line in f:

            line = line.strip()

            if (
                line
                and os.path.exists(line)
            ):

                playlist.append(
                    {
                        "title":
                            os.path.basename(line),
                        "path":
                            line,
                        "duration":
                            "Unknown"
                    }
                )

    return playlist


# ----------------------------------
# sync Helper
# ----------------------------------

def sync_current_song(song):

    st.session_state.current_song = song

    playlist = st.session_state.current_playlist

    for i, s in enumerate(playlist):
        if s["title"] == song["title"]:
            st.session_state.current_index = i
            return

def get_cached_lyrics(title, artist=""):

    key = f"{title}|{artist}"

    if key in st.session_state.lyrics_cache:

        print("CACHE HIT:", key)

        return st.session_state.lyrics_cache[key]

    print("FETCHING LYRICS:", key)
    
    print("FETCHING:", title, "|", artist)

    lyrics = get_lyrics(title, artist)

    if lyrics in [
        "Lyrics not found.",
        "Unable to fetch lyrics."
    ]:

        clean_title = (
            title
            .replace("ft.", "")
            .replace("feat.", "")
            .strip()
        )

        lyrics = get_lyrics(
            clean_title,
            artist
        )

    if lyrics not in [
        "Lyrics not found.",
        "Unable to fetch lyrics."
    ]:

        st.session_state.lyrics_cache[key] = lyrics

    return lyrics

def load_song_lyrics(song):

    if song.get("source") == "youtube":

        song_title = song["title"]

        artist = ""
        title = song_title

        if " - " in song_title:

            artist, title = song_title.split(
                " - ",
                1
            )

        return get_cached_lyrics(
            title.strip(),
            artist.strip()
        )

    return get_cached_lyrics(
        song["title"]
    )

# ----------------------------------
# Album Art Helper
# ----------------------------------

def get_album_art(song_path):

    try:

        tags = ID3(song_path)

        for tag in tags.values():

            if tag.FrameID == "APIC":

                return Image.open(
                    BytesIO(tag.data)
                )

    except Exception:
        pass

    return None

# ----------------------------------
# GET SONG METADATA
# ----------------------------------

def get_song_metadata(song_path):

    data = {
        "title": None,
        "artist": None,
        "album": None,
        "cover": None
    }

    try:

        audio = File(song_path)

        if audio:

            if audio.tags:

                if "TIT2" in audio.tags:
                    data["title"] = str(
                        audio.tags["TIT2"]
                    )

                if "TPE1" in audio.tags:
                    data["artist"] = str(
                        audio.tags["TPE1"]
                    )

                if "TALB" in audio.tags:
                    data["album"] = str(
                        audio.tags["TALB"]
                    )

            tags = ID3(song_path)

            for tag in tags.values():

                if tag.FrameID == "APIC":

                    data["cover"] = Image.open(
                        BytesIO(tag.data)
                    )

                    break

    except:
        pass

    return data
# ----------------------------------
# Title
# ----------------------------------

st.title("🎵 Music Genie")


# ----------------------------------
# Session State
# ----------------------------------

if "songs" not in st.session_state:
    st.session_state.songs = []

if "messages" not in st.session_state:
    st.session_state.messages = []

if "song_queue" not in st.session_state:
    st.session_state.song_queue = []

if "shuffle_mode" not in st.session_state:
    st.session_state.shuffle_mode = False

if "is_paused" not in st.session_state:
    st.session_state.is_paused = False

if "saved_playlists" not in st.session_state:
    st.session_state.saved_playlists = {}

if "current_playlist" not in st.session_state:
    st.session_state.current_playlist = []

if "current_index" not in st.session_state:
    st.session_state.current_index = 0

if "current_song" not in st.session_state:
    st.session_state.current_song = None

if "lyrics" not in st.session_state:
    st.session_state.lyrics = ""

if "lyrics_cache" not in st.session_state:
    st.session_state.lyrics_cache = {}

if "liked_songs" not in st.session_state:

    st.session_state.liked_songs = (
        load_liked_songs()
    )

ended = has_song_ended()

if ended:

    print("AUTO NEXT DETECTED")

    st.session_state.button_command = "next song"

    st.rerun()

# ----------------------------------
# Folder Input
# ----------------------------------

folder = st.text_input(
    "Enter music folder path",
    value=r"C:\Users\harsh\Music"
)

# ----------------------------------
# Scan Button
# ----------------------------------

if st.button("Scan Music"):
    st.session_state.songs = scan_music(folder)

# ----------------------------------
# Get Songs
# ----------------------------------

songs = st.session_state.songs

# ----------------------------------
# Display Results
# ----------------------------------

if len(songs) > 0:

    st.success(f"{len(songs)} songs found")

    df = build_df(songs)

    # ------------------------------
    # Statistics
    # ------------------------------

    known = df[df["duration"] != "Unknown"]

    if len(known) > 0:

        durations = known["duration"].astype(int)

        total_songs = len(df)
        total_duration = durations.sum()
        avg_duration = round(durations.mean())

        longest_song = known.loc[
            durations.idxmax()
        ]

        st.subheader("📊 Library Statistics")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "Total Songs",
                total_songs
            )

        with col2:
            st.metric(
                "Total Duration",
                f"{total_duration}s"
            )

        with col3:
            st.metric(
                "Average Length",
                f"{avg_duration}s"
            )

        with col4:
            st.metric(
                "Longest Song",
                longest_song["duration"]
            )

        st.info(
            f"🎧 Longest Song: {longest_song['title']}"
        )

    # ------------------------------
    # Search Songs
    # ------------------------------

    st.subheader("🔍 Search Songs")

    search = st.text_input(
        "Search by song name"
    )

    if search:

        filtered_df = df[
            df["title"].str.contains(
                search,
                case=False,
                na=False
            )
        ]

        st.dataframe(
            filtered_df,
            width="stretch"
        )

    else:

        st.subheader("🎵 Song Library")

        st.dataframe(
            df,
            width="stretch"
        )

    # ------------------------------
    # Playlist Creator
    # ------------------------------

    st.subheader("🎼 Playlist Creator")

    playlist_name = st.text_input(
        "Playlist Name"
    )

    selected_songs = st.multiselect(
        "Select Songs",
        options=df["title"].tolist()
    )

    if st.button("Create Playlist"):

        chosen = []

        for song in songs:

            if song["title"] in selected_songs:
                chosen.append(song)

        if playlist_name and len(chosen) > 0:

            st.success(
                "Playlist created successfully! "
            )

        else:

            st.error(
                "Enter playlist name and select songs."
            )

    # ------------------------------
    # AI Playlist Generator
    # ------------------------------
    st.subheader("🤖 AI Playlist Generator")


    mood = st.selectbox(
        "Choose Mood",
        [
            "Workout",
            "Study",
            "Relax"
        ]
    )

    playlist_size = st.slider(
        "Playlist Size",
        min_value=2,
        max_value=len(songs),
        value=min(5, len(songs))
    )

    if st.button("Generate AI Playlist"):

        generated = generate_playlist(
            mood,
            songs,
            playlist_size
        )

        st.session_state.saved_playlists[
            mood.lower()
        ] = generated

        ai_playlist_name = (
            mood + "_AI_Playlist"
        )

        
        st.success(
            f"AI Playlist Created!"
        )

        st.write(
            "### 🎵 Songs Selected"
        )

        ai_df = pd.DataFrame(generated)

        st.dataframe(
            ai_df,
            width="stretch"
        )

    # ------------------------------
    # CSV Download
    # ------------------------------

    csv = df.to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(
        "📥 Download Library Report",
        csv,
        "music_library.csv",
        "text/csv"
    )

else:

    st.info(
        "Enter a folder path and click 'Scan Music' to begin."
    )

# ----------------------------------
# Music Genie Assistant
# ----------------------------------

st.subheader("🤖 Music Genie Assistant")

# Show old messages

for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.write(message["content"])



# User Input

user_command = st.chat_input(
    "Ask Music Genie..."
)

if "button_command" in st.session_state:

    user_command = (
        st.session_state.button_command
    )

    del st.session_state.button_command

if st.session_state.get("control") == "playpause":

    if st.session_state.is_paused:

        pause_song()   # VLC toggle resume

        st.session_state.is_paused = False

    else:

        pause_song()   # VLC toggle pause

        st.session_state.is_paused = True

    del st.session_state.control

    st.rerun()

    
if user_command:
    
    intent = None

    # Store User Message

    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_command
        }
    )

    with st.chat_message("user"):

        st.write(user_command)

    command = user_command.lower().strip()

    # Fast commands (NO OLLAMA)

    if command in ["previous", "previous song", "back"]:
        pass


    elif command == "pause":
        pause_song()
        st.rerun()

    elif command == "resume":
        pause_song()
        st.session_state.is_paused = False
        st.rerun()

    elif command == "show queue":
        ...
        
    elif command == "show liked songs":
        ...

    # ONLY USE OLLAMA FOR COMPLEX REQUESTS
    else:
        intent = get_intent(user_command)

        intent = intent.strip().upper()

    # --------------------------
    # YES to recommendation
    # --------------------------

    if command in ["yes", "play it", "sure", "okay"]:

        if "pending_song" in st.session_state:

            song = st.session_state.pending_song

            response = (
                f"▶ Playing {song['title']}"
            )

            st.session_state.current_song = song

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": response
                }
            )
            del st.session_state.pending_song

            st.stop()
    
    # No Songs Loaded

    if len(songs) == 0:

        response = (
            "⚠ Please scan your music library first."
        )

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": response
            }
        )


    else:

        chat_df = pd.DataFrame(songs)

    # --------------------------
    # AI Mood Detection
    # --------------------------

        stress_words = [
            "stress",
            "stressed",
            "anxious",
            "overwhelmed",
            "pressure",
            "worried",
            "panic",
            "tension"
        ]

        if (
            intent
            and intent == "MOOD_STRESS"
            and any(
                word in command
                for word in stress_words
            )
        ):
            generated = generate_playlist(
                "Calming music",
                songs,
                10
            )

            st.session_state.saved_playlists["calm_music"] = generated
            

            first_song = generated[0]

            st.session_state.current_playlist = generated
            st.session_state.current_index = 0
            st.session_state.current_song = generated[0]

            play_song(
                generated[0]["path"]
            )

            st.session_state.lyrics = load_song_lyrics(
                first_song
            )

            first_song=generated[0]

            playlist_text = "\n".join(
                [f"- {song['title']}" for song in generated]
            )

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": "Calm music playlist created"
                }
            )

            with st.chat_message("assistant"):

                st.write("😌 You seem stressed. I've prepared a calming playlist.")

                st.write("###Playlist with Calm music Created")

                for song in generated:
                    st.write(f"• {song['title']}")

                st.write(f"▶ Now playing: {first_song['title']}")



                
        # --------------------------
        # Show Songs
        # --------------------------

        elif "show songs" in command:
        
            response = (
                f"🎵 Found {len(chat_df)} songs."
            )

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": response
                }
            )

            st.dataframe(
                chat_df,
                width="stretch"
            )
        
        elif command == "show liked songs":

            liked = st.session_state.liked_songs

            if liked:

                response = "❤️ Liked Songs\n\n"

                for i, song in enumerate(
                    liked,
                    start=1
                ):

                    response += (
                        f"{i}. "
                        f"{song['title']}\n"
                    )

            else:

                response = (
                    "No liked songs yet."
                )

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": response
                }
            )


        elif command == "like this song":
            
            if st.session_state.current_song:

                song = st.session_state.current_song

                exists = False

                for liked in st.session_state.liked_songs:

                    if liked["title"] == song["title"]:

                        exists = True
                        break

                if not exists:

                    liked_song = song.copy()

                    st.session_state.liked_songs.append(
                        liked_song
                    )

                    save_liked_songs(
                        st.session_state.liked_songs
                    )

                    response = (
                        f"❤️ Added "
                        f"{song['title']} "
                        f"to liked songs"
                    )

                else:

                    response = (
                        "❤️ Song already liked"
                    )

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": response
                    }
                )
            
            else:

                response = (
                    "❌ No song playing"
                )
        # --------------------------
        # Statistics
        # --------------------------

        elif (
            "statistics" in command
            or "stats" in command
        ):

            known = chat_df[
                chat_df["duration"] != "Unknown"
            ]

            durations = known["duration"].astype(int)

            longest = known.loc[
                durations.idxmax()
            ]

            shortest = known.loc[
                durations.idxmin()
            ]

            response = f"""
                    📊 Music Library Report

                    🎵 Songs: {len(chat_df)}

                    ⏱ Total Duration: {durations.sum()} sec

                    📈 Average Length: {round(durations.mean())} sec

                    🏆 Longest Song:
                    {longest['title']}

                    ⚡ Shortest Song:
                    {shortest['title']}
                    """

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": response
                }
            )

            

        # --------------------------
        # Workout Playlist
        # --------------------------

        elif (
            "workout playlist" in command
            or "gym playlist" in command
        ):

            generated = generate_playlist(
                "Workout",
                songs,
                10
            )
            st.session_state.saved_playlists["workout"] = generated
            st.session_state.current_playlist = generated
            st.session_state.current_index = 0
            st.session_state.current_song = generated[0]
            st.session_state.is_paused = False
            
            play_song(
                generated[0]["path"]
            )    
            
            st.session_state.lyrics = load_song_lyrics(
                generated[0]
            )

            response = (
                f"💪 Workout playlist created!"
            )

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": response
                }
            )


        # --------------------------
        # Study Playlist
        # --------------------------

        elif "study playlist" in command:

            generated = generate_playlist(
                "Study",
                songs,
                10
            )

            st.session_state.saved_playlists["study"] = generated
            st.session_state.current_playlist = generated
            st.session_state.current_index = 0
            st.session_state.current_song = generated[0]
            st.session_state.is_paused = False
            play_song(
                generated[0]["path"]
            )
            
            st.session_state.lyrics = load_song_lyrics(
                generated[0]
            )


            response = (
                f"📚 Study playlist created!"
            )

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": response
                }
            )

      


        # --------------------------
        # Relax Playlist
        # --------------------------

        elif "relax playlist" in command:

            generated = generate_playlist(
                "Relax",
                songs,
                10
            )
            
            st.session_state.saved_playlists["relax"] = generated
            st.session_state.current_playlist = generated
            st.session_state.current_index = 0
            st.session_state.current_song = generated[0]
            st.session_state.is_paused = False
            
            play_song(
                generated[0]["path"]
            )

            st.session_state.lyrics = load_song_lyrics(
                generated[0]
            )
            

            response = (
                f"😌 Relax playlist created!"
            )

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": response
                }
            )



        # --------------------------
        # Show Playlists
        # --------------------------
        elif command in [
            "show playlists",
            "show saved playlists"
        ]:

            response = "📀 Available Playlists:\n\n"

            # AI playlists (memory)
            if len(st.session_state.saved_playlists) > 0:

                response += "🤖 AI Playlists:  \n"

                for name, playlist in (
                    st.session_state.saved_playlists.items()
                ):

                    response += (
                        f"• {name} ({len(playlist)} songs)  \n"
                    )

            # Disk playlists
            disk_playlists = get_playlists(folder)

            if len(disk_playlists) > 0:

                response += "\n📁 Saved Playlists:  \n"

                for name in disk_playlists:

                    response += f"• {name}  \n"

            # Nothing found
            if (
                len(st.session_state.saved_playlists) == 0
                and len(disk_playlists) == 0
            ):

                response = "❌ No playlists found."

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": response
                }
            )

     

        # --------------------------
        # Show Queue
        # --------------------------

        elif command == "show queue":

            queue = st.session_state.song_queue

            if len(queue) == 0:

                response = "📭 Queue is empty."

            else:

                queue_text = "\n".join(
                    [
                        f"{i+1}. {song['title']}"
                        for i, song in enumerate(queue)
                    ]
                )

                response = (
                    f"🎵 Current Queue:\n\n{queue_text}"
                )

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": response
                }
            )

  

        # --------------------------
        # play random
        # --------------------------
        
        elif "play random" in command:

            import random

            found_song = random.choice(songs)

            st.session_state.current_song = found_song
            st.session_state.current_playlist = [found_song]
            st.session_state.current_index = 0
            st.session_state.is_paused = False

            play_song(
                found_song["path"]
            )
            
            st.session_state.lyrics = load_song_lyrics(
                found_song
            )

            response = (
                f"🎲 Playing random song:\n\n"
                f"{found_song['title']}"
            )

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": response
                }
            )



        # --------------------------
        # shortest song
        # --------------------------

        elif "shortest song" in command:

            known = [
                s for s in songs
                if s["duration"] != "Unknown"
            ]

            found_song = min(
                known,
                key=lambda x: x["duration"]
            )

            st.session_state.current_song = found_song
            st.session_state.current_playlist = [found_song]
            st.session_state.current_index = 0
            st.session_state.is_paused = False

            play_song(
                found_song["path"]
            )
            
            st.session_state.lyrics = load_song_lyrics(
                found_song
            )


            response = (
                f"⚡ Playing shortest song:\n\n"
                f"{found_song['title']}"
            )

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": response
                }
            )

           


        # --------------------------
        # longest song
        # --------------------------

        elif "longest song" in command:

            known = [
                s for s in songs
                if s["duration"] != "Unknown"
            ]

            found_song = max(
                known,
                key=lambda x: x["duration"]
            )

            st.session_state.current_song = found_song
            st.session_state.current_playlist = [found_song]
            st.session_state.current_index = 0
            st.session_state.is_paused = False

            play_song(
                found_song["path"]
            )
            
            st.session_state.lyrics = load_song_lyrics(
                found_song
            )

            response = (
                f"🏆 Playing longest song:\n\n"
                f"{found_song['title']}"
            )

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": response
                }
            )


    
        # --------------------------
        # Next song
        # --------------------------

        elif "next song" in command or "skip" in command:
            
            current_song = None

            # Queue has highest priority
            if len(st.session_state.song_queue) > 0:

                current_song = (
                    st.session_state.song_queue.pop(0)
                )
            
                sync_current_song(current_song)

                

            # No queue, use playlist
            elif len(st.session_state.current_playlist) > 0:

                playlist = st.session_state.current_playlist

                if len(playlist) == 1:

                    print("ONLY ONE SONG IN PLAYLIST")

                    current_song = None

                elif st.session_state.shuffle_mode:

                    import random

                    current_song = random.choice(
                        playlist
                    )

                else:

                    st.session_state.current_index += 1

                    if st.session_state.current_index >= len(playlist):

                        st.session_state.current_index = 0

                    current_song = playlist[
                        st.session_state.current_index
                    ]
            
            if current_song:

                sync_current_song(current_song)

                st.session_state.is_paused = False

                print(
                    "PLAYLIST LENGTH:",
                    len(st.session_state.current_playlist)
                )

                print(
                    "CURRENT INDEX:",
                    st.session_state.current_index
                )

                if current_song.get("source") == "youtube":

                    yt_song = get_audio_stream(
                        current_song["title"]
                    )

                    if yt_song:

                        current_song["path"] = yt_song["stream_url"]

                        current_song["thumbnail"] = yt_song.get(
                            "thumbnail"
                        )

                play_song(
                    current_song["path"]
                )


                st.session_state.lyrics = load_song_lyrics(
                    current_song
                )

                response = f"⏭ Playing {current_song['title']}"

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": response
                    }
                )
                                           
            # Nothing available
            else:

                st.write(
                    "❌ No queue or playlist available."
                )
                
        # --------------------------
        # Previous song
        # --------------------------

        elif "previous song" in command:

            if len(st.session_state.current_playlist) == 0:

                st.write("❌ No playlist is active.")

            else:

                playlist = st.session_state.current_playlist

                st.session_state.current_index -= 1

                if st.session_state.current_index < 0:
                    st.session_state.current_index = len(playlist) - 1

                current_song = playlist[
                    st.session_state.current_index
                ]

                sync_current_song(current_song)
                
                st.session_state.is_paused = False

                play_song(
                    current_song["path"]
                )

                st.session_state.lyrics = load_song_lyrics(
                    current_song
                )

                response = f"⏮ Playing {current_song['title']}"

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": response
                    }
                )

                st.rerun()



        # --------------------------
        # Replay
        # --------------------------

        elif command in [
            "replay",
            "replay song",
            "play again",
            "replay last song"
        ]:

            if st.session_state.current_song is None:

                st.write("❌ No song has been played yet.")

            else:

                current_song = st.session_state.current_song
                
                
                response = (
                    f"🔁 Replaying: {current_song['title']}"
                )
                

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": response
                    }
                )
                play_song(
                    current_song["path"]
                )

                st.session_state.lyrics = load_song_lyrics(
                    current_song
                )

                st.session_state.is_paused = False

                sync_current_song(current_song)

                st.rerun()

                

        # --------------------------
        # Queue Song
        # --------------------------

        elif command.startswith("queue "):

            song_name = command.replace(
                "queue",
                ""
            ).strip()

            found_song = None

            for song in songs:

                if song_name in song["title"].lower():

                    found_song = song
                    break

            if found_song:

                st.session_state.song_queue.append(
                    found_song
                )
                
                response = (
                    f"➕ Added to queue:\n\n"
                    f"{found_song['title']}"
                )

            else:    
                yt_song = get_audio_stream(
                song_name
                )
                print("YT SONG =", yt_song)

                if yt_song:

                    st.session_state.song_queue.append(
                        {
                            "title": yt_song["title"],
                            "path": yt_song["stream_url"],
                            "source": "youtube",
                            "duration": yt_song.get(
                                "duration",
                                "Unknown"
                            )
                        }
                    )

                    response = (
                        f"📥 Queued from YouTube: "
                        f"{yt_song['title']}"
                    )

                else:

                    response = (
                        f"❌ Song not found: "
                        f"{song_name}"
                    )
                    
            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": response
                }
            )

    
        
        # --------------------------
        # Shuffle ON
        # --------------------------

        elif "shuffle on" in command:

            st.session_state.shuffle_mode = True

            response = "🔀 Shuffle Mode Enabled"

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": response
                }
                )


        # --------------------------
        # Shuffle OFF
        # --------------------------

        elif command == "shuffle off":

            st.session_state.shuffle_mode = False

            response = "➡️ Shuffle Mode Disabled"

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": response
                }
            )

                
        # --------------------------
        # pause
        # --------------------------
        elif command == "pause":

            if st.session_state.current_song is None:

                st.write("❌ No song is playing.")

            else:

                current_song = st.session_state.current_song

                st.session_state.is_paused = True
                
                pause_song()

                response = (
                    f"⏸ Paused {current_song['title']}"
                )

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": response
                    }
                )

               
        
        elif command in [
            "play",
            "resume",
            "continue",
            "resume song"
        ]:

            if st.session_state.current_song is None:

                st.write("❌ No song selected.")

            else:

                current_song = st.session_state.current_song

                st.session_state.is_paused = False

                pause_song()

                response = (
                    f"▶ Resuming {current_song['title']}"
                )

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": response
                    }
                )

   


        # --------------------------
        # save Playlist
        # --------------------------
        
        elif command.startswith("save playlist"):

            playlist_name = command.replace(
                "save playlist",
                ""
            ).strip().lower()

            if playlist_name in st.session_state.saved_playlists:

                playlist = (
                    st.session_state.saved_playlists[
                        playlist_name
                    ]
                )

                filepath = create_playlist(
                    playlist_name,
                    playlist,
                    folder
                )

                response = (
                    f"💾 Playlist saved successfully!\n\n"
                    f"{filepath}"
                )

            else:

                response = (
                    f"❌ Playlist '{playlist_name}' not found."
                )

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": response
                }
            )



        # --------------------------
        # Play Playlist
        # --------------------------

        elif command.startswith("play playlist"):

            playlist_name = command.replace(
                "play playlist",
                ""
            ).strip().lower()

            if (
                playlist_name
                in st.session_state.saved_playlists
            ):

                playlist = (
                    st.session_state.saved_playlists[
                        playlist_name
                    ]
                )

                st.session_state.current_playlist = playlist
                st.session_state.current_index = 0
                st.session_state.current_song = playlist[0]
                
                play_song(
                    playlist[0]["path"]
                )

                st.session_state.lyrics = load_song_lyrics(
                    playlist[0]
                )

                st.session_state.is_paused = False
            

                response = (
                    f"▶ Playing playlist: {playlist_name}"
                )

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": response
                    }
                )
                st.rerun()

            else:

                playlists = get_playlists(folder)

                playlist_file = None

                for p in playlists:

                    if p.replace(".m3u", "").lower() == playlist_name:

                        playlist_file = p
                        break

                if playlist_file:

                    playlist = load_m3u_playlist(
                        folder,
                        playlist_file
                    )

                    if len(playlist) > 0:

                        st.session_state.current_playlist = playlist
                        st.session_state.current_index = 0
                        st.session_state.current_song = playlist[0]
                        play_song(
                            playlist[0]["path"]
                        )

                        st.session_state.lyrics = load_song_lyrics(
                            playlist[0]
                        )

                        st.session_state.is_paused = False

                        response = (
                            f"▶ Playing playlist: {playlist_file}"
                        )

                        st.session_state.messages.append(
                            {
                                "role": "assistant",
                                "content": response
                            }

                        )
                        st.rerun()   

                        
                    else:

                        response = (
                            "❌ Playlist is empty."
                        )

                        st.session_state.messages.append(
                        {
                            "role": "assistant",
                            "content": response,
                            
                        }
                    )

                    
                else:

                    response = (
                        f"❌ Playlist '{playlist_name}' not found."
                    )

                    st.session_state.messages.append(
                        {
                            "role": "assistant",
                            "content": response
                        }
                    )

                    

        elif command == "play liked songs":

            liked = st.session_state.liked_songs

            if len(liked) > 0:

                st.session_state.current_playlist = liked

                st.session_state.current_index = 0

                st.session_state.current_song = liked[0]

                song = liked[0]

                if song.get("source") == "youtube":

                    yt_song = get_audio_stream(
                        song["title"]
                    )

                    if yt_song:

                        song["path"] = yt_song["stream_url"]

                        song["thumbnail"] = yt_song.get(
                            "thumbnail"
                        )

                        play_song(
                            song["path"]
                        )

                        st.session_state.lyrics = load_song_lyrics(
                            song
                        )

                else:

                    play_song(
                        song["path"]
                    )
                    
                    st.session_state.lyrics = load_song_lyrics(
                        song
                    )

                st.rerun()


                    
        # --------------------------
        # Play
        # --------------------------

        elif command.startswith("play "):

            song_name = command.replace(
                "play",
                ""
            ).strip()

            found_song = None

            for song in songs:

                if song_name in song["title"].lower():

                    found_song = song
                    break

            if found_song:

                st.session_state.current_song = found_song
                

                # Don't destroy existing playlist
                if len(st.session_state.current_playlist) == 0:
                    st.session_state.current_playlist = songs

                # Move index to the selected song
                for i, song in enumerate(st.session_state.current_playlist):
                    if song["title"] == found_song["title"]:
                        st.session_state.current_index = i
                        break

                st.session_state.is_paused = False
                
                play_song(
                   found_song["path"]
                )

                st.session_state.lyrics = load_song_lyrics(
                    found_song
                )

                response = (
                    f"▶ Playing {found_song['title']}"
                )

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": response
                    }
                )

        
                
                st.rerun()

            else:

                yt_song = get_audio_stream(
                    song_name
                )

                if yt_song is None:

                    response = "❌ Could not find song on YouTube."

                    st.session_state.messages.append(
                        {
                            "role": "assistant",
                            "content": response
                        }
                    )

                else:

                    play_song(
                        yt_song["stream_url"]
                    )

                    song_title = yt_song["title"]

                    artist = ""
                    title = song_title

                    if " - " in song_title:

                        artist, title = song_title.split(
                            " - ",
                            1
                        )

                    print("TITLE =", title)
                    print("ARTIST =", artist)

                    st.session_state.lyrics = get_cached_lyrics(
                        title.strip(),
                        artist.strip()
                    )

                    st.session_state.current_song = {
                        "title": yt_song["title"],
                        "path": yt_song["stream_url"],

                        # ADD THIS
                        "youtube_url": yt_song.get("webpage_url", ""),
                        "source": "youtube",
                        "duration": yt_song.get(
                            "duration",
                            "Unknown"
                        ),
                        "thumbnail": yt_song.get(
                            "thumbnail"
                        )
                    }

                    st.session_state.current_playlist = [
                        st.session_state.current_song
                    ]

                    st.session_state.current_index = 0
                response = (
                    f"▶ Playing from YouTube: "
                    f"{yt_song['title']}"
                )
                
                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": response
                    }
                )

   

                    
        
        
        # --------------------------
        # Help
        # --------------------------

        else:

            response = (
                "Try:\n"
                "- study playlist\n"
                "- workout playlist\n"
                "- relax playlist\n"
                "- play husn\n"
                "- next song\n"
                "- previous song\n"
                "- show queue"
            )

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": response
                }
            )



# --------------------------
# Sidebar
# --------------------------

with st.sidebar:

    st.header("🎵 Now Playing")

    if st.session_state.current_song is not None:

        song = st.session_state.current_song

        if st.session_state.get("is_paused", False):

            st.write("⏸ Paused")

        else:

            st.write("▶ Playing")

        st.write(f"**{song['title']}**")

        if song.get("duration", "Unknown") != "Unknown":

            st.write(
                f"⏱ Duration: {song['duration']} sec"
            )

    else:

        st.write("No song selected.")

    st.divider()


    queue = st.session_state.get(
        "song_queue",
        []
    )

    st.subheader(
        f"📋 Queue ({len(queue)})"  
    )

    if len(queue) == 0:

        st.write("Queue is empty.")

    else:

        for i, song in enumerate(queue):

            st.write(
                f"{i+1}. {song['title']}"
            )

    st.divider()

    st.subheader("📀 Current Playlist")

    if (
        "current_playlist" in st.session_state
        and len(st.session_state.current_playlist) > 0
    ):

        playlist = st.session_state.current_playlist

        current_index = st.session_state.get(
            "current_index",
            0
        )

        st.write(
            f"▶ Current Position: {current_index + 1}/{len(playlist)}"
        )

        current_title = st.session_state.current_song["title"]

        for i, song in enumerate(playlist):

            is_current = (
                song["title"] == current_title
            )
            
            if song["title"] == current_title:

                st.markdown(
                f"""
                <div style="
                background:#241033;
                border-left:4px solid #ff4fd8;
                padding:12px;
                border-radius:12px;
                color:white;
                font-weight:bold;
                ">
                🎵 {song['title']}
                </div>
                """,
                unsafe_allow_html=True
                )

            else:

                st.write(
                    song["title"]
                )

    else:

        st.write(
            "No active playlist."
        )

    st.markdown(
        "Scan your local music library and view song analytics."
    )
    st.divider()

    st.subheader("🎼 Quick Playlists")

    all_playlists = list(
        st.session_state.saved_playlists.keys()
    )

    for playlist_name in all_playlists:

        if st.button(
            f"▶ {playlist_name}"
        ):

            st.session_state.button_command = (
                f"play playlist {playlist_name}"
            )

            st.rerun()

# --------------------------
# Music Player
# --------------------------

st_autorefresh(
    interval=1000,
    key="music_player_refresh"
)

st.divider()
st.write("")

if st.session_state.current_song is not None:

    song = st.session_state.current_song

    if song.get("source") == "youtube":

        song_title = song["title"]

        artist = ""
        title = song_title

        if " - " in song_title:

            artist, title = song_title.split(
                " - ",
                1
            )

        metadata = {
            "title": title,
            "artist": artist,
            "album": None
        }


        album_art = song.get(
            "thumbnail"
        )

    else:

        metadata = get_song_metadata(
            song["path"]
        )

        album_art = get_album_art(
            song["path"]
        )

    player_col1, player_col2 = st.columns(
        [1.2, 1]
    )

    with player_col1:

        if album_art:

            st.image(
                album_art,
                width="stretch"
            )

        else:

            st.info(
                "No Album Art"
            )

    with player_col2:


        st.markdown(
            f"""
            <h1 style="
            color:white;
            margin-bottom:5px;
            ">
            {metadata['title'] or song['title']}
            </h1>
            """,
            unsafe_allow_html=True
        )

        

        artist = metadata.get("artist", "")

        if artist:

            st.markdown(
                f"""
                <h3 style="
                color:#ff4fd8;
                margin-top:0;
                ">
                {artist}
                </h3>
                """,
                unsafe_allow_html=True
            )

        st.write("")

        

        if song.get("source") == "youtube":
            badge = "🌐 YouTube Audio"
        else:
            badge = "📁 Local File"

        st.markdown(
        f"""
        <div style="
        display:inline-block;
        padding:8px 16px;
        background:#241033;
        border:1px solid #ff4fd8;
        border-radius:20px;
        margin-bottom:20px;
        ">
        {badge}
        </div>
        """,
        unsafe_allow_html=True
        )

        st.write("")
            
        if metadata["album"]:

            st.write(
                f"💿 {metadata['album']}"
            )

        if len(st.session_state.current_playlist) > 0:

            st.caption(
                f"Track "
                f"{st.session_state.current_index + 1}"
                f"/"
                f"{len(st.session_state.current_playlist)}"
            )   

    st.write("")
        
    left, c1, c2, c3, c4, c5, c6, right = st.columns(
    [2,1,1,1,1,1,1,2]
)
    
    with c1:
        if st.button("🔀"):
            st.session_state.shuffle_mode = (
                not st.session_state.shuffle_mode
            )
            st.rerun()

    with c2:

        if st.button("⏮"):

            st.session_state.button_command = (
                "previous song"
            )

            st.rerun()


    play_icon = (
        "▶️"
        if st.session_state.get(
            "is_paused",
            False
        )
        else "⏸️"
    )

    with c3:

        if st.button(play_icon):
            st.session_state.control = "playpause"
            st.rerun()

    with c4:

        if st.button("⏭"):
            st.session_state.button_command = (
                "next song"
            )

            st.rerun()

    with c5:

        if st.button("🔁"):
            st.session_state.button_command = (
                "replay"
            )

            st.rerun()

    with c6:

        if st.button("❤️"):

            if st.session_state.current_song:

                song = st.session_state.current_song
                exists = any(
                    liked["title"] == song["title"]
                    for liked in st.session_state.liked_songs
                )

                if not exists:

                    liked_song = song.copy()

                    st.session_state.liked_songs.append(
                        liked_song
                    )

                    save_liked_songs(
                        st.session_state.liked_songs
                    )

                    st.toast(
                        "❤️ Added to liked songs"
                    )

                else:

                    st.toast(
                        "❤️ Already liked"
                    )
        
    st.write("")


    current_time = max(0, get_current_time())

    total_duration = max(1, get_duration())

    progress = min(
        current_time / total_duration,
        1.0
    )

    st.progress(progress)

    t1, t2 = st.columns(2)

    with t1:
        st.caption(format_time(current_time))

    with t2:
        st.markdown(
            f"""
            <div style="
            text-align:right;
            color:#cccccc;
            ">
            {format_time(total_duration)}
            </div>
            """,
            unsafe_allow_html=True
        )         

    st.markdown("""
    <style>

    .stProgress > div > div {
        height:8px;
        border-radius:20px;
    }

    </style>
    """, unsafe_allow_html=True)
    
if st.session_state.shuffle_mode:

    st.success("🔀 Shuffle ON")

else:

    st.caption("🔀 Shuffle OFF")

st.markdown("---")

st.markdown("""
<h2 style="
color:white;
margin-bottom:10px;
">
🎤 Lyrics
</h2>
""",
unsafe_allow_html=True)

st.markdown("""
<div style="
width:120px;
height:3px;
background:#ff4fd8;
margin-bottom:20px;
"></div>
""",
unsafe_allow_html=True)

lyrics = st.session_state.get(
    "lyrics",
    "No lyrics available."
)


lyrics = re.sub(r"\[\d+:\d+\.\d+\]", "", lyrics)

with st.container():

    st.markdown("""
    <style>
    .lyrics-box {
        background: linear-gradient(
            135deg,
            rgba(255,79,216,0.18),
            rgba(255,255,255,0.06)
        );

        border: 1px solid rgba(255,79,216,0.35);

        border-radius: 24px;

        padding: 25px;

        height: 350px;

        overflow-y: auto;

        color: white;

        line-height: 1.8;

        font-size: 16px;

        backdrop-filter: blur(12px);

        box-shadow: 0 8px 25px rgba(255,79,216,0.15);
    }
    </style>
        """,
    unsafe_allow_html=True)

    st.markdown(
    f"""
    <div class="lyrics-box">
        {lyrics.replace(chr(10), '<br>')}
    </div>
    """,
    unsafe_allow_html=True
    )