import pandas as pd
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize
import re

#nltk.download('stopwords')
#nltk.download('punkt')
ps = PorterStemmer()


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
        # Remove Stop Words
        stop_words = set(stopwords.words('english'))
        word_tokens = word_tokenize(s)

        filtered_sentence = [ps.stem(w) for w in word_tokens if not w in stop_words]
        s = ' '.join(filtered_sentence)
        word_ps.append(s)
    return word_ps


chart = []
with open('../Data/groceries.csv', 'r') as f:
    for line in f:
        chart.append(itemParser(line[:-1].split(',')))

f = open('../Data/groceries_norm.csv', 'w')
for basket in chart:
    x = ''
    for item in basket:
        x += item + ','
    x = x[:-1]
    f.write(x + '\n')
    
json_df_train = pd.read_json('../Data/train.json')
json_df_train['new_ingredients'] = json_df_train.apply(lambda x: itemParser(x.ingredients), axis=1)
json_df_train.to_csv('../Data/train_norm.csv')