import vlc
import time

instance = vlc.Instance()

player = instance.media_player_new()

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

def get_current_time():

    current = player.get_time()

    if current < 0:
        return 0

    return current // 1000

last_duration = 0

def get_duration():

    global last_duration

    duration = player.get_length()

    if duration > 0:
        last_duration = duration // 1000

    return last_duration

def play_song(song_path):

    global current_path

    player.stop()

    time.sleep(0.2)

    current_path = song_path

    media = vlc.Media(song_path)

    player.set_media(media)

    player.play()

    print(player.get_state())

    time.sleep(1)


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