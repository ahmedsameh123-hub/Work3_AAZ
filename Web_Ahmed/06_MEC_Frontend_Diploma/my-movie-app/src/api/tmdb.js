import axios from 'axios';

const apiKey = process.env.REACT_APP_TMDB_API_KEY;

export const getMovies = async () => {
  try {
    const response = await axios.get(`https://api.themoviedb.org/3/movie/popular?api_key=${apiKey}`);
    return response.data.results;
  } catch (error) {
    console.error('Error fetching movies:', error);
  }
};

export const searchMovies = async (query) => {
  try {
    const response = await axios.get(`https://api.themoviedb.org/3/search/movie?api_key=${apiKey}&query=${query}`);
    return response.data.results;
  } catch (error) {
    console.error('Error searching movies:', error);
  }
};
