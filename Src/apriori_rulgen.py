'''
    This file extract the frequent itemset from the normalized basket file
    And saves them into the ../Data/frequent_itemsets.txt file
    Furthermore, it identifies which are the association rules
    starting from the frequent itemsets
'''
from pyspark import SparkContext
import itertools
import findspark
import os
import argparse


# To be compatible with one OS
#java8_location= '/usr/lib/jvm/java-8-openjdk-amd64' # Set your own
#os.environ['JAVA_HOME'] = java8_location
# -----------------------------------------------

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


def log_to_file(text, fname):
    f = open(fname, 'a')
    for key in text:
        temp = str(key[0])[1:-1]
        f.write(temp.replace(' ', '') + '\n')
    f.close()


def apriori(sc, f_input, f_out, sup):

    # Read txt file
    data = sc.textFile(f_input)
    
    itemset = data.map(lambda line: sorted([int(item) for item in line.split(',')]))

    # Share itemset with all workers
    shared_itemset = sc.broadcast(itemset.map(lambda x: set(x)).collect())

    # Frequent itemset list
    frequent_itemset = []

    # Prepare candidate_1 (k=1)
    k = 1
    c_k = itemset.flatMap(lambda x: set(x)).distinct().collect()
    c_k = [{x} for x in c_k]

    # When candidate_k is not empty
    while len(c_k) > 0:

        # Generate freq_k
        f_k = generate_f_k(sc, c_k, shared_itemset, sup)
        print("Frequents{}: {}".format(k, f_k))
        log_to_file(f_k, f_out)
        frequent_itemset.append(f_k)
        # generate candidate_k+1
        k += 1
        c_k = generate_next_c([set(item) for item in map(lambda x: x[0], f_k)], k)

    sc.stop()


def frequent_itemsets_from_file(freq_items_file):
    newfile = open(freq_items_file)
    temp = []
    for x in newfile:
        temp_list = x.split(',')
        for i in range(0, len(temp_list)):
            if not temp_list[i] == '':
                temp_list[i] = int(temp_list[i])
        temp.append(temp_list)
    return temp


def getKeysByValue(dictOfElements, valueToFind):
    listOfKeys = list()
    listOfItems = dictOfElements.items()
    for item  in listOfItems:
        if item[1] == valueToFind:
            listOfKeys.append(item[0])
    return  listOfKeys


def get_support(bucket, left, fr_item):
    inc1 = 0
    inc2 = 0
    if set(left).issubset(set(bucket)):
        inc1 = 1
    if set(fr_item).issubset(set(bucket)):
        inc2 = 1
    return (0, [inc1, inc2])


def generate_association_rules(sc, in_file_name, freq_items_file, saved_dict_file, rules_out_file, confidence):

    dictionary_converter = eval(open(saved_dict_file, 'r').read())

    num = 1
    buckets = []

    doc = open(in_file_name).read()

    # Removing newline characters
    newfile = doc.split('\n')

    if sc is None:
        # Creating buckets
        for x in newfile:
            temp_list = x.split(',')
            for i in range(0, len(temp_list)):
                if not temp_list[i] == '':
                    temp_list[i] = int(temp_list[i])
                else:
                    temp_list.remove(temp_list[i])
            buckets.append(temp_list)
        len_buckets = len(buckets)
    else:
        data = sc.textFile(in_file_name)
        spark_baskets = data.map(lambda line: sorted([int(item) for item in line.split(',')]))
        len_buckets = spark_baskets.count()
        shared_itemset = sc.broadcast(spark_baskets.map(lambda x: set(x)).collect())

    L = frequent_itemsets_from_file(freq_items_file)

    print("===================== ASSOCIATION RULES =====================")

    rules_apped_file = open(rules_out_file, 'w')
    for fr_item in L:
        length = len(fr_item)
        count = 1
        while count < length:
            subsets = set(itertools.combinations(fr_item, count))
            count += 1
            for sub in subsets:
                inc1 = 0
                inc2 = 0
                left = list(sub)
                right = []

                if sc is None:
                    # Traditional counting
                    for bucket in buckets:
                        # Increase support for left and right sides
                        if set(left).issubset(set(bucket)):
                            inc1 += 1
                        if set(fr_item).issubset(set(bucket)):
                            inc2 += 1
                else:
                    # Map Reduce for support counting
                    support = spark_baskets.map(lambda bucket: get_support(bucket, left, fr_item)).reduceByKey(lambda x, y: [x[0] + y[0], x[1] + y[1]]).collect()[0][1]
                    inc1 = support[0]
                    inc2 = support[1]

                if inc1*inc2 != 0:
                    if inc2/inc1 >= confidence:
                        for index in fr_item:
                            if index not in left:
                                right.append(index)
                        #print("Rule#  %d : %s ==> %s Confidence:%d Interest:%d " % (num, left, rigth,  100*inc2/inc1, 100*inc2/inc1 - 100*inc1/len_buckets ))
                        for item in range(0, len(left)):
                            left[item] = getKeysByValue(dictionary_converter, left[item])
                        for item2 in range(0, len(right)):
                            right[item2] = getKeysByValue(dictionary_converter, right[item2])
                        #out = "%d : %s --> %s \t\t Conf:%d Int:%d" % (num, left, rigth,  100*inc2/inc1, 100*(inc2/inc1 - inc1/len_buckets))
                        
                        flat_left = []
                        for l in left:
                            flat_left.append(l[0])
                            
                        flat_right = []
                        for r in right:
                            flat_right.append(r[0])
                        
                        out = str(num) + ";" + str(flat_left) + ";" + str(flat_right) + ";" + str(inc2/inc1) + ";" + str(inc2/inc1 - inc1/len_buckets)
                        print(out)
                        rules_apped_file.write(out + '\n')
                        num += 1


# Construct the argument parser
ap = argparse.ArgumentParser()

# Add the arguments to the parser
ap.add_argument("-a", "--input_csv_file", required=True,
   help="input csv file normalized")
ap.add_argument("-b", "--output_freqitemset", required=True,
   help="output freqitemset txt file")
ap.add_argument("-c", "--dictionary_file", required=True,
   help="output freqitemset txt file")
ap.add_argument("-d", "--rules_out_file", required=True,
   help="output freqitemset txt file")
ap.add_argument("-sup", "--support", required=True,
   help="support of freq Items")
ap.add_argument("-conf", "--confidence", required=True,
   help="confidence of generated rules")
args = vars(ap.parse_args())

'''input_csv_file     = "../Data/groceries_int.csv"
output_freqitemset = "../Data/frequent_itemsets.txt"
dictionary_file    = "../Data/normalized_dictionary.txt"
rules_out_file     = "../Data/association_rules.txt"'''

input_csv_file     = args['input_csv_file']
output_freqitemset = args['output_freqitemset']
dictionary_file    = args['dictionary_file']
rules_out_file     = args['rules_out_file']

# Clear output file content
ftmp = open(output_freqitemset, 'w')
ftmp.close()

sc = SparkContext(appName="Spark Apriori Most Frequent Items")

# The suppurt is expressed in %
'''support = 50
confidence = 0.4'''

support = int(args['support'])
confidence = float(args['confidence'])

# Apriori in Spark
apriori(sc, input_csv_file, output_freqitemset, support)

# Rule generation part
generate_association_rules(None, input_csv_file, output_freqitemset, dictionary_file, rules_out_file, confidence)
