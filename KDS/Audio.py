import dataclasses
from typing import List, NamedTuple, Optional
import pygame
import pygame.mixer
import KDS.ConfigManager
import KDS.Events
import KDS.Logging
import KDS.Math

SoundMixer = pygame.mixer
MusicMixer = pygame.mixer.music

MusicVolume: float
EffectVolume: float
EffectChannels: List[SoundMixer.Channel]
def init():
    global MusicVolume, EffectVolume, EffectChannels
    pygame.mixer.init()

    SoundMixer.set_num_channels(KDS.ConfigManager.GetSetting("Mixer/channelCount", ...))

    MusicVolume = KDS.ConfigManager.GetSetting("Mixer/Volume/music", ...)
    EffectVolume = KDS.ConfigManager.GetSetting("Mixer/Volume/effect", ...)
    EffectChannels = []
    for c_i in range(SoundMixer.get_num_channels()):
        EffectChannels.append(SoundMixer.Channel(c_i))

class _MusicLoadedContext(NamedTuple):
    filepath: str

class _MusicPlayingContext(NamedTuple):
    filepath: str
    start: float
    loop: bool

class MusicOverrideHandle:
    def __init__(self, *, _ctx: _MusicPlayingContext | None, _musicmixer_pos_ms: float) -> None:
        self._ctx: _MusicPlayingContext | None = _ctx
        self._musicmixer_pos_ms: float = _musicmixer_pos_ms

        self._local_volume: float = 1.0
        self._is_active: bool = True

    @property
    def is_active(self) -> bool:
        return self._is_active

    def _checkActive(self):
        if not self._is_active:
            e = RuntimeError("Music Override Handle is not active anymore!")
            e.add_note("If you did not stop the overridden music, all music might have been stopped in the parent player or another base music might have been loaded.")
            raise e

    def SetLocalVolume(self, volume: float):
        self._checkActive()

        self._local_volume = volume
        self._UpdateLocalVolume()

    def _UpdateLocalVolume(self):
        self._checkActive()

        MusicMixer.set_volume(MusicVolume * self._local_volume)
        # MusicMixer.set_volume doesn't modify MusicVolume

    def Stop(self, *, _play_base_song: bool = True):
        """
        Starts playing the base music again. (restores the original MusicMixer state)
        Music position can only be restored if loops=0
        """

        self._checkActive()
        self._is_active = False

        Music.Overridden = None

        if self._ctx is not None:
            start: float
            if not self._ctx.loop:
                start = self._ctx.start + (self._musicmixer_pos_ms / 1000)
            else:
                start = 0.0

            MusicMixer.set_volume(MusicVolume)

            if _play_base_song:
                Music.Play(self._ctx.filepath, loop=self._ctx.loop, start=start)
        else:
            if _play_base_song:
                Music.Stop()

class Music:
    Loaded: _MusicLoadedContext | None = None
    """This value might change if the music is overridden."""
    Playing: _MusicPlayingContext | None = None
    """
    This value might change if the music is overridden.

    A song might be loaded, but is not playing. Only `Music.Playing` contains the up to date info on the currently playing song.
    """

    Overridden: MusicOverrideHandle | None = None

    @staticmethod
    def Play(path: Optional[str] = None, loop: bool = True, start: float = 0.0):
        global MusicMixer, MusicVolume
        if path != None and len(path) > 0:
            Music.Load(path=path)

        assert(Music.Loaded is not None)
        MusicMixer.play(loops=(-1 if loop else 0), start=start)
        MusicMixer.set_volume(MusicVolume)
        Music.Playing = _MusicPlayingContext(filepath=Music.Loaded.filepath, loop=loop, start=start)

    @staticmethod
    def Stop():
        global MusicMixer, MusicVolume
        if Music.Overridden is not None:
            Music.Overridden.Stop(_play_base_song=False)
        MusicMixer.stop()
        Music.Playing = None

    @staticmethod
    def Fadeout(seconds: float):
        global MusicMixer
        MusicMixer.fadeout(round(seconds * 1000.0))

    @staticmethod
    def Pause():
        global MusicMixer, MusicVolume
        MusicMixer.pause()

    @staticmethod
    def Unpause():
        global MusicMixer, MusicVolume
        MusicMixer.unpause()

    @staticmethod
    def Override(path: Optional[str] = None, loop: bool = True) -> MusicOverrideHandle:
        if Music.Overridden is not None:
            raise RuntimeError("Cannot override! Music has already been overridden.")

        handle = MusicOverrideHandle(
            _ctx=Music.Playing,
            _musicmixer_pos_ms=(MusicMixer.get_pos() / 1000)
        )
        Music.Play(path, loop=loop)
        Music.Overridden = handle

        return handle


    @staticmethod
    def Load(path: str):
        global MusicMixer, MusicVolume
        Music.Stop()
        if path == None: # type: ignore
            raise ValueError("Audio file path cannot be null!")
        MusicMixer.load(path)
        Music.Loaded = _MusicLoadedContext(filepath=path)

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
        if Music.Overridden is None:
            MusicMixer.set_volume(MusicVolume)
        else:
            Music.Overridden._UpdateLocalVolume()

    # @staticmethod
    # def SetPos(pos: float):
    #     global MusicMixer
    #     MusicMixer.set_pos(pos)

    @staticmethod
    def GetPlaying():
        global MusicMixer
        return MusicMixer.get_busy()

def quit():
    global MusicMixer, MusicVolume, EffectVolume, EffectChannels
    SoundMixer.quit()

def PlaySound(sound, volume: float = -1.0, loops: int = 0, fade_ms: int = 0) -> pygame.mixer.Channel:
    global MusicMixer, MusicVolume, EffectVolume, EffectChannels
    if volume == -1.0:
        volume = EffectVolume
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
    output = PlaySound(sound, volume, loops, fade_ms)
    del sound
    return output
