import random

list_of_items = open('items').readlines
common_items = []
for i in list_of_items:
    x = i.split()
    common_items.append(Item(x[0], x[1], int(x[2]), int(x[3])))

class Item
    def __init__(Name, Type, BasePower, AttackDelay)
        self.name, self.typ, self.base_power, self.att_delay = Name, Type, BasePower, AttackDelay
        self.status = 'common'
        self.bonus_power = 0

    def set_status(self, tag):
        if tag == 'uncommon':
            self.bonus_power = 2
        if tag == 'rare':
            self.bonus_power = 6
        if tag == 'epic':
            self.bonus_power = 10
        self.status = tag

def generate_random_common_item():
    return random.choice(common_items)

def generate_random_item():
    x = random.random()
    item = generate_random_common_item()
    if x > 0.85:
        item.set_status('uncommon')
    if x > 0.98:
        item.set_status('rare')
    if x > 0.999:
        item.set_status('epic')
    return item