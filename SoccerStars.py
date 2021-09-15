import kivy
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, ReferenceListProperty, ObjectProperty, BooleanProperty
from kivy.core.window import Window
from kivy.vector import Vector
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
from math import *

Window.size = (600, 950)

class Lopta(Widget):
    velocity_x = NumericProperty(0)
    velocity_y = NumericProperty(0)

    velocity = ReferenceListProperty(velocity_x,velocity_y)

    def move(self): 
        self.pos = Vector(*self.velocity) + self.pos    
        self.velocity_x *= 0.9
        self.velocity_y *= 0.9
        if abs(self.velocity_x) <= 0.5:
            self.velocity_x = 0
        if abs(self.velocity_y) <= 0.5:
            self.velocity_y = 0

    def ball_collide(self, player):
        if sqrt((self.center_x - player.center_x)**2 + (self.center_y - player.center_y)**2) <= (self.width /2) + (player.width/2):
            pocx = (player.center_x + self.center_x)/2  #koordinata u kojima se lopta
            pocy = (player.center_y + self.center_y)/2  # i igrač dodiruju, poc = point of collision
            if pocy == self.y:
                k = 0
            else:
                k = (self.x - pocx)/(pocy - self.y) #derivacija u točki dodira kugla, kako bi mogao odrediti kut pod kojima će se one odbiti
            
            if abs(k) > 0.4:
                kut_1 = degrees(atan(k)) 
            else:
                kut_1 = 0
            vel1 = Vector(self.velocity).rotate(kut_1)
            player.velocity = vel1 /2
            
            kut_2 = degrees(atan(-1/k))
            vel2 = Vector(self.velocity).rotate(kut_2)
            self.velocity = vel2 /2
            
            player.move()
            self.move()

class Igrac(Widget):
    score = NumericProperty(0)
    velocity_x = NumericProperty(0)
    velocity_y = NumericProperty(0)

    velocity = ReferenceListProperty(velocity_x, velocity_y)

    def move(self):
        self.pos = Vector(*self.velocity) + self.pos
                
        #stalno smanjivanje brzine igrača
        self.velocity_x *= 0.9
        self.velocity_y *= 0.9
        print(self.velocity)
        if abs(self.velocity_x) <= 0.5:
            self.velocity_x = 0
        if abs(self.velocity_y) <= 0.5:
            self.velocity_y = 0
        
    #sudar dva igraca
    def player_collide(self, player):
        if sqrt((self.center_x - player.center_x)**2 + (self.center_y - player.center_y)**2) <= (self.width /2) + (player.width/2):     
            pocx = (player.center_x + self.center_x)/2  #koordinate dodira
            pocy = (player.center_y + self.center_y)/2  #dve kugle
            if pocy == self.y:
                k = 0
            else:
                k = (self.x - pocx)/(pocy - self.y) #derivacija u točki dodira kugla, kako bi mogao odrediti kut pod kojima će se one odbiti
            
            
            if abs(k) > 0.4:
                kut_1 = degrees(atan(k))
            else:
                kut_1 = 0
            vel1 = Vector(self.velocity).rotate(kut_1)
            player.velocity = vel1 

            kut_2 = degrees(atan(-1/k))
            vel2 = Vector(self.velocity).rotate(kut_2)
            self.velocity = vel2 /2
            
            player.move()
            self.move()
    
class Igra(Widget):
    lopta = ObjectProperty(None)

    igrac1 = ObjectProperty(None)
    igrac2 = ObjectProperty(None)

    slijed = BooleanProperty(None) #provjerava ako si kliknuo igraca koji je na redu
    red = NumericProperty(1) #broji red odigranih koraka kako bi se znalo tko je na redu

    publika = SoundLoader.load("source/sound1.mp3").play()
    goal = SoundLoader.load("source/sound2.mp3")

    #kad se klikne provjerava koji je igrac kliknut
    def on_touch_down(self, touch):
        if self.igrac1.collide_point(*touch.pos):
            self.slijed = True
        elif self.igrac2.collide_point(*touch.pos):
            self.slijed = False
    
    #kad se otpusti klik, provjerava zadnja pozicija klika te se računa brzina koja se nadodaje igraču
    def on_touch_up(self, touch):
        if self.slijed and self.red % 2 == 1:
            self.igrac1.velocity_x = int((self.igrac1.center_x - touch.x)*3/4)
            self.igrac1.velocity_y = int((self.igrac1.center_y - touch.y)*3/4)
            self.slijed = BooleanProperty(None)
            self.red += 1
        elif self.red % 2 == 0 and not self.slijed:
            self.igrac2.velocity_x = int((self.igrac2.center_x - touch.x)*3/4)
            self.igrac2.velocity_y = int((self.igrac2.center_y - touch.y)*3/4)
            self.slijed = BooleanProperty(None)
            self.red += 1

    def restart(self):
        self.goal.play()
        self.lopta.center = (300, 454)
        self.lopta.velocity = (0,0)
        self.igrac1.center = (300, 200)
        self.igrac1.velocity = (0,0)
        self.igrac2.center = (300, 708)
        self.igrac2.velocity = (0,0)

    def update(self, dt):
        #pokretanje funkcije kretanja igraca, 60x u sekundi provodi micanje igraca        
        #provjerava i provodi odbijanje između igrača i igrača s loptom
        if self.igrac1.velocity_y != 0 or self.igrac2.velocity_x != 0:
            self.igrac1.move()
            self.igrac1.player_collide(self.igrac2)
            self.igrac1.player_collide(self.lopta)
        if self.igrac2.velocity_y != 0 or self.igrac2.velocity_y != 0:
            self.igrac2.move()
            self.igrac2.player_collide(self.igrac1)
            self.igrac2.player_collide(self.lopta)
        if self.lopta.velocity_y != 0 or self.lopta.velocity_x != 0:
            self.lopta.move()
            self.lopta.ball_collide(self.igrac1)
            self.lopta.ball_collide(self.igrac2)

        #Odbijanje od zidova terena
        if (self.igrac1.x <= 0) or (self.igrac1.right >= 600):
            self.igrac1.velocity_x *= -1
            self.igrac1.move()
        if (self.igrac1.y <= 0) or (self.igrac1.top >= 908):
            self.igrac1.velocity_y *= -1
            self.igrac1.move()
        if (self.igrac2.x <= 0) or (self.igrac2.right >= 600):
            self.igrac2.velocity_x *= -1
            self.igrac2.move()
        if (self.igrac2.y <= 0) or (self.igrac2.top >= 908):
            self.igrac2.velocity_y *= -1
            self.igrac2.move()
        
        #Odbijanje lopte od zidova i restartanje igre u slučaju gola
        if  (self.lopta.x <= 0) or (self.lopta.right >= 600):
            self.lopta.velocity_x *= -1
            self.lopta.move()
        if (self.lopta.y <= 0):
            self.igrac2.score += 1
            self.restart()
        elif (self.lopta.top >= 908):
            self.igrac1.score +=1
            self.restart()

class SoccerStars(App):
    def build(self):
        igra = Igra()
        Clock.schedule_interval(igra.update, 1.0 / 60.0) #funkcija update se poziva 60x u sekundi
        return igra

if __name__ == "__main__":
    SoccerStars().run()

