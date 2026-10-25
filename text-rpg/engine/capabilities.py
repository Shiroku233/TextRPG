#engine/capabilities.py

"""
流程：由build_item_context操作
1. effective_attrs依据EFFECTIVE_MODIFIERS收集有效属性
2. capabilities_from_attrs通过传入的有效属性推导能力集合
3. 返回ItemContext实例
"""

from engine.intent import ItemContext

EFFECTIVE_MODIFIERS = [
    {
        "id": "wet_reduces_flammability",
        "when": lambda e, r, p: (
            r is not None
            and r.get("wet") is True
            and e.get("material") == "木"
        ),
        "attr": "flammability",
        "delta": -4,
    },
    {
        "id": "whetstone_sharpens",
        "when": lambda e, r, p: (
            r is not None
            and r.get("has_whetstone") is True
            and e.get("sharpness", 0) > 0
        ),
        "attr": "sharpness",
        "delta": 2,
    },
    {
        "id": "burning_sharpens_tip",
        "when": lambda e, r, p: "burning" in e.states,
        "attr": "sharpness",
        "delta": 1,
    },
]

def effective_attrs(entity,room=None,actor=None):
    """
    返回实体在当前场景下的有效属性。不修改原对象。
    复制原始 attrs，然后逐条应用 EFFECTIVE_MODIFIERS。
    """
    a=dict(entity.attrs)
    for mod in EFFECTIVE_MODIFIERS:
        if mod["when"](entity,room,actor):
            attr = mod["attr"]
            a[attr]=a.get(attr,0)+mod["delta"]
    return a

def capabilities(entity, attrs):
    """
    具体是capabilities__from_attrs
    从已算好的属性字典推导能力集合。
    不重复调用 effective_attrs，供预计算和按需推导共用。
    """
    caps=set()
    if attrs.get("sharpness",0)>=1:
        caps.add("cut")
    if attrs.get("sharpness",0)>=3:
        caps.add("thrust")

    if attrs.get("flammability",0)>=5:
        caps.add("flammable")

    if "burning" in entity.states:
        caps.add("be_burning")
        caps.add("lighting")

    if attrs.get("capacity",0)>0:
        caps.add("capable")

    if attrs.get("drinkable"):
        caps.add("be_drinkable")

    if attrs.get("edible"):
        caps.add("be_edible")

    return caps



def build_context(item, room=None, actor=None):
    """
    预计算选中物品的 ItemContext，供法则匹配读取。
    ItemContext 持有 item、effective_attrs、capabilities，
    行动结束丢弃，不污染 item.attrs。
    """
    a = effective_attrs(item, room, actor)
    c = capabilities(item, a)
    return ItemContext(item=item, effective_attrs=a, capabilities=c)

