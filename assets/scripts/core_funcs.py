import numpy
import pygame, json, asyncio, os, base64, time
from random import randint
import math
from assets.scripts.particles import Particles
from math import sqrt, degrees, radians
if __import__("sys").platform == "emscripten":
    import platform
pygame.init()
global web
web =  False
global cursor_mask
global cursor_img
global button_sound
if not web:
    cursor_img = pygame.image.load("assets\Spritesheets\\cursor.png")
    button_sound = pygame.mixer.Sound("assets\\Audio\\click.ogg")
else:
    cursor_img = pygame.image.load("assets/Spritesheets//cursor.png")
    button_sound = pygame.mixer.Sound("assets/Audio/click.ogg")
cursor_mask = pygame.mask.from_surface(cursor_img)
flags = pygame.RESIZABLE | pygame.SCALED
if web:
    flags = pygame.SHOWN
win = pygame.display.set_mode((1280, 720), flags)
global win_size
win_size = [win.get_width(), win.get_height()]
pygame.display.set_caption("Shiftania")
global spawn_positions
spawn_positions = [[64, -3*64], [64, 4.5*64], [2816, 5120], [0, 0], [0, 0]]

def max_height_vertical(u, g):
    return (u*u)/(2*g)
def find_u(height, g):
    return sqrt(height*2*g)
def blit_center(img):
    win.blit(img, [win_size[0]-(img.get_width()/2), win_size[1]-(img.get_height()/2)])
def center_pos(img):
    return [win_size[0]/2-(img.get_width()/2), win_size[1]/2-(img.get_height()/2)]
def swap_color(img, col1, col2):
    pygame.transform.threshold(img ,img ,col1, (10, 10, 10), col2, 1, None, True)
def scale_image(img, factor=4.0):
    size = round(img.get_width() * factor), round(img.get_height() * factor)
    return pygame.transform.scale(img, size).convert()
def angle_between(points):
    return math.atan2(points[1][1] - points[0][1], points[1][0] - points[0][0])*180/math.pi
def isequal(color1:pygame.Color, color2:tuple) -> bool:
    if color1.r == color2[0] and color1.g == color2[1] and color1.b == color2[2]:
        return True
    else:
        return False
def isequal(color1:pygame.Color, color2:tuple) -> bool:
    if color1.r == color2[0] and color1.g == color2[1] and color1.b == color2[2]:
        return True
    else:
        return False
class FastMask:
    def __init__(self, position:tuple, surface:pygame.Surface, background_color:tuple = [0, 0, 0], scale:int = 1) -> None:
        self.outline = []
        self.rects = []
        self.on_border=False
        self.overall_rect = pygame.Rect(position[0], position[1], surface.get_width()*scale, surface.get_height()*scale)
        for j in range(surface.get_height()):
            for i in range(surface.get_width()):
                self.on_border=False
                if (i>0 and j>0 and i<surface.get_width()-1 and j<surface.get_height()-1):
                    color_1 = surface.get_at([i, j])
                    color_2 = surface.get_at([i-1, j])
                    color_3 = surface.get_at([i, j-1])
                    color_4 = surface.get_at([i+1, j])
                    color_5 = surface.get_at([i, j+1])
                    if not isequal(color_1, background_color):
                        if (i-1>=0):
                            if isequal(color_2, background_color):
                                self.on_border = True
                        else:
                            self.on_border = True
                        if (j-1>=0):
                            if isequal(color_3, background_color):
                                self.on_border = True
                        else:
                            self.on_border = True
                        if ((i+1)<surface.get_width()):
                            if isequal(color_4, background_color):
                                self.on_border = True
                        else:
                            self.on_border = True
                        if ((j+1)<surface.get_height()):
                            if isequal(color_5, background_color):
                                self.on_border = True
                        else:
                            self.on_border = True
                else:
                    if not isequal(surface.get_at([i, j]), background_color):
                        self.on_border=True
                if self.on_border:
                    self.outline.append([i, j])
        self.scale = scale
        for count, point in enumerate(self.outline):
            self.rects.append(pygame.Rect(position[0]+self.outline[count][0]*scale, position[1]+self.outline[count][1]*scale, scale, scale)) #creates outline rects
    def draw(self, screen:pygame.Surface, color:tuple=[255, 0, 0]):
        for rect in self.rects:
            pygame.draw.rect(screen, color, rect)
    def move(self, movement):
        for rect in self.rects:
            rect.x += movement[0]
            rect.y += movement[1]
        self.overall_rect.x += movement[0]
        self.overall_rect.y += movement[1]
    def move_to(self, position):
        self.rects = []
        for count, point in enumerate(self.outline):
            self.rects.append(pygame.Rect(position[0]+self.outline[count][0]*self.scale, position[1]+self.outline[count][1]*self.scale, self.scale, self.scale))
        self.overall_rect = pygame.Rect(position[0], position[1], self.overall_rect.w, self.overall_rect.h)
    def fast_collide(self, other_fast_mask):
        #if self.overall_rect.colliderect(other_fast_mask.overall_rect):
        for rect in self.rects:
                if rect.collidelist(other_fast_mask.rects) != -1:
                    return True
        return False                        
                    
class SpriteSheet:
    def __init__(self, sheet, size, colorkey = [0, 0, 0]):
        self.spritesheet = sheet
        self.colorkey = colorkey
        self.size = [self.spritesheet.get_width()/size[0], self.spritesheet.get_height()/size[1]]
        self.sheet = []
        for i in range(size[1]):
            self.sheet.append([])
            for j in range(size[0]):
                image = pygame.Surface((self.size))
                image.set_colorkey(self.colorkey)
                image.blit(self.spritesheet, (0, 0), [j*self.size[0], i*self.size[1], self.size[0], self.size[1]])
                self.sheet[i].append(image)
    def get(self, loc):
        return self.sheet[loc[1]][loc[0]]
class DeathParticle:
    def __init__(self, tex, pos, renderer, colkey = [0, 0, 0]):
        self.tex = tex
        self.pos = pos
        self.orig_x = pos[0]*1
        self.colkey = colkey
        self.alpha = 255
        self.colkey = colkey
        self.orig_pos = [pos[0], pos[1]]
        self.orig_x_change = renderer.camera.cam_change[0]*1
    def update(self, renderer):
        if self.alpha > 0:
            self.alpha -= (2*renderer.dt)
        self.pos[1] -= (1.5*renderer.dt)
        self.pos[0] = self.orig_x+randint(-5, 5)
        self.tex.set_alpha(self.alpha)
        win.blit(self.tex, [self.pos[0]+(renderer.camera.cam_change[0]-self.orig_x_change), self.pos[1]])
class Notification:
    def __init__(self, surf: pygame.Surface, type_):
        self.surf = surf
        self.alpha = 255
        self.pos = [(1280-self.surf.get_width())/2, (900-self.surf.get_height())/2]
        self.speed = 1
        self.type = type_
    def update(self, dt):
        self.pos[1]-=(self.speed*dt)
        self.alpha -= (self.speed*dt*2)
        if self.alpha <= 0:
            self.alpha = 0
        self.surf.set_alpha(int(self.alpha))
        win.blit(self.surf, self.pos)
class Shield:
    def __init__(self, pos, level) -> None:
        self.pos = [pos[0]*1, pos[1]*1]
        self.level = level
        wood_color = [115, 91, 66]
        iron_color = [161, 154, 150]
        gold_color = [238, 181, 81]
        diamond_color = [139, 176, 173]
        level_colors = [wood_color, iron_color, gold_color, diamond_color]
        if web:
            sprite = scale_image(pygame.image.load("assets/Spritesheets/shield_anim.png").convert())
        else:
            sprite = scale_image(pygame.image.load("assets\Spritesheets\shield_anim.png").convert())
        swap_color(sprite, wood_color, level_colors[level-1])
        self.sheet = SpriteSheet(sprite, [4, 3], [255, 255, 255])
        self.frame = [0, 0]
        self.mask = pygame.mask.from_surface(self.sheet.get(self.frame))
        self.health = self.level*8
        self.health_bar_length = 96*self.level
        self.unit_bar_length = self.health_bar_length/self.health
        self.health_bar_rect = pygame.Rect(32, 32, self.health_bar_length, 16)
        self.health_bar_rect_2 = pygame.Rect(32, 32, self.health_bar_length+4, 16)
        self.dead = False
    def update(self, renderer):
        if not self.dead:
            if self.health > 0:
                self.mask = pygame.mask.from_surface(self.sheet.get(self.frame))
                win.blit(self.sheet.get(self.frame), self.pos)
                pygame.draw.rect(win, [255, 0, 0], self.health_bar_rect)
                pygame.draw.rect(win, [255, 255, 255], self.health_bar_rect_2, 4)
                for i in range(self.level*8):
                    pygame.draw.rect(win, [255, 255, 255], pygame.Rect(32+(i*self.unit_bar_length), 32, 4, 16), 4)
            else:
                particle_sheet = SpriteSheet(self.sheet.get(self.frame), [self.sheet.get(self.frame).get_width()//4, self.sheet.get(self.frame).get_height()//4], [0, 0, 0])
                for j, sheet in enumerate(particle_sheet.sheet):
                    for i, surf in enumerate(sheet):
                        renderer.queue.append(DeathParticle(surf, [self.pos[0]+(i*4), self.pos[1]+(j*4)], renderer, [0, 0, 0]))
                self.dead = True
def reset(player, renderer, fell=False):
        maps = json.load(open("levels.json", "r"))
        renderer.levels = [maps["level_1"], maps["level_2"], maps["level_3"], maps["level_4"], maps["level_5"]]
        #renderer.level = 0
        renderer.side_rects = []
        renderer.init_render_pos = [[-1, -13.2], [-5, 0], [-5, 0], [-5, 0], [-5, 0]]
        #renderer.coin_channel = pygame.mixer.Channel(2)
        renderer.queue = [player]
        renderer.first_cycle = True
        renderer.clock = pygame.time.Clock()
        renderer.coin_appending = True
        renderer.added_coins = 0
        renderer.spikes = []
        renderer.played = False
        renderer.added_spikes = 0
        renderer.added_spikes_h = 0
        renderer.camera.cam_change = [0, 0]
        match renderer.level:
            case 0:
                if not player.on_door:
                    player.pos = [64, -3*64]
                
                else:
                    player.pos = [1604, -5*64]   
            case 1:
                if not player.on_door:
                    
                      
                            player.pos = [2816, 5952]
                else:
                    player.pos = [2816, 5152]
            case 2:
                if not player.on_door:

                            player.pos = [2816, 5952]

                else:
                    player.pos = [5376, 5152]
            case 3:
                if not player.on_door:
                    
                
                            player.pos = [2816, 5952]
                else:
                    player.pos = [3328, 5152]
            case 4:
                if not player.on_door:
                    
                
                            player.pos = [2816, 5952]
                else:
                    player.pos = [2816, 5152]
        #player.spritesheet = SpriteSheet(spritesheet, sheet_size)
        player.on_door = False
        player.t = False
        player.frame = [0, 0]
        player.fell = False
        player.vel = [0, 0]
        player.gravity = 0.2
        player.just_spawned = True
        player.delay = 0
        player.standing = False
        player.speed = 3
        player.cycles = 0
        player.just_col = []
        player.collided = False
        player.cur_row = [5, 4]
        player.jumping = False
        player.moving = True
        player.just_jumped = False
        renderer.cur_cycle += 1
        renderer.bullet_manager.bullets = []
        renderer.cycles = 0
        player.is_alive = True
        player.shield = Shield(player.pos, renderer.shop.shield_level)
        