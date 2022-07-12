import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
import re
import nltk
nltk.download('stopwords')
from nltk.corpus import stopwords
# from ..models import Product
# import random

product_data = pd.read_csv('scripts\89_ds.204_Product.csv')

# Function to process data
def pre_processing(text):
    text = text.lower() # lowercase
    text = re.sub('<.*?>', '', text) # Remove html tag,...
    text = re.sub(r'[^\w\s]', '', text) # Remove punctuation
    text = text.split(' ')
    stops = set(stopwords.words('english'))
    text = [w for w in text if not w in stops]
    text = ' '.join(text)
    return text

product_data["description"] = product_data["description"].astype(str)

for i in range(len(product_data)):
    product_data["description"].iloc[i] =  pre_processing(product_data["description"].iloc[i])

product_data = product_data.dropna()

# Calculate TF/IDF
vectorizer = TfidfVectorizer(stop_words="english")
tfidf_vectorizer = vectorizer.fit(product_data["description"])
overview_matrix = tfidf_vectorizer.transform(product_data["description"])

# Calculate similarity matrix
similarity_matrix = linear_kernel(overview_matrix, overview_matrix)

def get_asin(productid):
    return product_data['asin'].iloc[productid]

def recommend_product_based_on_description(product_input):
    # Calculate similarity score
    similarity_score = list(enumerate(similarity_matrix[product_input]))
    similarity_score = sorted(similarity_score, key = lambda x: x[1], reverse = True)
    similarity_score = similarity_score[1:]
    recommendations = [(productid, score) for productid, score in similarity_score]
    return recommendations

result = recommend_product_based_on_description(18)
a = [i[0] for i in result if i[1] > 0]
print(a)