class Event:
    def __init__(self, name, source="fact"):
        if source not in ("fact", "assumption", "proposed"):
            raise ValueError("source must be 'fact', 'assumption' or 'proposed'")
        self.name, self.source = str(name), source
    def __repr__(self):
        return f"Event({self.name!r}, {self.source!r})"

class Gate:
    def __init__(self, kind, children):
        children = list(children)
        if len(children) < 2:
            raise ValueError(f"{kind} needs at least two inputs")
        for c in children:
            if not isinstance(c, (Event, Gate)):
                raise TypeError(f"{kind} inputs must be Event(...), AND(...) or OR(...)")
        self.kind, self.children = kind, children

def AND(*children):
    return Gate("AND", children)

def OR(*children):
    return Gate("OR", children)

def events(tree):
    if isinstance(tree, Event):
        return [tree]
    seen, out = set(), []
    for c in tree.children:
        for e in events(c):
            if e.name not in seen:
                seen.add(e.name); out.append(e)
    return out

def _sets(tree):
    if isinstance(tree, Event):
        return [frozenset([tree.name])]
    parts = [_sets(c) for c in tree.children]
    if tree.kind == "OR":
        return [s for p in parts for s in p]
    acc = [frozenset()]
    for p in parts:
        acc = [a | s for a in acc for s in p]
    return acc

def cut_sets(tree):
    """Minimal cut sets: the smallest combinations of events that cause the top event."""
    sets = set(_sets(tree))
    minimal = [s for s in sets if not any(o < s for o in sets)]
    return sorted((tuple(sorted(s)) for s in minimal), key=lambda s: (len(s), s))

def single_points(tree):
    """Events that cause the top event on their own."""
    return [s[0] for s in cut_sets(tree) if len(s) == 1]
