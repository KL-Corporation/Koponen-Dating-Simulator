from shutil import move
from turtle import position
from typing import Callable, Tuple
import KDS.Animator
import KDS.ConfigManager
import KDS.Convert
import KDS.Math
import pygame
from pygame.locals import *
import os

slider_dragged = None

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

    def __init__(self, safe_name: str, slider_rect: pygame.Rect, handle_size: Tuple[int, int], default_value: float = 0.0, handle_move_area_padding: Tuple[int, int] = (0, 0), slider_default_color: Tuple[int, int, int] = (120, 120, 120), slider_fill_color: Tuple[int, int, int] = (0, 120, 0), handle_default_color: Tuple[int, int, int] = (100, 100, 100), handle_highlighted_color: Tuple[int, int, int] = (115, 115, 115), handle_pressed_color: Tuple[int, int, int] = (90, 90, 90), lerp_duration: int = 3, custom_dir: str = None, custom_safename: str = None):
        self.safe_name = safe_name
        self.slider_rect = slider_rect
        self.handle_rect = pygame.Rect(self.slider_rect.midleft[0] + (float(KDS.ConfigManager.GetSetting("Sliders", safe_name, str(default_value))) * self.slider_rect.width) - (handle_size[0] / 2), slider_rect.centery - (handle_size[1] / 2), handle_size[0], handle_size[1])
        self.handle_move_area_padding = handle_move_area_padding
        self.slider_default_color = slider_default_color
        self.slider_fill_color = slider_fill_color
        self.handle_default_color = handle_default_color
        self.handle_highlighted_color = handle_highlighted_color
        self.handle_pressed_color = handle_pressed_color
        self.handle_old_color = handle_default_color
        self.handle_color_fade = KDS.Animator.Float(0.0, 1.0, lerp_duration, KDS.Animator.AnimationType.Linear, KDS.Animator.OnAnimationEnd.Loop)
        if custom_dir != None:
            if custom_safename != None:
                self.custom_path = (custom_dir, custom_safename)
            else:
                self.custom_path = (custom_dir, safe_name)
        elif custom_safename != None:
            self.custom_path = ("Sliders", custom_safename)
        else:
            self.custom_path = None

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

        if handle_color != self.handle_old_color:
            fade = self.handle_color_fade.update()
            if fade == 1.0:
                handle_draw_color = handle_color
                self.handle_old_color = handle_color
            else:
                handle_draw_color = (KDS.Math.Lerp(self.handle_old_color[0], handle_color[0], fade), KDS.Math.Lerp(self.handle_old_color[1], handle_color[1], fade), KDS.Math.Lerp(self.handle_old_color[2], handle_color[2], fade))
        else:
            handle_draw_color = handle_color
        pygame.draw.rect(surface, self.slider_default_color, self.slider_rect)
        pygame.draw.rect(surface, self.slider_fill_color, pygame.Rect(self.slider_rect.x, self.slider_rect.y, self.handle_rect.centerx - self.slider_rect.x, self.slider_rect.height))
        pygame.draw.rect(surface, handle_draw_color, self.handle_rect)
        value = (self.handle_rect.centerx - self.slider_rect.midleft[0]) / (self.slider_rect.midright[0] - self.slider_rect.midleft[0] - self.handle_move_area_padding[0])
        KDS.ConfigManager.SetSetting("Sliders", self.safe_name, value)
        if self.custom_path != None:
            KDS.ConfigManager.SetSetting(self.custom_path[0], self.custom_path[1], value)
        return value

class Button:

    def __init__(self, rect: pygame.Rect, function, overlay: pygame.Surface = None, button_default_color: Tuple[int, int, int] = (100, 100, 100), button_highlighted_color: Tuple[int, int, int] = (115, 115, 115), button_pressed_color: Tuple[int, int, int] = (90, 90, 90), button_disabled_color: Tuple[int, int, int] = (75, 75, 75), lerp_duration: int = 3, enabled: bool = True, *args):
        """Instantiates a new Button

        Args:
            rect (Rect): The rect where the button will be drawn.
            function (Callable): A function to be called when the button is pressed.
            overlay (Surface, optional): Any surface you want to write on top of the button. Defaults to None.
            button_default_color (Tuple[int, int, int], optional): The color of the button by default. Defaults to (100, 100, 100).
            button_highlighted_color (Tuple[int, int, int], optional): The color of the button when highlighted. Defaults to (115, 115, 115).
            button_pressed_color (Tuple[int, int, int], optional): The color of the button when pressed. Defaults to (90, 90, 90).
            button_disabled_color (Tuple[int, int, int], optional): The color of the button when disabled. Defaults to (75, 75, 75).
            lerp_duration (int, optional): The duration it takes to switch from one color to another. Defaults to 3.
            enabled (bool, optional): Determines if the button is enabled or disabled from the start. Defaults to True.
        """
        self.rect = rect
        self.function = function
        self.overlay = overlay
        self.button_default_color = button_default_color
        self.button_highlighted_color = button_highlighted_color
        self.button_pressed_color = button_pressed_color
        self.button_disabled_color = button_disabled_color
        self.button_old_color = button_default_color if enabled else button_disabled_color
        self.button_color_fade = KDS.Animator.Float(0.0, 1.0, lerp_duration, KDS.Animator.AnimationType.Linear, KDS.Animator.OnAnimationEnd.Loop)
        self.enabled = enabled
        
    def update(self, surface: pygame.Surface, mouse_pos: Tuple[int, int], clicked: bool, *args):
        """Updates and draws the button onto a surface.

        Args:
            surface (Surface): The surface the button will be drawn onto.
            mouse_pos (Tuple[int, int]): The SCALED position of the mouse.
            clicked (bool): Determines if the button's function should be executed.
            args (any): Any arguments for the button's function.
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
        if button_color != self.button_old_color:
            fade = self.button_color_fade.update()
            if fade == 1.0:
                draw_color = button_color
                self.button_old_color = button_color
            else:
                draw_color = (KDS.Math.Lerp(self.button_old_color[0], button_color[0], fade), KDS.Math.Lerp(self.button_old_color[1], button_color[1], fade), KDS.Math.Lerp(self.button_old_color[2], button_color[2], fade))
        else:
            draw_color = button_color
        pygame.draw.rect(surface, draw_color, self.rect)

        if self.overlay != None:
            surface.blit(self.overlay, (int(self.rect.center[0] - (self.overlay.get_width() / 2)), int(self.rect.center[1] - (self.overlay.get_height() / 2))))

class Switch:
    """
    1. safe_name: An identifier that does not conflict with ANY other safe_names. (Slider value will be saved at "Settings", "safe_name")
    2. switch_rect: The pygame.Rect of the slider.
    3. handle_size: Width and height of the handle.
    4. handle_move_area_padding (OPTIONAL): Reduce the left and right move area of the handle. [DEFAULT: (0, 0)]
    5. slider_color (OPTIONAL): The color of the slider background. [DEFAULT: (120, 120, 120)]
    6. handle_default_color (OPTIONAL): The color of the handle in idle state. [DEFAULT: (115, 115, 115)]
    7. handle_highlighted_color (OPTIONAL): The color of the handle in idle state. [DEFAULT: (100, 100, 100)]
    8. handle_pressed_color (OPTIONAL): The color of the handle in idle state. [DEFAULT: (90, 90, 90)]
    """

    def __init__(self, safe_name, switch_rect: pygame.Rect, handle_size: Tuple[int, int], default_value: bool = False, switch_move_area_padding: Tuple[int, int] = (0, 0), switch_off_color: Tuple[int, int, int] = (120, 120, 120), switch_on_color: Tuple[int, int, int] = (0, 120, 0), handle_default_color: Tuple[int, int, int] = (100, 100, 100), handle_highlighted_color: Tuple[int, int, int] = (115, 115, 115), handle_pressed_color: Tuple[int, int, int] = (90, 90, 90), fade_lerp_duration: int = 3, move_lerp_duration: int = 15, custom_dir: str = None, custom_safename: str = None):
        self.safe_name = safe_name
        self.switch_rect = switch_rect
        self.state = KDS.Convert.ToBool(KDS.ConfigManager.GetSetting("Switches", safe_name, str(default_value)))
        self.range = (switch_rect.left + switch_move_area_padding[0] - (handle_size[0] / 2), switch_rect.right + switch_move_area_padding[1] - (handle_size[0] / 2))
        self.switch_move_area_padding = switch_move_area_padding
        self.switch_off_color = switch_off_color
        self.switch_on_color = switch_on_color
        self.handle_default_color = handle_default_color
        self.handle_highlighted_color = handle_highlighted_color
        self.handle_pressed_color = handle_pressed_color
        self.handle_old_color = handle_default_color
        self.handle_color_fade = KDS.Animator.Float(0.0, 1.0, fade_lerp_duration, KDS.Animator.AnimationType.Linear, KDS.Animator.OnAnimationEnd.Loop)
        self.handle_move_animation = KDS.Animator.Float(0.0, 1.0, move_lerp_duration, KDS.Animator.AnimationType.Linear, KDS.Animator.OnAnimationEnd.Stop)
        if custom_dir != None:
            if custom_safename != None:
                self.custom_path = (custom_dir, custom_safename)
            else:
                self.custom_path = (custom_dir, safe_name)
        elif custom_safename != None:
            self.custom_path = ("Switches", custom_safename)
        else:
            self.custom_path = None
        if self.state:
            self.handle_rect = pygame.Rect(self.range[0], switch_rect.centery - handle_size[1] / 2, int(handle_size[0]), int(handle_size[1]))
            #self.handle_move_animation.(move_lerp_duration)
        else:
            self.handle_rect = pygame.Rect(self.range[1], switch_rect.centery - handle_size[1] / 2, int(handle_size[0]), int(handle_size[1]))
            #self.handle_move_animation._set(0)

    def update(self, surface, mouse_pos, clicked):
        """
        1. surface: The surface this slider is going to be rendered.
        2. mouse_pos: The SCALED position of the mouse.
        """
        if self.switch_rect.collidepoint(mouse_pos) or self.handle_rect.collidepoint(mouse_pos):
            handle_color = self.handle_highlighted_color
            if clicked:
                self.state = not self.state
            if pygame.mouse.get_pressed()[0]:
                handle_color = self.handle_pressed_color
        else:
            handle_color = self.handle_default_color
            
        if handle_color != self.handle_old_color:
            fade = self.handle_color_fade.update()
            if fade == 1.0:
                handle_draw_color = handle_color
                self.handle_old_color = handle_color
            else:
                handle_draw_color = (KDS.Math.Lerp(self.handle_old_color[0], handle_color[0], fade), KDS.Math.Lerp(self.handle_old_color[1], handle_color[1], fade), KDS.Math.Lerp(self.handle_old_color[2], handle_color[2], fade))
        else:
            handle_draw_color = handle_color
        if self.state:
            handle_move = self.handle_move_animation.update(False)
            self.handle_rect.x = KDS.Math.Lerp(self.range[0], self.range[1], handle_move)
        else:
            handle_move = self.handle_move_animation.update(True)
            self.handle_rect.x = KDS.Math.Lerp(self.range[0], self.range[1], handle_move)
        switch_color = (KDS.Math.Lerp(self.switch_off_color[0], self.switch_on_color[0], handle_move), KDS.Math.Lerp(self.switch_off_color[1], self.switch_on_color[1], handle_move), KDS.Math.Lerp(self.switch_off_color[2], self.switch_on_color[2], handle_move))
        pygame.draw.rect(surface, switch_color, self.switch_rect)
        pygame.draw.rect(surface, handle_draw_color, self.handle_rect)
        KDS.ConfigManager.SetSetting("Switches", self.safe_name, self.state)
        if self.custom_path != None:
            KDS.ConfigManager.SetSetting(self.custom_path[0], self.custom_path[1], self.state)
        return self.state