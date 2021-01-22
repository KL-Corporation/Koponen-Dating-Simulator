import KDS.ConfigManager

def init(_mixer):
    global MusicMixer, MusicVolume, EffectVolume, EffectChannels, SoundMixer
    MusicMixer = _mixer.music
    SoundMixer = _mixer
    
    _mixer.set_num_channels(KDS.ConfigManager.GetSetting("Mixer/channelCount", 32))

    MusicVolume = KDS.ConfigManager.GetSetting("Mixer/Volume/music", 0.25)
    EffectVolume = KDS.ConfigManager.GetSetting("Mixer/Volume/effect", 0.75)
    EffectChannels = []
    for c_i in range(SoundMixer.get_num_channels()):
        EffectChannels.append(SoundMixer.Channel(c_i))
        
class Music:
    @staticmethod
    def Play(path: str, loops: int = -1):
        global MusicMixer, MusicVolume
        if MusicMixer.get_busy(): MusicMixer.stop()
        if path != None: MusicMixer.load(path)
        MusicMixer.play(loops)
        MusicMixer.set_volume(MusicVolume)
        
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
    def Unload():
        global MusicMixer, MusicVolume
        MusicMixer.unload()
        
    @staticmethod
    def Rewind():
        global MusicMixer, MusicVolume
        MusicMixer.rewind()
  
    @staticmethod
    def SetVolume(volume: float):
        global MusicVolume, MusicMixer
        MusicVolume = volume
        MusicMixer.set_volume(MusicVolume)
 
def quit():
    global MusicMixer, MusicVolume, EffectVolume, EffectChannels
    MusicMixer.quit()

def PlaySound(sound, volume: float = -1, loops: int = 0, fade_ms: int = 0):
    global MusicMixer, MusicVolume, EffectVolume, EffectChannels
    if volume == -1: volume = EffectVolume
    play_channel = SoundMixer.find_channel(True)
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

def PlayFromFile(path, volume: float = -1, loops: int = 0, fade_ms: int = 0):
    sound = SoundMixer.Sound(path)
    PlaySound(sound, volume, loops, fade_ms)