import os
import sys
import pygame
import random
from pygame.locals import *
from StateTemplates import *
from PlayerStates import *
from AIStates import *
from GameClasses import *

def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    image = pygame.image.load(fullname)
    image = image.convert_alpha()
    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0,0))
        image.set_colorkey(colorkey, RLEACCEL)
    return image, image.get_rect()

pygame.init()
pygame.font.init()
screen = pygame.display.set_mode((500, 500))
pygame.display.set_caption('Basic Pygame program')
BASE_SLOTS = ['left_hand', 'right_hand', 'helmet', 'legs', 'body', 'head']
BASE_DROP_CHANCE = 1
CAMERA = [0, 0]

BASE_IMAGE, BASE_RECT = load_image('base_image.png')
CRATE_IMAGE, CRATE_RECT = load_image('crate.png')
FIREBALL_IMAGE, FIREBALL_RECT = load_image('fireball.png')
ZOMBIE_IMAGE, ZOMBIE_RECT = load_image('zombie.png')
ZOMBIE_SPAWNER_IMAGE, ZOMBIE_SPAWNER_RECT = load_image('zombie_spawner.png')
HERO_IMAGE, HERO_RECT = load_image('hero.png')
background_im, background_rect = load_image('background.bmp')
background2_im, background2_rect = load_image('background2.bmp')
ground_im, ground_rect = load_image('earth.png')
myfont = pygame.font.SysFont('timesnewroman', 20)

GROUND_LEVEL = 400
ground_rect.move_ip(0, GROUND_LEVEL)
screen.blit(ground_im, ground_rect)



class fsm_adam():
    def update(self):
        self.fsm.update()

    def change_state(self, new_state):
        self.fsm.change_state(new_state)

class image_adam():
    def __init__(self, scene, rect, image, x = 0, y = 0):
        self.scene = scene
        self.image = image
        self.rect = rect.move(x, GROUND_LEVEL - rect.height - y)
        self.x = x
        self.y = y
        self.is_crate = False
        self.spiritual = False
        self.is_enemy = False
        self.is_living_adam = False

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

    def destroy(self):
        self.scene.del_object(self)


class hp_adam(image_adam):
    def __init__(self, scene, rect, image, x = 0, y = 0):
        image_adam.__init__(self, scene, rect, image, x, y) 
        self.hp = 1   
        self.speed = 1
        self.base_attack_damage = 1
        self.is_enemy = False
        self.is_living_adam = False       
        self.spiritual = False    
        self.orientation = 'R'

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
            self.hp = 0
            self.destroy()

    def attack_target(self):
        if self.target == None:
            return
        else:
            self.attack(self.target)

    def get_attack_damage(self):
        return base_attack_damage

    def attack(self, agent):
        agent.take_damage(self.get_attack_damage())


class true_adam(hp_adam, fsm_adam):
    def __init__(self, scene, rect, image, x = 0, y = 0):
        hp_adam.__init__(self, scene, rect, image, x, y)
        self.scene = scene


class enemy_adam(true_adam):
    def __init__(self, scene, rect, image, x, y):
        true_adam.__init__(self, scene, rect, image, x, y)
        self.drop_chance = BASE_DROP_CHANCE

    def destroy(self):
        true_adam.destroy(self)
        player.give_exp(self.exp_reward)
        x = random.random()
        if x <= self.drop_chance:
            self.scene.player.add_loot(GENERATE_RANDOM_ITEM())

class FireBall(hp_adam):
    def __init__(self, scene, host, x, y):
        hp_adam.__init__(self, scene, FIREBALL_RECT, FIREBALL_IMAGE, x, y)
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
        for item in self.scene.Objects:
            if not item.spiritual and checking_rect.colliderect(item.get_rect()) and item.is_enemy:
                item.take_damage(self.damage, 'fire')
                self.scene.del_object(self)


class Item():
    def __init__(self, name, typ, slot, damage, armour, weight):
        (self.name, self.typ, self.slot, self.damage, self.armour, self.weight) = (name, typ, slot, damage, armour, weight)


sword = Item('sword', 'sword', 'right_hand', 5, 0, 5)


def GENERATE_RANDOM_ITEM():
    return sword



class Spell:
    def __init__(self, manacost, cast):
        self.manacost = manacost
        self.cast = cast

    def use(self, host):
        host.change_mana(-self.manacost)
        self.cast(host)

class Wand(Item):
    def __init__(self, name, spell):
        Item.__init__(self, name, 'wand', 'right_hand', 0, 0, 1)
        self.spell = spell

    def use(self, host):
        if host.get_mana() >= self.spell.manacost:
            self.spell.use(host)

def Cast_fireball(host):
    host.scene.add_object(FireBall(host.scene, host, host.x, host.y + 30))

SummonFireball = Spell(50, Cast_fireball)
fireball_wand = Wand('firewand', SummonFireball)

class player_adam(true_adam):
    def __init__(self, scene):
        true_adam.__init__(self, scene, HERO_RECT, HERO_IMAGE, 0, 0)
        self.fsm = StateMachine(self, PlayerIdle)
        self.key_pressed = 'NONE'
        self.is_living_adam = True
        self.hp = 10
        self.mana = 200
        self.max_mana = 200
        self.max_hp = 10
        self.mana_regen = 50
        self.speed = 2
        self.exp = 0
        self.lvl = 1
        self.skill_points = 0
        self.equip = Doll(self)
        self.inv = Inventory(self)
        self.equip.try_equip(fireball_wand)
        self.loot = [-1]

    def add_loot(self, item):
        self.loot.append(item)

    def take_loot(self, ind):
        if self.inv.is_full():
            return
        self.inv.add_item(self.loot[ind])
        self.loot[ind] = -1

    def get_loot_name(self, ind):
        if self.loot[ind] == -1:
            return('None')
        return self.loot[ind].name

    def update(self):
        true_adam.update(self)
        self.change_mana(self.mana_regen)

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
                self.try_attack()

    def spend_mana(self, x):
        if self.mana - x >= 0:
            self.mana -= x
            return True
        return False

    def change_mana(self, x):
        self.mana += x
        if self.mana < 0 :
            self.mana = 0
        if self.mana > self.max_mana:
            self.mana = self.max_mana

    def try_attack(self):
        if self.equip.get_tag('right_hand') == -1:
            checking_rect = self.rect.inflate(self.base_attack_range, 0)
            if self.orientation == 'L':
                checking_rect = checking_rect.move(-self.base_attack_range)
            for item in self.scene.Objects:
                if not item.spiritual and checking_rect.colliderect(item.get_rect()) and item.is_enemy:
                    self.attack(item)
        elif self.equip.get_tag('right_hand').typ == 'wand':
            self.equip.get_tag('right_hand').use(self)

    def give_exp(self, x):
        self.exp += x
        while self.exp > self.exp_to_next_lvl():
            self.exp -= self.exp_to_next_lvl()
            self.levelup()

    def exp_to_next_lvl(self):
        return self.lvl * 100

    def levelup(self):
        self.lvl += 1
        self.give_sp(2)

    def give_sp(self, x):
        self.skill_points += x

    def has_sp(self):
        return self.skill_points > 0

    def spend_sp_on_mana(self):
        if self.has_sp():
            self.skill_points -= 1
            self.max_mana += 10

    def spend_sp_on_hp(self):
        if self.has_sp():
            self.skill_points -= 1
            self.max_hp += 10

    def equip_inventory_slot(self, ind):
        tmp1 = self.inv.get_ind(ind)       
        if tmp1 == -1:
            return
        tmp2 = self.equip.get_tag(tmp1.slot)
        slot = tmp1.slot
        if tmp2 == -1:
            self.equip.set_tag(slot, tmp1)
            self.inv.erase_ind(ind)
            return
        self.inv.set_ind(ind, tmp2)
        self.equip.set_tag(slot, tmp1)

    def get_inventory_slot(self, ind):
        return self.inv.get_ind_name(ind)

    def get_mana(self):
        return self.mana

    def unequip(self, tag):
        if self.inv.is_full():
            return
        tmp = self.equip.get_tag(tag)
        if tmp == -1:
            return
        self.equip.clear_tag(tmp.slot)
        self.inv.add_item(tmp)

class Zombie(enemy_adam):
    def __init__(self, scene, x, y):
        enemy_adam.__init__(self, scene, ZOMBIE_RECT, ZOMBIE_IMAGE, x, y)
        self.speed = 1
        self.fsm = StateMachine(self, EnemyIdle)
        self.is_enemy = True
        self.target = None
        self.orientation = 'L'
        self.attack_distance = 20
        self.attack_damage = 1
        self.hp = 2
        self.exp_reward = 5

    def update_target(self):
        closest_target = None
        dist = 0
        for item in self.scene.Objects:
            if not item.is_enemy and item.is_living_adam and item.hp > 0:
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

    def cancel_target(self):
        self.target = None


class ZSpawner(enemy_adam):
    def __init__(self, scene, ticks, child, x):
        enemy_adam.__init__(self, scene, ZOMBIE_SPAWNER_RECT, ZOMBIE_SPAWNER_IMAGE, x, 0)
        (self.ticks, self.child, self.spawning_point) = (ticks, child, x)
        self.current_tick = 0
        self.is_enemy = True
        self.is_living_adam = False
        self.spiritual = False
        self.hp = 10
        self.fsm = StateMachine(self, SpawnerIdle)
        self.exp_reward = 100

    def spawn(self):
        tmp_child = self.child(self.scene, self.spawning_point, 0)
        self.scene.add_object(tmp_child)


def get_string_of_player_status():
    s = ''
    s += 'hp: ' + str(player.hp) + '/' + str(player.max_hp)
    s += ' mana: ' + str(player.mana) + '/' + str(player.max_mana)
    s += ' exp: ' + str(player.exp) + '/' + str(player.exp_to_next_lvl())
    s += ' lvl: ' + str(player.lvl)
    return s


class SceneManager():
    def __init__(self):
        self.data = dict()
        self.current_scene = None
        self.current_tag = '_'
        self.prev_tag = '_'

    def add_scene(self, scene, tag):
        self.data[tag] = scene
        scene.load()

    def switch_scene(self, tag):
        print('1:', self.current_tag, self.prev_tag)
        self.prev_tag = self.current_tag
        self.current_scene = self.data[tag]
        self.current_tag = tag
        print('2:', self.current_tag, self.prev_tag)

    def switch_to_prev(self):
        self.switch_scene(self.prev_tag)

    def run(self):
        while 1:
            event_queue = pygame.event.get()
            for event in event_queue:
                if event.type == QUIT:
                    return 
                if event.type == KEYDOWN and event.key == K_TAB:
                    if self.current_tag != 'game_menu':
                        self.switch_scene('game_menu')
                    else:
                        self.switch_to_prev()
            self.update_current_scene(event_queue)
            pygame.time.delay(100)

    def update_current_scene(self, events):
        if self.current_scene != None:
            self.current_scene.update(events)

class Scene():
    def __init__(self, screen, background_im):
        self.Objects = set()
        self.DeadObjects = set()
        self.NewObjects = set()
        self.need_loading = False
        self.screen = screen
        self.background_im = background_im

    def add_object(self, x):
        self.NewObjects.add(x)
    
    def del_object(self, x):
        self.DeadObjects.add(x)

    def update_set_of_objects(self):
        for item in self.DeadObjects:
            self.Objects.discard(item)
        self.DeadObjects = set()

        for item in self.NewObjects:
            self.Objects.add(item)
        self.NewObjects = set()

    def update(self, events):
        self.screen.blit(self.background_im, (0, 0))
        self.update_set_of_objects()
        for i in self.Objects:
            i.update()
            i.draw()
        pygame.display.update()


class BattleScene(Scene):
    def __init__(self, screen, text = 'empty_scene.txt', background = background2_im):
        Scene.__init__(self, screen, background)
        self.data = text
        self.run = False
        self.pause = False
        self.need_loading = True

    def load(self):
        x = open(self.data)
        for i in x.readlines():
            s, p = i.split()
            p = int(p)
            if s == 'zspawner':
                self.add_object(ZSpawner(self, 20, Zombie, p))
        self.need_loading = False

    def start(self):
        self.run = True
        self.load()

    def pause(self):
        self.pause = not self.pause     

    def update(self, events):
        Scene.update(self, events)
        if self.pause:
            return
        for event in events:
            if event.type == QUIT:
                self.run = False
                return
            elif event.type == KEYDOWN or event.type == KEYUP:
                self.player.translate_event(event)  

        textsurface = myfont.render(get_string_of_player_status(), False, (255, 255, 0))
        screen.blit(background_im, (0, 0))
        screen.blit(ground_im, ground_rect)
        screen.blit(textsurface, (0, 0))

        for item in self.Objects:
            item.update()
        for item in self.Objects:
            item.draw()

        pygame.display.update()

    def add_player(self, x):
        self.add_object(x)
        self.player = x
        player.scene = self

class MenuScene(Scene):
    def __init__(self, screen, background = background_im):
        Scene.__init__(self, screen, background)
        self.need_loading = True

    def load(self):
        self.add_object(UpdatingLabel(get_string_of_player_status, 10, 0))
        self.add_object(UpdatingLabel(lambda: 'Skill points: ' + str(player.skill_points), 10, 25))
        self.add_object(Button('Increase maximum mana', 10, 50, player.spend_sp_on_mana, player.has_sp))
        self.add_object(Button('Increase maximum hp', 10, 75, player.spend_sp_on_hp, player.has_sp))
        self.add_object(InventorySlotLabel(player, 0, 10, 100))
        self.add_object(InventorySlotLabel(player, 1, 10, 125))
        self.add_object(InventorySlotLabel(player, 2, 10, 150))
        self.add_object(InventorySlotLabel(player, 3, 10, 175))
        self.add_object(InventorySlotLabel(player, 4, 10, 200))
        self.add_object(InventorySlotLabel(player, 5, 10, 225))
        self.add_object(Label('Equip:', 10, 250))
        self.add_object(EquipSlotLabel(player, 'left_hand', 10, 275))
        self.add_object(EquipSlotLabel(player, 'right_hand', 10, 300))
        self.add_object(EquipSlotLabel(player, 'body', 10, 325))
        self.add_object(EquipSlotLabel(player, 'head', 10, 350))
        self.add_object(Label('Loot:', 220, 25))
        self.add_object(LootLabel(220, 50))
        

        self.need_loading = False 
       

class Label():
    def __init__(self, text, x, y):
        self.surf = myfont.render(text, True, (255, 255, 255))
        self.x, self.y = x, y

    def update(self):
        pass

    def draw(self):
        screen.blit(self.surf, (self.x, self.y))

class UpdatingLabel(Label):
    def __init__(self, f, x, y):
        self.surf = myfont.render(f(), True, (255, 255, 255))
        self.x, self.y = x, y
        self.text = f

    def update(self):
        self.surf = myfont.render(self.text(), True, (255, 255, 255))


class Button:
    def __init__(self, text, x, y, command, activation_condition = lambda: True):
        self.surf = myfont.render(text, True, (255, 255, 255))
        self.rect = self.surf.get_rect()
        self.rect = self.rect.move(x, y)
        self.command = command
        self.active = activation_condition
        self.howered = False
        self.pressed = True

    def draw(self):
        if not self.active():
            pygame.draw.rect(screen, (50, 50, 50), self.rect)
        elif self.pressed:
            pygame.draw.rect(screen, (180, 180, 180), self.rect)
        elif self.howered:
            pygame.draw.rect(screen, (100, 100, 100), self.rect)
        else:
            pygame.draw.rect(screen, (50, 50, 50), self.rect)
        screen.blit(self.surf, self.rect)

    def update(self):
        mouse_on_button = self.rect.collidepoint(pygame.mouse.get_pos())
        mouse_is_pressed = pygame.mouse.get_pressed()[0]
        if mouse_on_button:
            self.howered = True
            if pygame.mouse.get_pressed()[0]:
                self.pressed = True
        if self.pressed and mouse_on_button and not mouse_is_pressed and self.active():
            self.command()
            self.pressed = False
        if not mouse_on_button:
            self.howered = False
            self.pressed = False

class InventorySlotLabel:
    def __init__(self, host, ind, x, y):
        self.x = x
        self.y = y
        self.ind = ind
        self.host = host
        self.ind_label = Label(str(ind), x, y)
        self.item_label = UpdatingLabel(lambda: player.get_inventory_slot(self.ind), x + 20, y)
        self.equip_button = Button('equip', x + 150, y, lambda: host.equip_inventory_slot(self.ind))

    def update(self):
        self.ind_label.update()
        self.item_label.update()
        self.equip_button.update()

    def draw(self):
        self.ind_label.draw()
        self.item_label.draw()
        self.equip_button.draw()

class EquipSlotLabel:
    def __init__(self, host, tag, x, y):
        self.x = x
        self.y = y
        self.tag = tag
        self.host = host
        self.tag_label = Label(tag, x, y)
        self.item_label = UpdatingLabel(lambda: player.equip.get_tag_text(self.tag), x + 100, y)
        self.unequip_button = Button('unequip', x + 200, y, lambda: host.unequip(self.tag), lambda: host.equip.get_tag(tag) != -1)

    def update(self):
        self.tag_label.update()
        self.item_label.update()
        self.unequip_button.update()

    def draw(self):
        self.tag_label.draw()
        self.item_label.draw()
        self.unequip_button.draw()

class LootLabel:
    def __init__(self, x, y):
        self.ind = 0
        self.prev_button = Button('prev', x, y, lambda: self.prev(), lambda: self.ind > 0)
        self.text1 = UpdatingLabel(lambda: player.get_loot_name(self.ind), x + 50, y)
        self.take_button = Button('take', x + 150, y, lambda: player.take_loot(self.ind), lambda: player.loot[self.ind] != -1)
        self.next_button = Button('next', x + 200, y, lambda: self.next(), lambda: self.ind < len(player.loot) - 1)

    def prev(self):
        self.ind -= 1

    def next(self):
        self.ind += 1

    def update(self):
        self.prev_button.update()
        self.text1.update()
        self.take_button.update()
        self.next_button.update()

    def draw(self):
        self.prev_button.draw()
        self.text1.draw()
        self.take_button.draw()
        self.next_button.draw()


class CrateLabel:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.b_prev = Button()


zombie = BattleScene(screen, 'zombie_spawner_scene.txt')
player = player_adam(zombie)
zombie.add_player(player)

Manager = SceneManager()
Manager.add_scene(zombie, 'zomb')
Manager.add_scene(MenuScene(screen), 'game_menu')
Manager.switch_scene('zomb')
Manager.run()