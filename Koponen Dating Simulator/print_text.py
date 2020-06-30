
class pygame_print_text:

    def __init__(self, color, topleft, width, display):
        self.text_font = pygame.font.Font("COURIER.ttf", 30, bold=0, italic=0)
        self.display_to_blit = display
        self.color = tuple(color)
        self.topleft = tuple(topleft)
        self.width = width
    
    def print_text(self, text):
        self.screen_text = self.text_font.render(text, True, self.color)
        self.display_to_blit.blit(self.screen_text, self.topleft)