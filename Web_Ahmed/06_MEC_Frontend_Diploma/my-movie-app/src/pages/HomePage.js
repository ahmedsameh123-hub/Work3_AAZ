import React, { useState, useEffect } from 'react';
import { getMovies } from '../api/tmdb';
import MovieCard from '../components/MovieCard';

const HomePage = () => {
  const [movies, setMovies] = useState([]);

  useEffect(() => {
    const fetchMovies = async () => {
      const movieData = await getMovies();
      setMovies(movieData);
    };
    fetchMovies();
  }, []);

  return (
    <div className="container">
      <h1 className="text-center my-4">Popular Movies</h1>
      <div className="row">
        {movies.map((movie) => (
          <div className="col-md-4 mb-3" key={movie.id}>
            <MovieCard movie={movie} />
          </div>
        ))}
      </div>
    </div>
  );
};

export default HomePage;
