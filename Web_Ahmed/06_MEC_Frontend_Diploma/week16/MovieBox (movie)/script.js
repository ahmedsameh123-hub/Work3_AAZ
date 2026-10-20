const API_KEY = '1d49a0cb9c42c074398f4d3dce1584e7';
const BASE_URL = 'https://api.themoviedb.org/3';
const IMAGE_URL = 'https://image.tmdb.org/t/p/w500';

document.addEventListener("DOMContentLoaded", () => {
    fetchMovies('movie/now_playing', '#featured');
    fetchMovies('movie/top_rated', '#topRated');
    fetchMovies('movie/popular', '#popular');
});

function fetchMovies(endpoint, containerId) {
    fetch(`${BASE_URL}/${endpoint}?api_key=${API_KEY}&language=en-US`)
        .then(response => response.json())
        .then(data => {
            const container = document.querySelector(containerId);
            container.innerHTML = data.results.map(movie => `
                <div class="movie" onclick="showDetails(${movie.id})">
                    <img src="${IMAGE_URL + movie.poster_path}" alt="${movie.title}">
                    <h3>${movie.title}</h3>
                </div>
            `).join('');
        })
        .catch(error => console.log('Error:', error));
}

function searchMovies() {
    const query = document.getElementById('searchInput').value;
    fetch(`${BASE_URL}/search/movie?api_key=${API_KEY}&query=${query}`)
        .then(response => response.json())
        .then(data => {
            const container = document.querySelector('#featured');
            container.innerHTML = data.results.map(movie => `
                <div class="movie" onclick="showDetails(${movie.id})">
                    <img src="${IMAGE_URL + movie.poster_path}" alt="${movie.title}">
                    <h3>${movie.title}</h3>
                </div>
            `).join('');
        })
        .catch(error => console.log('Error:', error));
}

function showDetails(movieId) {
    window.location.href = `details.html?id=${movieId}`;
}
