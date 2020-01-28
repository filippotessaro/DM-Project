"""
This file is useful to convert a file with products as string
into a file with IDs encoded in a correct way.
"""

superm = []
baskets = []
with open('../data/groceries.csv', 'r') as f:
    for line in f:
        basket = []
        items = line.split(",")
        for item in items:
            superm.append(item)
            basket.append(item)
        baskets.append(basket)

elems = set()
for b in baskets:
    elems.update(b)

mapping = {}
reverseMapping = {}
key = 0
for e in elems:
    mapping[e] = key
    reverseMapping[key] = e
    key += 1

print("Mapping")
print(mapping)

f = open("../outData/dict.txt","w")
f.write( str(mapping) )
f.close()

newBaskets = []

fileNew = open('../outData/test.txt', 'a')

for basket in baskets:
    line_file = list()
    for item in basket:
        line_file.append(mapping[item])
    fileNew.write(str(line_file) + '\n')
    line_file = []
