import winsound
import threading
import os

def play_sound(sound_type: str) -> None:
    """Воспроизвести системный звук Windows."""
    def _play():
        if sound_type == "start":
            winsound.PlaySound("SystemAsterisk", winsound.SND_ALIAS)
        elif sound_type == "stop":
            winsound.PlaySound("SystemExclamation", winsound.SND_ALIAS)
    
    # Воспроизводим звук в отдельном потоке, чтобы не блокировать UI
    thread = threading.Thread(target=_play)
    thread.daemon = True
    thread.start()

def play_start_sound() -> None:
    """Воспроизвести звук начала отслеживания."""
    play_sound("start")

def play_stop_sound() -> None:
    """Воспроизвести звук завершения отслеживания."""
    play_sound("stop") 