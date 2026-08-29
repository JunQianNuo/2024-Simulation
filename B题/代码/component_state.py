"""Q2/Q3 共用的零件质量—信息状态语义。"""

MISSING, BAD, GOOD = -1, 0, 1
INFO_MISSING, UNKNOWN, KNOWN_GOOD = "M", "U", "G"
SRC_MISSING, NEW, RECOVERED = "M", "N", "R"


def positive_transitions(items):
    return [(state, probability) for state, probability in items if probability > 0.0]


def purchase_options(quality, info, source, defect):
    if quality != MISSING:
        return [((quality, info, source), 1.0)]
    return positive_transitions([
        ((GOOD, UNKNOWN, NEW), 1 - defect),
        ((BAD, UNKNOWN, NEW), defect),
    ])


def inspect_component(quality, info, enabled):
    """返回 (是否收费, 是否淘汰, 检后信息)。"""
    if not enabled or info == KNOWN_GOOD:
        return False, False, info
    return True, quality == BAD, KNOWN_GOOD if quality == GOOD else info


def closed_transient_classes(p, terminal):
    graph = [[j for j, value in enumerate(row) if value > 0.0] for row in p]
    reverse = [[i for i in range(len(p)) if p[i, j] > 0.0] for j in range(len(p))]
    seen, order = set(), []

    def visit(i):
        seen.add(i)
        for j in graph[i]:
            if j not in seen:
                visit(j)
        order.append(i)

    for i in range(len(p)):
        if i not in seen:
            visit(i)
    seen, groups = set(), []

    def collect(i, group):
        seen.add(i)
        group.append(i)
        for j in reverse[i]:
            if j not in seen:
                collect(j, group)

    for root in reversed(order):
        if root in seen:
            continue
        group = []
        collect(root, group)
        inside = set(group)
        if all(terminal[i] == 0.0 and all(j in inside for j in graph[i]) for i in group):
            groups.append(group)
    return groups
