import pickle
import requests
import streamlit as st

# Function to download file from Dropbox
def download_file_from_dropbox(url):
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code != 200:
        raise Exception(f"Failed to download file: HTTP Status Code {response.status_code}")

    try:
        # Load the content as a pickle
        return pickle.loads(response.content)
    except Exception as e:
        raise Exception("The downloaded content is not a valid pickle file or is corrupted. Error: " + str(e))

# Dropbox URLs for the files
movie_list_url = 'https://www.dropbox.com/scl/fi/7i7vnl3zbfocwuoctvscl/movie_list.pkl?rlkey=509gp12jke633suvkfe2y8658&st=2u5y5rz4&dl=1'  # Movie list file URL
similarity_url = 'https://www.dropbox.com/scl/fi/eb077copqhdrvmqs6lris/similarity.pkl?rlkey=vky04wfyjaf9jc06xx9nvmdq2&st=8sblkwvo&dl=1'  # Similarity file URL

# Load movies and similarity from Dropbox
try:
    movies = download_file_from_dropbox(movie_list_url)
    similarity = download_file_from_dropbox(similarity_url)
except Exception as e:
    st.error("Failed to load data from Dropbox: {}".format(e))
    st.stop()

# Function to fetch poster image from TMDb API
def fetch_poster(movie_id):
    # Correctly format the URL for fetching the poster image
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
            col.text(recommended_movie_names[idx])  # Show movie name
            col.image(recommended_movie_posters[idx])  # Show movie poster
