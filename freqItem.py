import sys
import time


def openfile():
    "Opening input file"
    file_name = './data/groceries.csv'
    minsupport = 20
    nbuckets = 4
    "Reading input file"
    doc = open(file_name).read()
    "Removing newline characters"
    newfile = doc.split()
    "Creating buckets"
    buckets = []
    for x in newfile:
        buckets.append(x.split(','))

    size1freqset(minsupport, nbuckets, buckets);


def size1freqset(minsupport, nbuckets, buckets):
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
                if (k == j):
                    support += 1
        if support >= minsupport:
            finalist1.append(k)
            f.write('\n' + str(k) + '\t' + str(support))
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

        size2freqset(minsupport, nbuckets, itemiddic, buckets, finalist1);
    else:
        print("That's all folks: size1freqset!")


def size2freqset(minsupport, nbuckets, itemiddic, buckets, finalist1):
    k = 3

    countofbuckets = [0] * nbuckets
    bitmap = [0] * nbuckets
    pairs = []

    "PCY Pass 1"
    for i in range(0, len(buckets)):
        for x in range(0, len(buckets[i]) - 1):
            for y in range(x + 1, len(buckets[i])):
                if buckets[i][x] < buckets[i][y]:
                    countofbuckets[int(str(itemiddic[buckets[i][x]]) + str(itemiddic[buckets[i][y]])) % nbuckets] += 1
                    if ([buckets[i][x], buckets[i][y]] not in pairs):
                        pairs.append(sorted([buckets[i][x], buckets[i][y]]))
                else:
                    countofbuckets[int(str(itemiddic[buckets[i][y]]) + str(itemiddic[buckets[i][x]])) % nbuckets] += 1
                    if ([buckets[i][y], buckets[i][x]] not in pairs):
                        pairs.append(sorted([buckets[i][y], buckets[i][x]]))

    pairs = sorted(pairs)

    for x in range(0, len(countofbuckets)):
        if countofbuckets[x] >= minsupport:
            bitmap[x] = 1
        else:
            bitmap[x] = 0

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
            if bitmap[int(str(itemiddic[prunedpairs[i][j]]) + str(itemiddic[prunedpairs[i][j + 1]])) % nbuckets] == 1:
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
        sizekfreqset(minsupport, nbuckets, itemiddic, buckets, finalist2, k)
    else:
        print("That's all folks!")


def sizekfreqset(minsupport, nbuckets, itemiddic, buckets, prevout, k):
    """Creating Candidate List of Size k"""
    kcountofbuckets = [0] * nbuckets
    kbitmap = [0] * nbuckets
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
        kcountofbuckets[int(hashingstring) % nbuckets] += 1
        hashingstring = ""

    for x in range(0, len(kcountofbuckets)):
        if kcountofbuckets[x] >= minsupport:
            kbitmap[x] = 1
        else:
            kbitmap[x] = 0

    "Condition 1 is automatically satisfied"

    "Checking condition 2 of PCY Pass 2"
    hashingstring = ""
    klist = []

    for i in range(0, len(kcombination)):
        for j in kcombination[i]:
            hashingstring += str(itemiddic[j])
        if kbitmap[int(hashingstring) % nbuckets] == 1:
            klist.append(kcombination[i])
        teststring = ""

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
        sizekfreqset(minsupport, nbuckets, itemiddic, buckets, output, k);
    else:
        print("That's all folks!")


def create_rules(freq_items, item_support_dict, min_confidence):
    """
    create the association rules, the rules will be a list.
    each element is a tuple of size 4, containing rules'
    left hand side, right hand side, confidence and lift
    """
    association_rules = []

    # for the list that stores the frequent items, loop through
    # the second element to the one before the last to generate the rules
    # because the last one will be an empty list. It's the stopping criteria
    # for the frequent itemset generating process and the first one are all
    # single element frequent itemset, which can't perform the set
    # operation X -> Y - X
    for idx, freq_item in enumerate(freq_items[1:(len(freq_items) - 1)]):
        for freq_set in freq_item:

            # start with creating rules for single item on
            # the right hand side
            subsets = [frozenset([item]) for item in freq_set]
            rules, right_hand_side = compute_conf(freq_items, item_support_dict,
                                                  freq_set, subsets, min_confidence)
            association_rules.extend(rules)

            # starting from 3-itemset, loop through each length item
            # to create the rules, as for the while loop condition,
            # e.g. suppose you start with a 3-itemset {2, 3, 5} then the
            # while loop condition will stop when the right hand side's
            # item is of length 2, e.g. [ {2, 3}, {3, 5} ], since this
            # will be merged into 3 itemset, making the left hand side
            # null when computing the confidence
            if idx != 0:
                k = 0
                while len(right_hand_side[0]) < len(freq_set) - 1:
                    ck = create_candidate_k(right_hand_side, k=k)
                    rules, right_hand_side = compute_conf(freq_items, item_support_dict,
                                                          freq_set, ck, min_confidence)
                    association_rules.extend(rules)
                    k += 1

    return association_rules


def compute_conf(freq_items, item_support_dict, freq_set, subsets, min_confidence):
    """
    create the rules and returns the rules info and the rules's
    right hand side (used for generating the next round of rules)
    if it surpasses the minimum confidence threshold
    """
    rules = []
    right_hand_side = []

    for rhs in subsets:
        # create the left hand side of the rule
        # and add the rules if it's greater than
        # the confidence threshold
        lhs = freq_set - rhs
        conf = item_support_dict[freq_set] / item_support_dict[lhs]
        if conf >= min_confidence:
            lift = conf / item_support_dict[rhs]
            rules_info = lhs, rhs, conf, lift
            rules.append(rules_info)
            right_hand_side.append(rhs)

    return rules, right_hand_side


t0 = time.time()
openfile()
t1 = time.time()

total = t1 - t0
print('Elapsed Time:', str(t1))
