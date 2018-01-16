import os
import sys
import pygame
import random
from pygame.locals import *
from StateTemplates import *
from PlayerStates import *
from AIStates import *
from GameClasses import *
from Magic import *

def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    image = pygame.image.load(fullname)
    image = image.convert_alpha()
    if colorkey is not None:
        if colorkey is None:
            colorkey = image.get_at((0,0))
        image.set_colorkey(colorkey, RLEACCEL)
    return image, image.get_rect()




pygame.init()
pygame.font.init()
screen = pygame.display.set_mode((500, 500))
pygame.display.set_caption('game')
myfont = pygame.font.SysFont('timesnewroman', 20)



States = dict()
States['player'] = PlayerIdle
States['enemy'] = EnemyIdle
States['enemy_spawner'] = SpawnerIdle
States['idle'] = IdleState


BASE_SLOTS = ['left_hand', 'right_hand', 'legs', 'body', 'head']
DISPLAYABLE_SLOTS = ['body', 'head', 'left_hand', 'right_hand']
BASE_ANIMATIONS = ['idle', 'move']
DAMAGE_TYPES = ['fire', 'shock', 'cold', 'phys']

background_im, background_rect = load_image('background.bmp')
background2_im, background2_rect = load_image('background2.bmp')
ground_im, ground_rect = load_image('earth.png')
GROUND_LEVEL = 400
ground_rect.move_ip(0, GROUND_LEVEL)


class ViewAdam():
    def __init__(self, scene, tag, side = None, x = 0, y = 0):
        self.scene = scene

        self.animation = dict()
        self.current_animation = 'idle'
        self.current_animation_tick = 0
        self.tag = tag
        image, rect = load_image(tag + '_idle_0.png')
        self.rect = rect.move(x, GROUND_LEVEL - rect.height - y)

        file = open(tag + '_animations.txt')
        for i in file.readlines():
            anim_tag = i.split()[0]
            anim_count = int(i.split()[1])
            self.add_animation_from_tag(anim_tag, anim_count)

        self.x = x
        self.y = y
        self.side = side
        self.orientation = 'R'

    def draw(self):
        self.scene.screen.blit(self.get_image(), self.get_rect())


    def get_rect(self):
        return self.rect

    def get_image(self):
        if self.orientation == 'R':
            return self.animation[self.current_animation][self.current_animation_tick]
        return pygame.transform.flip(self.animation[self.current_animation][self.current_animation_tick], True, False)

    def move(self, x, y):
        self.rect = self.rect.move(x, -y)
        self.x += x
        self.y += y
        if self.y < 0:
            self.y = 0

    def move_to(self, x):
        self.move(-self.x + x, 0)        

    def dist(self, item):
        tmp = self.get_rect()
        rect = item.get_rect()
        if tmp.colliderect(rect):
            return 0
        return min(abs(tmp.left - rect.right), abs(tmp.right - rect.left))

    def destroy(self):
        self.scene.del_object(self)

    def set_orientation(self, orientation):
        if self.orientation == orientation:
            return
        self.orientation = orientation
        self.image = pygame.transform.flip(self.image, True, False)

    def add_animation(self, tag, list_of_image):
        self.animation[tag] = list_of_image

    def add_animation_from_tag(self, tag, count):
        self.animation[tag] = []
        for i in range(count):
            image, tmp = load_image(self.tag + '_' + tag + '_' + str(i) + '.png')
            self.animation[tag].append(image)

    def change_animation(self, tag):
        self.current_animation_tick = 0
        self.current_animation = tag

    def next_image(self):
        self.current_animation_tick += 1
        if self.current_animation_tick >= len(self.animation[self.current_animation]):
            self.current_animation_tick = 0
        return self.animation[self.current_animation][self.current_animation_tick]

    def update(self):
        self.image = self.next_image()
        if self.orientation == 'L':
            self.image = pygame.transform.flip(self.image, True, False)

    def translate_event(self, event):
        pass

    def check_collisions_after(self, speed):
        checking_rect = self.get_rect().inflate(speed, 0)
        if self.orientation == 'L':
            checking_rect.move_ip(speed, 0)
        for item in self.scene.Objects:
            if checking_rect.colliderect(item.get_rect()) and item.root.char.side != self.root.char.side:
                self.root.action(item)
                if self.get('pierce') == self.get('max_pierce'):
                    self.destroy()
                else:
                    self.set('pierce', self.get('pierce') + 1)

class CharacterAdam():
    def __init__(self, tag, x, y = 0, side = 'None'):
        file = open(tag + '.txt')
        self.attributes = dict()
        for s in file.readlines():
            self.translate(s)
        self.x = x
        self.y = y
        self.side = side
        self.target = None

    def translate(self, string):
        a = string.split()
        if a[0] == 'initial_state':
            self.fsm = StateMachine(self, States[a[1]])
            return
        if a[0] == 'spell':
            self.spell = Spells[a[1]]
            return
        self.attributes[a[0]] = int(a[1])

    def update(self):
        self.update_hp()
        self.update_mana()

    def take_damage(self, attack):
        tmp = 0
        for i in DAMAGE_TYPES:
            x = min(0, self.get(i + '_def') - attack.get(i + '_damage'))
            tmp += x
        self.change_hp(tmp)

    def change_hp(self, x):
        self.change_tag('hp', x)

    def change_mana(self, x):
        self.change_tag('mana', x)

    def change_tag(self, tag, x):
        tmp = self.get(tag) + x
        if tmp < 0:
            self.set(tag, 0)
            if tag == 'hp':
                self.destroy()
        elif tmp > self.get('max_' + tag):
            self.set(tag, self.get('max_' + tag))
        else:
            self.set(tag, tmp)

    def attack(self):
        if self.target == None:
            return
        else:
            self.attack(self.target)

    def get(self, tag):
        return self.attributes[tag]

    def set(self, tag, x):
        self.attributes[tag] = x

    def attack(self, agent):
        agent.take_damage(self.get_attack())

    def get_attack(self):
        return Attack(self)

    def update_hp(self):
        self.change_hp(self.get('hp_regen'))

    def update_mana(self):
        self.change_mana(self.get('mana_regen'))

    def step_left(self):
        self.move_left(self.get('speed'))

    def step_right(self):
        self.move_right(self.get('speed'))

    def update_target(self):
        closest_target = None
        dist = 0
        for item in self.scene.Objects:
            if item.side != 'projectile' and item.side != self.side and item.get('hp') > 0:
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

    def dist(self, item):
        return self.root.view.dist(item)

    def distance_to_target(self):
        if self.target == None:
            return 9999
        else:
            return self.dist(self.target)

    def cancel_target(self):
        self.target = None

class AnimatedCharacter(ViewAdam, CharacterAdam):
    def __init__(self, scene, tag, side = None, x = 0):

        ViewAdam.__init__(self, scene, tag, side = side, x = x)
        CharacterAdam.__init__(self, tag, x, side = side)

        self.scene = scene
        self.equip = Doll(self)


    def update(self):
        self.fsm.update()
        ViewAdam.update(self)
        CharacterAdam.update(self)

    def draw(self):
        ViewAdam.draw(self)
        for tag in ['body', 'head', 'left_hand']:
            tmp = self.equip.get_slot(tag)
            if tmp != None:
                tmp = tmp.image
                if self.orientation == 'L':
                    tmp = pygame.transform.flip(tmp, True, False)
                screen.blit(tmp, self.rect)

    def destroy(self):
        self.scene.del_object(self)

    def move_left(self, x):
        self.set_orientation('L')
        self.move(-x, 0)

    def move_right(self, x):
        self.set_orientation('R')
        self.move(x, 0)

    def change_state(self, new_state):
        self.fsm.change_state(new_state)

    def get_with_equip(self, tag):
        return self.get(tag) + self.equip.get(tag)


class Attack:
    def __init__(self, host):
        self.attributes = dict()
        for i in DAMAGE_TYPES:
            self.attributes[i + '_damage'] = host.get_with_equip(i + '_damage')
    
    def get(self, tag):
        return self.attributes[tag]

class PlayerAdam(AnimatedCharacter):
    def __init__(self, scene, tag, x):
        AnimatedCharacter.__init__(self, scene, 'hero', '0')
        self.key_pressed = None
        self.x = x

        self.inv = Inventory(self)
        self.loot = [None]
        self.attributes['exp'] = 0
        self.attributes['lvl'] = 1
        self.attributes['skill_points'] = 0
        self.attributes['money'] = 0
    

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
            if key == K_SPACE:
                if self.x >= 490:
                    print('trying to travel')
                    self.scene.go_next(self)

    def try_attack(self):
        tmp = self.equip.get_slot('right_hand')
        if tmp == None:
            attack_range = self.get('attack_range')
            checking_rect = self.rect.inflate(attack_range, 0)
            if self.orientation == 'L':
                checking_rect = checking_rect.move(-attack_range, 0)
            for item in self.scene.Objects:
                if checking_rect.colliderect(item.get_rect()) and item.side != self.side:
                    self.attack(item)

        elif tmp.typ == 'sword' or tmp.typ == 'spear':
            weap = WeaponInstance(self.scene, tmp.rect, tmp.image, self)
            if self.orientation == 'L':
                weap.set_orientation('L')           
            self.scene.add_object(weap)
            for item in self.scene.Objects:
                if weap.rect.colliderect(item.get_rect()) and item.side != self.side:
                    self.attack(item)

        elif self.equip.get_tag('right_hand').typ == 'wand':
            self.equip.get_tag('right_hand').use(self)

    def add_loot(self, item):
        self.loot.append(item)

    def take_loot(self, ind):
        if self.inv.is_full():
            return
        self.inv.add_item(self.loot[ind])
        self.loot[ind] = None

    def update_loot(self):
        tmp = []
        for i in self.loot:
            if i != None:
                tmp.append(i)
        if len(tmp) == 0:
            tmp = [None]
        self.loot = tmp

    def get_loot_name(self, ind):
        if self.loot[ind] == None:
            return('None')
        return self.loot[ind].get_name()

    def drop(self, ind):
        tmp = self.inv.get_ind(ind)
        if tmp != None:
            self.inv.erase_ind(ind)
            self.add_loot(tmp)

    def equip_inventory_slot(self, ind):
        tmp1 = self.inv.get_ind(ind)       
        if tmp1 == None:
            return
        tmp2 = self.equip.get_tag(tmp1.slot)
        slot = tmp1.slot
        if tmp2 == None:
            self.equip.set_tag(slot, tmp1)
            self.inv.erase_ind(ind)
            return
        self.inv.set_ind(ind, tmp2)
        self.equip.set_tag(slot, tmp1)

    def get_inventory_slot(self, ind):
        return self.inv.get_ind_name(ind)

    def unequip(self, tag):
        if self.inv.is_full():
            return
        tmp = self.equip.get_tag(tag)
        if tmp == None:
            return
        self.equip.clear_tag(tmp.slot)
        self.inv.add_item(tmp)

    def sell(self, ind):
        self.money += self.inv.get_ind(ind).get_cost()
        self.inv.erase_ind(ind)


    def give_exp(self, x):
        tmp = self.get('exp')
        tmp += x
        while tmp >= self.exp_to_next_lvl():
            tmp -= self.exp_to_next_lvl()
            self.levelup()
        self.set('exp', tmp)

    def exp_to_next_lvl(self):
        return self.get('lvl') * 100

    def get(self, tag):
        return self.attributes[tag]

    def set(self, tag, x):
        self.attributes[tag] = x

    def levelup(self):
        self.attributes['lvl'] += 1
        self.give_sp(2)

    def give_sp(self, x):
        self.attributes['skill_points'] += x

    def has_sp(self):
        return self.attributes['skill_points'] > 0

    def spend_sp_on_mana(self):
        if self.has_sp():
            self.attributes['skill_points'] -= 1
            self.set('max_mana', self.get('max_mana') + 10)

    def spend_sp_on_hp(self):
        if self.has_sp():
            self.attributes['skill_points'] -= 1
            self.set('max_hp', self.get('max_hp') + 10)

    def can_trade(self):
        return self.scene.can_trade

class Item():
    def __init__(self, file):
        self.attributes = dict()
        for s in file.readlines():
            self.translate(s)
        self.pre = None
        self.suf = None

    def translate(self, string):
        a = string.split()
        self.attributes[a[0]] = int(a[1])

    def get_full(self, tag, sep = None):
        if sep != None:
            tmp = 0
            if self.suf != None:
                tmp += self.aff.get(tag)
            tmp += sep + self.get(tag) + sep
            if self.pre != None:
                tmp += self.pre.get(tag)
            return tmp
        tmp = 0
        if self.suf != None:
            tmp += self.aff.get(tag)
        tmp += self.get(tag)
        if self.pre != None:
            tmp += self.pre.get(tag)

    def get(self, tag):
        return self.attributes[tag]

    def add_suf(self, suf):
        self.suf = suf

    def add_pre(self, pre):
        self.pre = pre

class ItemMod():
    def __init__(self, file):
        self.attributes = dict()
        for s in file.readlines():
            self.translate(s)

    def translate(self, string):
        a = string.split()
        self.attributes[a[0]] = int(a[1])

class WeaponInstance(ViewAdam):
    def __init__(self, scene, tag, host):
        ViewAdam.__init__(self, scene, tag)
        self.count = 0
        self.move(host.rect.center[0], host.y + 20)
        self.set_orientation(host.root.view.orientation)

    def update(self):
        ViewAdam.update(self)
        if self.count == 1:
            self.destroy()
        self.count += 1

    def set_orientation(self, x):
        if self.orientation == x:
            return
        if self.orientation == 'R':
            self.move(-self.rect.width, 0)
            self.image = pygame.transform.flip(self.image, True, False)
            self.orientation = 'L'

class Projectile(AnimatedCharacter):
    def __init__(self, host, tag, pierce):
        AnimatedCharacter.__init__(host.scene, tag, side = 'projectile')
        self.orientation = host.orientation
        self.attributes['pierce'] = 0
        self.attributes['max_pierce'] = pierce

    def update(self):
        AnimatedCharacter.update(self)
        self.view.check_collisions_after(self.char.get('speed'))
        if self.orientation == 'R':
            self.char.step_right()
        else:
            self.char.step_left()

        if self.view.dist(host.view) >= self.char.get('max_distance'):
            self.destroy()

    def action(self, item):
        item.take_damage(Attack(self))

class SummonSpell:
    def __init__(self, tag, manacost):
        self.summon_tag = tag
        self.manacost = manacost

    def cast(self, host):
        if host.get('mana') >= self.manacost:
            tmp = AnimatedCharacter(host.scene, self.summon_tag, host.side, host.x)
            host.scene.add_object(tmp)
            host.change_mana(-manacost)

class ProjectileSpell:
    def __init__(self, tag, pierce, manacost):
        self.tag = tag
        self.pierce = pierce
        self.manacost = manacost

    def cast(self, host):
        if host.get('mana') >= self.manacost:
            tmp = Projectile(host, tag, pierce)
            host.scene.add_object(tmp)
            host.change_mana(-manacost)



Spells = dict()
file = open('spells.txt')
lines = file.readlines()
for line in lines:
    (tag, typ, x1, x2, manacost) = tuple(line.split())
    manacost = int(manacost)
    if typ == 'summon':
        Spells[tag] = SummonSpell(x1, manacost)
    elif typ == 'projectile':
        Spells[tag] = ProjectileSpell(x1, int(x2), manacost)



class SceneManager(Stack):
    def __init__(self):
        Stack.__init__(self)
        self.scenes_dict = dict()
        self.main_scene = None

    def add_scene(self, scene, tag, is_main_scene = False):
        pygame.time.delay(10)
        self.scenes_dict[tag] = scene
        if is_main_scene == True:
            self.main_scene = scene
        scene.load()

    def run(self):
        while 1:
            event_queue = pygame.event.get()
            for event in event_queue:
                if event.type == QUIT:
                    return 
                if event.type == KEYDOWN and event.key == K_TAB:
                    if self.top().is_battle_scene:
                        self.push(self.scenes_dict['game_menu'])
                        pygame.time.delay(10)
                    else:
                        self.pop()
                        pygame.time.delay(10)
            self.update_current_scene(event_queue)
            pygame.time.delay(100)

    def update_current_scene(self, events):
        if self.get_len() != 0:
            self.top().update(events)

    def push_tag(self, tag):
        self.push(self.scenes_dict[tag])
        pygame.time.delay(10)

    def pop_and_push_tag(self, tag):
        if self.main_scene == self.pop():
            self.main_scene = self.scenes_dict[tag]    
        self.push(self.main_scene)

    def set_main_scene(self, scene):
        self.main_scene = scene

class Scene():
    def __init__(self, screen = screen, background_im = background_im):
        self.Objects = set()
        self.DeadObjects = set()
        self.NewObjects = set()
        self.need_loading = False
        self.screen = screen
        self.background = background_im
        self.scripts = []
        self.is_battle_scene = False
        self.next = None

    def add_object(self, x):
        self.NewObjects.add(x)
    
    def del_object(self, x):
        try:
            if x.side == 'enemy':
                player.give_exp(x.get('exp_cost'))
        except:
            pass
        self.DeadObjects.add(x)

    def update_set_of_objects(self):
        for item in self.DeadObjects:
            self.Objects.discard(item)
        self.DeadObjects = set()

        for item in self.NewObjects:
            self.Objects.add(item)
        self.NewObjects = set()

    def update(self, events):
        self.screen.blit(self.background, (0, 0))
        self.update_set_of_objects()
        # for event in events:
        #     for i in self.Objects:
        #         i.translate_event(event)
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
        self.is_battle_scene = True
        self.player = None
        self.can_trade = False

    def load(self):
        x = open(self.data)
        for i in x.readlines():
            tag, x, side = i.split()
            x = int(x)
            self.add_object(AnimatedCharacter(self, tag, x = x, side = side))
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
                if self.player != None:
                    self.player.translate_event(event)

        textsurface = myfont.render(get_string_of_player_status(), False, (255, 255, 0))
        screen.blit(ground_im, ground_rect)
        screen.blit(textsurface, (0, 0))

        # for item in self.Objects:
        #     item.update()
        # for item in self.Objects:
        #     item.draw()

        pygame.display.update()

    def add_player(self, x):
        self.add_object(x)
        self.player = x
        player.scene = self
        player.move_to(0)

    def go_next(self, player):
        print('ok')
        Manager.pop()
        Manager.push(self.next)
        Manager.set_main_scene(self.next)
        self.next.add_player(self.player)
        self.player = None

class MenuScene(Scene):
    def __init__(self, screen, background = background_im):
        Scene.__init__(self, screen, background)
        self.need_loading = True

    def load(self):
        self.add_object(UpdatingLabel(get_string_of_player_status, 10, 0))
        self.add_object(UpdatingLabel(lambda: 'Skill points: ' + str(player.get('skill_points')), 10, 25))

        self.add_object(Button('Spend skillpoins', 10, 50, lambda: Manager.push_tag('skill_menu')))

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
        self.add_object(Label('Loot:', 150, 25))
        self.add_object(LootLabel(150, 50))        

        self.need_loading = False 

class StartMenu(Scene):
    def __init__(self):
        Scene.__init__(self)
        self.need_loading = True

    def load(self):
        self.add_object(Button('Start Game', 50, 50, lambda: Manager.push_tag('zomb')))

class SkillsScene(Scene):
    def __init__(self):
        Scene.__init__(self)
        self.need_loading = True

    def load(self):
        self.add_object(UpdatingLabel(get_string_of_player_status, 10, 0))
        self.add_object(UpdatingLabel(lambda: 'Skill points: ' + str(player.get('skill_points')), 10, 25))
        self.add_object(Button('Increase maximum mana', 10, 75, player.spend_sp_on_mana, player.has_sp))
        self.add_object(Button('Increase maximum hp', 10, 100, player.spend_sp_on_hp, player.has_sp))

        self.need_loading = False

class TravelScene(Scene):
    def __init__(self):
        Scene.__init__(self)
        self.need_loading = True

    def load(self):
        pass

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
        text = f()
        self.surf = myfont.render(text, True, choose_color(text))
        self.x, self.y = x, y
        self.text = f

    def update(self):
        self.surf = myfont.render(self.text(), True, choose_color(self.text()))

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

    def translate_event(self, event):
        pass

class InventorySlotLabel:
    def __init__(self, host, ind, x, y):
        self.x = x
        self.y = y
        self.ind = ind
        self.host = host
        self.ind_label = Label(str(ind), x, y)
        self.item_label = UpdatingLabel(lambda: player.get_inventory_slot(self.ind), x + 20, y)
        self.equip_button = Button('equip', x + 200, y, lambda: host.equip_inventory_slot(self.ind))
        self.drop_button = Button('drop', x + 260, y, lambda: host.drop(ind))
        self.sell_button = Button('sell', x + 320, y, lambda: host.sell(ind), lambda: host.can_trade())

    def update(self):
        self.ind_label.update()
        self.item_label.update()
        self.equip_button.update()
        self.drop_button.update()
        self.sell_button.update()

    def draw(self):
        self.ind_label.draw()
        self.item_label.draw()
        self.equip_button.draw()
        self.drop_button.draw()
        self.sell_button.draw()

class EquipSlotLabel:
    def __init__(self, host, tag, x, y):
        self.x = x
        self.y = y
        self.tag = tag
        self.host = host
        self.tag_label = Label(tag, x, y)
        self.item_label = UpdatingLabel(lambda: player.equip.get_slot_text(self.tag), x + 100, y)
        self.unequip_button = Button('unequip', x + 300, y, lambda: host.unequip(self.tag), lambda: host.equip.get_slot(tag) != None)

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
        self.take_button = Button('take', x + 185, y, lambda: player.take_loot(self.ind), lambda: player.loot[self.ind] != None)
        self.next_button = Button('next', x + 225, y, lambda: self.next(), lambda: self.ind < len(player.loot) - 1)
        self.update_button =  Button('update', x + 265, y, lambda: self.update_loot())

    def update_loot(self):
        player.update_loot()
        self.ind = 0

    def prev(self):
        self.ind -= 1

    def next(self):
        self.ind += 1

    def update(self):
        self.prev_button.update()
        self.text1.update()
        self.take_button.update()
        self.next_button.update()
        self.update_button.update()

    def draw(self):
        self.prev_button.draw()
        self.text1.draw()
        self.take_button.draw()
        self.next_button.draw()
        self.update_button.draw()

def choose_color(text):
    color = (255, 255, 255)
    if text.startswith('rare '):
        color = (255, 120, 0)
    if text.startswith('uncommon '):
        color = (153, 204, 255)
    if text.startswith('epic '):
        color = (255, 0, 0)
    return color


def get_string_of_player_status():
    s = ''
    s += 'hp: ' + str(player.get('hp')) + '/' + str(player.get('max_hp'))
    s += ' mana: ' + str(player.get('mana')) + '/' + str(player.get('max_mana'))
    s += ' exp: ' + str(player.attributes['exp']) + '/' + str(player.exp_to_next_lvl())
    s += ' lvl: ' + str(player.get('lvl'))
    s += ' money: ' + str(player.get('money'))
    return s







zombie = BattleScene(screen, 'zombie_spawner_scene.txt')
travel = BattleScene(screen)
travel.can_trade = True
zombie.next = travel
player = PlayerAdam(zombie, 'hero', 0)
zombie.add_player(player)

Manager = SceneManager()
Manager.add_scene(zombie, 'zomb', True)
Manager.add_scene(MenuScene(screen), 'game_menu')
Manager.add_scene(SkillsScene(), 'skill_menu')
Manager.add_scene(StartMenu(), 'main_menu')
Manager.add_scene(travel, 'travel')
Manager.push_tag('main_menu')
Manager.run()