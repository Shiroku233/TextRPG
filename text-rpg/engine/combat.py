import random
from engine.models import Character



def roll(n):
    return random.randint(1, n)

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