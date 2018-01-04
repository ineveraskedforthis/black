
BASE_SLOTS = ['left_hand', 'right_hand', 'helmet', 'legs', 'body', 'head']

class Doll:
    def __init__(self, owner):
        self.items = dict()
        self.owner = owner
        for i in BASE_SLOTS:
            self.items[i] = -1

    def try_equip(self, x):
        if self.free(x.slot):
            self.items[x.slot] = x
            return 1
        return -1

    def free(self, slot):
        if self.items[slot] == -1:
            return True

    def get_tag(self, tag):
        return self.items[tag]

    def set_tag(self, tag, item):
        self.items[tag] = item

    def get_tag_text(self, tag):
        if self.items[tag] == -1:
            return('empty')
        else:
            return(self.items[tag].name)
    
    def get_equip_damage(self):
        curr = 0
        for tag in BASE_SLOTS:
            if self.items[tag] != -1:
                curr += self.items[tag].dmg
        return curr
    
    def get_equip_armour(self):
        curr = 0
        for tag in BASE_SLOTS:
            if self.items[tag] != -1:
                curr += self.items[tag].armour
        return curr

    def clear_tag(self, tag):
        self.items[tag] = -1


class Inventory():
    def __init__(self, host):
        self.max_items = 6
        self.items = [-1] * self.max_items
        self.host = host

    def add_item(self, x):
        for i in range(self.max_items):
            if self.items[i] == -1:
                self.items[i] = x
                return

    def get_ind(self, ind):
        if ind < self.max_items:
            return self.items[ind]
        return -1

    def set_ind(self, ind, item):
        self.items[ind] = item

    def get_ind_name(self, ind):
        if self.items[ind] == -1:
            return ''
        return self.items[ind].name

    def erase_ind(self, ind):
        self.items[ind] = -1

    def is_empty(self):
        for i in range(self.max_items):
            if self.items[i] != -1:
                return False
        return True

    def is_full(self):
        for i in range(self.max_items):
            if self.items[i] == -1:
                return False
        return True
