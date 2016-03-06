from datascraper import wikiscraper
from datamanipulator import dataman
from collections import OrderedDict
from operator import itemgetter
import json


def loadData():
    page = wikiscraper.loadRawHTML()
    return wikiscraper.extractFullDataset(page)

def printLevel(objlevel):
    keylist = []
    if isinstance(objlevel, OrderedDict):
        toprint = ""
        count = 1
        for n in objlevel.keys():
            if n == "link_key":
                continue
            toprint += "(%d): %s " % (count, n)
            keylist.append(n)
            count += 1
    elif isinstance(objlevel, list):
        toprint = ""
        count = 1
        for n in objlevel:
            toprint += "(%d): %s " % (count, n)
            keylist.append(n)
            count += 1
    else:
        toprint = str(objlevel)
        keylist.append(str(objlevel))
    print(toprint)
    return keylist

def navigator(categories, selector):
    obj_level = [categories]
    shadow_nav = [selector]
    while len(obj_level) > 0:
        print("Use a number to select one of the following (0 to navigate up)")
        keylist = printLevel(obj_level[-1])
        input_correct = False
        while not input_correct:
            try:
                navnum = int(input("> "))
                input_correct = True
            except Exception:
                pass
        if navnum <= 0:
            obj_level.pop()
            shadow_nav.pop()
        elif navnum < len(keylist)+1:
            try:
                obj_level.append(obj_level[-1][keylist[navnum-1]])
                shadow_nav.append(shadow_nav[-1][keylist[navnum-1]])
            except Exception:
                shadow_nav[-1].append(keylist[navnum-1])
                print("added value: %s" % keylist[navnum-1])

def main():
    tables = loadData()
    categories = dataman.verticalCategories(tables)
    selector = dataman.emptyVericalSelector(tables)
    navigator(categories, selector)

    allkeys = dataman.getKeysList(tables)
    resultlist = []
    for key in allkeys:
        resultlist.append(dataman.scoredCompare(key, tables, selector))
    resultlist = sorted(resultlist, key=itemgetter(1), reverse=True)
    best = dataman.selectByKey(resultlist[0][0], tables, "appearance")
    weakn = dataman.selectByKey(resultlist[0][0], tables, "weaknesses")
    print("Identity:")
    print(json.dumps(best, indent=2))
    print("Weaknesses:")
    print(json.dumps(weakn, indent=2))

if __name__ == "__main__":
    main()