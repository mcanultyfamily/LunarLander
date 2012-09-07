# encoding=utf-8
import time
import pygame

# -- Init pygame and main surfaces
pygame.init()
MAX_X_SIZE = 1000
MAX_Y_SIZE = 700
screen = pygame.display.set_mode((0,0), pygame.FULLSCREEN)
X_SIZE, Y_SIZE = screen.get_size()

pygame.display.set_caption("Lunar Lander")
background = pygame.Surface(screen.get_size())
background = background.convert()
background.fill((0, 0, 0))
FONT_SIZE = 16
font = pygame.font.SysFont("monospace", FONT_SIZE, True, False)
clock = pygame.time.Clock()

# -- Render the top-line text
_last_text = {}
def render_text(s):
    global _last_text
    s = s.strip()
    if s!=_last_text.get('s'):
        text = font.render(s, True, (255, 255, 255), (0, 0, 0))
        textRect = text.get_rect()

        textRect.left = screen.get_rect().left+4
        textRect.top = screen.get_rect().bottom-(4+FONT_SIZE)
        _last_text = {"s":s, 'text':text, 'textRect':textRect}
    screen.blit(_last_text['text'], _last_text['textRect'])    

def _box_sprite(r, g, b):
    box = pygame.Surface((10, 10))
    box = box.convert()
    box.fill((r, g, b))
    return box
    
# http://pygame.org/wiki/Spritesheet
class SpriteSheet(object):
    def __init__(self, filename):
        try:
            self.sheet = pygame.image.load(filename).convert()
        except pygame.error, message:
            print 'Unable to load spritesheet image:', filename
            raise SystemExit, message
    # Load a specific image from a specific rectangle
    def image_at(self, rectangle, colorkey = None):
        "Loads image from x,y,x+offset,y+offset"
        rect = pygame.Rect(rectangle)
        image = pygame.Surface(rect.size).convert()
        image.blit(self.sheet, (0, 0), rect)
        if colorkey is not None:
            if colorkey is -1:
                colorkey = image.get_at((0,0))
            image.set_colorkey(colorkey, pygame.RLEACCEL)
        return image
    # Load a whole bunch of images and return them as a list
    def images_at(self, rects, colorkey = None):
        "Loads multiple images, supply a list of coordinates" 
        return [self.image_at(rect, colorkey) for rect in rects]
    # Load a whole strip of images
    def load_strip(self, rect, image_count, colorkey = None):
        "Loads a strip of images and returns them as a list"
        tups = [(rect[0]+rect[2]*x, rect[1], rect[2], rect[3])
                for x in range(image_count)]
        return self.images_at(tups, colorkey)

SPRITES = {}
sheet = SpriteSheet("Sprites.png")

class Sprite(object):
    def __init__(self, name, r, g, b, row, col, h):
        self.box = _box_sprite(r, g, b)
        TILE_SIZE = 16
        top = TILE_SIZE*row
        bottom = top+(TILE_SIZE*h)
        left = TILE_SIZE*col
        right = left+TILE_SIZE
        self.tile = sheet.image_at((left, top, TILE_SIZE, TILE_SIZE*h))
        SPRITES[name] = self.tile
        
Sprite('freefall', 255, 255, 255,   0, 0, 1)
Sprite('landed', 0, 255, 0,     0, 1, 1)
Sprite('fullpower', 255, 208, 0,    0, 2, 2)
Sprite('halfpower', 255, 168, 0,    0, 3, 2)
Sprite('lowpower', 255, 128, 0,    0, 4, 2)
Sprite('landingpower', 255, 88, 0,    1, 0, 1)
Sprite('boom', 255, 0, 0,    1, 1, 1)
    

class LunarMath(object):
    def __init__(self):
        self.result = None

        self.x = 10.0
        self.y = Y_SIZE-50.0
        
        self.xv = 1.0
        self.yv = 0.0
        
        self.g = -0.1
        self.atmo = 0.0
        self.motor = 0.0
        self.motor_max = 1.2
        self.motor_ramp_up = 0.02
        self.motor_ramp_down = 0.1
        self.motor_on = "OFF"
        self.t = 0

    def throttle(self, on):
        if on:
            self.motor_on = "ON"
        else:
            self.motor_on = "OFF"

    def game_tick(self):
        LANDING_Y = FONT_SIZE+Y_SIZE+4
        if self.y>0.0 and self.y<Y_SIZE and self.x>=0.0 and self.x<X_SIZE:
            self.t += 1
            if self.motor_on=='ON':
                self.motor = min(self.motor_max, self.motor+self.motor_ramp_up)
            else:
                self.motor = max(0.0, self.motor-self.motor_ramp_down)        
            
            self.yv += self.g
            self.yv += self.atmo
            self.yv += self.motor
            
            self.xv += self.atmo
            
            self.x += self.xv
            self.y += self.yv        
    
            return self.display()
        else:
            if not self.result:
                if self.y<=LANDING_Y and self.yv>=-2.0:
                    self.result = 'LAND'
                elif self.y<=LANDING_Y:
                    self.result = 'CRASH'
                else:
                    self.result = 'MISS'
            return "%s - %s\n" % (self.display(), self.result)

    def display(self):
        DISPLAY_FMT = "[%4s] x: %8.3f (%6.2f)  y: %8.3f (%6.2f) - M: %-3s-%7.3f"
        s = DISPLAY_FMT % (self.t, self.x, self.xv, self.y, self.yv, self.motor_on, self.motor)
        return s
        
def one_run():
    
    lunar = LunarMath()
    
    keepGoing = True
    
    while keepGoing:
    
        clock.tick(30)
    
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:            
                keys = [event.key]
                if event.key in (pygame.K_q, pygame.K_ESCAPE):
                    return False # QUIT Command
                elif event.key == pygame.K_n:
                    return True # START OVER
                elif event.key == pygame.K_UP:
                    lunar.throttle(True) # THROTTLE UP
                elif event.key == pygame.K_DOWN:
                    lunar.throttle(False)
    
        s = lunar.game_tick()          
        if lunar.result == 'LAND':
            sprite = SPRITES['landed'] 
        elif lunar.result == 'CRASH':
            sprite = SPRITES['boom'] 
        elif lunar.result == 'MISS':
            sprite = SPRITES['freefall'] 
        elif lunar.motor>0.8:
            sprite = SPRITES['fullpower'] 
        elif lunar.motor>0.6:
            sprite = SPRITES['halfpower'] 
        elif lunar.motor>0.2:
            sprite = SPRITES['lowpower'] 
        elif lunar.motor>0.0:
            sprite = SPRITES['landingpower'] 
        else:
            sprite = SPRITES['freefall'] 
                
        for idx, v in enumerate(SPRITES.values()):
            screen.blit(v, (100, 100+(16*2*idx)))
            
        screen.blit(background, (0, 0))
        screen.blit(sprite, (lunar.x-10, Y_SIZE-lunar.y-10))
        render_text(s)
        pygame.display.flip()

while one_run():
    pass
    