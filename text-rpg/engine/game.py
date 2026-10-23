import random

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

def roll(n):
    return random.randint(1, n)


def use_item(actor,item):
    if actor.inventory.get(item,0)<=0:
        print(f"缺少物品 {item} 。")
        return False
    if item=="治疗药水":
        heal=10
        actor.hp=min(actor.max_hp,actor.hp+heal)
        actor.inventory[item]-=1
        print(f"你喝下治疗药水，恢复 {heal} 点 HP（当前 {actor.hp}/{actor.max_hp}）")
        return True
    return False

def make_enemy(config):
    return Character(config["name"],config["hp"],config["attack"],config["defense"])

def attack(actor,target):
    is_hit=True if roll(100)>25 else False
    if is_hit:
        amount=actor.attack + actor.weapon_bonus + roll(3)
        actual_amount=target.take_damage(amount)
        print(f"{actor.name} 对 {target.name} 造成 {actual_amount} 点伤害（{target.name} 剩余 {target.hp} HP）")
    else:
        print(f"{actor.name}的攻击落空了！")

def heavy_attack(actor,target):
    is_hit = True if roll(100) > 60 else False
    if is_hit:
        amount = actor.attack*2 + actor.weapon_bonus + roll(5)
        actual_amount = target.take_damage(amount)
        print(f"{actor.name}使出重击， 对 {target.name} 造成 {actual_amount} 点伤害（{target.name} 剩余 {target.hp} HP）")
    else:
        print(f"{actor.name}的攻击落空了！")
