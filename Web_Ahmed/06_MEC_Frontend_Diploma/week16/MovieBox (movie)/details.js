const API_KEY = '1d49a0cb9c42c074398f4d3dce1584e7';
const BASE_URL = 'https://api.themoviedb.org/3';
const IMAGE_URL = 'https://image.tmdb.org/t/p/w500';

document.addEventListener("DOMContentLoaded", () => {
    const urlParams = new URLSearchParams(window.location.search);
    const movieId = urlParams.get('id');
    fetchMovieDetails(movieId);
});

function fetchMovieDetails(movieId) {
    fetch(`${BASE_URL}/movie/${movieId}?api_key=${API_KEY}&language=en-US`)
        .then(response => response.json())
        .then(movie => {
            const container = document.getElementById('movieDetails');
            container.innerHTML = `
                <div>
                    <img src="${IMAGE_URL + movie.poster_path}" alt="${movie.title}">
                    <h2>${movie.title}</h2>
                    <p>${movie.overview}</p>
                    <p><strong>Rating:</strong> ${movie.vote_average}/10</p>
                    <p><strong>Release Date:</strong> ${movie.release_date}</p>
                </div>
            `;
        })
        .catch(error => console.log('Error:', error));
}
