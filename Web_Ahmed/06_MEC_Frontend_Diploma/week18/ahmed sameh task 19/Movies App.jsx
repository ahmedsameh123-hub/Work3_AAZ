const API_KEY = '1d49a0cb9c42c074398f4d3dce1584e7';

function MoviesApp() {
  const [movies, setMovies] = useState([]);
  const [query, setQuery] = useState("");

  useEffect(() => {
    fetch(`https://api.themoviedb.org/3/trending/movie/week?api_key=${API_KEY}`)
      .then(response => response.json())
      .then(data => setMovies(data.results));
  }, []);

  const searchMovies = () => {
    fetch(`https://api.themoviedb.org/3/search/movie?api_key=${API_KEY}&query=${query}`)
      .then(response => response.json())
      .then(data => setMovies(data.results));
  };

  return (
    <div>
      <input
        type="text"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
      />
      <button onClick={searchMovies}>Search</button>
      <div>
        {movies.map(movie => (
          <div key={movie.id}>
            <h4>{movie.title}</h4>
            <p>{movie.overview}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
