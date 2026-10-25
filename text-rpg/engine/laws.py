from dataclasses import dataclass

from engine.language import Subject, Application, Operation, Condition, Result

@dataclass
class Law:
    id: str
    priority: int
    when: list[tuple[Subject,Operation,Condition]]
    then: list[tuple[Subject,Application,Result]]
    desc: str=""

LAWS = {
    "attack": [
        Law(
            id="burning_attack",
            priority=90,
            when=[
                (Subject("item_context.capabilities"), Operation("contains"), Condition("be_burning")),
                (Subject("target"), Operation("exists"), Condition(None)),
            ],
            then=[
                (Subject("target.attrs.hp"), Application("subtract"),
                 Result("item.attrs.sharpness * 2 + 3")),
                (Subject("log"), Application("record"),
                 Result("你用燃烧的{item.name}攻击{target.name}，造成{actual}点火焰伤害。")),
            ],
            desc="燃烧中的物品攻击额外造成火焰伤害",
        ),
        Law(
            id="sharp_attack",
            priority=80,
            when=[
                (Subject("item_context.capabilities"), Operation("contains"), Condition("cut")),
                (Subject("target"), Operation("exists"), Condition(None)),
                (Subject("item.states"), Operation("not_contains"), Condition("burning")),
            ],
            then=[
                (Subject("target.attrs.hp"), Application("subtract"),
                 Result("item.attrs.sharpness + actor.attrs.attack // 2")),
                (Subject("log"), Application("record"),
                 Result("你用{item.name}攻击{target.name}，造成{actual}点伤害。")),
            ],
        ),
    ],
    "ignite": [
        Law(
            id="ignite",
            priority=100,
            when=[
                (Subject("item_context.capabilities"), Operation("contains"), Condition("flammable")),
                (Subject("room.attrs.has_fire"), Operation("=="), Condition(True)),
            ],
            then=[
                (Subject("item.states"), Application("add_state"), Result("burning")),
                (Subject("log"), Application("record"),
                 Result("你点燃了{item.name}，它现在是一支火把。")),
            ],
        ),
    ],
    "drink": [
        Law(
            id="drink_potion",
            priority=70,
            when=[
                (Subject("item_context.capabilities"), Operation("contains"), Condition("be_drinkable")),
            ],
            then=[
                (Subject("actor.attrs.hp"), Application("add"), Result("item.attrs.heal")),
                (Subject("item.states"), Application("add_state"), Result("consumed")),
                (Subject("log"), Application("record"),
                 Result("你喝下{item.name}，恢复若干点生命。")),
            ],
        ),
    ],
    "tick": [
        Law(
            id="burning_tick",
            priority=200,
            when=[
                (Subject("item.states"), Operation("contains"), Condition("burning")),
            ],
            then=[
                (Subject("item.state_data.burning.remaining"), Application("subtract"), Result(1)),
                (Subject("log"), Application("record"), Result("{item.name}的火势减弱了。")),
            ],
        ),
    ],
}

def evaluate_laws(intent,ctx):
    laws=LAWS.get(intent.verb,[])
    for law in sorted(laws,key=lambda l: -l.priority):
        matched=all(
            op.compare(subject.resolve(ctx),condition.value)
            for subject,op,condition in law.when
        )
        if matched:
            for subject,ap,result in law.then:
                content=result.evaluate(ctx)
                ap.apply(ctx,subject,content)
            return True
    return False
