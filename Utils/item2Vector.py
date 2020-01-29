"""
This file is useful to convert a file with products as string
into a file with IDs encoded in a correct way.

OUTPUT:
- dictionary file ../outData/norm-dict.txt
- vectorized dataset ../outData/norm-groceries.txt
"""

baskets = []
with open('../data/groceries.csv', 'r') as f:
    for line in f:
        basket = []
        line = line[:-1]
        items = line.split(",")
        for item in items:
            basket.append(item)
        baskets.append(basket)

#baskets = set(baskets)
elems = set()
for b in baskets:
    elems.update(b)


mapping = {}
reverseMapping = {}
key = 0
for basket in elems:
    mapping[basket] = key
    reverseMapping[key] = basket
    key += 1

print("Mapping")
print(mapping)

dict = open("../outData/norm-dict.txt", "w")
dict.write(str(mapping))
dict.close()

ds = open('../outData/norm-groceries.txt', 'a')
for basket in baskets:
    line_file = list()
    for item in basket:
        line_file.append(mapping[item])
    ds.write(str(line_file)[1:-1] + '\n')
    line_file = []
ds.close()
