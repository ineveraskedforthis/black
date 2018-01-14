import os
import sys
import pygame
from pygame.locals import *

def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    image = pygame.image.load(fullname)
    image = image.convert_alpha()
    if colorkey is not None:
        if colorkey is None:
            colorkey = image.get_at((0,0))
        image.set_colorkey(colorkey, RLEACCEL)
    return image, image.get_rect()




class Spell
    def __init__(self, tag, manacost = 0)
        self.tag = tag
        self.manacost = manacost

    def cast(self, host = None, target = None):
        pass

class Projectile(hp_adam):
    def __init__(self, Host, Scene, Image, Rect, Name, Power, Speed, MaxDistance = 500, Pierce = 1, Update = None, CheckCollisions = None, Action = None):
        hp_adam.__init__(self, Scene, Rect, Image, Host.x, Host.y + 20)
        self.host = Host
        if Update != None:
            self.update = Update
        if CheckCollisions != None:
            self.check_collisions = CheckCollisions
        if Action != None:
            self.action = Action
        self.orientation = 'R'        
        self.name = Name
        self.power = Power
        self.pierce = Pierce
        self.max_distance = MaxDistance
        self.speed = Speed
        self.set_orientation(self.host.orientation)
        self.spiritual = True
        self.is_enemy = False
        self.pierced = 0

    def update(self):
        hp_adam.update(self)
        self.check_collisions()
        if self.orientation == 'R':
            self.move(self.speed, 0)
        else:
            self.move(-self.speed, 0)

        if abs(self.x - self.host.x) >= self.max_distance:
            self.destroy()
    
    def check_collisions(self):
        checking_rect = self.get_rect().inflate(self.speed, 0)
        if self.orientation == 'L':
            checking_rect.move_ip(self.speed, 0)
        for item in self.scene.Objects:
            if checking_rect.colliderect(item.get_rect()) and item.is_enemy:
                self.action(item)
                self.pierced += 1
                if self.pierced = self.pierce:
                    self.destroy()

    def action(self, agent):
        agent.take_damage(self.power, 'fire')


class ProjectileSpell(Spell):
    def __init__(self, tag, power, manacost = 0, pierce = 0):
        Spell.__init__(self, tag, manacost)
        self.image, self.rect = load_image(tag)
        self.power = power
        self.bonus_power = 0

    def increase_power(self, x):
        self.bonus_power = x

    def cast(self, host)
        if host.mana >= self.manacost:
            tmp = Projectile(host, host.scene, self.image, self.rect, self.name, self.power + self.bonus_power, self.speed)
            host.scene.add_object(tmp)
            host.change_mana(-self.manacost)


class SummonSpell(Spell):
    def __init__(self, tag, summon_tag, manacost):
        Spell.__init__(tag, manacost)
        self.summon = summon_tag

    def cast(self, host):
        tmp = Creature[self.summon_tag](host.scene, host.x)
        host.scene.add_object(tmp)


def load_spells():
    Spellbook = Dict()
    x = open('spells.txt').readlines()
    n = int(x[0])
    for i in range(1, n + 1):
        s = x.split()
        if s[1] == 'projectile':
            Spellbook[s[0]] = ProjectileSpell(s[0], int(s[2]), int(s[3]))
        if s[1] == 'summon':
            Spellbook[s[0]] = SummonSpell(s[0], s[2], int(s[3]))
    return Spellbook