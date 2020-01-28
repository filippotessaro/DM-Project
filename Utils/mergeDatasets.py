import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
import matplotlib.pyplot as plt
from scipy.special import comb
from itertools import combinations, permutations
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
from nltk.tokenize import sent_tokenize, word_tokenize
import nltk
import re
import os

#nltk.download('stopwords')
#nltk.download('punkt')
ps = PorterStemmer()


#os.mkdir('../norm-dataset/')


def itemParser(row):
    """
    Row items cleaner.

    This function is useful to normalize the items of the chart

    Parameters:
    row (list): Row of chart items

    Returns:
    list: Normalized items

    """
    word_ps = []
    for s in row:
        # REGULAR EXPRESSIONS:

        # Remove punctuations
        s = re.sub(r'[^\w\s]', '', s)

        # Remove Digits
        s = re.sub(r"(\d)", "", s)

        # Remove content inside paranthesis
        s = re.sub(r'\([^)]*\)', '', s)

        # Remove Brand Name
        s = re.sub(u'\w*\u2122', '', s)

        # Convert to lowercase
        s = s.lower()

        # print(ps.stem(s))
        # Remove Stop Words
        stop_words = set(stopwords.words('english'))
        word_tokens = word_tokenize(s)

        filtered_sentence = [ps.stem(w) for w in word_tokens if not w in stop_words]
        # print(filtered_sentence)
        s = ' '.join(filtered_sentence)
        # print("join:" + s)
        word_ps.append(s)
    return word_ps

chart = []
with open('../data/groceries.csv', 'r') as f:
    for line in f:
        chart.append(itemParser(line[:-1].split(',')))
print('End loading groceries')

with open('../data/groceries - groceries.csv', 'r') as f:
    first = True
    for line in f:
        if not first:
            chart.append(itemParser(line[:-1].split(',')))
        first = False
print('End loading groceries - groceries')


f = open('../norm-dataset/groceries.txt', 'a')
for basket in chart:
    f.write(str(basket) + '\n')
print('norm-dataset/groceries.csv Successfully created!')

print('Load Json Recipes')
json_df_train = pd.read_json('../data/train.json')
json_df_test = pd.read_json('../data/test.json')

final_json_df = json_df_train.append(json_df_test)
print('End Merging Jsons')

print('Start Normalization Jsons')
final_json_df['new_ingredients'] = final_json_df.apply(lambda x: itemParser(x.ingredients), axis=1)
print('End Normalization Json')
final_json_df.to_csv('../norm-dataset/recipes.csv')