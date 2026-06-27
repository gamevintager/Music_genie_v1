# 🎵 Music Genie

> An AI-powered music player built with Python and Streamlit that combines local music playback, YouTube streaming, smart playlists, lyrics, album art, and an intelligent music assistant.

---

## 📸 Preview

<img width="1920" height="865" alt="Screenshot (204)" src="https://github.com/user-attachments/assets/44a2d7f4-5263-43db-8e0d-fdf792b50b64" />
<img width="1920" height="872" alt="Screenshot (205)" src="https://github.com/user-attachments/assets/0de24431-fd31-4810-9e06-f4ec5fef9a70" />
<img width="1920" height="863" alt="Screenshot (206)" src="https://github.com/user-attachments/assets/7807a69e-ae57-4e77-9e1d-00bfdcbaf1a3" />
<img width="1920" height="866" alt="Screenshot (207)" src="https://github.com/user-attachments/assets/ebbd00ca-3edb-46f9-ac18-5b79136e7098" />
<img width="1920" height="868" alt="Screenshot (208)" src="https://github.com/user-attachments/assets/79d4321c-4f41-4d22-a64a-cebe1f92c477" />
<img width="1920" height="878" alt="Screenshot (209)" src="https://github.com/user-attachments/assets/7c06e4c7-307b-47ff-9bad-677161e95441" />







- Home Screen
- Music Player
- AI Playlist Generator
- Lyrics View

---

## ✨ Features

### 🎵 Music Playback
- Local music playback
- YouTube playback using yt-dlp
- VLC-based audio engine
- Pause / Resume
- Next / Previous
- Replay
- Auto-next when song ends
- Playback progress bar
- Shuffle mode

### 🤖 AI Music Assistant
- Natural language commands
- Song recommendations
- Play random songs
- Library statistics
- Mood-based playlist generation

Example commands:

```text
play believer
play playlist study
study playlist
show songs
show queue
next song
previous song
replay
pause
resume
like this song
play liked songs
```

### 🎼 Playlist Management

- Create manual playlists
- AI-generated playlists
- Playlist preview before playback
- Save playlists to library
- Load saved playlists
- Sidebar playlist browser

### ❤️ Favorites

- Like songs
- Save favorites
- Play liked songs playlist

### 🎤 Lyrics & Album Art

- Automatic lyrics fetching
- Album artwork display
- YouTube thumbnails
- Local embedded cover art

### 📋 Queue System

- Queue local songs
- Queue YouTube songs
- Queue priority over playlists

---

# 🛠 Built With

- Python 3
- Streamlit
- VLC (python-vlc)
- yt-dlp
- Mutagen
- Pillow
- Pandas
- Ollama (AI Assistant)

---

# 📂 Project Structure

```text
music_genie/
│
├── app.py
├── ai_assistant.py
├── ai_playlist.py
├── local_manager.py
├── playlist_manager.py
├── playlist_viewer.py
├── player_controller.py
├── youtube_player.py
├── lyrics.py
├── liked_songs.json
└── MusicGenie/
    └── Playlists/
```

---

# 🚀 Installation

Clone the repository

```bash
git clone https://github.com/gamevintager/Music_genie_v1.git
```

Enter the project

```bash
cd Music_genie_v1
```

Install dependencies

```bash
pip install -r requirements.txt
```

Run the application

```bash
streamlit run app.py
```

---

# 🎮 Usage

1. Scan your local music folder.
2. Browse your music library.
3. Ask Music Genie using natural language.
4. Create manual or AI playlists.
5. Queue songs.
6. Enjoy lyrics and album art.

---

# 📸 Screenshots

*(Replace these with your own screenshots.)*

- Home Screen
- AI Playlist Generator
- Music Player
- Lyrics Panel
- Playlist Sidebar

---

# 🗺 Roadmap

## ✅ Version 1.0

- Local music playback
- YouTube playback
- AI assistant
- AI playlists
- Queue system
- Playlist management
- Lyrics
- Album art
- Favorites
- Progress bar
- Shuffle
- Auto-next

## 🚀 Version 1.1

- Mixed Local + YouTube playlists
- Playlist rename
- Playlist delete
- Recently played
- Shuffle Once

---

# 🤝 Contributing

Suggestions, issues, and pull requests are welcome.

---

# 📄 License

This project is licensed under the MIT License.

---

Music Genie was developed as a personal project to explore AI-assisted music playback, playlist management, and modern Python application development.
