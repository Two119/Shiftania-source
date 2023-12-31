from assets.scripts.core_funcs import *
class Crusher:
    def __init__(self, pos):
        self.tile_pos = [int(pos[0]/64), int(pos[1]/64)]
        if not web:
            img = scale_image(pygame.image.load("assets\Spritesheets\crusher.png").convert(), 4)
            swap_color(img, [87, 114, 119], [255, 255, 255])
            swap_color(img, [129, 151, 150], [195, 195, 195])
            swap_color(img, [168, 181, 178], [195, 195, 195])
            self.spritesheet = SpriteSheet(img, [12, 1])
            self.sound = pygame.mixer.Sound("assets\Audio\crusher.ogg")
        else:
            img = scale_image(pygame.image.load("assets/Spritesheets/crusher.png").convert(), 4)
            swap_color(img, [87, 114, 119], [255, 255, 255])
            swap_color(img, [129, 151, 150], [195, 195, 195])
            swap_color(img, [168, 181, 178], [195, 195, 195])
            self.spritesheet = SpriteSheet(img, [12, 1])
            self.sound = pygame.mixer.Sound("assets/Audio/crusher.ogg")
        self.dust_sheet = SpriteSheet(scale_image(pygame.image.load("assets/Spritesheets/dust_2.png").convert()), [8, 1], [255, 255, 255])
        self.dust_frame = 0
        self.dust_blowing = False
        self.spritesheet.size = [64*4, 64*4]
        self.frame = [0, 0]
        self.pos = [pos[0], pos[1]+4]
        self.rect = pygame.Rect(self.pos[0]+(16*4), self.pos[1], 32*4, 64*4)
        self.falling = False
        self.adder = 1
        self.cycles = 0
        self.time = time.time()
        self.dust_time = time.time()
    def update_animation(self, renderer):

        if time.time() - self.time >= 0.09:
            self.frame[0] += self.adder
            self.time = time.time()
        if self.frame[0] > 11:
            self.frame[0] = 11
            self.adder=-1
            renderer.coin_channel.play(self.sound)
        if self.frame[0] < 0:
            self.frame[0] = 0
            self.adder=1
            self.falling = False
        if self.frame[0] >= 10 and self.adder == 1:
            self.dust_blowing = True
            #self.dust_time = time.time()
        self.mask = pygame.mask.from_surface(self.spritesheet.get(self.frame))
    def update(self, renderer):
        self.cycles += 1
        if self.cycles == 1:
            for obj in renderer.queue:
                if obj.__class__.__name__ == "MovingPlatform":
                    if obj.rect.collidepoint(self.pos):
                        obj.objects.append(self)
        if hasattr(renderer.queue[0], "rect"):
            if renderer.camera.bigger_window_rect.collidepoint(self.pos):
                self.rect = pygame.Rect(self.pos[0]+(16*4), self.pos[1], 32*4, 64*4)
                if self.rect.colliderect(renderer.queue[0].rect):
                    self.falling = True
                for e in renderer.queue:
                    if (e.__class__.__name__ == "EnemySwordsman" or e.__class__.__name__ == "EnemyWizard") and hasattr(e, "rect"):
                        if self.rect.colliderect(e.rect):
                            self.falling = True
                if self.falling:
                    self.update_animation(renderer)
                if self.dust_blowing:
                    if time.time() - self.dust_time >= 0.1:
                        self.dust_frame += 1
                        self.dust_time = time.time()
                        if self.dust_frame > 6:
                            self.dust_frame = 0
                            self.dust_blowing = False
                            win.blit(self.spritesheet.get(self.frame), self.pos)
                            return
                    surf_ = self.dust_sheet.get([self.dust_frame, 0])
                    win.blit(surf_, [self.pos[0]-self.dust_sheet.size[0]+64, self.pos[1]+self.spritesheet.size[1]-self.dust_sheet.size[1]])
                    surf_ = pygame.transform.flip(self.dust_sheet.get([self.dust_frame, 0]), True, False)
                    win.blit(surf_, [self.pos[0]+64+128, self.pos[1]+self.spritesheet.size[1]-self.dust_sheet.size[1]])
                win.blit(self.spritesheet.get(self.frame), self.pos)