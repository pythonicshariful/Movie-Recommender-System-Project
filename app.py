"""
Flask Movie Recommender System
A web application that recommends movies based on content-based filtering
"""

from flask import Flask, render_template, request, jsonify
import pickle
import pandas as pd
import difflib

app = Flask(__name__)

# Load the preprocessed data
print("Loading movie data...")
movies_dict = pickle.load(open('movies_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)
similarity = pickle.load(open('similarity.pkl', 'rb'))
print(f"Loaded {len(movies)} movies")

def get_recommendations(movie_title, num_recommendations=5):
    """
    Get movie recommendations based on similarity
    
    Args:
        movie_title: Name of the movie
        num_recommendations: Number of recommendations to return
        
    Returns:
        List of recommended movie titles
    """
    try:
        # Find the movie index
        movie_index = movies[movies['title'] == movie_title].index[0]
        
        # Get similarity scores
        distances = similarity[movie_index]
        
        # Sort and get top recommendations (excluding the movie itself)
        movie_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:num_recommendations+1]
        
        # Get movie titles
        recommendations = []
        for i in movie_list:
            recommendations.append({
                'title': movies.iloc[i[0]].title,
                'similarity_score': round(i[1] * 100, 2)
            })
        
        return recommendations
    except IndexError:
        return []

def find_closest_match(movie_name):
    """
    Find the closest matching movie title using fuzzy matching
    
    Args:
        movie_name: Partial or full movie name
        
    Returns:
        List of matching movie titles
    """
    all_titles = movies['title'].tolist()
    
    # Try exact match first
    exact_matches = [title for title in all_titles if movie_name.lower() in title.lower()]
    
    if exact_matches:
        return exact_matches[:10]  # Return top 10 matches
    
    # Use difflib for fuzzy matching
    close_matches = difflib.get_close_matches(movie_name, all_titles, n=10, cutoff=0.6)
    
    return close_matches

@app.route('/')
def index():
    """Home page"""
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    """Search for movies"""
    query = request.form.get('movie_name', '')
    
    if not query:
        return render_template('index.html', error="Please enter a movie name")
    
    # Find matching movies
    matches = find_closest_match(query)
    
    if not matches:
        return render_template('index.html', error=f"No movies found matching '{query}'")
    
    return render_template('index.html', matches=matches, query=query)

@app.route('/recommend/<movie_title>')
def recommend(movie_title):
    """Get recommendations for a specific movie"""
    # Check if movie exists
    if movie_title not in movies['title'].values:
        return render_template('index.html', error=f"Movie '{movie_title}' not found")
    
    # Get recommendations
    recommendations = get_recommendations(movie_title, num_recommendations=10)
    
    if not recommendations:
        return render_template('index.html', error=f"Could not generate recommendations for '{movie_title}'")
    
    return render_template('recommendations.html', 
                         movie_title=movie_title, 
                         recommendations=recommendations)

@app.route('/api/autocomplete')
def autocomplete():
    """API endpoint for autocomplete suggestions"""
    query = request.args.get('q', '')
    
    if len(query) < 2:
        return jsonify([])
    
    matches = find_closest_match(query)
    return jsonify(matches[:5])  # Return top 5 for autocomplete

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
