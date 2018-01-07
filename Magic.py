def DefaultUpdate(self):
    self.check_collisions(self.speed)
    if self.orientation == 'R':
        self.move(self.speed, 0)
    else:
        self.move(-self.speed, 0)

    if abs(self.x - self.host.x) >= self.max_distance:
        self.destroy()

def DefaultCheckCollisions(self, speed):
    checking_rect = self.get_rect().inflate(speed, 0)
    if self.orientation == 'L':
        checking_rect.move_ip(speed, 0)
    for item in self.scene.Objects:
        if not item.spiritual and checking_rect.colliderect(item.get_rect()) and item.is_enemy:
            self.Action(item)
        if not self.pierce:
            self.destroy()

def DefaultAction(self, item):
    item.take_damage(Power, 'fire')

