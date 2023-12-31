from assets.scripts.core_funcs import *
class Button():
    def __init__(self, position, textures, function, screen):
        self.textures = textures;
        self.onlick = function[0];
        self.args = function[1];
        self.pos = position;
        self.screen = screen;
        self.current = 0;
        self.rect = self.textures[self.current].get_rect(topleft=self.pos);
        self.click_delay = 0;
        self.max_delay = 500;
        self.delaying = False;
        self.clicked = False
    def update(self, renderer):
        self.current = 0;
        if self.delaying:
            self.click_delay += 1;
        if self.click_delay >= self.max_delay:
            self.delaying = False;
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            if pygame.mouse.get_pressed()[0]:
                if not self.delaying and not self.clicked:
                    self.onlick(self.args);
                    renderer.coin_channel.play(button_sound)
                    self.clicked = True
            else:
                self.clicked = False
            self.current = 1;
        self.screen.blit(self.textures[self.current], self.pos);
        self.rect = self.textures[self.current].get_rect(topleft=self.pos);