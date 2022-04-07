from asyncore import loop
from email import contentmanager
from pickle import FALSE, STOP
from re import X
from tracemalloc import start, stop
from turtle import begin_fill
import pygame

import sys

class Spritesheet:
    def __init__(self, file):
        self.sheet = pygame.image.load(file).convert()

    def get_sprite(self, x, y, width, height):
        sprite = pygame.Surface([width, height])
        sprite.blit(self.sheet, (0, 0), (x, y, width, height))
        sprite.set_colorkey(Config.WHITE)
        return sprite



class Config:
    TILE_SIZE = 32
    WINDOW_WIDTH = TILE_SIZE * 15
    WINDOW_HEIGHT = TILE_SIZE * 10
    BLACK = (0, 0, 0)
    RED = (255, 0, 0)
    GREEN = (255, 255, 255)
    GREY = (128, 128, 128)
    WHITE = (255, 255, 255)
    FPS = 30
    BG_SPEED = -3



class BaseSprite(pygame.sprite.Sprite):
    def __init__(self, game, x, y, x_pos=0, y_pos=0, width=Config.TILE_SIZE, height=Config.TILE_SIZE, layer=0, groups=None, spritesheet=None):
        self._layer = layer
        groups = (game.all_sprites, ) if groups == None else (game.all_sprites, groups)
        super().__init__(groups)
        self.game = game
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.width = width
        self.height = height

        if spritesheet == None:
            self.image = pygame.Surface([self.width, self.height])
            self.image.fill(Config.GREY)
        else:
            self.spritesheet = spritesheet
            self.image = self.spritesheet.get_sprite(
                self.x_pos,
                self.y_pos,
                self.width,
                self.height
            )
        self.rect = self.image.get_rect()
        self.rect.x = x * Config.TILE_SIZE
        self.rect.y = y * Config.TILE_SIZE

    def scale(self, factor=2):
        self.rect.width *= factor
        self.rect.height *= factor
        self.image = pygame.transform.scale(self.image, (self.rect.width, self.rect.height))


class PlayerSprite(BaseSprite):
    def __init__(self, game, x, y, **kwargs):
        img_data = {
            'spritesheet': Spritesheet("res/player3.png"),
            'width': 32,
            'height': 32
        }
        super().__init__(game, x, y, groups=game.players, layer=1, **img_data, **kwargs)
        self.speed = 5
        self.color = Config.RED
        self.anim_counter = 0
        self.animation_frames = [0, 32]
        self.current_frame = 0
        self.animation_duration = 30
        self.y_velocity = 10
        

    def animate(self, x_diff):
        self.anim_counter += abs(x_diff)
        new_frame = round(self.anim_counter / self.animation_duration) % len(self.animation_frames)
        if self.current_frame != new_frame:
            new_pos = self.animation_frames[new_frame]
            self.image = self.spritesheet.get_sprite(new_pos, self.y_pos, self.width, self.height)
            self.current_frame = new_frame
            self.anim_counter = self.anim_counter % (len(self.animation_frames) * self.animation_duration)

    
    def update(self):
        self.rect.x = self.rect.x + self.speed
        self.rect.y = self.rect.y - self.y_velocity
        self.y_velocity -= 0.5
        self.handle_movement()
        self.check_collision()


    def handle_movement(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            self.y_velocity = 10
        self.update_camera()


    def update_camera(self):
        x_c, y_c = self.game.screen.get_rect().center
        x_diff = x_c - self.rect.centerx
        y_diff = y_c - self.rect.centery
        for sprite in self.game.all_sprites:
            sprite.rect.x += x_diff
            sprite.rect.y += y_diff
        self.animate(x_diff)

        # Shift Background
        self.game.bg_x += x_diff * Config.BG_SPEED
        if self.game.bg_x > Config.WINDOW_WIDTH:
            self.game.bg_x = -Config.WINDOW_WIDTH
        elif self.game.bg_x < -Config.WINDOW_WIDTH:
            self.game.bg_x = Config.WINDOW_WIDTH


    def is_standing(self, hit):
        if abs(hit.rect.top - self.rect.bottom) > abs(self.speed):
            return False
        if abs(self.rect.left - hit.rect.right) <= abs(self.speed):
            return False
        if abs(hit.rect.left - self.rect.right) <= abs(self.speed):
            return False
        return True

    def hit_head(self, hit):
        if abs(self.rect.top - hit.rect.bottom) > abs(self.speed):
            return False
        if abs(self.rect.left - hit.rect.right) <= abs(self.speed):
            return False
        if abs(hit.rect.left - self.rect.right) <= abs(self.speed):
            return False
        return True


    def check_collision(self):
        hits = pygame.sprite.spritecollide(self, self.game.ground, False)
        for hit in hits:
            if self.is_standing(hit):
                self.rect.bottom = hit.rect.top
                break
            print ("zusammenstoss")
            if self.hit_head(hit):
                self.y_velocity = 0
                self.rect.top = hit.rect.bottom
                break
            self.game.playing = False          


class GroundSprite(BaseSprite):
    def __init__(self, game, x, y):
        img_data = {
            'spritesheet': Spritesheet("res/Mais1.png"),
            'width': 54,
            'height': 64
        }
        super().__init__(game, x, y, groups=game.ground, layer=0, **img_data)

class HandSprite(BaseSprite):
    def __init__(self, game, x, y):
        img_data = {
            'spritesheet': Spritesheet("res/Hand.jpg"),
            'width': 402,
            'height': 701
        }
        super().__init__(game, x, y, groups=game.ground, layer=0, **img_data)

class PeperoniSprite(BaseSprite):
    def __init__(self, game, x, y):
        img_data = {
            'spritesheet': Spritesheet("res/Peperoni.png"),
            'width': 36,
            'height': 52
        }
        super().__init__(game, x, y, groups=game.ground, layer=0, **img_data)        

class FischSprite(BaseSprite):
    def __init__(self, game, x, y):
        img_data = {
            'spritesheet': Spritesheet("res/Fisch.png"),
            'width': 48,
            'height': 48
        }
        super().__init__(game, x, y, groups=game.ground, layer=0, **img_data)    

class UntergrundSprite(BaseSprite):
    def __init__(self, game, x, y):
        img_data = {
            'spritesheet': Spritesheet("res/Untergrund.jpg"),
            'width': 32,
            'height': 32
        }
        super().__init__(game, x, y, groups=game.ground, layer=0, **img_data)

class GabelSprite(BaseSprite):
    def __init__(self, game, x, y):
        img_data = {
            'spritesheet': Spritesheet("res/Gabel1.png"),
            'width': 72,
            'height': 286
        }
        super().__init__(game, x, y, groups=game.ground, layer=0, **img_data)

class FeuerSprite(BaseSprite):
    def __init__(self, game, x, y):
        img_data = {
            'spritesheet': Spritesheet("res/Feuer.png"),
            'width': 23,
            'height': 32
        }
        super().__init__(game, x, y, groups=game.ground, layer=0, **img_data)      
class Game:
    def __init__(self):
        pygame.init()
        pygame.font.init()
        self.font = pygame.font.Font(None, 30)
        self.screen = pygame.display.set_mode( (Config.WINDOW_WIDTH, Config.WINDOW_HEIGHT) ) 
        self.clock = pygame.time.Clock()
        self.bg = pygame.image.load("res/Grill.png")
        self.go = pygame.image.load("res/Gameover.png")
        self.bg_x = 0
        self.gameover = False
        self.playing = False
        self.waiting = False
        self.score=0

    
    def load_map(self, mapfile):
        with open(mapfile, "r") as f:
            for (y, lines) in enumerate(f.readlines()):
                for (x, c) in enumerate(lines):
                    if c == "b":
                        GroundSprite(self, x, y)
                    if c == "c":
                        PeperoniSprite(self, x, y)
                    if c == "f":
                        FischSprite(self, x, y)
                    if c == "u":
                        UntergrundSprite(self, x, y)
                    if c == "e":
                        FeuerSprite(self, x, y)
                    if c == "g":
                        GabelSprite(self, x, y)
                    if c == "h":
                        HandSprite(self, x, y)
                    if c == "p":
                        self.player = PlayerSprite(self, x, y)

    def new(self):
        self.playing = True
        self.score=0
        self.all_sprites = pygame.sprite.LayeredUpdates()
        self.ground = pygame.sprite.LayeredUpdates()
        self.players = pygame.sprite.LayeredUpdates()

        self.load_map("maps/level-01.txt")

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.playing = False
                self.gameover = True
                self.waiting = False

    def update(self):
        self.all_sprites.update()

    def draw(self):
        self.screen.blit(self.bg, (self.bg_x, 0))
        tmp_bg = pygame.transform.flip(self.bg, True, False)
        second_x = Config.WINDOW_WIDTH + self.bg_x
        if self.bg_x > 0:
            second_x -= 2*Config.WINDOW_WIDTH
        self.screen.blit(tmp_bg, (second_x, 0))

        self.all_sprites.draw(self.screen)
        self.score= self.score + 1/Config.FPS
        textsurface= self.font.render (f'{self.score:.0f}', False, Config.WHITE)
        if self.gameover:
            self.playing= False
        self.screen.blit(textsurface,(32,32))
        pygame.display.update()



    def game_loop(self):
        while self.playing:                                
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(Config.FPS)
        self.waiting = True
        self.screen = pygame.display.set_mode( (500, 200) ) 
        
        while self.waiting:
            self.screen.blit(self.go, (0, 0))
            self.handle_events()
            self.clock.tick(Config.FPS)
            pygame.display.update()

    def main(self):
        while self.playing:
            self.event()
            self.update()
            self.draw()
    
def main():
    g = Game()
    g.new()

    while not g.gameover:
        g.game_loop()

    pygame.quit()
    sys.exit()
