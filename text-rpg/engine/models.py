class Character:
    def __init__(self, name,hp,attack,defense):
        self.name = name
        self.hp = hp
        self.max_hp = hp
        self.attack=attack
        self.defense=defense
        self.weapon_bonus = 0
        self.inventory = {"治疗药水": 2}

    def is_alive(self):
        return self.hp > 0

    def take_damage(self,amount):
        actual_amount = max(1,amount-self.defense)
        self.hp=max(0,self.hp-actual_amount)
        return actual_amount