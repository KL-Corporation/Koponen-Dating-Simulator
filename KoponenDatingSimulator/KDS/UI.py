import KDS.ConfigManager
import pygame
from pygame.locals import *
import os

slider_dragged = None

class New:
    
    class Slider:

        """
        1. safe_name: An identifier that does not conflict with ANY other safe_names. (Slider value will be saved at "Settings", "safe_name")
        2. slider_rect: The pygame.Rect of the slider.
        3. handle_size: Width and height of the handle.
        4. handle_move_area_padding (OPTIONAL): Reduce the left and right move area of the handle. [DEFAULT: (0, 0)]
        5. slider_color (OPTIONAL): The color of the slider background. [DEFAULT: (120, 120, 120)]
        6. handle_default_color (OPTIONAL): The color of the handle in idle state. [DEFAULT: (115, 115, 115)]
        7. handle_highlighted_color (OPTIONAL): The color of the handle in idle state. [DEFAULT: (100, 100, 100)]
        8. handle_pressed_color (OPTIONAL): The color of the handle in idle state. [DEFAULT: (90, 90, 90)]
        """

        def __init__(self, safe_name, slider_rect, handle_size: (int, int), default_value=0.0, handle_move_area_padding=(0, 0), slider_color=(120, 120, 120), handle_default_color=(100, 100, 100), handle_highlighted_color=(115, 115, 115), handle_pressed_color=(90, 90, 90)):
            self.safe_name = safe_name
            self.slider_rect = slider_rect
            self.handle_rect = pygame.Rect(slider_rect.midleft[0] + (float(KDS.ConfigManager.LoadSetting("Settings", safe_name, str(default_value))) * slider_rect.width) - (handle_size[0] / 2), 0, handle_size[0], handle_size[1])
            self.handle_move_area_padding = handle_move_area_padding
            self.slider_color = slider_color
            self.handle_default_color = handle_default_color
            self.handle_highlighted_color = handle_highlighted_color
            self.handle_pressed_color = handle_pressed_color

        def update(self, surface, fullscreen_scaling, fullscreen_offset):
            """
            1. surface: The surface this slider is going to be rendered.
            2. fullscreen_scaling: The fullscreen_scaling value FullscreenGet.scaling returns.
            3. fullscreen_offset: The fullscreen_offset value FullscreenGet.offset returns.
            """

            global slider_dragged
            slider_rect = pygame.Rect(self.slider_rect.x * fullscreen_scaling + fullscreen_offset[0], self.slider_rect.y * fullscreen_scaling + fullscreen_offset[1], self.slider_rect.width * fullscreen_scaling, self.slider_rect.height * fullscreen_scaling)
            handle_rect = pygame.Rect(self.handle_rect.x * fullscreen_scaling + fullscreen_offset[0], slider_rect.center[1] - (self.handle_rect.height / 2 * fullscreen_scaling) + fullscreen_offset[1], self.handle_rect.width * fullscreen_scaling, self.handle_rect.height * fullscreen_scaling)
            handle_move_area_padding = (self.handle_move_area_padding[0] * fullscreen_scaling, self.handle_move_area_padding[1] * fullscreen_scaling)

            pointer = pygame.mouse.get_pos()

            if not pygame.mouse.get_pressed()[0]:
                slider_dragged = None
            else:
                if handle_rect.collidepoint(pointer):
                    slider_dragged = self.safe_name

            if slider_dragged == self.safe_name:
                handle_color = self.handle_pressed_color
                position = pointer[0]
                if position < slider_rect.midleft[0] + handle_move_area_padding[0]:
                    position = slider_rect.midleft[0] + handle_move_area_padding[0]
                if position > slider_rect.midright[0] - handle_move_area_padding[1]:
                    position = slider_rect.midright[0] - handle_move_area_padding[1]
            else:
                position = handle_rect.centerx
                if handle_rect.collidepoint(pointer):
                    handle_color = self.handle_highlighted_color
                else:
                    handle_color = self.handle_default_color
            handle_rect.centerx = position

            pygame.draw.rect(surface, self.slider_color, slider_rect)
            pygame.draw.rect(surface, handle_color, handle_rect)
            self.handle_rect = pygame.Rect((handle_rect.x - fullscreen_offset[0]) / fullscreen_scaling, (handle_rect.y - fullscreen_offset[1]) / fullscreen_scaling, handle_rect.width / fullscreen_scaling, handle_rect.height / fullscreen_scaling)
            value = (handle_rect.centerx - slider_rect.midleft[0]) / (slider_rect.midright[0] - slider_rect.midleft[0] - handle_move_area_padding[0])
            KDS.ConfigManager.SetSetting("Settings", self.safe_name, str(value))
            return value
    
    class Button:

        def __init__(self, rect, function, text, button_default_color=(100, 100, 100), button_highlighted_color=(115, 115, 115), button_pressed_color=(90, 90, 90), button_disabled_color=(75, 75, 75), enabled=True):
            self.rect = rect
            self.function = function
            self.text = text
            self.button_default_color = button_default_color
            self.button_highlighted_color = button_highlighted_color
            self.button_pressed_color = button_pressed_color
            self.button_disabled_color = button_disabled_color
            self.enabled = enabled
            
        def update(self, surface, clicked, fullscreen_scaling=1, fullscreen_offset=(0, 0)):
            """
            1. surface: The surface this button is going to be rendered.
            2. fullscreen_scaling (OPTIONAL): The fullscreen_scaling value FullscreenGet.scaling returns.
            3. fullscreen_offset (OPTIONAL): The fullscreen_offset value FullscreenGet.offset returns.
            """

            pointer = pygame.mouse.get_pos()
            button_rect_scaled = pygame.Rect(self.rect.topleft[0] * fullscreen_scaling + fullscreen_offset[0], self.rect.topleft[1] * fullscreen_scaling + fullscreen_offset[1], self.rect.width * fullscreen_scaling, self.rect.height * fullscreen_scaling)
            button_color = self.button_disabled_color
            if self.enabled:
                if button_rect_scaled.collidepoint(pointer):
                    if clicked:
                        self.function()
                    button_color = self.button_highlighted_color
                    if pygame.mouse.get_pressed()[0]:
                        button_color = self.button_pressed_color
                else:
                    button_color = self.button_default_color

            pygame.draw.rect(surface, button_color, button_rect_scaled)

            text_size_scaled = (self.text.get_width() * fullscreen_scaling, self.text.get_height() * fullscreen_scaling)
            surface.blit(pygame.transform.scale(self.text, (int(text_size_scaled[0]), int(text_size_scaled[1]))), (int(button_rect_scaled.center[0] - (text_size_scaled[0] / 2)), int(button_rect_scaled.center[1] - (text_size_scaled[1] / 2))))
