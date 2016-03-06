from urllib import request
from bs4 import BeautifulSoup
from collections import OrderedDict
import json
import re


datapage = "https://en.wikipedia.org/wiki/List_of_vampire_traits_in_folklore_and_fiction"

def loadRawHTML():
    req = request.Request(
            datapage,
            data=None
        )
    with request.urlopen(req) as page:
        return page.read().decode("utf-8")

def stripUnwantedCellContent(cell):
    for s in cell.find_all("sup"):
        s.extract()

def expandMultiRows(table):
    splitter = re.compile("([^:]+): (.+)")
    tofix = []
    rc = 0
    for row in table.find_all("tr"):
        cells = row.find_all("td")
        if len(cells) >= 2:
            if cells[0].get("rowspan") is not None:
                link = cells[0].find("a")
                if link is not None:
                    linkaddr = str(link.get("href"))
                else:
                    linkaddr = ""
                tofix.append({"start": rc,
                              "end": rc + int(cells[0].get("rowspan")),
                              "header": str(cells[0].get_text()),
                              "linkaddr": linkaddr})
        rc += 1
    if len(tofix) == 0:
        return
    rw = 0
    for row in table.find_all("tr"):
        if len(tofix) == 0:
            break
        if rw >= tofix[0]["start"] and rw < tofix[0]["end"]:
            #print("row before:")
            #print(row)
            cells = row.find_all("td")
            trailer = ""
            if rw == tofix[0]["start"]:
                secondcell = 1
            else:
                secondcell = 0
            cellone = str(cells[secondcell].get_text())
            rematch = splitter.match(cells[secondcell].get_text())
            if rematch is not None:
                trailer = rematch.group(1)
                cellone = rematch.group(2)
            if rw == tofix[0]["start"]:
                cells[0].extract()
            newcell = BeautifulSoup("<td></td>", "html.parser")
            if tofix[0]["linkaddr"] != "":
                newcell.td.insert(1, newcell.new_tag("a",
                                               href=tofix[0]["linkaddr"] + "_" + trailer))
                newcell.td.a.insert(1, tofix[0]["header"] + " " + trailer)
            else:
                newcell.td.insert(1, tofix[0]["header"] + " " + trailer)
            row.insert(1, newcell)
            #print("inserted: " + str(newcell))
            cells[secondcell].clear()
            cells[secondcell].insert(1, cellone)
            #print("replaced: " + str(cells[secondcell]))
            #print("fixed row:")
            #print(row)
            if rw == tofix[0]["end"] - 1:
                tofix.pop(0)
        rw += 1

def extractSingleTable(table):
    keys = []
    dataset = []
    theader = table.find_all("tr")[0]
    for coltitle in theader.find_all("th"):
        keys.append(str(coltitle.get_text()))
    for row in table.find_all("tr")[1:]:
        newentry = OrderedDict()
        cells = row.find_all("td")
        key_index = 0
        for cell in cells:
            if key_index == 0:
                link = cell.find("a")
                if link is not None:
                    newentry["link_key"] = str(link.get("href"))
                else:
                    newentry["link_key"] = str(cell.get_text())
            stripUnwantedCellContent(cell)
            newentry[keys[key_index]] = str(cell.get_text())
            key_index += 1
        #print("loaded " + newentry["link_key"])
        dataset.append(newentry)
    return dataset

def extractFullDataset(html):
    retables = OrderedDict()
    soup = BeautifulSoup(html, "html.parser")
    htmltables = soup.find_all("table", attrs={"class": list("wikitable sortable jquery-tablesorter".split(" "))})
    assert len(htmltables) == 5  # TODO: make more flexible
    for i in range(5):
        expandMultiRows(htmltables[i])
    retables["appearance"] = extractSingleTable(BeautifulSoup(str(htmltables[0]), "html.parser"))
    retables["weaknesses"] = extractSingleTable(BeautifulSoup(str(htmltables[1]), "html.parser"))
    retables["supernatural powers"] = extractSingleTable(BeautifulSoup(str(htmltables[2]), "html.parser"))
    retables["reproduction and feeding"] = extractSingleTable(BeautifulSoup(str(htmltables[3]), "html.parser"))
    retables["setting characteristics"] = extractSingleTable(BeautifulSoup(str(htmltables[4]), "html.parser"))
    return retables


if __name__ == "__main__":
    print("fetching html data....")
    page = loadRawHTML()
    print("extracting tables....")
    tables = extractFullDataset(page)
    print("saving data....")
    with open("database.json", "w") as file:
        json.dump(tables, file, indent=4)