import React, { useEffect, useState } from 'react';
import MovieCard from './MovieCard';
import '../styles/App.css'; // استيراد ملف CSS هنا

const MoviesList = () => {
  const [movies, setMovies] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchMovies = async () => {
    try {
      const response = await fetch('https://api.themoviedb.org/3/movie/popular?api_key=YOUR_API_KEY');
      const data = await response.json();
      setMovies(data.results);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching movies:', error);
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMovies();
  }, []);

  if (loading) {
    return <div>تحميل الأفلام...</div>;
  }

  return (
    <div className="movies-list">
      {movies.map(movie => (
        <MovieCard key={movie.id} movie={movie} />
      ))}
    </div>
  );
};
const response = await fetch('https://api.themoviedb.org/3/movie/popular?api_key=YOUR_API_KEY');
const data = await response.json();
console.log(data); // أضف هذه السطر للتحقق من البيانات


export default MoviesList;
