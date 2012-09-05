# encoding=utf-8
import time
import progress
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
        textRect.top = screen.get_rect().top+4
        _last_text = {"s":s, 'text':text, 'textRect':textRect}
    screen.blit(_last_text['text'], _last_text['textRect'])    

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
        self.motor_max = 2.0
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
                if self.y<=0.0 and self.yv>=-2.0:
                    self.result = 'LAND'
                elif self.y<=0.0:
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
    
    box = pygame.Surface((10, 10))
    box = box.convert()
    box.fill((255, 255, 255))
    while keepGoing:
    
        clock.tick(30)
    
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:            
                keys = [event.key]
                if event.key == pygame.K_q:
                    return False # QUIT Command
                elif event.key == pygame.K_n:
                    return True # START OVER
                elif event.key == pygame.K_UP:
                    lunar.throttle(True) # THROTTLE UP
                elif event.key == pygame.K_DOWN:
                    lunar.throttle(False)
    
        s = lunar.game_tick()          
        
        if lunar.result == 'LAND':
            box.fill((0, 255, 0))
        elif lunar.result == 'CRASH':
            box.fill((255, 0, 0))
        elif lunar.result == 'MISS':
            box.fill((0, 0, 255))
        elif lunar.motor>0.0:
            box.fill((200,88,0))
        else:
            box.fill((255,255,255))
                

        screen.blit(background, (0, 0))
        screen.blit(box, (lunar.x-10, Y_SIZE-lunar.y-10))
        render_text(s)
        pygame.display.flip()

while one_run():
    pass
    