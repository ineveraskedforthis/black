
BASE_SLOTS = ['left_hand', 'right_hand', 'helmet', 'legs', 'body', 'head']

class Doll:
    def __init__(self, owner):
        self.items = dict()
        self.owner = owner
        for i in BASE_SLOTS:
            self.items[i] = None

    def try_equip(self, x):
        if self.free(x.slot):
            self.items[x.slot] = x
            return 1
        return None

    def free(self, slot):
        if slot == 'left_hand' and not self.free('right_hand') and self.get_tag('right_hand').is_twohanded:
            return False
        if self.items[slot] == None:
            return True
        return False

    def get_slot(self, tag):
        return self.items[tag]

    def set_slot(self, tag, item):
        self.items[tag] = item

    def get_slot_text(self, tag):
        if self.items[tag] == None:
            return('empty')
        else:
            return(self.items[tag].get_name())

    def get(self, tag):
        curr = 0
        for i in BASE_SLOTS:
            if self.items[i] != None:
                curr += self.items[i].get(tag)
        return curr

    def clear_slot(self, tag):
        self.items[tag] = None


class Inventory():
    def __init__(self, host):
        self.max_items = 6
        self.items = [None] * self.max_items
        self.host = host

    def add_item(self, x):
        for i in range(self.max_items):
            if self.items[i] == None:
                self.items[i] = x
                return

    def get_ind(self, ind):
        if ind < self.max_items:
            return self.items[ind]
        return None

    def set_ind(self, ind, item):
        self.items[ind] = item

    def get_ind_name(self, ind):
        if self.items[ind] == None:
            return ''
        return self.items[ind].get_name()

    def erase_ind(self, ind):
        self.items[ind] = None

    def is_empty(self):
        for i in range(self.max_items):
            if self.items[i] != None:
                return False
        return True

    def is_full(self):
        for i in range(self.max_items):
            if self.items[i] == None:
                return False
        return True


class Stack:
    def __init__(self):
        self.length = 0
        self.data = []

    def push(self, item):
        if self.length == len(self.data):
            self.data.append(item)
        else:
            self.data[self.length] = item
        self.length += 1

    def top(self):
        return self.data[self.length - 1]

    def pop(self):
        self.length -= 1
        return self.data[self.length]

    def get_len(self):
        return self.length