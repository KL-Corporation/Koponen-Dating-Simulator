import os
import importlib
import pygame
from pygame.locals import *
import KDS.ConfigManager, KDS.UI,  KDS.Colors

AppDataPath = os.path.join(os.getenv('APPDATA'), "Koponen Development Inc", "Koponen Dating Simulator")
button_font = pygame.font.Font("Assets/Fonts/gamefont2.ttf", 26, bold=0, italic=0)
button_font1 = pygame.font.Font("Assets/Fonts/gamefont2.ttf", 52, bold=0, italic=0)

def settings_menu(main, surface):
    global main_menu_running, esc_menu, main_running, settings_running, DebugMode, clearLag
    c = False
    settings_running = True

    def return_def():
        return False

    def reset_window():
        main.ResizeWindow(main.display_size)

    def reset_settings():
        return_def()
        os.remove(os.path.join(AppDataPath, "settings.cfg"))
        importlib.reload(KDS.ConfigManager)
        main.Fullscreen.Set(True)
    
    def reset_data():
        main.KDS_Quit(True, True)
    
    return_button = KDS.UI.New.Button(pygame.Rect(465, 700, 270, 60), return_def, button_font1.render(
        "Return", True, KDS.Colors.GetPrimary.White))
    music_volume_slider = KDS.UI.New.Slider(
        "MusicVolume", pygame.Rect(450, 135, 340, 20), (20, 30), 1, custom_dir="Settings")
    effect_volume_slider = KDS.UI.New.Slider(
        "SoundEffectVolume", pygame.Rect(450, 185, 340, 20), (20, 30), 1, custom_dir="Settings")
    clearLag_switch = KDS.UI.New.Switch("ClearLag", pygame.Rect(450, 240, 100, 30), (30, 50), custom_dir="Settings")
    reset_window_button = KDS.UI.New.Button(pygame.Rect(470, 360, 260, 40), reset_window, button_font.render("Reset Window Size", True, KDS.Colors.GetPrimary.White))
    reset_settings_button = KDS.UI.New.Button(pygame.Rect(340, 585, 240, 40), reset_settings, button_font.render("Reset Settings", True, KDS.Colors.GetPrimary.White))
    reset_data_button = KDS.UI.New.Button(pygame.Rect(620, 585, 240, 40), reset_data, button_font.render("Reset Data", True, KDS.Colors.GetPrimary.White))
    music_volume_text = button_font.render(
        "Music Volume", True, KDS.Colors.GetPrimary.White)
    effect_volume_text = button_font.render(
        "Sound Effect Volume", True, KDS.Colors.GetPrimary.White)
    clear_lag_text = button_font.render(
        "Clear Lag", True, KDS.Colors.GetPrimary.White)

    while settings_running:
        mouse_pos = (int((pygame.mouse.get_pos()[0] - main.Fullscreen.offset[0]) / main.Fullscreen.scaling), int(
            (pygame.mouse.get_pos()[1] - main.Fullscreen.offset[1]) / main.Fullscreen.scaling))

        for event in pygame.event.get():
            if event.type == MOUSEBUTTONUP:
                if event.button == 1:
                    c = True
            elif event.type == KEYDOWN:
                if event.key == K_F11:
                    main.Fullscreen.Set()
                elif event.key == K_F4:
                    if pygame.key.get_pressed()[K_LALT]:
                        main.KDS_Quit()
                elif event.key == K_ESCAPE:
                    settings_running = False
                elif event.key == K_F3:
                    main.DebugMode = not main.DebugMode
            elif event.type == pygame.QUIT:
                main.KDS_Quit()

            elif event.type == pygame.VIDEORESIZE:
                main.ResizeWindow(event.size)

        display.blit(settings_background, (0, 0))

        display.blit(pygame.transform.flip(
            menu_trashcan_animation.update(), False, False), (279, 515))

        display.blit(music_volume_text, (50, 135))
        display.blit(effect_volume_text, (50, 185))
        display.blit(clear_lag_text, (50, 240))
        Audio.MusicVolume = music_volume_slider.update(display, mouse_pos)
        Audio.MusicMixer.set_volume(Audio.MusicVolume)
        Audio.setVolume(effect_volume_slider.update(display, mouse_pos))

        return_button.update(display, mouse_pos, c)
        reset_window_button.update(display, mouse_pos, c)
        reset_settings_button.update(display, mouse_pos, c)
        reset_data_button.update(display, mouse_pos, c)
        clearLag = clearLag_switch.update(display, mouse_pos, c)

        KDS.Logging.Profiler(DebugMode)
        if DebugMode:
            debugSurf = pygame.Surface((200, 40))
            debugSurf.fill(KDS.Colors.GetPrimary.DarkGray)
            debugSurf.set_alpha(128)
            display.blit(debugSurf, (0, 0))
            
            fps_text = "FPS: " + str(int(round(clock.get_fps())))
            fps_text = score_font.render(
                fps_text, True, KDS.Colors.GetPrimary.White)
            display.blit(pygame.transform.scale(fps_text, (int(
                fps_text.get_width() * 2), int(fps_text.get_height() * 2))), (10, 10))

        window.blit(pygame.transform.scale(display, (int(display_size[0] * Fullscreen.scaling), int(
            display_size[1] * Fullscreen.scaling))), (Fullscreen.offset[0], Fullscreen.offset[1]))
        pygame.display.update()
        window.fill((0, 0, 0))
        c = False
        clock.tick(60)