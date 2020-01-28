import json

from pyspark import SparkContext
import shutil
import os
import ast
import pandas as pd
import itertools


def generate_next_c(f_k, k):
    next_c = [var1 | var2 for index, var1 in enumerate(f_k) for var2 in f_k[index + 1:] if
              list(var1)[:k - 2] == list(var2)[:k - 2]]
    return next_c


def generate_f_k(sc, c_k, shared_itemset, sup):
    def get_sup(x):
        x_sup = len([1 for t in shared_itemset.value if x.issubset(t)])
        if x_sup >= sup:
            return x, x_sup
        else:
            return ()

    f_k = sc.parallelize(c_k).map(get_sup).filter(lambda x: x).collect()
    return f_k


def LogToFile(text):
    f = open('./outData/rules-numbers.txt', 'a')
    for key in text:
        temp = str(key[0]).replace("{", "")
        temp = temp.replace("}", "")
        f.write(temp + '\n')


def apriori(sc, f_input, f_output, min_sup):
    # read txt file
    data = sc.textFile(f_input)
    # min_suport
    sup = min_sup
    # split sort
    itemset = data.map(lambda line: sorted([int(item) for item in line.strip().split(',')]))
    # share itemset with all workers
    shared_itemset = sc.broadcast(itemset.map(lambda x: set(x)).collect())
    # frequent itemset list
    frequent_itemset = []

    # prepare candidate_1
    k = 1
    c_k = itemset.flatMap(lambda x: set(x)).distinct().collect()
    c_k = [{x} for x in c_k]

    # when candidate_k is not empty
    while len(c_k) > 0:
        # generate freq_k
        print("Candiates{}: {}".format(k, c_k))
        f_k = generate_f_k(sc, c_k, shared_itemset, sup)
        print("Frequents{}: {}".format(k, f_k))
        LogToFile(f_k)
        frequent_itemset.append(f_k)
        # generate candidate_k+1
        k += 1
        c_k = generate_next_c([set(item) for item in map(lambda x: x[0], f_k)], k)

    # Remove Old Dir
    isFile = os.path.isdir('./result/')
    if isFile:
        shutil.rmtree('./result/')
    # Save to File
    sc.parallelize(frequent_itemset, numSlices=1).saveAsTextFile(f_output)
    sc.stop()

def findsubsets(S,m):
    return set(itertools.combinations(S, m))


def frequent_itemsetsFromFile(freq_items_file):
    newfile = open(freq_items_file)
    temp = []
    for x in newfile:
        temp_list = x.split(',')
        for i in range(0, len(temp_list)):
            if not temp_list[i] == '':
                temp_list[i] = int(temp_list[i])
        temp.append(temp_list)
    return temp


def reading_dict(in_file):
    whip = eval(open(in_file, 'r').read())
    return whip


def getKeysByValue(dictOfElements, valueToFind):
    listOfKeys = list()
    listOfItems = dictOfElements.items()
    for item  in listOfItems:
        if item[1] == valueToFind:
            listOfKeys.append(item[0])
    return  listOfKeys

def generate_association_rules(in_file_name, freq_items_file, saved_dict_file, confidence):
    dictionary_converter = reading_dict(saved_dict_file)
    s = []
    r = []
    num = 1
    m = []
    buckets = []
    doc = open(in_file_name).read()
    "Removing newline characters"
    newfile = doc.split('\n')
    "Creating buckets"
    for x in newfile:
        temp_list = x.split(',')
        for i in range(0, len(temp_list)):
            if not temp_list[i] == '':
                temp_list[i] = int(temp_list[i])
            else:
                temp_list.remove(temp_list[i])
        buckets.append(temp_list)

    L = frequent_itemsetsFromFile(freq_items_file)

    print("---------------------ASSOCIATION RULES------------------")

    for lista in L:
        length = len(lista)
        count = 1
        while count < length:
            s = []
            r = findsubsets(lista, count)
            count += 1
            for item in r:
                inc1 = 0
                inc2 = 0
                s = []
                m = []
                for i in item:
                    s.append(i)
                for T in buckets:
                    if set(s).issubset(set(T)):
                        inc1 += 1
                    if set(lista).issubset(set(T)):
                        inc2 += 1
                if not inc1 == 0 and not inc2 == 0:
                    if inc2/inc1 >= confidence:
                        for index in lista:
                            if index not in s:
                                m.append(index)
                        #print("Rule#  %d : %s ==> %s Confidence:%d Interest:%d " % (num, s, m,  100*inc2/inc1, 100*inc2/inc1 - 100*inc1/len(buckets) ))
                        for item in range(len(s)):
                            s[item] = getKeysByValue(dictionary_converter, s[item])
                        for item2 in range(len(m)):
                            m[item2] = getKeysByValue(dictionary_converter, m[item2])
                        print("Rule#  %d : %s ==> %s Confidence:%d Interest:%d " % (num, s, m,  100*inc2/inc1, 100*inc2/inc1 - 100*inc1/len(buckets) ))



                        num += 1

if __name__ == "__main__":
    #if os.path.exists(sys.argv[2]):
        #shutil.rmtree(sys.argv[2])
    #apriori(SparkContext(appName="Spark Apriori"), sys.argv[1], sys.argv[2], float(sys.argv[3]))
    #apriori(SparkContext(appName="Spark Apriori Most Frequent Items"), "./outData/test.txt", "./result/test", 100)

    # Rule generation part
    generate_association_rules("./outData/test.txt", "./outData/rules-numbers.txt", "./outData/dict.txt", 0.5)
