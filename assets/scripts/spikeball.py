from assets.scripts.core_funcs import *
class SpikeBall:
    def __init__(self, pos):
        if not web:
            self.spikeball = scale_image(pygame.image.load("assets\Spritesheets\spikeball.png").convert(), 4)
            self.spikeball.set_colorkey([236, 28, 36])
            self.spikeball_spikes = SpriteSheet(scale_image(pygame.image.load("assets\Spritesheets\spikeball_spikes.png").convert(), 4), [4, 1], [236, 28, 36])
        else:
            self.spikeball = scale_image(pygame.image.load("assets/Spritesheets/spikeball.png").convert(), 4)
            self.spikeball.set_colorkey([236, 28, 36])
            self.spikeball_spikes = SpriteSheet(scale_image(pygame.image.load("assets/Spritesheets/spikeball_spikes.png").convert(), 4), [4, 1], [236, 28, 36])
        self.spikeball_spikes.size = [50*4, 50*4]
        self.frame = [0, 0]
        self.angle = 0
        self.init_tile_pos = [int(pos[0]/64), int(pos[1]/64)]
        self.pos = [pos[0]+32, pos[1]+32]
        self.cur_img = self.spikeball_spikes.get(self.frame)
        self.time = time.time()
        self.standing = False
        self.just_spawned = True
        self.rect = self.cur_img.get_rect(topleft=self.pos)
    def spawn_animation(self, row):
        if self.just_spawned:
            self.frame[1] = row
            if time.time() - self.time >= 0.1:
                self.frame[0] += 1
                self.time = time.time()
            if self.frame[0] > 3:
                self.frame[0] = 3
                self.just_spawned = False
            self.cur_img = self.spikeball_spikes.get(self.frame)
    def update(self, renderer):
        self.rect = self.cur_img.get_rect(topleft=self.pos)
        if hasattr(renderer, "dt") and hasattr(renderer.queue[0], "mask") and self.rect.colliderect(renderer.camera.window_rect):
            if renderer.camera.bigger_window_rect.collidepoint(self.pos):
                self.angle -= 3*renderer.dt
                img = pygame.transform.rotate(self.spikeball, self.angle)
                self.mask_s = pygame.mask.from_surface(img)
                img_ = pygame.transform.rotate(self.cur_img, self.angle)
                self.mask = pygame.mask.from_surface(img_)
                if self.just_spawned:
                    self.spawn_animation(0)
                if hasattr(self, "mask"):
                    if self.mask.overlap(renderer.queue[0].mask, (renderer.queue[0].pos[0]-(self.pos[0]-(img_.get_width()/2)), renderer.queue[0].pos[1]-(self.pos[1]-(img_.get_height()/2)))) == None:
                        pass
                    else:
                        renderer.queue[0].is_alive = False
                        
                        #renderer.queue = [ob for ob in renderer.queue if ob != self]
                        #reset(renderer.queue[0], renderer)
                        renderer.queue[0].deaths += 1
                        #del self
                        #return
                    for e in renderer.queue:
                        if (e.__class__.__name__ == "EnemySwordsman" or e.__class__.__name__ == "EnemyWizard"):
                            if self.mask.overlap(e.mask, (e.pos[0]-(self.pos[0]-(img_.get_width()/2)), e.pos[1]-(self.pos[1]-(img_.get_height()/2)))) == None:
                                pass
                            else:
                                #print("collide")
                                e.is_alive = False
                                

                renderer.standing_masks.append([self.mask_s, [self.pos[0]-int(img.get_width()/2), self.pos[1]-int(img.get_height()/2)], self, self.init_tile_pos])
                win.blit(img, [self.pos[0]-int(img.get_width()/2), self.pos[1]-int(img.get_height()/2)])
                win.blit(img_, [self.pos[0]-int(img_.get_width()/2), self.pos[1]-int(img_.get_height()/2)])
