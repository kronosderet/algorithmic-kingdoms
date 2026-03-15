class ResourceManager:
    def __init__(self, gold=0, wood=0, iron=0, steel=0, stone=0, tonic=0):
        self.gold = gold
        self.wood = wood
        self.iron = iron
        self.steel = steel
        self.stone = stone
        self.tonic = tonic

    def can_afford(self, gold=0, wood=0, iron=0, steel=0, stone=0, tonic=0):
        return (self.gold >= gold and self.wood >= wood and self.iron >= iron
                and self.steel >= steel and self.stone >= stone
                and self.tonic >= tonic)

    def spend(self, gold=0, wood=0, iron=0, steel=0, stone=0, tonic=0):
        self.gold -= gold
        self.wood -= wood
        self.iron -= iron
        self.steel -= steel
        self.stone -= stone
        self.tonic -= tonic

    def add(self, rtype, amount):
        if rtype == "gold":
            self.gold += amount
        elif rtype == "wood":
            self.wood += amount
        elif rtype == "iron":
            self.iron += amount
        elif rtype == "steel":
            self.steel += amount
        elif rtype == "stone":
            self.stone += amount
        elif rtype == "tonic":
            self.tonic += amount
