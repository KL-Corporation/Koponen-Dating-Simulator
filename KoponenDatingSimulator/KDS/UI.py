import KDS.ConfigManager
import pygame
import os

class New:
    
    class Slider:

        """
        1. safe_name: An identifier that does not conflict with ANY other safe_names.
        2. slider_rect: The pygame.Rect of the slider.
        3. handle_size: Width and height of the handle.
        4. handle_move_area_padding (OPTIONAL): Reduce the left and right move area of the handle. [DEFAULT: (0, 0)]
        5. slider_color (OPTIONAL): The color of the slider background. [DEFAULT: (120, 120, 120)]
        6. handle_default_color (OPTIONAL): The color of the handle in idle state. [DEFAULT: (115, 115, 115)]
        7. handle_highlighted_color (OPTIONAL): The color of the handle in idle state. [DEFAULT: (100, 100, 100)]
        8. handle_pressed_color (OPTIONAL): The color of the handle in idle state. [DEFAULT: (90, 90, 90)]
        """

        slider_dragged = None

        def __init__(self, safe_name, slider_rect, handle_size: (int, int), handle_move_area_padding=(0, 0), slider_color=(120, 120, 120), handle_default_color=(115, 115, 115), handle_highlighted_color=(100, 100, 100), handle_pressed_color=(90, 90, 90)):
            self.safe_name = safe_name
            self.slider_rect = slider_rect
            self.handle_rect = pygame.Rect(slider_rect.midleft + float(KDS.ConfigManager.LoadSetting("Settings", safe_name, "0")), slider_rect.y, handle_size[0], handle_size[1])
            self.handle_move_area_padding = handle_move_area_padding
            self.slider_color = slider_color
            self.handle_default_color = handle_default_color
            self.handle_highlighted_color = handle_highlighted_color
            self.handle_pressed_color = handle_pressed_color

        def update(self, surface, fullscreen_scaling: int, fullscreen_offset: (int, int)):
            """
            1. surface: The surface this slider is going to be rendered.
            2. fullscreen_scaling: The fullscreen_scaling value the FullscreenCalculator returns.
            3. fullscreen_offset: The fullscreen_offset value the FullscreenCalculator returns.
            """
            global slider_dragged
            handle_rect = pygame.Rect(self.handle_rect.x * fullscreen_scaling + fullscreen_offset[0], self.handle_rect.y * fullscreen_scaling + fullscreen_offset[1], self.handle_rect.width * fullscreen_scaling, self.handle_rect.height * fullscreen_scaling)
            slider_rect = pygame.Rect(self.slider_rect.x * fullscreen_scaling + fullscreen_offset[0], self.slider_rect.y * fullscreen_scaling + fullscreen_offset[1], self.slider_rect.width * fullscreen_scaling, self.slider_rect.height * fullscreen_scaling)

            if pygame.mouse.get_pressed()[0]:
                if handle_rect.colliderpoint(pygame.mouse.get_pos()):
                    slider_dragged = self
            else:
                slider_dragged = None

            if slider_dragged == self:
                handle_color = self.handle_pressed_color
                position = int(pygame.mouse.get_pos()[0])
                if position < slider_rect.midleft + (self.handle_move_area_padding[0] * fullscreen_scaling):
                    position = slider_rect.midleft + (self.handle_move_area_padding[0] * fullscreen_scaling)
                if position > slider_rect.midright - (self.handle_move_area_padding[1] * fullscreen_scaling):
                    position = slider_rect.midright - (self.handle_move_area_padding[1] * fullscreen_scaling)
                handle_rect.x = position
                KDS.ConfigManager.SetSetting("Settings", self.safe_name, str(position))
            elif handle_rect.colliderpoint(pygame.mouse.get_pos()):
                handle_color = self.handle_highlighted_color
            else:
                handle_color = self.handle_default_color

            pygame.draw.rect(surface, self.slider_color, slider_rect)
            pygame.draw.rect(surface, handle_color, handle_rect)
            return (position - slider_rect.midleft[0]) / (slider_rect.midright[0] - slider_rect.midleft[0])