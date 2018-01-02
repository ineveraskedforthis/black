import os
import sys
import pygame
from pygame.locals import *
from StateTemplates import *
from PlayerStates import *
from AIStates import *


pygame.init()
screen = pygame.display.set_mode((500, 500))
pygame.display.set_caption('Basic Pygame program')

def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    image = pygame.image.load(fullname)
    image = image.convert_alpha()
    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0,0))
        image.set_colorkey(colorkey, RLEACCEL)
    return image, image.get_rect()

BASE_IMAGE, BASE_RECT = load_image('base_image.png')
CAMERA = [0, 0]
FIREBALL_IMAGE, FIREBALL_RECT = load_image('fireball.png')
ZOMBIE_IMAGE, ZOMBIE_RECT = load_image('zombie.png')
ZOMBIE_SPAWNER_IMAGE, ZOMBIE_SPAWNER_RECT = load_image('zombie_spawner.png')
HERO_IMAGE, HERO_RECT = load_image('hero.png')
Objects = set()
DeadObjects = set()
NewObjects = set()
background_im, background_rect = load_image('background.bmp')

ground_im, ground_rect = load_image('earth.png')
GROUND_LEVEL = 400
ground_rect.move_ip(0, GROUND_LEVEL)
screen.blit(ground_im, ground_rect)


class fsm_adam():
    def update(self):
        self.fsm.update()

    def change_state(self, new_state):
        self.fsm.change_state(new_state)


class image_adam():
    def __init__(self, rect = BASE_RECT, image = BASE_IMAGE, x = 0, y = 0):
        self.image = image
        self.rect = rect.move(x, GROUND_LEVEL - rect.height - y)
        self.x = x
        self.y = y

    def draw(self):
        tmpRect = self.get_rect().move(CAMERA[0], CAMERA[1])
        screen.blit(self.get_image(), tmpRect)

    def get_rect(self):
        return self.rect

    def get_image(self):
        return self.image

    def move(self, x, y):
        self.rect = self.rect.move(x, -y)
        self.x += x
        self.y += y
        if self.y < 0:
            self.y = 0

    def dist(self, agent):
        return abs(self.x - agent.x)


class hp_adam(image_adam):
    def __init__(self, rect = BASE_RECT, image = BASE_IMAGE, x = 0, y = 0):
        image_adam.__init__(self, rect, image, x, y) 
        self.hp = 1   
        self.speed = 1
        self.attack_damage = 1
        self.is_enemy = False
        self.is_living_adam = False       
        self.spiritual = False    
        self.orientation = 'R'

    def destroy(self):
        DeadObjects.add(self)

    def step_right(self):
        self.set_orientation('R')
        self.move(self.speed, 0)

    def step_left(self):
        self.set_orientation('L')
        self.move(-self.speed, 0)

    def set_orientation(self, orientation):
        if self.orientation == orientation:
            return
        self.orientation = orientation
        self.image = pygame.transform.flip(self.image, True, False)

    def take_damage(self, x, type = 'phys'):
        self.change_hp(-x)

    def change_hp(self, x):
        self.hp += x
        if self.hp <= 0:
            self.destroy()

    def attack_target(self):
        if self.target == None:
            return
        else:
            self.attack(self.target)

    def attack(self, agent):
        agent.take_damage(self.attack_damage)


class true_adam(hp_adam, fsm_adam):
    def __init__(self, rect = BASE_RECT, image = BASE_IMAGE, x = 0, y = 0):
        hp_adam.__init__(self, rect, image, x, y)


class FireBall(hp_adam):
    def __init__(self, host, x, y):
        hp_adam.__init__(self, FIREBALL_RECT, FIREBALL_IMAGE, x, y)
        self.speed = 5
        self.host = host
        self.orientation = host.orientation
        self.spiritual = True
        self.damage = 1

    def update(self):
        self.check_collisions(self.speed)
        if self.orientation == 'R':
            self.move(self.speed, 0)
        else:
            self.move(-self.speed, 0)
        if abs(self.x - self.host.x) >= 500:
            self.destroy()

    def check_collisions(self, speed):
        checking_rect = self.get_rect().inflate(speed, 0)
        for item in Objects:
            if not item.spiritual and checking_rect.colliderect(item.get_rect()) and item.is_enemy:
                item.take_damage(self.damage, 'fire')
                self.destroy()


class player_adam(true_adam):
    def __init__(self):
        true_adam.__init__(self, HERO_RECT, HERO_IMAGE, 0, 0)
        self.fsm = StateMachine(self, PlayerIdle)
        self.key_pressed = 'NONE'
        self.is_living_adam = True
        self.hp = 10

    def update(self):
        fsm_adam.update(self)
        print(self.x, self.y)
   #     self.move(0, -1)

    def translate_event(self, event):
        key = event.key
        if event.type == KEYUP:
            self.key_pressed = 'NONE'
        elif event.type == KEYDOWN:
            if key == K_d:
                self.key_pressed = 'RIGHT'
            if key == K_a:
                self.key_pressed = 'LEFT'
            if key == K_w:
                self.key_pressed = 'UP'
            if key == K_s:
                self.key_pressed = 'DOWN'
            if key == K_e:
                self.cast_magic()

    def cast_magic(self):
        tmp = FireBall(self, self.x + 4, self.y + 30)
        Objects.add(tmp)


class Enemy(true_adam):
    def __init__(self, x, y):
        true_adam.__init__(self, ZOMBIE_RECT, ZOMBIE_IMAGE, x, y)
        self.speed = 1
        self.fsm = StateMachine(self, EnemyIdle)
        self.is_enemy = True
        self.target = None
        self.orientation = 'L'
        self.attack_distance = 20
        self.attack_damage = 1
        self.hp = 2

    def update_target(self):
        closest_target = None
        dist = 0
        for item in Objects:
            if not item.is_enemy and item.is_living_adam:
                if closest_target == None:
                    closest_target = item
                    dist = self.dist(item)
                elif self.dist(item) < dist:
                    closest_target = item
                    dist = self.dist(item)
        self.target = closest_target

    def move_to_target(self):
        if self.target == None:
            return
        else:
            if self.target.x > self.x:
                self.step_right()
            else:
                self.step_left()

    def distance_to_target(self):
        if self.target == None:
            return 9999
        else:
            return self.dist(self.target)

    def get_attack_distance(self):
        return self.attack_distance


class ZSpawner(true_adam):
    def __init__(self, ticks, child, x):
        true_adam.__init__(self, ZOMBIE_SPAWNER_RECT, ZOMBIE_SPAWNER_IMAGE, x)
        (self.ticks, self.child, self.spawning_point) = (ticks, child, x)
        self.current_tick = 0
        self.is_enemy = False
        self.is_living_adam = False
        self.spiritual = False
        self.hp = 10
        self.fsm = StateMachine(self, SpawnerIdle)        

    def spawn(self):
        tmp_child = self.child(self.spawning_point, 0)
        NewObjects.add(tmp_child)



player = player_adam()
zombie_spawner = ZSpawner(20, Enemy, 400)
Objects.add(player)
Objects.add(zombie_spawner)

screen.blit(background_im, (0, 0))
player.draw()
pygame.display.update()  

while 1:
    for event in pygame.event.get():
        if event.type == QUIT:
            exit()
        elif event.type == KEYDOWN or event.type == KEYUP:
            player.translate_event(event)                    
    
    screen.blit(background_im, (0, 0))
    screen.blit(ground_im, ground_rect)
    for item in DeadObjects:
        Objects.discard(item)
    DeadObjects = set()
    for item in NewObjects:
        Objects.add(item)
    NewObjects = set()

    for item in Objects:
        item.update()
    for item in Objects:
        item.draw()
    pygame.display.update()
    pygame.time.delay(100)