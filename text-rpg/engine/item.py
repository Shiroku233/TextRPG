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

def pick_up(player, item_name):
    """捡起物品：消耗品进背包，装备直接生效。"""
    if item_name == "铁剑":
        player.weapon_bonus = 4
        print("你捡起铁剑，攻击力提升了。")
    else:
        player.inventory[item_name] = player.inventory.get(item_name, 0) + 1
        print(f"你捡起了 {item_name}。")