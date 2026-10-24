from engine.models import Character
from engine.combat import attack,heavy_attack,make_enemy
from engine.item import use_item,pick_up
from engine.world import ROOMS

def run_battle(player,enemy):
    print(f"你遇到了 {enemy.name}！")
    while player.is_alive() and enemy.is_alive():
        print(f"\n你的 HP: {player.hp}/{player.max_hp}  |  {enemy.name} HP: {enemy.hp}/{enemy.max_hp}")
        cmd = input("输入 'a' 攻击，'h' 重击，'u' 喝药，'q' 逃跑：").strip().lower()

        if cmd == "q":
            print("你逃走了。")
            return False
        elif cmd == "a":
            attack(player, enemy)
            if enemy.is_alive():
                attack(enemy, player)
        elif cmd == "h":
            heavy_attack(player, enemy)
            if enemy.is_alive():
                attack(enemy, player)
        elif cmd == "u":
            use_item(player, "治疗药水")
        else:
            print("无效指令。")
            continue
        if enemy.is_alive():
            attack(enemy, player)
    if player.is_alive():
        print(f"\n你击败了 {enemy.name}！")
        return True
    else:
        print(f"\n你被 {enemy.name} 击败了……")
        return False

def run_game():
    player = Character("你", hp=30, attack=8, defense=2)
    current = "森林入口"

    while player.is_alive():
        room = ROOMS[current]
        print(f"\n=== {current} ===")
        print(room["desc"])

        # 捡地上的东西
        if room["items"]:
            print(f"地上有：{', '.join(room['items'])}")
            cmd = input("'pick' 捡起，或直接回车继续：").strip().lower()
            if cmd == "pick":
                item = room["items"].pop(0)
                pick_up(player, item)

        # 敌人
        if room["enemy"]:
            enemy = make_enemy(room["enemy"])
            survived = run_battle(player, enemy)
            if not survived:
                break
            room["enemy"] = None
            print(f"{enemy.name} 被击败了。")

        # 移动
        exits = room["exits"]
        print(f"出口：{', '.join(exits.keys())}")
        cmd = input("输入方向移动，'q' 退出：").strip()
        if cmd == "q":
            break
        if cmd in exits:
            current = exits[cmd]
        else:
            print("那个方向走不通。")




