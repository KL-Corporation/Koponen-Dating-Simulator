from typing import Optional
import pygame
import KDS.ConfigManager
import KDS.Events
import KDS.Logging

MUSICENDEVENT = pygame.event.custom_type()

def init(_mixer):
    global MusicMixer, MusicVolume, EffectVolume, EffectChannels, SoundMixer
    MusicMixer = _mixer.music
    MusicMixer.set_endevent(MUSICENDEVENT)
    SoundMixer = _mixer

    _mixer.set_num_channels(KDS.ConfigManager.GetSetting("Mixer/channelCount", 128))

    MusicVolume = KDS.ConfigManager.GetSetting("Mixer/Volume/music", 0.25)
    EffectVolume = KDS.ConfigManager.GetSetting("Mixer/Volume/effect", 0.75)
    EffectChannels = []
    for c_i in range(SoundMixer.get_num_channels()):
        EffectChannels.append(SoundMixer.Channel(c_i))

class Music:
    Loaded = None
    OnEnd = KDS.Events.Event()

    @staticmethod
    def Play(path: str = None, loops: int = -1):
        global MusicMixer, MusicVolume
        if path != None and len(path) > 0:
            Music.Load(path=path)
        if Music.Loaded != None:
            MusicMixer.play(loops)
            MusicMixer.set_volume(MusicVolume)
        else:
            KDS.Logging.AutoError("No music track has been loaded to play!")

    @staticmethod
    def Stop():
        global MusicMixer, MusicVolume
        MusicMixer.stop()

    @staticmethod
    def Pause():
        global MusicMixer, MusicVolume
        MusicMixer.pause()

    @staticmethod
    def Unpause():
        global MusicMixer, MusicVolume
        MusicMixer.unpause()

    @staticmethod
    def Load(path: str):
        global MusicMixer, MusicVolume
        if MusicMixer.get_busy(): MusicMixer.stop()
        if path == None:
            raise ValueError("Audio file path cannot be null!")
        MusicMixer.load(path)
        Music.Loaded = path

    @staticmethod
    def Unload():
        global MusicMixer, MusicVolume
        MusicMixer.unload()
        Music.Loaded = None

    @staticmethod
    def Rewind():
        global MusicMixer, MusicVolume
        MusicMixer.rewind()

    @staticmethod
    def SetVolume(volume: float):
        global MusicVolume, MusicMixer
        MusicVolume = volume
        MusicMixer.set_volume(MusicVolume)

    @staticmethod
    def GetPlaying():
        global MusicMixer
        return MusicMixer.get_busy()

def quit():
    global MusicMixer, MusicVolume, EffectVolume, EffectChannels
    MusicMixer.quit()

def PlaySound(sound, volume: float = -1.0, loops: int = 0, fade_ms: int = 0) -> pygame.mixer.Channel:
    global MusicMixer, MusicVolume, EffectVolume, EffectChannels
    if volume == -1.0: volume = EffectVolume
    play_channel = SoundMixer.find_channel(True) # Won't return None, because force is true
    play_channel.play(sound, loops, fade_ms)
    play_channel.set_volume(volume)
    return play_channel

def StopAllSounds():
    global MusicMixer, MusicVolume, EffectVolume, EffectChannels
    for i in range(len(EffectChannels)):
        EffectChannels[i].stop()

def PauseAllSounds():
    global MusicMixer, MusicVolume, EffectVolume, EffectChannels
    for i in range(len(EffectChannels)):
        EffectChannels[i].pause()

def UnpauseAllSounds():
    global MusicMixer, MusicVolume, EffectVolume, EffectChannels
    for i in range(len(EffectChannels)):
        EffectChannels[i].unpause()

def GetBusyChannels():
    global MusicMixer, MusicVolume, EffectVolume, EffectChannels
    busyChannels = []
    for i in range(len(EffectChannels)):
        if EffectChannels[i].get_busy():
            busyChannels.append(EffectChannels[i])
    return busyChannels

def SetVolume(volume: float):
    global MusicMixer, MusicVolume, EffectVolume, EffectChannels
    EffectVolume = volume
    for i in range(len(EffectChannels)):
        EffectChannels[i].set_volume(volume)

def PlayFromFile(path: str, volume: float = -1.0, clip_volume: float = 1.0, loops: int = 0, fade_ms: int = 0) -> pygame.mixer.Channel:
    sound = SoundMixer.Sound(path)
    if clip_volume != 1.0:
        sound.set_volume(clip_volume)
    return PlaySound(sound, volume, loops, fade_ms)