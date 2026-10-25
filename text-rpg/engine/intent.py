from dataclasses import dataclass,field
"""
Intent 是玩家请求的结构化表示。
ItemContext 是选中物品的预计算视图，
不碰 item.attrs，行动结束丢弃
"""

@dataclass
class Intent:
    verb:str
    modifier:str|None=None
    target_type:str|None=None
    extra:dict=field(default_factory=dict)

@dataclass
class ItemContext:
    item:object
    effective_attrs:dict
    capabilities:set[str]