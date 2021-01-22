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
    def play(path: str, loops: int = -1):
        global MusicMixer, MusicVolume
        if MusicMixer.get_busy(): MusicMixer.stop()
        if path != None: MusicMixer.load(path)
        MusicMixer.play(loops)
        MusicMixer.set_volume(MusicVolume)
        
    @staticmethod
    def stop():
        global MusicMixer, MusicVolume
        MusicMixer.stop()
        
    @staticmethod
    def pause():
        global MusicMixer, MusicVolume
        MusicMixer.pause()
        
    @staticmethod
    def unpause():
        global MusicMixer, MusicVolume
        MusicMixer.unpause()
        
    @staticmethod
    def unload():
        global MusicMixer, MusicVolume
        MusicMixer.unload()
        
    @staticmethod
    def rewind():
        global MusicMixer, MusicVolume
        MusicMixer.rewind()
  
    @staticmethod
    def setVolume(volume: float):
        global MusicVolume, MusicMixer
        MusicVolume = volume
        MusicMixer.set_volume(MusicVolume)
 
def quit():
    global MusicMixer, MusicVolume, EffectVolume, EffectChannels
    MusicMixer.quit()

def playSound(sound, volume: float = -1, loops: int = 0, fade_ms: int = 0):
    global MusicMixer, MusicVolume, EffectVolume, EffectChannels
    if volume == -1: volume = EffectVolume
    play_channel = SoundMixer.find_channel(True)
    play_channel.play(sound, loops, fade_ms)
    play_channel.set_volume(volume)
    return play_channel

def stopAllSounds():
    global MusicMixer, MusicVolume, EffectVolume, EffectChannels
    for i in range(len(EffectChannels)):
        EffectChannels[i].stop()

def pauseAllSounds():
    global MusicMixer, MusicVolume, EffectVolume, EffectChannels
    for i in range(len(EffectChannels)):
        EffectChannels[i].pause()

def unpauseAllSounds():
    global MusicMixer, MusicVolume, EffectVolume, EffectChannels
    for i in range(len(EffectChannels)):
        EffectChannels[i].unpause()

def getBusyChannels():
    global MusicMixer, MusicVolume, EffectVolume, EffectChannels
    busyChannels = []
    for i in range(len(EffectChannels)):
        if EffectChannels[i].get_busy():
            busyChannels.append(EffectChannels[i])
    return busyChannels

def setVolume(volume: float):
    global MusicMixer, MusicVolume, EffectVolume, EffectChannels
    EffectVolume = volume
    for i in range(len(EffectChannels)):
        EffectChannels[i].set_volume(volume)

def playFromFile(path, volume: float = -1, loops: int = 0, fade_ms: int = 0):
    sound = SoundMixer.Sound(path)
    playSound(sound, volume, loops, fade_ms)