const API_KEY = '1d49a0cb9c42c074398f4d3dce1584e7';
const BASE_URL = 'https://api.themoviedb.org/3';

document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('search');
    const featuredMoviesSection = document.getElementById('featured-movies');
    const searchResultsSection = document.getElementById('search-results');
    const movieDetailsSection = document.getElementById('movie-details');
    const watchlistSection = document.getElementById('watchlist');
    const toggleThemeButton = document.getElementById('toggle-theme');

    searchInput.addEventListener('input', searchMovies);

    async function fetchMovies(endpoint) {
        const response = await fetch(`${BASE_URL}${endpoint}&api_key=${API_KEY}`);
        return response.json();
    }

    async function displayFeaturedMovies() {
        const data = await fetchMovies('/movie/popular');
        const movieGrid = featuredMoviesSection.querySelector('.movie-grid');
        movieGrid.innerHTML = data.results.map(movie => `
            <div class="movie-card" data-id="${movie.id}">
                <img src="https://image.tmdb.org/t/p/w500${movie.poster_path}" alt="${movie.title}">
                <h3>${movie.title}</h3>
            </div>
        `).join('');
    }

    async function searchMovies() {
        const query = searchInput.value;
        if (query) {
            const data = await fetchMovies(`/search/movie?query=${query}`);
            const movieGrid = searchResultsSection.querySelector('.movie-grid');
            movieGrid.innerHTML = data.results.map(movie => `
                <div class="movie-card" data-id="${movie.id}">
                    <img src="https://image.tmdb.org/t/p/w500${movie.poster_path}" alt="${movie.title}">
                    <h3>${movie.title}</h3>
                </div>
            `).join('');
            searchResultsSection.classList.remove('hidden');
        } else {
            searchResultsSection.classList.add('hidden');
        }
    }

    async function displayMovieDetails(movieId) {
        const data = await fetchMovies(`/movie/${movieId}`);
        document.getElementById('movie-title').textContent = data.title;
        document.getElementById('movie-poster').src = `https://image.tmdb.org/t/p/w500${data.poster_path}`;
        document.getElementById('movie-summary').textContent = data.overview;
        document.getElementById('movie-rating').textContent = data.vote_average;
        document.getElementById('movie-release-date').textContent = data.release_date;
        movieDetailsSection.classList.remove('hidden');
    }

    document.getElementById('close-details').addEventListener('click', () => {
        movieDetailsSection.classList.add('hidden');
    });

    document.getElementById('watch-trailer').addEventListener('click', () => {
        window.open(`https://www.youtube.com/results?search_query=${document.getElementById('movie-title').textContent} trailer`);
    });

    toggleThemeButton.addEventListener('click', () => {
        document.body.classList.toggle('dark-mode');
    });

    document.addEventListener('click', event => {
        if (event.target.classList.contains('movie-card')) {
            const movieId = event.target.dataset.id;
            displayMovieDetails(movieId);
        }
    });

    // Load featured movies on page load
    displayFeaturedMovies();
});
