import streamlit as st
import pickle
import pandas as pd
import requests

# TMDb API Key (Replace with your actual API key)
TMDB_API_KEY = "a34ef5187f01ae5fc86fba5c2e8446fd"

# Function to fetch movie poster from TMDb
def fetch_poster(movie_title):
    try:
        search_url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={movie_title}"
        response = requests.get(search_url)
        data = response.json()
        
        if data['results']:
            poster_path = data['results'][0].get('poster_path', None)
            if poster_path:
                return f"https://image.tmdb.org/t/p/w500{poster_path}"  # TMDb poster base URL
    except Exception as e:
        st.error(f"Error fetching poster: {e}")
    
    return None  # Return None if no poster is found

# Load movie data
try:
    movies_list = pickle.load(open('movies.pkl', 'rb'))
    similarity = pickle.load(open('similarity.pkl', 'rb'))
    movies_list = pd.DataFrame(movies_list)  # Ensure it's a DataFrame
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()

# Extract movie titles
if 'title' not in movies_list.columns:
    st.error("Missing 'title' column in movie dataset.")
    st.stop()

movie_titles = movies_list['title'].values

# Recommendation function
def recommend(movie):
    try:
        movie_index = movies_list[movies_list['title'] == movie].index[0]
        distances = similarity[movie_index]
        movie_indices = sorted(enumerate(distances), key=lambda x: x[1], reverse=True)[1:6]

        recommended_movies = []
        for i in movie_indices:
            title = movies_list.iloc[i[0]].title
            poster_url = fetch_poster(title)  # Fetch poster from TMDb
            recommended_movies.append((title, poster_url))

        return recommended_movies
    except IndexError:
        return []

# Streamlit UI
st.title("🎬 Movie Recommender System")
st.markdown("Select a movie, and we'll suggest similar ones for you!")

selected_movie_name = st.selectbox("Choose a movie:", movie_titles)

if st.button("Recommend"):
    recommendations = recommend(selected_movie_name)

    if recommendations:
        st.subheader("Recommended Movies:")
        cols = st.columns(5)  # Display 5 movies in a row
        for idx, (title, poster) in enumerate(recommendations):
            with cols[idx]:
                st.write(title)
                if poster:
                    st.image(poster, use_container_width=True)  # ✅ Updated parameter
                else:
                    st.write("🎥 No poster available")
    else:
        st.warning("No recommendations found. Try another movie!")

