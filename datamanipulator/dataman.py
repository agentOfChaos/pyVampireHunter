from collections import OrderedDict


def verticalCategories(tables):
    categories = OrderedDict()
    for k,v in tables.items():
        categories[k] = OrderedDict()
        for entry in v:
            for h,w in entry.items():
                if h in categories[k].keys():
                    if not w in categories[k][h]:
                        categories[k][h].append(w)
                else:
                    categories[k][h] = [w]
    return categories

def emptyVericalSelector(tables):
    selector = OrderedDict()
    for k,v in tables.items():
        selector[k] = OrderedDict()
        for entry in v:
            for h,w in entry.items():
                if h not in selector[k].keys():
                    selector[k][h] = []
    return selector

def getKeysList(tables):
    keys = []
    for k,v in tables.items():
        for entry in v:
            if entry["link_key"] not in keys:
                keys.append(entry["link_key"])
    return keys

def scoredCompare(key, tables, selector):
    score = 0
    for k,v in tables.items():
        for entry in v:
            if entry["link_key"] != key:
                continue
            for h,w in entry.items():
                paragon = selector[k][h]
                if w in paragon:
                    score += 1
    return (key, score)

def selectByKey(key, tables, subtable):
    for entry in tables[subtable]:
        if entry["link_key"] == key:
            return entry
    return None
