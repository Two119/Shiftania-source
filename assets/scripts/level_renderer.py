from assets.scripts.core_funcs import *
from assets.scripts.coin import *
from assets.scripts.crusher import *
from assets.scripts.hidden_spike import *
from assets.scripts.spikeball import *
from assets.scripts.button import *
from assets.scripts.moving_platform import *
from assets.scripts.swinging_axe import *
from assets.scripts.firebox import *
from assets.scripts.falling_block import *
from assets.scripts.enemy import *
from assets.scripts.shop import *
from assets.scripts.bullet_manager import *
from assets.scripts.psycho import *
from assets.scripts.jumper import *
class CheckPoint:
    def __init__(self, position:tuple, type_of:int):
        self.type_of = type_of
        self.orig_pos = [position[0]*1, position[1]*1]
        self.pos = [position[0]-60, position[1]-60]
        self.rect = pygame.Rect(self.pos[0], self.pos[1], 64, 128)
        t_d = {1:1, -1:0}
        self.tex = SpriteSheet(scale_image(pygame.image.load("assets/Spritesheets/doors.png").convert()), [2, 1], [255, 255, 255]).get([t_d[type_of], 0]).copy()
    def update(self, renderer):
        self.rect = pygame.Rect(self.pos[0]+64, self.pos[1]+64, 64, 128)
        if hasattr(renderer.queue[0], "rect"):
            if self.rect.colliderect(renderer.queue[0].rect):
                if pygame.key.get_pressed()[pygame.K_TAB] and renderer.level + self.type_of >= 0:
                    renderer.queue[0].is_alive = False
                    renderer.level += self.type_of
                    renderer.queue[0].t = True
                    if self.type_of == -1:
                        renderer.queue[0].on_door = True
                    if not renderer.level in renderer.queue[0].levels_unlocked:
                        renderer.queue[0].levels_unlocked.append(renderer.level)
        win.blit(self.tex, self.pos)
        #pygame.draw.rect(win, [255, 0, 0], self.rect)
        #print(self.pos)
class StaffIcon:
    def __init__(self, staff, pos):
        self.staff = staff
        self.pos = pos
        self.scale = 1
        self.adder = 1
    def update(self, renderer):
        if self.adder == 1:
            self.scale += 0.006*renderer.dt
        else:
            self.scale -= 0.006*renderer.dt
        if self.scale > 1.1:
            self.adder = -1
        if self.scale < 0.9:
            self.adder = 1
        s = pygame.transform.scale_by(self.staff, self.scale)
        win.blit(s, [self.pos[0]-(s.get_width()-self.staff.get_width()), self.pos[1]-(s.get_height()-self.staff.get_height())])
        self.mask = pygame.mask.from_surface(s)
        if hasattr(renderer.queue[0], "mask"):
            if renderer.queue[0].mask.overlap(self.mask, [self.pos[0]-renderer.queue[0].pos[0], self.pos[1]-renderer.queue[0].pos[1]]):
                renderer.queue[0].has_staff = True
                renderer.queue.remove(self)
                particle_sheet = SpriteSheet(self.staff, [self.staff.get_width()//4, self.staff.get_height()//4], [0, 0, 0])
                for j, sheet in enumerate(particle_sheet.sheet):
                    for i, surf in enumerate(sheet):
                        if not isequal(surf.get_at([0, 0]), [0, 0, 0]):
                            renderer.queue.append(DeathParticle(surf, [self.pos[0]+(i*4), self.pos[1]+(j*4)], renderer, [0, 0, 0]))
                del self
class LevelRenderer:
    def __init__(self, levels : tuple, tilesheet : pygame.Surface, tilesheet_size : tuple, spike_images : tuple, colors : tuple, background : pygame.Surface, coin_image):
        final_color = [30, 30, 30]
        self.playing = True
        swap_color(background, [255, 255, 255], final_color)
        swap_color(background, [0, 0, 0], final_color)
        tilesheet.set_colorkey([255, 255, 255])
        self.spikes = []
        self.rects = []
        self.shop = None
        self.font = None
        self.delay = 0
        self.just_spike_notified = False
        if not web:
            self.spike_image = pygame.image.load("assets\Spritesheets\spikes.png").convert()
            self.button_sprites = SpriteSheet(scale_image(pygame.image.load("assets\Spritesheets\\buttons.png").convert()), [2, 1], [255, 255, 255])
        else:
            self.spike_image = pygame.image.load("assets/Spritesheets/spikes.png").convert()
            self.button_sprites = SpriteSheet(scale_image(pygame.image.load("assets/Spritesheets/buttons.png").convert()), [2, 1], [255, 255, 255])
        self.hit_sfx = pygame.mixer.Sound("assets/Audio/hit.ogg")
        self.swoosh_sfx = pygame.mixer.Sound("assets/Audio/swoosh.ogg")
        self.axe_swoosh_sfx = pygame.mixer.Sound("assets/Audio/axe_swoosh.ogg")
        self.spikesheet = SpriteSheet(scale_image(self.spike_image, 4).convert(), [4, 1], [236, 28, 36])
        self.attr_dict = {"pos":0, "delay":1, "just_spawned":2, "rect_surf":3, "is_hovered":4, "played":5}
        self.frame = [0, 0]
        self.button = None
        #spike[self.attr_dict["pos"]] = pos
        #self.delay = 0
        self.fire_time = time.time()
        self.def_frame = 60
        self.enemies = []
        self.notifications = []
        self.surf = pygame.Surface(win_size)
        pygame.draw.rect(self.surf, (0, 0, 0), pygame.Rect(0, 0, win_size[0], win_size[1]))
        self.surf.set_alpha(50)
        #self.just_spawned = True
        self.played = False
        self.rect_surf = pygame.Surface((64, 64))
        self.rect_surf.set_alpha(75)
        pygame.draw.rect(self.rect_surf, (255, 0, 0), pygame.Rect(0, 0, 64, 64))
        self.levels = levels
        self.level = 0
        self.coin_img = coin_image.convert()
        self.changed = []
        self.background = scale_image(background, win_size[0]/background.get_width())
        self.background.convert()
        self.colorkeys = colors
        self.tilesheet = SpriteSheet(tilesheet, tilesheet_size)
        self.images = []
        self.tilesheet_size = tilesheet_size
        for i in range(self.tilesheet_size[1]):
            for j in range(self.tilesheet_size[0]):
                img = scale_image(self.tilesheet.get([j, i]), 4)
                for color in self.colorkeys:
                    pygame.transform.threshold(img,img, color, (10, 10 ,10), (0, 0, 0), 1, None, True)
                img.set_colorkey((0, 0, 0))
                img.convert()
                self.images.append(img)
        self.spike_images = spike_images
        self.damage_masks = []
        self.standing_masks = []
        self.side_rects = []
        self.enemies = []
        self.special_blocks = []
        self.axe_channel = pygame.mixer.Channel(1)
        self.swoosh_channel = pygame.mixer.Channel(2)
        self.thwack_channel = pygame.mixer.Channel(3)
        self.firebox_channel = pygame.mixer.Channel(4)
        self.coin_channel = pygame.mixer.Channel(5)
        
        self.coin_channel.set_volume(0.5)
        self.thwack_channel.set_volume(0.5)
        self.swoosh_channel.set_volume(0.5)
        self.axe_channel.set_volume(0.5)
        self.tile_size = [64, 64]
        self.init_render_pos = [[-1, -9.2], [-1, -12.2]]
        self.firebox_frame = 0
        self.x = self.init_render_pos[self.level][0]
        self.y = self.init_render_pos[self.level][1]
        self.queue = []
        self.decorative_tiles = [74, 75, 76, 87, 89, 100, 101, 102, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 104, 105, 106, 107, 108, 109, 110, 112, 113, 114, 123, 124, 125, 126, 127]
        self.changed = []
        self.deleted = []
        self.player_death_limit = [1500, 7000, 7000, 7000, 7000]
        self.first_tile_pos = []
        self.queue_updating = True
        self.first_cycle = True
        self.clock = pygame.time.Clock()
        self.death_anims = []
        self.first_layer = []
        self.coin_appending = True
        self.level_firebox_y_offset_dict = {0:0, 1:4, 2:4, 3:4, 4:4}
        self.added_coins = 0
        self.added_spikes = 0
        self.added_spikes_h = 0
        self.firebox_in_cam = False
        self.camera = None
        self.exceptions = [32, 33, 60, 88, 111, 116, 117, 118, 119, 120, 121, 122, 129, 135, 136, 137, 138, 139, 140, 141, 142, 103]
        self.ground = ["SpikeBall", "MovingPlatform", "FireBox", "FallingBlock", "Jumper"]
        self.bullet_manager = BulletManager(self)
        self.cycles = 0 
        self.cur_cycle = -1
    def spawn_animation(self, delay_wait, spike):
        renderer = self
        if (renderer.clock.get_fps()) != 0 and spike[self.attr_dict["just_spawned"]]:
                #spike[self.attr_dict["delay"]] += 1
                if time.time() - spike[self.attr_dict["delay"]] >= 0.08:
                        self.frame[0] += 1
                        spike[self.attr_dict["delay"]] = time.time()
                if self.frame[0] > 3:
                    self.frame[0] = 3
                    spike[self.attr_dict["just_spawned"]] = False
                self.mask = pygame.mask.from_surface(self.spikesheet.get(self.frame))
                self.mask_2 = pygame.mask.from_surface(pygame.transform.flip(self.spikesheet.get(self.frame), False, spike[6]))
                self.mask_3 = pygame.mask.from_surface(pygame.transform.rotate(self.spikesheet.get(self.frame), 90))
                self.mask_4 = pygame.mask.from_surface(pygame.transform.rotate(self.spikesheet.get(self.frame), -90))
                
    def spike_update(self):
        renderer = self
        self.cycles += 1
        for spike in self.spikes:
            if self.cycles == 1:
                for obj in self.queue:
                    if obj.__class__.__name__ == "MovingPlatform":
                        if spike[len(spike)-2] != -90:
                            if obj.rect.collidepoint(spike[self.attr_dict["pos"]]):
                                obj.spikes.append(spike)
                                if self.cur_cycle == 0:
                                    if spike[len(spike)-3] and spike[len(spike)-2]==0:
                                        spike[self.attr_dict["pos"]][0]-=32
                                    if spike[len(spike)-2]==90:
                                        spike[self.attr_dict["pos"]][0]+=36
                                    if spike[len(spike)-2]==0 and not spike[len(spike)-3] :
                                        spike[self.attr_dict["pos"]][0]+=32
                                else:
                                    if spike[len(spike)-3] and spike[len(spike)-2]==0:
                                        spike[self.attr_dict["pos"]][0]-=64
                        else:
                            if obj.rect.collidepoint(spike[self.attr_dict["pos"]]):
                                obj.spikes.append(spike)
                                if self.cur_cycle == 0:
                                    spike[self.attr_dict["pos"]][0]+=32             
        if hasattr(renderer, "dt"):
            for spike in self.spikes:
                
                if spike[self.attr_dict["just_spawned"]]:
                    self.spawn_animation(4, spike)
                if spike[7]==0:
                    win.blit(pygame.transform.flip(self.spikesheet.get(self.frame), False, spike[6]), spike[self.attr_dict["pos"]])
                else:
                    win.blit(pygame.transform.rotate(self.spikesheet.get(self.frame), spike[7]), spike[self.attr_dict["pos"]])
                mouse_pos = pygame.mouse.get_pos()
                if hasattr(self, "mask") and hasattr(self.queue[0], "mask"):
                    if spike[7]==0:
                        if not spike[6]:
                            if (cursor_mask.overlap(self.mask, (spike[self.attr_dict["pos"]][0]-mouse_pos[0], spike[self.attr_dict["pos"]][1]-mouse_pos[1])) == None):
                                spike[self.attr_dict["is_hovered"]] = False
                            else:
                                if len(spike) != 10:
                                    if not renderer.queue_updating:
                                        spike[self.attr_dict["is_hovered"]] = True
                                    else:
                                        spike[self.attr_dict["is_hovered"]] = False
                        else:
                            if (cursor_mask.overlap(self.mask_2, (spike[self.attr_dict["pos"]][0]-mouse_pos[0], spike[self.attr_dict["pos"]][1]-mouse_pos[1])) == None):
                                spike[self.attr_dict["is_hovered"]] = False
                            else:
                                if len(spike) != 10:
                                    if not renderer.queue_updating:
                                        spike[self.attr_dict["is_hovered"]] = True
                                    else:
                                        spike[self.attr_dict["is_hovered"]] = False
                    else:
                        if spike[7]==90:
                            if (cursor_mask.overlap(self.mask_3, (spike[self.attr_dict["pos"]][0]-mouse_pos[0], spike[self.attr_dict["pos"]][1]-mouse_pos[1])) == None):
                                spike[self.attr_dict["is_hovered"]] = False
                            else:
                                if len(spike) != 10:
                                    if not renderer.queue_updating:
                                        spike[self.attr_dict["is_hovered"]] = True
                                    else:
                                        spike[self.attr_dict["is_hovered"]] = False
                        else:
                            if (cursor_mask.overlap(self.mask_4, (spike[self.attr_dict["pos"]][0]-mouse_pos[0], spike[self.attr_dict["pos"]][1]-mouse_pos[1])) == None):
                                spike[self.attr_dict["is_hovered"]] = False
                            else:
                                if len(spike) != 10:
                                    if not renderer.queue_updating:
                                        spike[self.attr_dict["is_hovered"]] = True
                                    else:
                                        spike[self.attr_dict["is_hovered"]] = False
                    if spike[self.attr_dict["is_hovered"]]:
                        if pygame.mouse.get_pressed()[2]:
                            if not (renderer.queue[0].tile in [117, 129, 138, 139, 118, 135, 136, 137, 121]):
                                shiftable = True
                                for obj in renderer.queue:
                                    if isinstance(obj, MovingPlatform):
                                        if spike in obj.spikes:
                                            shiftable = False
                                if shiftable:
                                    
                                    if self.level != 0:
                                        if renderer.queue[0].tile == 116:
                                            if renderer.queue[0].shapeshifts >= 4:
                                                renderer.levels[renderer.level][int(spike[self.attr_dict["pos"]][1]/renderer.tile_size[1])+(0-int(renderer.init_render_pos[renderer.level][1]))][4+int((spike[self.attr_dict["pos"]][0]+8-renderer.camera.cam_change[0])/renderer.tile_size[0])] = renderer.queue[0].tile
                                                self.spikes = [sp for sp in self.spikes if sp != spike]
                                                #renderer.queue[0].shapeshifts -= 1
                                        else:
                                
                                                    renderer.levels[renderer.level][int(spike[self.attr_dict["pos"]][1]/renderer.tile_size[1])+(0-int(renderer.init_render_pos[renderer.level][1]))][4+int((spike[self.attr_dict["pos"]][0]+8-renderer.camera.cam_change[0])/renderer.tile_size[0])] = renderer.queue[0].tile
                                                    self.spikes = [sp for sp in self.spikes if sp != spike]
                                                    renderer.queue[0].shapeshifts -= 1
                                    else:
                                        
                                        if renderer.queue[0].tile == 116:
                                            if renderer.queue[0].shapeshifts >= 4:
                                                renderer.levels[renderer.level][int(spike[self.attr_dict["pos"]][1]/renderer.tile_size[1])+(0-int(renderer.init_render_pos[renderer.level][1]))][int((spike[self.attr_dict["pos"]][0]+8-renderer.camera.cam_change[0])/renderer.tile_size[0])] = renderer.queue[0].tile
                                                self.spikes = [sp for sp in self.spikes if sp != spike]
                                                #renderer.queue[0].shapeshifts -= 1
                                        else:
                      
                                                    renderer.levels[renderer.level][int(spike[self.attr_dict["pos"]][1]/renderer.tile_size[1])+(0-int(renderer.init_render_pos[renderer.level][1]))][int((spike[self.attr_dict["pos"]][0]+8-renderer.camera.cam_change[0])/renderer.tile_size[0])] = renderer.queue[0].tile
                                                    self.spikes = [sp for sp in self.spikes if sp != spike]
                                                    renderer.queue[0].shapeshifts -= 1
                                    if renderer.queue[0].tile == 116:
                                        if not spike[3]:
                                            if renderer.queue[0].shapeshifts >= 4:
                                                self.queue.append(FireBox([spike[8][0]+self.camera.cam_change[0], spike[8][1]+self.camera.cam_change[1]+8], True))
                                            
                                                renderer.queue[0].shapeshifts -= 4
                                        else:
                                            if renderer.queue[0].shapeshifts >= 4:
                                                self.queue.append(FireBox([spike[8][0], spike[8][1]+4], True, True))
                                            
                                                renderer.queue[0].shapeshifts -= 4
                                        renderer.queue[0].shapeshifting=False
                                        renderer.queue_updating = True
                            else:
                                if renderer.queue[0].tile != 121:
                                    if not self.just_spike_notified:
                                        text = self.font.render("Why are you trying to shapeshift spikes into other spikes?", False, [255, 0, 0], [0, 0, 0])
                                        text.set_colorkey([0, 0, 0])
                                        self.notifications.append(Notification(text, 1))
                                        self.just_spike_notified = True
                        else:
                            self.just_spike_notified = False
                        if self.rect_surf.get_alpha() != 50:
                            self.rect_surf.set_alpha(50)
                        shiftable = True
                        for obj in renderer.queue:
                            if isinstance(obj, MovingPlatform):
                                if spike in obj.spikes:
                                    shiftable = False
                        if shiftable:
                            if spike[7]==0:
                                win.blit(self.rect_surf, [spike[self.attr_dict["pos"]][0]+4, spike[self.attr_dict["pos"]][1]+8])
                            elif spike[7]==90:
                                win.blit(self.rect_surf, [spike[self.attr_dict["pos"]][0]+4, spike[self.attr_dict["pos"]][1]])
                            elif spike[7]==-90:
                                win.blit(self.rect_surf, [spike[self.attr_dict["pos"]][0], spike[self.attr_dict["pos"]][1]+6])
                    if spike[7]==0:
                        if not spike[6]:
                            if (renderer.queue[0].mask.overlap(self.mask, (spike[self.attr_dict["pos"]][0]-renderer.queue[0].pos[0], spike[self.attr_dict["pos"]][1]-renderer.queue[0].pos[1])) == None):
                                pass
                            else:
                                renderer.queue[0].is_alive = False
                                
                                #reset(renderer.queue[0], renderer)
                                renderer.queue[0].deaths += 1
                        else:
                            if (renderer.queue[0].mask.overlap(self.mask_2, (spike[self.attr_dict["pos"]][0]-renderer.queue[0].pos[0], spike[self.attr_dict["pos"]][1]-renderer.queue[0].pos[1])) == None):
                                pass
                            else:
                                renderer.queue[0].is_alive = False
                                
                                #reset(renderer.queue[0], renderer)
                                renderer.queue[0].deaths += 1
                    else:
                        if spike[7]==90:
                            if (renderer.queue[0].mask.overlap(self.mask_3, (spike[self.attr_dict["pos"]][0]-renderer.queue[0].pos[0], spike[self.attr_dict["pos"]][1]-renderer.queue[0].pos[1])) == None):
                                pass
                            else:
                                renderer.queue[0].is_alive = False
                                
                                #reset(renderer.queue[0], renderer)
                                renderer.queue[0].deaths += 1
                        else:
                            if (renderer.queue[0].mask.overlap(self.mask_4, (spike[self.attr_dict["pos"]][0]-renderer.queue[0].pos[0], spike[self.attr_dict["pos"]][1]-renderer.queue[0].pos[1])) == None):
                                pass
                            else:
                                renderer.queue[0].is_alive = False
                                
                                #reset(renderer.queue[0], renderer)
                                renderer.queue[0].deaths += 1
                    if spike[7]==0:
                        if not spike[6]:
                            for obj in self.queue:
                                if isinstance(obj, EnemySwordsman) or isinstance(obj, EnemyWizard):
                                    enemy = self.queue.index(obj)
                                else:
                                    continue
                                if (renderer.queue[enemy].mask.overlap(self.mask, (spike[self.attr_dict["pos"]][0]-renderer.queue[enemy].pos[0], spike[self.attr_dict["pos"]][1]-renderer.queue[enemy].pos[1])) == None):
                                    pass
                                else:
                                    obj.is_alive = False
                                    #self.queue.remove(renderer.queue[enemy])
                                    #renderer.queue[enemy].is_alive = False
                                    if spike[3]:
                                        if spike in self.spikes:
                                            self.spikes.remove(spike)
                                            if self.level != 0:
                                                renderer.levels[renderer.level][int(spike[self.attr_dict["pos"]][1]/renderer.tile_size[1])+(0-int(renderer.init_render_pos[renderer.level][1]))][4+int((spike[self.attr_dict["pos"]][0]+8-renderer.camera.cam_change[0])/renderer.tile_size[0])] = -1
                                            else:
                                                renderer.levels[renderer.level][int(spike[self.attr_dict["pos"]][1]/renderer.tile_size[1])+(0-int(renderer.init_render_pos[renderer.level][1]))][int((spike[self.attr_dict["pos"]][0]+8-renderer.camera.cam_change[0])/renderer.tile_size[0])] = -1
                                            return
                        else:
                            for obj in self.queue:
                                if isinstance(obj, EnemySwordsman) or isinstance(obj, EnemyWizard):
                                    enemy = self.queue.index(obj)
                                else:
                                    continue
                                if (renderer.queue[enemy].mask.overlap(self.mask_2, (spike[self.attr_dict["pos"]][0]-renderer.queue[enemy].pos[0], spike[self.attr_dict["pos"]][1]-renderer.queue[enemy].pos[1])) == None):
                                    pass
                                else:
                                    obj.is_alive = False
                                    #renderer.queue[enemy].is_alive = False
                                    #self.queue.remove(renderer.queue[enemy])
                                    if spike[3]:
                                        if spike in self.spikes:
                                            self.spikes.remove(spike)
                                            if self.level != 0:
                                                renderer.levels[renderer.level][int(spike[self.attr_dict["pos"]][1]/renderer.tile_size[1])+(0-int(renderer.init_render_pos[renderer.level][1]))][4+int((spike[self.attr_dict["pos"]][0]+8-renderer.camera.cam_change[0])/renderer.tile_size[0])] = -1
                                            else:
                                                renderer.levels[renderer.level][int(spike[self.attr_dict["pos"]][1]/renderer.tile_size[1])+(0-int(renderer.init_render_pos[renderer.level][1]))][int((spike[self.attr_dict["pos"]][0]+8-renderer.camera.cam_change[0])/renderer.tile_size[0])] = -1
                                            return
                    else:
                        if spike[7]==90:
                            for obj in self.queue:
                                if isinstance(obj, EnemySwordsman) or isinstance(obj, EnemyWizard):
                                    enemy = self.queue.index(obj)
                                else:
                                    continue
                                if (renderer.queue[enemy].mask.overlap(self.mask_3, (spike[self.attr_dict["pos"]][0]-renderer.queue[enemy].pos[0], spike[self.attr_dict["pos"]][1]-renderer.queue[enemy].pos[1])) == None):
                                    pass
                                else:
                                    obj.is_alive = False
                                    #self.enemies.remove(enemy)
                                    #self.queue.remove(renderer.queue[enemy])
                                    if spike[3]:
                                        if spike in self.spikes:
                                            self.spikes.remove(spike)
                                            if self.level != 0:
                                                renderer.levels[renderer.level][int(spike[self.attr_dict["pos"]][1]/renderer.tile_size[1])+(0-int(renderer.init_render_pos[renderer.level][1]))][4+int((spike[self.attr_dict["pos"]][0]+8-renderer.camera.cam_change[0])/renderer.tile_size[0])] = -1
                                            else:
                                                renderer.levels[renderer.level][int(spike[self.attr_dict["pos"]][1]/renderer.tile_size[1])+(0-int(renderer.init_render_pos[renderer.level][1]))][int((spike[self.attr_dict["pos"]][0]+8-renderer.camera.cam_change[0])/renderer.tile_size[0])] = -1
                                            return
                        else:
                            for obj in self.queue:
                                if isinstance(obj, EnemySwordsman) or isinstance(obj, EnemyWizard):
                                    enemy = self.queue.index(obj)
                                else:
                                    continue
                                if (renderer.queue[enemy].mask.overlap(self.mask_4, (spike[self.attr_dict["pos"]][0]-renderer.queue[enemy].pos[0], spike[self.attr_dict["pos"]][1]-renderer.queue[enemy].pos[1])) == None):
                                    pass
                                else:
                                    obj.is_alive = False
                                    #self.queue.remove(renderer.queue[enemy])
                                    #renderer.enemies.remove(enemy)
                                    if spike[3]:
                                        if spike in self.spikes:
                                            self.spikes.remove(spike)
                                            if self.level != 0:
                                                renderer.levels[renderer.level][int(spike[self.attr_dict["pos"]][1]/renderer.tile_size[1])+(0-int(renderer.init_render_pos[renderer.level][1]))][4+int((spike[self.attr_dict["pos"]][0]+8-renderer.camera.cam_change[0])/renderer.tile_size[0])] = -1
                                            else:
                                                renderer.levels[renderer.level][int(spike[self.attr_dict["pos"]][1]/renderer.tile_size[1])+(0-int(renderer.init_render_pos[renderer.level][1]))][int((spike[self.attr_dict["pos"]][0]+8-renderer.camera.cam_change[0])/renderer.tile_size[0])] = -1
                                            return
                    if not self.played:
                        if not web:
                            renderer.coin_channel.play(pygame.mixer.Sound("assets\Audio\spike_spawn.ogg"))
                        else:
                            renderer.coin_channel.play(pygame.mixer.Sound("assets/Audio/spike_spawn.ogg"))
                    self.played = True
    def add_spike_u(self, pos, shifted=False):
        self.spikes.append([[pos[0], pos[1]], time.time(), True, shifted, False, False, False, 0, pos])
    def add_spike_d(self, pos, shifted=False):
        self.spikes.append([[pos[0], pos[1]+4], time.time(), True, shifted, False, False, True, 0, pos])
    def add_spike_r(self, pos, shifted=False):
        selfpos = [pos[0]+((16*90)/90)+((20*90)/90)-int(self.spikesheet.get([3, 0]).get_width()/2)-8, pos[1]+44-int(self.spikesheet.get([3, 0]).get_height()/2)]
        self.spikes.append([selfpos, time.time(), True, shifted, False, False, True, 90, pos])
    def add_spike_l(self, pos, shifted=False):
        selfpos = [pos[0]+((16*-90)/-90)+((26*-90)/-90)-int(self.spikesheet.get([3, 0]).get_width()/2)-4, pos[1]+38-int(self.spikesheet.get([3, 0]).get_height()/2)]
        self.spikes.append([selfpos, time.time(), True, shifted, False, False, True, -90, pos])
    def render(self):
        self.rects = []
        self.coin_count = 0
        self.spike_count = 0
        self.spike_h_count = 0
        self.damage_masks = []
        self.side_rects = []
        self.standing_masks = []
        win.blit(self.background, [0, 0])
        #pygame.draw.rect(win, [0, 0, 255], self.camera.rect)
        
        tilemap = self.levels[self.level]
        self.num_row = -1
        self.num_col = -1
        self.y = self.init_render_pos[self.level][1]
        for abs_j, row in enumerate(tilemap):
            self.y += 1
            self.num_col = -1
            self.num_row += 1
            self.x = self.init_render_pos[self.level][0]
            for abs_x, tile in enumerate(row):
                self.num_col += 1
                self.x+=1
                #if not [self.x*self.tile_size[0], self.y*self.tile_size[1]] in self.deleted:
                if not tile in [-1, 60] and (not(tile in self.exceptions) or tile == 116):
                    
                        if tile != 116:
                            if self.camera.bigger_window_rect.collidepoint([self.x*self.tile_size[0], self.y*self.tile_size[1]]):
                                win.blit(self.images[tile], [self.x*self.tile_size[0], self.y*self.tile_size[1]])
                        if not (tile in self.decorative_tiles):
                            #if self.standing_masks[]
                            if not tile == 116:
                                if self.queue_updating:
                                    if not tile == 19:
                                        if (tilemap[self.num_row-1][self.num_col] in [-1, 60]) or (tilemap[self.num_row-1][self.num_col] in self.decorative_tiles):
                                            self.standing_masks.append([pygame.mask.from_surface(self.images[tile]), [self.x*self.tile_size[0], self.y*self.tile_size[1]], tile, [abs_x, abs_j]])
                                            #self.rects.append(pygame.Rect(self.x*self.tile_size[0], self.y*self.tile_size[1], 64, 64))
                                else:
                                    self.standing_masks.append([pygame.mask.from_surface(self.images[tile]), [self.x*self.tile_size[0], self.y*self.tile_size[1]], tile, [abs_x, abs_j]])
                                    #self.rects.append(pygame.Rect(self.x*self.tile_size[0], self.y*self.tile_size[1], 64, 64))
                            if not tile in [26, 27, 28, 29]:
                                if not tile == 116:
                                    if tilemap[self.num_row][self.num_col-1] in [-1, 60] or tilemap[self.num_row][self.num_col-1] in self.decorative_tiles:
                                        if not tilemap[self.num_row-1][self.num_col] in [-1, 60] and not(tilemap[self.num_row-1][self.num_col] in self.decorative_tiles):
                                            self.side_rects.append([pygame.Rect(self.x*self.tile_size[0]+4, (self.y*self.tile_size[1]+4), 1, (self.tile_size[1])), -1])
                                            #pygame.draw.rect(win, (255, 0, 0), pygame.Rect(self.x*self.tile_size[0]+4, (self.y*self.tile_size[1]+4), 1, (self.tile_size[1])))
                                        else:
                                            self.side_rects.append([pygame.Rect(self.x*self.tile_size[0]+4, (self.y*self.tile_size[1]+14), 1, (self.tile_size[1]-10)), -1])
                                            #pygame.draw.rect(win, (255, 0, 0), pygame.Rect(self.x*self.tile_size[0]+4, (self.y*self.tile_size[1]+14), 1, (self.tile_size[1]-10)))
                                    if self.num_col+1 < len(tilemap[self.num_row]):
                                        if tilemap[self.num_row][self.num_col+1] in [-1, 60] or tilemap[self.num_row][self.num_col+1] in self.decorative_tiles:
                                            if not tilemap[self.num_row-1][self.num_col] in [-1, 60] and not(tilemap[self.num_row-1][self.num_col] in self.decorative_tiles):
                                                self.side_rects.append([pygame.Rect((self.x+1)*self.tile_size[0]+4, (self.y*self.tile_size[1])+4, 1, (self.tile_size[1])), 1])
                                                #pygame.draw.rect(win, (255, 0, 0), pygame.Rect((self.x+1)*self.tile_size[0]+4, (self.y*self.tile_size[1])+4, 1, (self.tile_size[1])))
                                            else:
                                                self.side_rects.append([pygame.Rect((self.x+1)*self.tile_size[0]+4, (self.y*self.tile_size[1]+10)+4, 1, (self.tile_size[1]-10)), 1])
                                                #pygame.draw.rect(win, (255, 0, 0), pygame.Rect((self.x+1)*self.tile_size[0]+4, (self.y*self.tile_size[1]+14), 1, (self.tile_size[1]-10)))
                                    if self.num_row+1 < len(tilemap):
                                        if tilemap[self.num_row+1][self.num_col] in [-1, 60] or tilemap[self.num_row+1][self.num_col] in self.decorative_tiles:
                                            self.side_rects.append([pygame.Rect((self.x*self.tile_size[0])+7.5, ((self.y+1)*self.tile_size[1])+7.5, (self.tile_size[0]), 1), 2])
                                            #pygame.draw.rect(win, (255, 0, 0), pygame.Rect((self.x*self.tile_size[0])+7.5, ((self.y+1)*self.tile_size[1])+7.5, (self.tile_size[0]), 1))
                            else:
                                if self.num_row+1 < len(tilemap):
                                    if tilemap[self.num_row+1][self.num_col] in [-1, 60]:
                                        if self.num_col+1 < len(row):
                                            if tilemap[self.num_row][self.num_col+1] in [-1, 60]:
                                                self.side_rects.append([pygame.Rect((self.x*self.tile_size[0]), ((self.y+1)*self.tile_size[1])-38, (self.tile_size[0]), 1), 2])
                                                #pygame.draw.rect(win, (255, 0, 0), pygame.Rect((self.x*self.tile_size[0]), ((self.y+1)*self.tile_size[1])-38, (self.tile_size[0]), 1))
                                            else:
                                                self.side_rects.append([pygame.Rect((self.x*self.tile_size[0])+7.5, ((self.y+1)*self.tile_size[1])-38, (self.tile_size[0]), 1), 2])
                                                #pygame.draw.rect(win, (255, 0, 0), pygame.Rect((self.x*self.tile_size[0])+7.5, ((self.y+1)*self.tile_size[1])-38, (self.tile_size[0]), 1))
                                        else:
                                            self.side_rects.append([pygame.Rect((self.x*self.tile_size[0])+7.5, ((self.y+1)*self.tile_size[1])-38, (self.tile_size[0]), 1), 2])
                                            #pygame.draw.rect(win, (255, 0, 0), pygame.Rect((self.x*self.tile_size[0])+7.5, ((self.y+1)*self.tile_size[1])-38, (self.tile_size[0]), 1))
                if tile == 60:
                    if self.coin_appending:
                        self.queue.append(Coin([self.x*self.tile_size[0], self.y*self.tile_size[1]], self.coin_img, [4, 1]))
                        self.added_coins += 1
                    self.coin_count += 1
                    if self.coin_count > self.added_coins:
                        self.queue.append(Coin([self.x*self.tile_size[0], self.y*self.tile_size[1]], self.coin_img, [4, 1]))
                        self.added_coins += 1
                elif tile == 117:
                    if self.coin_appending:
                        self.add_spike_u([self.x*self.tile_size[0], self.y*self.tile_size[1]])
                        self.added_spikes += 1
                    self.spike_count += 1
                    if self.spike_count > self.added_spikes:
                        self.add_spike_u([self.x*self.tile_size[0], self.y*self.tile_size[1]])
                        self.added_spikes += 1
                elif tile == 129:
                    if self.coin_appending:
                        self.add_spike_d([self.x*self.tile_size[0], self.y*self.tile_size[1]])
                        self.added_spikes += 1
                    self.spike_count += 1
                    if self.spike_count > self.added_spikes:
                        self.add_spike_d([self.x*self.tile_size[0], self.y*self.tile_size[1]])
                        self.added_spikes += 1
                elif tile == 138:
                    if self.coin_appending:
                        self.add_spike_r([self.x*self.tile_size[0], self.y*self.tile_size[1]])
                        self.added_spikes += 1
                    self.spike_count += 1
                    if self.spike_count > self.added_spikes:
                        self.add_spike_r([self.x*self.tile_size[0], self.y*self.tile_size[1]])
                        self.added_spikes += 1
                elif tile == 139:
                    if self.coin_appending:
                        self.add_spike_l([self.x*self.tile_size[0], self.y*self.tile_size[1]])
                        self.added_spikes += 1
                    self.spike_count += 1
                    if self.spike_count > self.added_spikes:
                        self.add_spike_l([self.x*self.tile_size[0], self.y*self.tile_size[1]])
                        self.added_spikes += 1
                elif tile == 118:
                    if self.coin_appending:
                        self.queue.append(HiddenSpike(self.spike_image, [4, 1], [self.x*self.tile_size[0], self.y*self.tile_size[1]]))
                        self.added_spikes_h += 1
                    self.spike_h_count += 1
                    if self.spike_h_count > self.added_spikes_h:
                        self.queue.append(HiddenSpike(self.spike_image, [4, 1], [self.x*self.tile_size[0], self.y*self.tile_size[1]]))
                        self.added_spikes_h += 1
                elif tile == 135:
                    if self.coin_appending:
                        self.queue.append(HiddenSpike(self.spike_image, [4, 1], [self.x*self.tile_size[0], self.y*self.tile_size[1]], True))
                        self.added_spikes_h += 1
                    self.spike_h_count += 1
                    if self.spike_h_count > self.added_spikes_h:
                        self.queue.append(HiddenSpike(self.spike_image, [4, 1], [self.x*self.tile_size[0], self.y*self.tile_size[1]], True))
                        self.added_spikes_h += 1
                elif tile == 136:
                    if self.coin_appending:
                        self.queue.append(HiddenSpike(self.spike_image, [4, 1], [self.x*self.tile_size[0], self.y*self.tile_size[1]], False, 90))
                        self.added_spikes_h += 1
                    self.spike_h_count += 1
                    if self.spike_h_count > self.added_spikes_h:
                        self.queue.append(HiddenSpike(self.spike_image, [4, 1], [self.x*self.tile_size[0], self.y*self.tile_size[1]], False, 90))
                        self.added_spikes_h += 1
                elif tile == 137:
                    if self.coin_appending:
                        self.queue.append(HiddenSpike(self.spike_image, [4, 1], [self.x*self.tile_size[0], self.y*self.tile_size[1]], False, -90))
                        self.added_spikes_h += 1
                    self.spike_h_count += 1
                    if self.spike_h_count > self.added_spikes_h:
                        self.queue.append(HiddenSpike(self.spike_image, [4, 1], [self.x*self.tile_size[0], self.y*self.tile_size[1]], False, -90))
                        self.added_spikes_h += 1
                elif tile == 119:
                    if self.coin_appending:
                        self.queue.append(Crusher([self.x*self.tile_size[0], self.y*self.tile_size[1]]))
                elif tile == 120:
                    if self.coin_appending:
                        self.queue.append(SpikeBall([self.x*self.tile_size[0], self.y*self.tile_size[1]]))
                elif tile == 121:
                    if self.coin_appending:
                        self.queue.append(SwingingAxe([self.x*self.tile_size[0], self.y*self.tile_size[1]]))
                elif tile == 122:
                    if self.coin_appending:
                        length = 1
                        for i in range(abs_x+1, abs_x+5):
                            if row[i] == 108:
                                length += 1
                            else:
                                break
                        self.queue.append(MovingPlatform(length, [self.x*self.tile_size[0], self.y*self.tile_size[1]], 3, length*64))
                elif tile == 116:
                    if self.coin_appending:
                        self.queue.append(FireBox([self.x*self.tile_size[0], self.y*self.tile_size[1]+self.level_firebox_y_offset_dict[self.level]], True))
                elif tile == 140:
                    if self.coin_appending:
                        self.enemies.append(len(self.queue))
                        self.queue.append(EnemySwordsman([self.x*self.tile_size[0], self.y*self.tile_size[1]], self))
                elif tile == 141:
                    if self.coin_appending:
                        self.enemies.append(len(self.queue))
                        self.queue.append(EnemyWizard([self.x*self.tile_size[0], self.y*self.tile_size[1]], self))
                elif tile == 142:
                    if self.coin_appending and not self.queue[0].has_staff:
                        self.queue.append(StaffIcon(self.queue[0].staff.copy(),[self.x*self.tile_size[0], self.y*self.tile_size[1]]))
                elif tile == 88:
                    if self.coin_appending:
                        self.queue.append(CheckPoint([self.x*self.tile_size[0], self.y*self.tile_size[1]], -1))
                elif tile == 111:
                    if self.coin_appending:
                        self.queue.append(CheckPoint([self.x*self.tile_size[0], self.y*self.tile_size[1]], 1))
                elif tile == 32:
                    if self.coin_appending:
                        length = 1
                        final_tile = [abs_x, 0]
                        for i in range(abs_j+1, abs_j+25):
                            if i in range(len(tilemap)):
                                if (tilemap[i][abs_x] in [-1, 60, 111, 88]) or (tilemap[i][abs_x] in self.decorative_tiles):
                                    length += 1
                                    final_tile[1] = i 
                                else:
                                    break
                            else:
                                break
                        self.queue.append(FallingBlock([self.x*self.tile_size[0], self.y*self.tile_size[1]], self.images[79], final_tile, [abs_x, abs_j], length))
                elif tile == 103:
                    if self.coin_appending:
                        self.queue.append(Psycho([self.x*self.tile_size[0], self.y*self.tile_size[1]]))
                elif tile == 33:
                    if self.coin_appending:
                        self.queue.append(Jumper([self.x*self.tile_size[0], self.y*self.tile_size[1]]))
        self.first_cycle = False
        self.coin_appending = False
    def update(self):
        if self.clock.get_fps() != 0:
            self.dt = 60/self.clock.get_fps()
        else:
            self.dt = 1
        if self.dt > 1.5:
            self.dt = 1
   
        if time.time() - self.fire_time >= 0.3:
            self.firebox_frame+=1
            if (self.firebox_frame>12):
                self.firebox_frame = 0
            self.fire_time = time.time()
        if not self.firebox_in_cam:
            self.firebox_channel.fadeout(2000)
        self.firebox_channel.set_volume(self.coin_channel.get_volume())
        self.thwack_channel.set_volume(self.coin_channel.get_volume())
        self.swoosh_channel.set_volume(self.coin_channel.get_volume())
        self.axe_channel.set_volume(self.coin_channel.get_volume())
        self.queue[0].combat = False
        self.render()
        self.enemies = []
        self.firebox_in_cam = False
        if self.queue != []:
            for obj in self.queue:
                if isinstance(obj, FireBox) or isinstance(obj, Jumper):
                    obj.append_rects(self)
                if obj.__class__.__name__ ==  "CheckPoint":
                    obj.update(self)
            for obj in self.queue:
                if obj.__class__.__name__ in self.ground:
                    obj.update(self)
                    continue
              
            self.spike_update()
            for obj in self.queue:
                if obj != None:
                    if not (obj.__class__.__name__ in self.ground) and not (isinstance(obj, CheckPoint)):
                        obj.update(self)
                if isinstance(obj, FireBox):
                    if obj.rect.colliderect(self.camera.rect) and self.queue[0].is_alive:
                        self.firebox_in_cam = True
                if isinstance(obj, DeathParticle):
                    if obj.alpha <= 0:
                        self.queue.remove(obj)
        
        self.bullet_manager.update_physics(self)
        self.bullet_manager.update_graphics(self)
        for notification in self.notifications:
            notification.update(self.dt)
        #if not web:
            #print(self.clock.get_fps())

        
