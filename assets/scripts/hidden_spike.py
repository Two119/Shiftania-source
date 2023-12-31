from assets.scripts.core_funcs import *
from assets.scripts.swinging_axe import *
from assets.scripts.firebox import *
class HiddenSpike:
    def __init__(self, spritesheet, sheet_size, pos, down=False, ang=0, shifted=False):
        self.spritesheet = SpriteSheet(pygame.transform.flip(scale_image(spritesheet, 4).convert(), False, down), sheet_size, [236, 28, 36])
        self.shifted = shifted
        self.enemies_destroyed = 0
        rect_surf = pygame.Surface(self.spritesheet.size)
        rect_surf.fill([0, 0, 0])
        rect_surf.set_colorkey([0, 0, 0])
        pygame.draw.rect(rect_surf, [255, 0, 0], pygame.Rect(0, self.spritesheet.size[1]-2, 64, 2))
        self.spritesheet.sheet[0].append(rect_surf)
        self.frame = [0, 0]
        self.orig_pos = [pos[0]*1, pos[1]*1]
        if ang==0:
            self.pos = pos
        else:
            if ang==-90:
                self.pos = [pos[0]+((16*ang)/-90)+((62*ang)/-90)-int(self.spritesheet.get(self.frame).get_width()/2), pos[1]+72-int(self.spritesheet.get(self.frame).get_height()/2)]
            else:
                self.pos = [pos[0]+((16*ang)/90)+((62*ang)/90)-int(self.spritesheet.get(self.frame).get_width()/2), pos[1]+72-int(self.spritesheet.get(self.frame).get_height()/2)]
        self.down = down
        self.ang = ang
        self.time = time.time()
        self.just_spawned = None
        self.rect_surf = pygame.Surface((64, 64))
        self.rect_surf.set_alpha(50)
        self.is_hovered = False
        self.played = False
        self.shiftable = True
        self.cycles = 0
        self.i = 0
        for img in self.spritesheet.sheet[0]:
            self.spritesheet.sheet[0][self.i] = pygame.transform.rotate(img, self.ang)
            self.i+=1
    def spawn_animation(self, row, renderer):
        if self.just_spawned:
            self.frame[1] = row
            
            if time.time() - self.time >= 0.08:
                self.frame[0] += 1
                self.time = time.time()
            if self.frame[0] > 3:
                self.frame[0] = 3
                self.just_spawned = False
        if not self.played:
                if not web:
                    renderer.coin_channel.play(pygame.mixer.Sound("assets\Audio\spike_spawn.ogg"))
                else:
                    renderer.coin_channel.play(pygame.mixer.Sound("assets/Audio/spike_spawn.ogg"))
        self.played = True
        self.mask = pygame.mask.from_surface(self.spritesheet.get(self.frame))
    def update(self, renderer):
        self.cycles += 1
        if self.cycles == 1:
            for obj in renderer.queue:
                if obj.__class__.__name__ == "MovingPlatform":
                    if self.ang != -90:
                        if obj.rect.collidepoint(self.pos):
                            obj.objects.append(self)
                            if renderer.cur_cycle == 0:
                                if self.ang == 90:
                                    self.pos[0]+=22
                                    self.pos[1]-=4
                                if self.down:
                                    self.pos[0]-=32
                                    self.pos[1]+=4
                                if self.ang == 0 and not self.down:
                                    self.pos[0]+=36
                            else:
                                if self.down:
                                    self.pos[0]-=64
                                    self.pos[1]+=4
                                if self.ang == 90:
                                    self.pos[0]-=8
                                    self.pos[1]-=4
                    else:
                        if obj.rect.collidepoint(self.pos):
                            obj.objects.append(self)
                            if renderer.cur_cycle == 0:
                                self.pos[0]+=26
                            else:
                                self.pos[0]-=4
                                self.pos[1]-=4
        if hasattr(renderer, "dt") and hasattr(renderer.queue[0], "rect"):
            if renderer.camera.bigger_window_rect.collidepoint(self.pos):    
                self.rect = self.spritesheet.get(self.frame).get_rect(topleft=self.pos)
                self.rect.x += 10
                self.rect.width -= 10
                if self.ang == 90 or self.ang == -90:
                    self.rect.y -= 28
                    if self.ang == 90:
                        self.rect.x -= 38
                    else:
                        self.rect.x -= 44
                #pygame.draw.rect(win, [0, 255, 0], self.rect)
                if self.rect.colliderect(renderer.camera.window_rect):
                    if self.rect.colliderect(renderer.queue[0].rect) and self.just_spawned == None:
                        self.just_spawned = True
                    if self.just_spawned == None:
                        for enemy in renderer.enemies:
                            e = renderer.queue[enemy]
                            if (e.__class__.__name__ == "EnemySwordsman" or e.__class__.__name__ == "EnemyWizard") and hasattr(e, "rect"):
                                if self.rect.colliderect(e.rect):
                                    self.just_spawned = True
                    if not self.just_spawned == None:
                        if self.just_spawned:
                            self.spawn_animation(0, renderer)
                    else:
                        if self.ang == 0 and not self.down:
                            win.blit(self.spritesheet.get([4, 0]), [self.pos[0]+4, self.pos[1]])
                        if self.down:
                            win.blit(self.spritesheet.get([4, 0]), [self.pos[0]+4, self.pos[1]-72])
                        if self.ang == 90:
                            win.blit(self.spritesheet.get([4, 0]), [self.pos[0]-int(self.spritesheet.get(self.frame).get_width()/2), self.pos[1]+4-int(self.spritesheet.get(self.frame).get_height()/2)])
                        if self.ang == -90:
                            win.blit(self.spritesheet.get([4, 0]), [self.pos[0]-int(self.spritesheet.get(self.frame).get_width()/2), self.pos[1]+8-int(self.spritesheet.get(self.frame).get_height()/2)])
                            
                    if hasattr(self, "mask") and hasattr(renderer.queue[0], "mask"):
                        if self.ang == 0:
                            if self.mask.overlap(renderer.queue[0].mask, (renderer.queue[0].pos[0]-self.pos[0], renderer.queue[0].pos[1]-self.pos[1])) == None:
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
                                    if self.mask.overlap(e.mask, (e.pos[0]-self.pos[0], e.pos[1]-self.pos[1])) == None:
                                        pass
                                    else:
                                        e.is_alive = False
                                        self.enemies_destroyed+=1
                                        #renderer.queue = [ob for ob in renderer.queue if ob != self]
                                        #del self
                                        #return
                                if self.shifted and self.enemies_destroyed > 1:
                                    renderer.queue = [ob for ob in renderer.queue if ob != self]
                                    renderer.levels[renderer.level][int((self.pos[1]-28)/renderer.tile_size[1])+(0-int(renderer.init_render_pos[renderer.level][1]))][int(((self.pos[0]-32)-renderer.camera.cam_change[0])/renderer.tile_size[0])+4] = -1
                                    return
                        else:
                            if self.mask.overlap(renderer.queue[0].mask, (renderer.queue[0].pos[0]-(self.pos[0]-int(self.spritesheet.get(self.frame).get_width()/2)), renderer.queue[0].pos[1]-(self.pos[1]-int(self.spritesheet.get(self.frame).get_height()/2)))) == None:
                                pass
                            else:
                                renderer.queue[0].is_alive = False
                                
                                #renderer.queue = [ob for ob in renderer.queue if ob != self]
                                #reset(renderer.queue[0], renderer)
                                renderer.queue[0].deaths += 1
                                #del self
                                #return
                            for enemy in renderer.enemies:
                                e = renderer.queue[enemy]
                                if (e.__class__.__name__ == "EnemySwordsman" or e.__class__.__name__ == "EnemyWizard"):
                                    if self.mask.overlap(e.mask, (e.pos[0]-(self.pos[0]-int(self.spritesheet.get(self.frame).get_width()/2)), e.pos[1]-(self.pos[1]-int(self.spritesheet.get(self.frame).get_height()/2)))) == None:
                                        pass
                                    else:
                                        e.is_alive = False
                                        self.enemies_destroyed+=1
                                if self.shifted and self.enemies_destroyed > 1:
                                    renderer.queue = [ob for ob in renderer.queue if ob != self]
                                    renderer.levels[renderer.level][int((self.pos[1]-28)/renderer.tile_size[1])+(0-int(renderer.init_render_pos[renderer.level][1]))][int(((self.pos[0]-32)-renderer.camera.cam_change[0])/renderer.tile_size[0])+4] = -1
                                    return
                    if not self.just_spawned == None:
                        if self.ang == 0:
                            win.blit(self.spritesheet.get(self.frame), self.pos)
                        else:
                            win.blit(self.spritesheet.get(self.frame), [self.pos[0]-int(self.spritesheet.get(self.frame).get_width()/2), self.pos[1]-int(self.spritesheet.get(self.frame).get_height()/2)])
                    if not self.shiftable:
                        self.is_hovered = False
                    
                    if self.is_hovered and not(self.just_spawned):
                        if not self.ang == 0:
                            if self.ang == 90:
                                if pygame.mouse.get_pressed()[2] and renderer.queue[0].tile not in [117, 129, 138, 139, 118, 135, 136, 137, 116, 121]:
                                    renderer.queue[0].shapeshifts -= 1
                                    
                                    renderer.levels[renderer.level][int((self.pos[1]-28)/renderer.tile_size[1])+(0-int(renderer.init_render_pos[renderer.level][1]))][int(((self.pos[0]-32)-renderer.camera.cam_change[0])/renderer.tile_size[0])+4] = renderer.queue[0].tile
                                    renderer.queue = [ob for ob in renderer.queue if ob != self]
                                    renderer.queue[0].shapeshifting=False
                                    renderer.queue_updating = True
                                    return
                                    
                                pygame.draw.rect(self.rect_surf, (255, 0, 0), pygame.Rect(0, 0, 64, 64))
                                win.blit(self.rect_surf, [self.pos[0]-32, self.pos[1]-28])
                            else:
                                if pygame.mouse.get_pressed()[2] and renderer.queue[0].tile not in [117, 129, 138, 139, 118, 135, 136, 137, 116, 121]:
                                    renderer.queue[0].shapeshifts -= 1
                                    
                                    renderer.levels[renderer.level][int((self.pos[1]-28)/renderer.tile_size[1])+(0-int(renderer.init_render_pos[renderer.level][1]))][int(((self.pos[0]-36)-renderer.camera.cam_change[0])/renderer.tile_size[0])+4] = renderer.queue[0].tile
                                    renderer.queue = [ob for ob in renderer.queue if ob != self]
                                    renderer.queue[0].shapeshifting=False
                                    renderer.queue_updating = True
                                    return
                                pygame.draw.rect(self.rect_surf, (255, 0, 0), pygame.Rect(0, 0, 64, 64))
                                win.blit(self.rect_surf, [self.pos[0]-36, self.pos[1]-28])
                        else:
                            if pygame.mouse.get_pressed()[2] and renderer.queue[0].tile not in [117, 129, 138, 139, 118, 135, 136, 137, 116, 121]:
                                renderer.queue[0].shapeshifts -= 1
                                
                                renderer.levels[renderer.level][int((self.pos[1]+4)/renderer.tile_size[1])+(0-int(renderer.init_render_pos[renderer.level][1]))][int(((self.pos[0]+8)-renderer.camera.cam_change[0])/renderer.tile_size[0])+4] = renderer.queue[0].tile
                                renderer.queue = [ob for ob in renderer.queue if ob != self]
                                renderer.queue[0].shapeshifting=False
                                renderer.queue_updating = True
                                return
                            pygame.draw.rect(self.rect_surf, (255, 0, 0), pygame.Rect(0, 0, 64, 64))
                            win.blit(self.rect_surf, [self.pos[0]+8, self.pos[1]+8])
                    
                    