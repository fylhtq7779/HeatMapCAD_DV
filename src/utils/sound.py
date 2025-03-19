import os
import platform
import threading
import subprocess

def play_sound(sound_type: str) -> None:
    """Воспроизвести системный звук."""
    def _play():
        system = platform.system()
        if system == "Windows":
            import winsound
            if sound_type == "start":
                winsound.PlaySound("SystemAsterisk", winsound.SND_ALIAS)
            elif sound_type == "stop":
                winsound.PlaySound("SystemExclamation", winsound.SND_ALIAS)
        elif system == "Linux":
            # Используем стандартный системный звук
            if sound_type == "start":
                subprocess.run(["aplay", "/usr/share/sounds/freedesktop/stereo/message.oga"], 
                             stdout=subprocess.DEVNULL, 
                             stderr=subprocess.DEVNULL)
            elif sound_type == "stop":
                subprocess.run(["aplay", "/usr/share/sounds/freedesktop/stereo/complete.oga"], 
                             stdout=subprocess.DEVNULL, 
                             stderr=subprocess.DEVNULL)
    
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