import random

from data.defs import DEFS


class Entity:
    def __init__(self, name, kind,**attrs):
        self.name = name
        self.kind = kind
        self.attrs = attrs
        self.states=set()
        self.state_data={}

    def get(self,key,default=None):
        return self.attrs.get(key,default)

    def has(self,key):
        return key in self.attrs


def create(name):
    defn=DEFS.get(name)
    if not defn:
        raise ValueError(f"未知定义：{name} ")
    attrs={}
    for attr ,value in defn["attrs"].items():
        # 固定单值，直接转为attr:fixed_value
        if "fixed" in value:
            attrs[attr]=value["fixed"]
            continue

        #存在偏差情况，做偏差设置
        base,var=value["base"],value.get("var",0)
        if isinstance(base, int):
            attrs[attr] = base + random.randint(-var, var)
        else:
            attrs[attr] = round(base + random.uniform(-var, var), 2)
    return Entity(name=name, kind=defn["kind"], **attrs)

def create_from_dict(config):
    """从房间配置字典创建敌人实例。"""
    name = config["name"]
    e = Entity(name=name, kind="character")
    e.attrs.update(config)
    return e