def load_monsters(file):
    Creatures = dixt()
    x = file.readlines()
    for s in x:
        s.rstrip()
        Creatures[s] = Creature open(s + '.txt')
