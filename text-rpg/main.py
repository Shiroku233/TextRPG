from game import Game

def main():
    game = Game()
    print("文字 RPG 原型。输入 q 退出。")
    while True:
        game.status()
        try:
            cmd = input("> ")
        except (EOFError, KeyboardInterrupt):
            break
        try:
            game.command(cmd)
        except SystemExit:
            break
        if game.actor.get("hp", 0) <= 0:
            print("游戏结束。刷新或重跑 main() 重开。")


if __name__ == "__main__":
    main()