import pygame
import KDS.Colors
import KDS.Convert
import threading
pygame.init()

running = False

loadingCircle = None
loadingBackground = None
debugFont = None

def __rendering(surface: pygame.Surface, _runningFunc, clock: pygame.time.Clock, background: pygame.Surface, circle: pygame.Surface, debug: bool):
    angle = 0
    surface_size = surface.get_size()
    while _runningFunc():
        surface.blit(background, (surface_size[0] / 2 - background.get_width() / 2, surface_size[1] / 2 - background.get_height() / 2))
        cpy = pygame.transform.rotate(circle, angle)
        surface.blit(cpy, (int(surface_size[0] / 2) - cpy.get_width() / 2, 600 - cpy.get_height() / 2))
        angle += 4
        while angle >= 360: angle -= 360
        if debug:
            debugSurf = pygame.Surface((200, 40))
            debugSurf.fill(KDS.Colors.DarkGray)
            debugSurf.set_alpha(128)
            surface.blit(debugSurf, (0, 0))
            
            fps_text = "FPS: " + str(round(clock.get_fps()))
            fps_text = debugFont.render(fps_text, True, KDS.Colors.White)
            surface.blit(pygame.transform.scale(fps_text, (int(
                fps_text.get_width() * 2), int(fps_text.get_height() * 2))), (10, 10))
            
        clock.tick_busy_loop(60)
        pygame.display.flip()

def Start(surface: pygame.Surface, clock: pygame.time.Clock, debug: bool = False):
    global loadingCircle, loadingBackground, debugFont, running
    if loadingCircle == None:
        loadingCircle = pygame.image.load("Assets/Textures/UI/loading_circle.png").convert()
        loadingCircle.set_colorkey(KDS.Colors.White)
        loadingBackground = pygame.image.load("Assets/Textures/UI/loading_background.png").convert()
        debugFont = pygame.font.Font("Assets/Fonts/gamefont.ttf", 10, bold=0, italic=0)
    running = True
    surface_size = surface.get_size()
    scaledLoadingBackground = KDS.Convert.AspectScale(loadingBackground, surface_size)
    scaledLoadingCircle = KDS.Convert.AspectScale(loadingCircle, (int(surface_size[0] / 7), int(surface_size[0] / 7)))
    ld_thread = threading.Thread(target=__rendering, args=(surface, lambda: running, clock, scaledLoadingBackground, scaledLoadingCircle, debug))
    ld_thread.setDaemon(True)
    ld_thread.start()
    scaledLoadingBackground = KDS.Convert.AspectScale(loadingBackground, surface_size)
    surface.blit(scaledLoadingBackground, (surface_size[0] / 2 - scaledLoadingBackground.get_width() / 2, surface_size[1] / 2 - scaledLoadingBackground.get_height() / 2))
    pygame.display.flip()

def Stop():
    global running
    running = False