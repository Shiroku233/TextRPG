import re
from dataclasses import dataclass



@dataclass
class Subject:
    path:str

    def resolve(self, ctx):
        parts = self.path.split(".")
        first = parts[0]

        # item_context 是独立命名空间，不经过 Entity 的 attrs 逻辑
        if first == "item_context":
            obj = ctx.get("item_context")
            for part in parts[1:]:
                if obj is None:
                    return None
                if part == "capabilities":
                    obj = getattr(obj, "capabilities", None)
                elif part == "attrs":
                    obj = getattr(obj, "effective_attrs", None)
                elif isinstance(obj, dict):
                    obj = obj.get(part)
                else:
                    obj = getattr(obj, part, None)
            return obj

        obj = ctx.get(first)
        for part in parts[1:]:
            if obj is None:
                return None
            if part == "attrs":
                obj = getattr(obj, "attrs", {})
            elif part == "capabilities":
                caps = getattr(obj, "capabilities", None)
                if caps is None:
                    from engine.capabilities import build_context
                    caps = build_context(obj, ctx.get("room"), ctx.get("actor")).capabilities
                obj = caps
            elif part == "states":
                obj = getattr(obj, "states", None)
            elif isinstance(obj, dict):
                obj = obj.get(part)
            else:
                obj = getattr(obj, part, None)
        return obj

    def set(self, ctx, value):
        parts = self.path.split(".")
        first = parts[0]

        if first == "item_context":
            obj = ctx.get("item_context")
            for part in parts[1:-1]:
                if obj is None:
                    return
                if part == "attrs":
                    obj = getattr(obj, "effective_attrs", None)
                elif isinstance(obj, dict):
                    obj = obj.get(part)
                else:
                    obj = getattr(obj, part, None)
            last = parts[-1]
            if obj is None:
                return
            if isinstance(obj, dict):
                obj[last] = value
            else:
                setattr(obj, last, value)
            return

        obj = ctx.get(first)
        for part in parts[1:-1]:
            if obj is None:
                return
            if isinstance(obj, dict):
                obj = obj.get(part)
            else:
                obj = getattr(obj, part, None)
        last = parts[-1]
        if obj is None:
            return
        if isinstance(obj, dict):
            obj[last] = value
        else:
            setattr(obj, last, value)

@dataclass
class Operation:
    name: str

    def compare(self, value, target):
        match self.name:
            case "==": return value == target
            case "!=": return value != target
            case ">=": return value is not None and value >= target
            case "<=": return value is not None and value <= target
            case "contains": return value is not None and target in value
            case "not_contains": return value is None or target not in value
            case "exists": return value is not None
            case "not_exists": return value is None
            case _: return False


@dataclass
class Condition:
    value:object

@dataclass
class Application:
    name:str

    def apply(self,ctx,subject,content):
        if self.name == "record":
            ctx.setdefault("log", []).append(str(content))
            return

        current = subject.resolve(ctx)
        if self.name == "subtract":
            subject.set(ctx, (current or 0) - content)
        elif self.name == "add":
            subject.set(ctx, (current or 0) + content)
        elif self.name == "set":
            subject.set(ctx, content)
        elif self.name == "add_state":
            if current is None:
                current = set()
                subject.set(ctx, current)
            current.add(content)
        elif self.name == "remove_state":
            if current is not None:
                current.discard(content)


_FORMULA_RE = re.compile(r"^[\w.()+*/\s-]+$")

@dataclass
class Result:
    content:object

    def evaluate(self, ctx):
        if not isinstance(self.content, str):
            return self.content
        # 只有纯公式才走 eval；含中文、花括号的叙事模板直接返回
        if _FORMULA_RE.match(self.content) and "." in self.content:
            local = _build_eval_locals(ctx)
            try:
                return eval(self.content, {"__builtins__": {}}, local)
            except Exception:
                return self.content
        return self.content

class _View:
    """递归包装字典，让嵌套字段可用 . 访问。"""
    def __init__(self, data):
        for k, v in data.items():
            if isinstance(v, dict):
                setattr(self, k, _View(v))
            else:
                setattr(self, k, v)


def _build_eval_locals(ctx):
    local = {}
    item_ctx = ctx.get("item_context")
    if item_ctx is not None:
        merged = {**getattr(item_ctx, "attrs", {}), **item_ctx.effective_attrs}
        view = _View(merged)
        view.attrs = _View(merged)   # 让 item.attrs.sharpness 也能读
        local["item"] = view
    for key in ("item", "target", "room", "actor"):
        obj = ctx.get(key)
        if obj is None:
            continue
        if isinstance(obj, dict):
            local[key] = _View(obj)
        elif hasattr(obj, "attrs"):
            view = _View(obj.attrs)
            view.attrs = _View(obj.attrs)
            local[key] = view
        else:
            local[key] = obj
    if "intent" in ctx:
        local["intent"] = ctx["intent"]
    return local