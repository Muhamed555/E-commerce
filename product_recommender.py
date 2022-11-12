import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def get_name_from_index(index):
    return df[df['index'] == index]['Name'].values[0]


def get_index_from_name(name):
    return df[df.Name == name]['index'].values[0]


def get_image_from_index(index):
    return df[df['index'] == index]['Image'].values[0]


df = pd.read_csv('modified_wearables.csv', encoding='latin')

features = ['Name', 'Body.Location', 'Category', 'Company...City', 'Company.Name']


def recommender(index):
    cv = CountVectorizer()

    count_matrix = cv.fit_transform(df['combined_features'])

    # Compute the cosine similarty
    cosine_sim = cosine_similarity(count_matrix)


    similar_products = list(enumerate(cosine_sim[index]))

    sorted_similar_products = sorted(similar_products, key=lambda x: x[1], reverse=True)

    index_of_similar_products = []
    counter = 0
    for i in sorted_similar_products:
        index_of_similar_products.append(i[0])
        counter = 1 + counter
        if counter == 9:
            break

    return index_of_similar_products


