dictionary = eval(open("../Data/normalized_dictionary.txt", "r").read())

f = open("../Data/frequent_itemsets.txt", "r")
out = open("../Data/frequent_itemsets_name.txt", "w+")

def getKeysByValue(dictOfElements, valueToFind):
    listOfKeys = list()
    listOfItems = dictOfElements.items()
    for item  in listOfItems:
        if item[1] == valueToFind:
            listOfKeys.append(item[0])
    return  listOfKeys

for row in f.readlines():
    row = row[:-1]
    items = row.split(",")
    names = ""
    for item in items:
        names += str(getKeysByValue(dictionary, int(item))[0]) + ","
    names = names[:-1]
    out.write(names + "\n")

out.close()
f.close()
