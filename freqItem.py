import itertools
import time
import pandas as pd
import ast
import pync


# Global variables
confidence = 0.2
buckets = []


def openfile():
    "Opening input file"
    file_name = './data/groceries.csv'
    minsupport = 50
    nBucketsBitmap = 50
    "Reading input file"
    doc = open(file_name).read()
    "Removing newline characters"
    newfile = doc.split()
    "Creating buckets"
    for x in newfile:
        buckets.append(x.split(','))
    #size1freqset(minsupport, nBucketsBitmap, buckets)


def size1freqset(minsupport, nBucketsBitmap, buckets):
    "Creating Candidate List of Size 1"
    candidatelist1 = []
    finalist1 = []

    for i in range(0, len(buckets)):
        for b in buckets[i]:
            candidatelist1.append(b)

    candidatelist1 = sorted(set(candidatelist1))

    "Appending frequent items of size 1 to finallist1"
    support = 0
    f = open("./outData/demofile.txt", 'a')
    for k in candidatelist1:
        for i in range(0, len(buckets)):
            for j in buckets[i]:
                if k == j:
                    support += 1
        if support >= minsupport:
            finalist1.append(k)
            f.write('\n[\'' + str(k) + '\']\t' + str(support))
        support = 0

    itemiddic = {}
    counter = 1
    for c in candidatelist1:
        itemiddic[c] = counter
        counter += 1

    if finalist1:
        print("Frequent Itemsets of size 1")

        for x in finalist1:
            print(x)

        size2freqset(minsupport, nBucketsBitmap, itemiddic, buckets, finalist1);
    else:
        print("That's all folks: size1freqset!")


def size2freqset(minsupport, nBucketsBitmap, itemiddic, buckets, finalist1):
    k = 3

    countofbuckets = [0] * nBucketsBitmap
    bitmap = [0] * nBucketsBitmap
    pairs = []

    "PCY Pass 1"
    for i in range(0, len(buckets)):
        for x in range(0, len(buckets[i]) - 1):
            for y in range(x + 1, len(buckets[i])):
                if buckets[i][x] < buckets[i][y]:
                    countofbuckets[int(str(itemiddic[buckets[i][x]]) + str(itemiddic[buckets[i][y]])) % nBucketsBitmap] += 1
                    if ([buckets[i][x], buckets[i][y]] not in pairs):
                        pairs.append(sorted([buckets[i][x], buckets[i][y]]))
                else:
                    countofbuckets[int(str(itemiddic[buckets[i][y]]) + str(itemiddic[buckets[i][x]])) % nBucketsBitmap] += 1
                    if ([buckets[i][y], buckets[i][x]] not in pairs):
                        pairs.append(sorted([buckets[i][y], buckets[i][x]]))

    pairs = sorted(pairs)

    for x in range(0, len(countofbuckets)):
        if countofbuckets[x] >= minsupport:
            bitmap[x] = True
        else:
            bitmap[x] = False

    prunedpairs = []

    "Checking condition 1 of PCY Pass 2"

    for i in range(0, len(pairs)):
        for j in range(0, len(pairs[i]) - 1):
            if pairs[i][j] in finalist1 and pairs[i][j + 1] in finalist1:
                prunedpairs.append(pairs[i])

    candidatelist2 = []

    "Checking condition 2 of PCY Pass 2"
    for i in range(0, len(prunedpairs)):
        for j in range(0, len(prunedpairs[i]) - 1):
            if bitmap[int(str(itemiddic[prunedpairs[i][j]]) + str(itemiddic[prunedpairs[i][j + 1]])) % nBucketsBitmap]:
                candidatelist2.append(prunedpairs[i])

    "Appending frequent items of size 2 to finallist2"
    finalist2 = []
    p = 0
    f = open("./outData/demofile.txt", 'a')
    for c in range(0, len(candidatelist2)):
        for b in range(0, len(buckets)):
            if set(candidatelist2[c]).issubset(set(buckets[b])):
                p += 1
        if p >= minsupport and p != 0:
            finalist2.append(sorted(candidatelist2[c]))
            f.write('\n' + str(sorted(candidatelist2[c])) + '\t' + str(p))
        p = 0

    finalist2 = sorted(finalist2)

    if finalist2:
        print("\nFrequent Itemsets of size 2")
        for b in finalist2:
            print(','.join(b))
        sizekfreqset(minsupport, nBucketsBitmap, itemiddic, buckets, finalist2, k)

    else:
        print("That's all folks!")


def sizekfreqset(minsupport, nBucketsBitmap, itemiddic, buckets, prevout, k):
    """Creating Candidate List of Size k"""
    kcountofbuckets = [0] * nBucketsBitmap
    kbitmap = [0] * nBucketsBitmap
    kcombination = []
    prevout = prevout

    "Make k combination e.g. triplets"
    for a in prevout:
        for b in prevout:
            if (a != b):
                if set(a) & set(b) and len(list(set(a) & set(b))) >= k - 2:
                    kcombination.append(sorted(set(a) | set(b)))

    # print("checking kcombination")
    kcombination = sorted(kcombination)

    "PCY Pass 1 Hashing"

    hashingstring = ""

    for i in range(0, len(kcombination)):
        for x in kcombination[i]:
            hashingstring += str(itemiddic[x])
        kcountofbuckets[int(hashingstring) % nBucketsBitmap] += 1
        hashingstring = ""

    for x in range(0, len(kcountofbuckets)):
        if kcountofbuckets[x] >= minsupport:
            kbitmap[x] = True
        else:
            kbitmap[x] = False

    "Condition 1 is automatically satisfied"

    "Checking condition 2 of PCY Pass 2"
    hashingstring = ""
    klist = []

    for i in range(0, len(kcombination)):
        for j in kcombination[i]:
            hashingstring += str(itemiddic[j])
        if kbitmap[int(hashingstring) % nBucketsBitmap]:
            klist.append(kcombination[i])

    "Creating Candidate List of Size k"
    candidatelistk = []
    count = 1
    for i in range(1, len(klist)):
        if klist[i] == klist[i - 1]:
            count += 1
        else:
            # print("ELement is: ",klist[i-1]," and count is: ",count)
            if count >= k:
                candidatelistk.append(klist[i - 1])
            count = 1
    if count >= k:
        candidatelistk.append(klist[i - 1])
        # print("ELement is: ",klist[i-1]," and count is: ",count)

    "Appending frequent items of size k to output"
    output = []
    counter = 0
    f = open("./outData/demofile.txt", 'a')
    for c in range(0, len(candidatelistk)):
        for b in range(0, len(buckets)):
            if set(candidatelistk[c]).issubset(set(buckets[b])):
                counter += 1
        if counter >= minsupport and counter != 0:
            output.append(candidatelistk[c])
            f.write('\n' + str(sorted(candidatelistk[c])) + '\t' + str(counter))
        counter = 0

    if output:
        print("\nFrequent Itemsets of size ", k)
        for b in output:
            print(','.join(b))
        k += 1
        sizekfreqset(minsupport, nBucketsBitmap, itemiddic, buckets, output, k);
    else:
        print("That's all folks!")


def findsubsets(S,m):
    return set(itertools.combinations(S, m))


def frequent_itemsetsFromFile():
    freqDf = pd.read_csv('./outData/demofile.txt', sep='\t', header=None)
    return freqDf[0].values.tolist()


def generate_association_rules():
    s = []
    r = []
    length = 0
    count = 1
    inc1 = 0
    inc2 = 0
    num = 1
    m = []
    L = frequent_itemsetsFromFile()

    print("---------------------ASSOCIATION RULES------------------")

    for lista in L:
        lista = ast.literal_eval(lista)

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
                if inc2/inc1 >= confidence:
                    for index in lista:
                        if index not in s:
                            m.append(index)
                    print("Rule#  %d : %s ==> %s Confidence:%d Interest:%d " % (num, s, m,  100*inc2/inc1, 100*inc2/inc1 - 100*inc1/len(buckets) ))
                    num += 1


t0 = time.time()
openfile()
t1 = time.time()
total = t1 - t0
print('Elapsed Time PCY:', str(t1))

pync.notify('End PCY - Frequent Items')

generate_association_rules()

pync.notify('End RULES - Frequent Items')


