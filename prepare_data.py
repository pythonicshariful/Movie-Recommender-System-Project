"""
Data Preparation Script for Movie Recommender System
This script processes the movie datasets and creates the necessary pickle files
for the Flask application.
"""

import pandas as pd
import numpy as np
import ast
import pickle
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from nltk.stem.porter import PorterStemmer

print("Loading datasets...")
# Load datasets
movies = pd.read_csv('dataset/tmdb_5000_movies.csv')
credits = pd.read_csv('dataset/tmdb_5000_credits.csv')

# Merge datasets
movies = movies.merge(credits, on='title')

# Select relevant columns
movies = movies[['movie_id', 'title', 'overview', 'genres', 'keywords', 'cast', 'crew']]

# Drop null values
movies.dropna(inplace=True)

print(f"Processing {len(movies)} movies...")

# Helper functions
def convert(obj):
    """Convert JSON string to list of names"""
    L = []
    for i in ast.literal_eval(obj):
        L.append(i['name'])
    return L

def convert3(obj):
    """Convert JSON string to list of top 3 names"""
    L = []
    c = 0
    for i in ast.literal_eval(obj):
        L.append(i['name'])
        c += 1
        if c >= 3:
            break
    return L

def fetch_directors(obj):
    """Extract director names from crew"""
    L = []
    for i in ast.literal_eval(obj):
        if i['job'] == 'Director':
            L.append(i['name'])
    return L

# Process columns
print("Processing genres, keywords, cast, and crew...")
movies['genres'] = movies['genres'].apply(convert)
movies['keywords'] = movies['keywords'].apply(convert)
movies['cast'] = movies['cast'].apply(convert3)
movies['crew'] = movies['crew'].apply(fetch_directors)

# Process overview
movies['overview'] = movies['overview'].apply(lambda x: x.split())

# Remove spaces from all lists
movies['genres'] = movies['genres'].apply(lambda x: [i.replace(" ", "") for i in x])
movies['keywords'] = movies['keywords'].apply(lambda x: [i.replace(" ", "") for i in x])
movies['cast'] = movies['cast'].apply(lambda x: [i.replace(" ", "") for i in x])
movies['crew'] = movies['crew'].apply(lambda x: [i.replace(" ", "") for i in x])

# Create tags
print("Creating tags...")
movies['tag'] = movies['overview'] + movies['genres'] + movies['keywords'] + movies['cast'] + movies['crew']

# Create new dataframe
new_df = movies[['movie_id', 'title', 'tag']].copy()
new_df['tag'] = new_df['tag'].apply(lambda x: " ".join(x))
new_df['tag'] = new_df['tag'].apply(lambda x: x.lower())

# Stemming
print("Applying stemming...")
ps = PorterStemmer()

def stem(text):
    y = []
    for i in text.split():
        y.append(ps.stem(i))
    return " ".join(y)

new_df['tag'] = new_df['tag'].apply(stem)

# Vectorization
print("Creating vectors...")
cv = CountVectorizer(max_features=5000, stop_words='english')
vectors = cv.fit_transform(new_df['tag']).toarray()

# Calculate similarity
print("Calculating similarity matrix...")
similarity = cosine_similarity(vectors)

# Save to pickle files
print("Saving pickle files...")
pickle.dump(new_df.to_dict(), open('movies_dict.pkl', 'wb'))
pickle.dump(similarity, open('similarity.pkl', 'wb'))

print("Data preparation complete!")
print(f"Created movies_dict.pkl and similarity.pkl")
print(f"Total movies processed: {len(new_df)}")
