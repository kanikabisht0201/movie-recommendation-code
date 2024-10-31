import pickle
import requests
import streamlit as st

# Function to download file from Dropbox
def download_file_from_dropbox(url):
    response = requests.get(url)
    return pickle.loads(response.content)

# Use the actual file URLs from Dropbox
movie_list_url = 'https://www.dropbox.com/scl/fi/7i7vnl3zbfocwuoctvscl/movie_list.pkl?rlkey=509gp12jke633suvkfe2y8658&dl=1'  # Change dl=0 to dl=1
similarity_url = 'https://www.dropbox.com/scl/fi/eb077copqhdrvmqs6lris/similarity.pkl?rlkey=vky04wfyjaf9jc06xx9nvmdq2&dl=1'  # Change dl=0 to dl=1

# Load movies and similarity from Dropbox
try:
    movies = download_file_from_dropbox(movie_list_url)
    similarity = download_file_from_dropbox(similarity_url)
except Exception as e:
    st.error("Failed to load data from Dropbox: {}".format(e))
    st.stop()

# Function to fetch poster image from TMDb API
def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=31dea30241045ff2b6e028a1ed1bf151&language=en-US"
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
            # Display movie name with increased font size
            col.markdown(f"<h3 style='font-size: 20px;'>{recommended_movie_names[idx]}</h3>", unsafe_allow_html=True)  # Adjust font size as needed
            col.image(recommended_movie_posters[idx])  # Show movie poster
