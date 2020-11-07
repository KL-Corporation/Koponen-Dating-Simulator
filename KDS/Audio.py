import KDS.ConfigManager

def init(_mixer):
    global MusicMixer, MusicVolume, EffectVolume, EffectChannels, SoundMixer
    MusicMixer = _mixer.music
    SoundMixer = _mixer
    
    _mixer.set_num_channels(KDS.ConfigManager.GetSetting("Mixer", "channelCount", 32))

    MusicVolume = KDS.ConfigManager.GetSetting("Settings", "MusicVolume", 1.0)
    EffectVolume = KDS.ConfigManager.GetSetting("Settings", "SoundEffectVolume", 1.0)
    EffectChannels = []
    for c_i in range(SoundMixer.get_num_channels()):
        EffectChannels.append(SoundMixer.Channel(c_i))
        
def quit():
    global MusicMixer, MusicVolume, EffectVolume, EffectChannels
    MusicMixer.quit()

def playSound(sound, volume: float = -1, loops: int = 0):
    global MusicMixer, MusicVolume, EffectVolume, EffectChannels
    if volume == -1:
        volume = EffectVolume
    play_channel = SoundMixer.find_channel(True)
    play_channel.play(sound, loops)
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