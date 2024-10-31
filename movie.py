import pickle
import requests
import streamlit as st

# Function to download file from Google Drive
def download_file_from_google_drive(file_id):
    url = f'https://drive.google.com/uc?id={file_id}'
    response = requests.get(url)
    if response.status_code == 200:
        try:
            return pickle.loads(response.content)
        except pickle.UnpicklingError:
            raise Exception("The downloaded content is not a valid pickle file.")
    else:
        raise Exception(f"Failed to download file: HTTP Status Code {response.status_code}")

# Use the actual file IDs from Google Drive
movie_list_id = '1Fh33IwObUb3vwvuIMQTeY8oEtgTyUNZD'  # Movie list file ID
similarity_id = '1zbyGYZYP_VJX_CtUwty16mEEiY8vI0l8'  # Similarity file ID

# Load movies and similarity from Google Drive
try:
    movies = download_file_from_google_drive(movie_list_id)
    similarity = download_file_from_google_drive(similarity_id)
except Exception as e:
    st.error("Failed to load data from Google Drive: {}".format(e))
    st.stop()

# Function to fetch poster image from TMDb API
def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=YOUR_API_KEY&language=en-US"
    data = requests.get(url)
    data = data.json()
    poster_path = data.get('poster_path')
    if poster_path:
        full_path = "https://image.tmdb.org/t/p/w500/" + poster_path
        return full_path
    return ""  # Return an empty string if no poster found

# Function to recommend similar movies
def recommend(movie):
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    recommended_movie_names = []
    recommended_movie_posters = []
    for i in distances[1:6]:  # Get top 5 recommendations
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movie_posters.append(fetch_poster(movie_id))
        recommended_movie_names.append(movies.iloc[i[0]].title)
    return recommended_movie_names, recommended_movie_posters

# Streamlit UI
st.header('Movie Recommender System')

# Display a dropdown of movie titles
movie_list = movies['title'].values
selected_movie = st.selectbox(
    "Type or select a movie from the dropdown",
    movie_list
)

# Display recommendations when button is clicked
if st.button('Show Recommendation'):
    recommended_movie_names, recommended_movie_posters = recommend(selected_movie)
    cols = st.columns(5)  # Create 5 columns for displaying recommended movies
    for idx, col in enumerate(cols):
        if idx < len(recommended_movie_names):
            col.text(recommended_movie_names[idx])  # Show movie name
            col.image(recommended_movie_posters[idx])  # Show movie poster
