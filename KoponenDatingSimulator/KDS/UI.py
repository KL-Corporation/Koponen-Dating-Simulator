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
            self.handle_rect = pygame.Rect(self.slider_rect.midleft[0] + (float(KDS.ConfigManager.LoadSetting("Settings", safe_name, str(default_value))) * self.slider_rect.width) - (handle_size[0] / 2), slider_rect.centery - (handle_size[1] / 2), handle_size[0], handle_size[1])
            self.handle_move_area_padding = handle_move_area_padding
            self.slider_color = slider_color
            self.handle_default_color = handle_default_color
            self.handle_highlighted_color = handle_highlighted_color
            self.handle_pressed_color = handle_pressed_color

        def update(self, surface, mouse_pos):
            """
            1. surface: The surface this slider is going to be rendered.
            2. mouse_pos: The SCALED position of the mouse.
            """
            global slider_dragged

            if not pygame.mouse.get_pressed()[0]:
                slider_dragged = None
            elif slider_dragged == None:
                if self.handle_rect.collidepoint(mouse_pos):
                    slider_dragged = self.safe_name

            if slider_dragged == self.safe_name:
                handle_color = self.handle_pressed_color
                position = mouse_pos[0]
                if position < self.slider_rect.midleft[0] + self.handle_move_area_padding[0]:
                    position = self.slider_rect.midleft[0] + self.handle_move_area_padding[0]
                if position > self.slider_rect.midright[0] - self.handle_move_area_padding[1]:
                    position = self.slider_rect.midright[0] - self.handle_move_area_padding[1]
            else:
                position = self.handle_rect.centerx
                if self.handle_rect.collidepoint(mouse_pos) and slider_dragged == None:
                    handle_color = self.handle_highlighted_color
                else:
                    handle_color = self.handle_default_color
            self.handle_rect.centerx = position

            pygame.draw.rect(surface, self.slider_color, self.slider_rect)
            pygame.draw.rect(surface, handle_color, self.handle_rect)
            self.handle_rect = pygame.Rect(self.handle_rect.x, self.handle_rect.y, self.handle_rect.width, self.handle_rect.height)
            value = (self.handle_rect.centerx - self.slider_rect.midleft[0]) / (self.slider_rect.midright[0] - self.slider_rect.midleft[0] - self.handle_move_area_padding[0])
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
            
        def update(self, surface, mouse_pos: tuple, clicked, *args):
            """
            1. surface: The surface this button is going to be rendered.
            2. mouse_pos: The SCALED position of the mouse.
            3. clicked: A bool to determine if button's function should be executed.
            4. args: Any arguments for the button's function.
            """

            button_color = self.button_disabled_color
            if self.enabled:
                if self.rect.collidepoint(mouse_pos):
                    if clicked:
                        self.function(*args)
                    button_color = self.button_highlighted_color
                    if pygame.mouse.get_pressed()[0]:
                        button_color = self.button_pressed_color
                else:
                    button_color = self.button_default_color

            pygame.draw.rect(surface, button_color, self.rect)

            text_size_scaled = (self.text.get_width(), self.text.get_height())
            surface.blit(pygame.transform.scale(self.text, (int(text_size_scaled[0]), int(text_size_scaled[1]))), (int(self.rect.center[0] - (text_size_scaled[0] / 2)), int(self.rect.center[1] - (text_size_scaled[1] / 2))))

    class TrueFalseButton:

        def __init__(self, rect: pygame.Rect, current_state = False, button_default_color=(100,100,100), button_highlighted_color=(115,115,115), button_pressed_color=(90,90,90), button_disabled_color=(75,75,75), button_background_color=(150,150,150), enabled = True):
            self.rect = rect
            self.current_state = current_state
            self.enabled = enabled
            self.button_default_color = button_default_color
            self.button_highlighted_color = button_highlighted_color
            self.button_pressed_color = button_pressed_color
            self.button_disabled_color = button_disabled_color
            self.button_background_color = button_background_color
            self.bc_rect = pygame.Rect(rect.x, rect.y, rect.width*2, rect.height)

            if current_state:
                self.rect.x += self.rect.width

        def update(self, surface, mouse_pos: tuple, clicked, *args):
            """
            1. surface: The surface this button is going to be rendered.
            2. mouse_pos: The SCALED position of the mouse.
            3. clicked: A bool to determine if button's state should be flipped.
            """

            button_color = self.button_disabled_color
            if self.enabled:
                if self.bc_rect.collidepoint(mouse_pos):
                    if clicked:
                        if self.current_state:
                            self.rect.x -= self.rect.width
                        else:
                            self.rect.x += self.rect.width
                        self.current_state = not self.current_state
                    button_color = self.button_highlighted_color
                    if pygame.mouse.get_pressed()[0]:
                        button_color = self.button_pressed_color
                else:
                    button_color = self.button_default_color
            pygame.draw.rect(surface, self.button_background_color, self.bc_rect)
            pygame.draw.rect(surface, button_color, self.rect)
            return self.current_state