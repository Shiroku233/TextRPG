# game.py

from engine.entities import Entity, create, create_from_dict
from engine.intent import Intent
from engine.capabilities import build_context
from engine.laws import evaluate_laws
from engine.world import ROOMS


def make_room_entity(name):
    """按 ROOMS 配置创建一个房间 Entity。

    敌人由配置字典转为持久的 Entity 实例，后续行动直接读写该实例，
    而不是每次重建（否则敌人的 states/state_data/hp 都会丢失）。
    配置字典不再被引用共享，也不会被写回 ROOMS。
    """
    cfg = ROOMS[name]
    enemy_cfg = cfg["enemy"]
    return Entity(
        name=name,
        kind="room",
        desc=cfg["desc"],
        exits=cfg["exits"],
        items=list(cfg["items"]),
        has_fire=cfg["has_fire"],
        wet=cfg["wet"],
        enemy=create_from_dict(enemy_cfg) if enemy_cfg else None,
    )


class Game:
    def __init__(self):
        self.actor = Entity(
            "你", kind="character",
            hp=30, max_hp=30, attack=8, defense=2,
        )
        self.actor.attrs["bag"] = []
        self.current_room_name = "森林入口"
        self.room = make_room_entity(self.current_room_name)
        self.log = []

    def say(self, msg):
        self.log.append(msg)
        print(msg)

    def status(self):
        p = self.actor
        lines = [
            f"\n=== {self.current_room_name} ===",
            self.room.get("desc", ""),
        ]
        if self.room.get("items"):
            lines.append(f"地上有：{', '.join(self.room.get('items'))}")
        bag_names = [i.name for i in p.attrs["bag"]]
        lines.append(f"HP: {p.get('hp')}/{p.get('max_hp')}  背包：{bag_names}")
        enemy = self.room.get("enemy")
        if enemy:
            lines.append(f"敌人：{enemy.name}（HP {enemy.get('hp', 0)}）")
        lines.append(f"出口：{', '.join(self.room.get('exits', {}).keys())}")
        print("\n".join(lines))

    # ---------------- 指令入口 ----------------

    def command(self, text):
        text = text.strip()
        if not text:
            return
        low = text.lower()
        self.say(f"> {text}")

        if low in ("a", "attack", "攻击"):
            self._run_intent(Intent(verb="attack"))
        elif low in ("h", "heavy", "重击"):
            self._run_intent(Intent(verb="attack", modifier="heavy"))
        elif low.startswith("ignite "):
            name = text[7:].strip()
            item = self._find_item(name)
            if item is None:
                self.say(f"背包里没有「{name}」。")
                return
            self._run_intent(Intent(verb="ignite"), item=item)
        elif low.startswith("drink "):
            name = text[6:].strip()
            item = self._find_item(name)
            if item is None:
                self.say(f"背包里没有「{name}」。")
                return
            self._run_intent(Intent(verb="drink"), item=item)
        elif low in ("pick", "捡"):
            self._pick_up()
        elif low == "tick":
            self._tick()
        elif text in self.room.get("exits", {}):
            self._move(text)
        elif low in ("q", "quit", "退出"):
            raise SystemExit
        else:
            self.say("无效指令。可用：a / h / ignite 物品名 / drink 物品名 / pick / tick / 方向 / q")

    # ---------------- 核心流程 ----------------

    def _run_laws(self, intent, ctx):
        """执行法则，并把法则新产生的叙事日志打印到终端。"""
        start = len(self.log)
        matched = evaluate_laws(intent, ctx)
        for line in self.log[start:]:
            print(line)
        return matched

    def _run_intent(self, intent, item=None):
        if item is None:
            item = self._default_item()
        item_ctx = build_context(item, self.room, self.actor)

        ctx = {
            "item_context": item_ctx,
            "item": item,
            "room": self.room,
            "actor": self.actor,
            "intent": intent,
            "log": self.log,
        }
        enemy = self.room.get("enemy")
        if enemy is not None:
            ctx["target"] = enemy

        matched = self._run_laws(intent, ctx)

        if not matched:
            self.say(f"你尝试了 {intent.verb}，什么也没发生。")

        # 死亡判定：法则直接写在房间持有的敌人 Entity 上，无需写回配置
        if enemy is not None and enemy.get("hp", 0) <= 0:
            self.say(f"{enemy.name} 被击败了！")
            self.room.attrs["enemy"] = None
            enemy = None

        # 敌人回合（玩家没死且敌人还在）
        if self.actor.get("hp", 0) > 0 and enemy is not None:
            self._enemy_turn()

        if self.actor.get("hp", 0) <= 0:
            self.say("你倒下了……")

    def _default_item(self):
        """空手，或背包里第一把有切割能力的物品。"""
        for item in self.actor.attrs["bag"]:
            ctx = build_context(item, self.room, self.actor)
            if "cut" in ctx.capabilities:
                return item
        return Entity("空手", kind="item")

    def _find_item(self, name):
        for item in self.actor.attrs["bag"]:
            if item.name == name:
                return item
        return None

    def _pick_up(self):
        items = self.room.get("items", [])
        if not items:
            self.say("地上没有东西。")
            return
        name = items.pop(0)
        item = create(name)
        self.actor.attrs["bag"].append(item)
        self.say(f"你捡起了 {item.name}（重 {item.get('weight')}，锋利 {item.get('sharpness')}）。")

    def _move(self, direction):
        target_name = self.room.get("exits")[direction]
        self.current_room_name = target_name
        self.room = make_room_entity(target_name)
        self.say(f"你来到了 {target_name}。")

    def _tick(self):
        for item in self.actor.attrs["bag"]:
            item_ctx = build_context(item, self.room, self.actor)
            ctx = {
                "item_context": item_ctx,
                "item": item,
                "room": self.room,
                "actor": self.actor,
                "intent": Intent(verb="tick"),
                "log": self.log,
            }
            self._run_laws(Intent(verb="tick"), ctx)

    def _enemy_turn(self):
        enemy = self.room.get("enemy")
        dmg = enemy.get("attack", 0)
        actual = max(1, dmg - self.actor.get("defense", 0))
        self.actor.attrs["hp"] = max(0, self.actor.get("hp", 0) - actual)
        self.say(f"{enemy.name} 反击，对你造成 {actual} 点伤害。")
