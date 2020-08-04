import KDS.ConfigManager
import pygame
import os

slider_dragged = None

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

        def __init__(self, safe_name, slider_rect, handle_size: (int, int), handle_move_area_padding=(0, 0), slider_color=(120, 120, 120), handle_default_color=(100, 100, 100), handle_highlighted_color=(90, 90, 90), handle_pressed_color=(80, 80, 80)):
            self.safe_name = safe_name
            self.slider_rect = slider_rect
            self.handle_rect = pygame.Rect(slider_rect.midleft[0] + (float(KDS.ConfigManager.LoadSetting("Settings", safe_name, "0")) * slider_rect.width) - (handle_size[0] / 2), 0, handle_size[0], handle_size[1])
            self.handle_move_area_padding = handle_move_area_padding
            self.slider_color = slider_color
            self.handle_default_color = handle_default_color
            self.handle_highlighted_color = handle_highlighted_color
            self.handle_pressed_color = handle_pressed_color

        def update(self, surface, fullscreen_scaling: int, fullscreen_offset: tuple):
            """
            1. surface: The surface this slider is going to be rendered.
            2. fullscreen_scaling: The fullscreen_scaling value the Fullscreen.Get.scaling command returns.
            3. fullscreen_offset: The fullscreen_offset value the Fullscreen.Get.offset returns.
            """

            global slider_dragged
            slider_rect = pygame.Rect(self.slider_rect.x * fullscreen_scaling + fullscreen_offset[0], self.slider_rect.y * fullscreen_scaling + fullscreen_offset[1], self.slider_rect.width * fullscreen_scaling, self.slider_rect.height * fullscreen_scaling)
            handle_rect = pygame.Rect(self.handle_rect.x * fullscreen_scaling + fullscreen_offset[0], (slider_rect.center[1] - (self.handle_rect.height / 2)) * fullscreen_scaling + fullscreen_offset[1], self.handle_rect.width * fullscreen_scaling, self.handle_rect.height * fullscreen_scaling)
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