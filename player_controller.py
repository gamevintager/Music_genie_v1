import vlc
import time

player = vlc.MediaPlayer()

current_path = None

song_end_flag = False

def song_ended(event):

    global song_end_flag

    song_end_flag = True

def has_song_ended():

    global song_end_flag

    if song_end_flag:

        song_end_flag = False

        return True

    return False

def play_song(song_path):

    global current_path

    player.stop()

    time.sleep(0.2)

    current_path = song_path

    media = vlc.Media(song_path)

    player.set_media(media)

    player.play()


def pause_song():

    player.pause()


def stop_song():

    player.stop()


def is_playing():

    return bool(
        player.is_playing()
    )


def get_current_path():

    return current_path


def get_player():

    return player

def song_finished():

    if current_path is None:
        return False

    state = player.get_state()

    return (
        state == vlc.State.Ended
    )

def register_end_callback(callback):

    event_manager = player.event_manager()

    event_manager.event_attach(
        vlc.EventType.MediaPlayerEndReached,
        callback
    )

register_end_callback(song_ended)