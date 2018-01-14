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
pygame.display.set_caption('Basic Pygame program')
BASE_SLOTS = ['left_hand', 'right_hand', 'legs', 'body', 'head']
DISPLAYABLE_SLOTS = ['body', 'head', 'left_hand', 'right_hand']
BASE_ANIMATIONS = ['idle', 'move']
BASE_DROP_CHANCE = 0.5
CAMERA = [0, 0]


ZOMBIE_MOVE_0, tmp = load_image('zombie_move_0.png')
ZOMBIE_MOVE_1, tmp = load_image('zombie_move_1.png')
BASE_IMAGE, BASE_RECT = load_image('base_image.png')
CRATE_IMAGE, CRATE_RECT = load_image('crate.png')
FIREBALL_IMAGE, FIREBALL_RECT = load_image('fireball.png')
ZOMBIE_IMAGE, ZOMBIE_RECT = load_image('zombie.png')
ZOMBIE_SPAWNER_IMAGE, ZOMBIE_SPAWNER_RECT = load_image('zombie_spawner.png')
SLASH_IMAGE, SLASH_RECT = load_image('slash.png')
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
        self.is_enemy = False
        self.is_ally = False
        self.orientation = 'R'
        self.animation = dict()
        self.current_animation_tick = 0
        self.animation['idle'] = [self.image]
        self.current_animation = 'idle'

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

    def move_to(self, x, y = 0):
        self.move(-self.x + x, -self.y + y)
        print(self.x)

    def dist(self, agent):
        return abs(self.x - agent.x)

    def destroy(self):
        self.scene.del_object(self)

    def set_orientation(self, orientation):
        if self.orientation == orientation:
            return
        self.orientation = orientation
        self.image = pygame.transform.flip(self.image, True, False)

    def step_right(self):       
        self.set_orientation('R')
        self.move(self.speed, 0)

    def step_left(self):
        self.set_orientation('L')
        self.move(-self.speed, 0) 

    def add_animation(self, tag, list_of_image):
        self.animation[tag] = list_of_image

    def change_animation(self, tag):
        self.current_tick = 0
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



class hp_adam(image_adam):
    def __init__(self, scene, rect, image, x = 0, y = 0, max_hp = 1):
        image_adam.__init__(self, scene, rect, image, x, y) 
        self.hp = max_hp
        self.max_hp = max_hp
        self.speed = 1
        self.base_attack_damage = 1
        self.is_enemy = False
        self.is_ally = False
        self.base_defence = 0

    def take_damage(self, x, type = 'phys'):
        tmp = min(0, self.get_defence() - x)
        self.change_hp(tmp)

    def change_hp(self, x):
        self.hp = min(self.hp + x, self.max_hp)
        if self.hp <= 0:
            self.hp = 0
            self.destroy()

    def attack_target(self):
        if self.target == None:
            return
        else:
            self.attack(self.target)

    def get_attack_damage(self):
        return self.base_attack_damage

    def attack(self, agent):
        agent.take_damage(self.get_attack_damage())

    def get_defence(self):
        return self.base_defence


class true_adam(hp_adam, fsm_adam):
    def __init__(self, scene, rect, image, x = 0, y = 0, max_hp = 2):
        hp_adam.__init__(self, scene, rect, image, x, y, max_hp)
        self.scene = scene

    def update(self):
        hp_adam.update(self)
        fsm_adam.update(self)

class Item():
    def __init__(self, Name, Type, Slot, BasePower):
        self.name, self.typ, self.slot, self.power = Name, Type, Slot, BasePower
        self.status = 'common'
        self.bonus_power = 0
        if Slot == 'two_hands':
            self.slot = 'right_hand'
            self.is_twohanded = True
        else:
            self.is_twohanded = False
        if Slot in DISPLAYABLE_SLOTS:
            self.image, self.rect = load_image(self.name + '.png')

    def set_status(self, tag):
        if tag == 'uncommon':
            self.bonus_power = 2
        if tag == 'rare':
            self.bonus_power = 6
        if tag == 'epic':
            self.bonus_power = 10
        self.status = tag

    def get_power(self):
        return self.power + self.bonus_power

    def get_name(self):
        return self.status + ' ' + self.name

    def get_cost(self):
        return 10

list_of_items = open('items.txt').readlines()
common_items = []
for i in list_of_items:
    x = i.split()
    common_items.append(Item(x[0], x[1], x[2], int(x[3])))



class SpellInstance(hp_adam):
    def __init__(self, Host, Scene, Image, Rect, Name, Power, Speed, MaxDistance, Pierce, Update, CheckCollisions, Action):
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
                if not self.pierce:
                    self.destroy()

    def action(self, agent):
        agent.take_damage(self.power, 'fire')


class Spell(hp_adam):
    def __init__(self, Image, Rect, Name, Power, 
                Manacost = 10,
                Speed = 5, 
                MaxDistance = 500, 
                Pierce = False, 
                Update = None, 
                CheckCollisions = None, 
                Action = None):
        self.image = Image
        self.rect = Rect
        self.name = Name
        self.power = Power
        self.pierce = Pierce
        self.update = Update
        self.check_collisions = CheckCollisions
        self.action = Action
        self.max_distance = MaxDistance
        self.speed = Speed
        self.manacost = Manacost
        self.bonus_power = 0

    def increase_power(self, x):
        self.bonus_power = x

    def cast(self, host):
        # print(host.name, 'is casting')
        if host.mana >= self.manacost:
            tmp = SpellInstance(host, host.scene, self.image, self.rect, self.name, self.power + self.bonus_power, self.speed, self.max_distance, self.pierce, self.update, self.check_collisions, self.action)
            host.scene.add_object(tmp)
            host.change_mana(-self.manacost)


FireBall = Spell(FIREBALL_IMAGE, FIREBALL_RECT, 'fireball', 1, 10, 5)


def generate_random_common_item():
    return random.choice(common_items)

def generate_random_item():
    x = random.random()
    item = generate_random_common_item()
    if x > 0.95:
        item.set_status('uncommon')
    if x > 0.99:
        item.set_status('rare')
    if x > 0.9999:
        item.set_status('epic')
    if item.typ == 'wand':
        item.spell = FireBall
        item.spell.increase_power(item.get_power())
        item.use = lambda host: item.spell.cast(host)
    return item

def GENERATE_RANDOM_ITEM():
    return generate_random_item()
    # return common_items[0]


class WeaponInstance(image_adam):
    def __init__(self, scene, rect, image, host):
        image_adam.__init__(self, scene, rect, image)
        self.count = 0
        self.move(host.rect.center[0], host.y + 20)

    def update(self):
        image_adam.update(self)
        if self.count == 2:
            self.destroy()
        self.count += 1

    def set_orientation(self, x):
        if self.orientation == x:
            return
        if self.orientation == 'R':
            self.move(-self.rect.width, 0)
            self.image = pygame.transform.flip(self.image, True, False)
            self.orientation = 'L'
        # else
        # no need for this branch



class player_adam(true_adam):
    def __init__(self, scene):
        true_adam.__init__(self, scene, HERO_RECT, HERO_IMAGE, 0, 0)
        self.fsm = StateMachine(self, PlayerIdle)
        self.key_pressed = 'NONE'
        self.hp = 10
        self.mana = 10
        self.max_mana = 10
        self.max_hp = 10
        self.mana_regen = 1
        self.hp_regen = 1
        self.speed = 3
        self.exp = 0
        self.lvl = 1
        self.skill_points = 0
        self.equip = Doll(self)
        self.inv = Inventory(self)
        self.inv.add_item(GENERATE_RANDOM_ITEM())
        self.base_attack_distance = 20
        self.loot = [None]
        self.name = 'hero'
        self.is_ally = True
        self.money = 0


    def update_loot(self):
        tmp = []
        for i in self.loot:
            if i != None:
                tmp.append(i)
        if len(tmp) == 0:
            tmp = [None]
        self.loot = tmp

    def draw(self):
        true_adam.draw(self)
        for tag in ['body', 'head', 'left_hand']:
            tmp = self.equip.get_tag(tag)
            if tmp != None:
                tmp = tmp.image
                if self.orientation == 'L':
                    tmp = pygame.transform.flip(tmp, True, False)
                screen.blit(tmp, self.rect)


    def drop(self, ind):
        tmp = self.inv.get_ind(ind)
        if tmp != None:
            self.inv.erase_ind(ind)
            self.add_loot(tmp)

    def add_loot(self, item):
        self.loot.append(item)

    def take_loot(self, ind):
        if self.inv.is_full():
            return
        self.inv.add_item(self.loot[ind])
        self.loot[ind] = None

    def get_loot_name(self, ind):
        if self.loot[ind] == None:
            return('None')
        return self.loot[ind].get_name()

    def update(self):
        true_adam.update(self)
        self.change_mana(self.mana_regen)
        self.change_hp(self.hp_regen)

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

    def get_attack_range(self):
        if self.equip.get_tag('right_hand') == None:
            return self.base_attack_distance
        else:
            return 20

    def try_attack(self):
        tmp = self.equip.get_tag('right_hand')
        if tmp == None:
            checking_rect = self.rect.inflate(self.get_attack_range(), 0)
            if self.orientation == 'L':
                checking_rect = checking_rect.move(-self.get_attack_range(), 0)
            for item in self.scene.Objects:
                if checking_rect.colliderect(item.get_rect()) and item.is_enemy:
                    self.attack(item)

        elif tmp.typ == 'sword' or tmp.typ == 'spear':
            weap = WeaponInstance(self.scene, tmp.rect, tmp.image, self)
            if self.orientation == 'L':
                weap.set_orientation('L')            
            self.scene.add_object(weap)
            for item in self.scene.Objects:
                if weap.rect.colliderect(item.get_rect()) and item.is_enemy:
                    self.attack(item)

        elif self.equip.get_tag('right_hand').typ == 'wand':
            self.equip.get_tag('right_hand').use(self)


    def give_exp(self, x):
        self.exp += x
        while self.exp >= self.exp_to_next_lvl():
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

    def get_mana(self):
        return self.mana

    def unequip(self, tag):
        if self.inv.is_full():
            return
        tmp = self.equip.get_tag(tag)
        if tmp == None:
            return
        self.equip.clear_tag(tmp.slot)
        self.inv.add_item(tmp)

    def get_defence(self):
        return self.base_defence + self.equip.get_defence()

    def sell(self, ind):
        self.money += self.inv.get_ind(ind).get_cost()
        self.inv.erase_ind(ind)

    def can_trade(self):
        return self.scene.can_trade




class enemy_adam(true_adam):
    def __init__(self, scene, rect, image, x, y, max_hp):
        true_adam.__init__(self, scene, rect, image, x, y, max_hp)
        self.drop_chance = BASE_DROP_CHANCE
        self.is_enemy = True

    def destroy(self):
        true_adam.destroy(self)
        player.give_exp(self.exp_reward)
        x = random.random()
        if x <= self.drop_chance:
            self.scene.player.add_loot(GENERATE_RANDOM_ITEM())


class MovingEnemy(enemy_adam):
    def __init__(self, scene, x, y, max_hp, rect = ZOMBIE_RECT, img = ZOMBIE_IMAGE):
        enemy_adam.__init__(self, scene, rect, img, x, y, max_hp)
        self.speed = 1
        self.fsm = StateMachine(self, EnemyIdle)
        self.is_enemy = True
        self.target = None
        self.orientation = 'L'
        self.attack_distance = 20
        self.base_attack_damage = 1
        self.exp_reward = 5
        self.add_animation('move', [ZOMBIE_MOVE_0, ZOMBIE_MOVE_1])

    def update_target(self):
        closest_target = None
        dist = 0
        for item in self.scene.Objects:
            if not item.is_enemy and item.is_ally and item.hp > 0:
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
        enemy_adam.__init__(self, scene, ZOMBIE_SPAWNER_RECT, ZOMBIE_SPAWNER_IMAGE, x, 0, 100)
        (self.ticks, self.child, self.spawning_point) = (ticks, child, x)
        self.current_tick = 0
        self.is_enemy = True
        self.is_living_adam = False
        self.spiritual = False
        self.fsm = StateMachine(self, SpawnerIdle)
        self.exp_reward = 100

    def spawn(self):
        tmp_child = self.child(self.scene, self.spawning_point, 0, 2)
        self.scene.add_object(tmp_child)
        pass


def get_string_of_player_status():
    s = ''
    s += 'hp: ' + str(player.hp) + '/' + str(player.max_hp)
    s += ' mana: ' + str(player.mana) + '/' + str(player.max_mana)
    s += ' exp: ' + str(player.exp) + '/' + str(player.exp_to_next_lvl())
    s += ' lvl: ' + str(player.lvl)
    s += ' money: ' + str(player.money)
    return s

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
        # print(x)
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
        self.screen.blit(self.background, (0, 0))
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
        self.is_battle_scene = True
        self.player = None
        self.can_trade = False

    def load(self):
        x = open(self.data)
        for i in x.readlines():
            s, p = i.split()
            p = int(p)
            if s == 'zspawner':
                self.add_object(ZSpawner(self, 20, MovingEnemy, p))
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
        self.add_object(UpdatingLabel(lambda: 'Skill points: ' + str(player.skill_points), 10, 25))
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
        self.add_object(UpdatingLabel(lambda: 'Skill points: ' + str(player.skill_points), 10, 25))
        self.add_object(Button('Increase maximum mana', 10, 75, player.spend_sp_on_mana, player.has_sp))
        self.add_object(Button('Increase maximum hp', 10, 100, player.spend_sp_on_hp, player.has_sp))

        self.need_loading = False

class TravelScene(Scene):
    def __init__(self):
        Scene.__init__(self)
        self.need_loading = True

    def load(self):
        pass


def choose_color(text):
    color = (255, 255, 255)
    if text.startswith('rare '):
        color = (255, 120, 0)
    if text.startswith('uncommon '):
        color = (153, 204, 255)
    if text.startswith('epic '):
        color = (255, 0, 0)
    return color


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
        self.item_label = UpdatingLabel(lambda: player.equip.get_tag_text(self.tag), x + 100, y)
        self.unequip_button = Button('unequip', x + 300, y, lambda: host.unequip(self.tag), lambda: host.equip.get_tag(tag) != None)

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


# class CrateLabel:
#     def __init__(self, x, y):
#         self.x, self.y = x, y
#         self.b_prev = Button()


zombie = BattleScene(screen, 'zombie_spawner_scene.txt')
travel = BattleScene(screen)
travel.can_trade = True
zombie.next = travel
player = player_adam(zombie)
zombie.add_player(player)

Manager = SceneManager()
Manager.add_scene(zombie, 'zomb', True)
Manager.add_scene(MenuScene(screen), 'game_menu')
Manager.add_scene(SkillsScene(), 'skill_menu')
Manager.add_scene(StartMenu(), 'main_menu')
Manager.add_scene(travel, 'travel')
Manager.push_tag('main_menu')
Manager.run()