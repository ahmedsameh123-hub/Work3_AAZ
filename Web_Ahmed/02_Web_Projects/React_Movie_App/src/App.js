import React from 'react';
import MoviesList from './components/MoviesList';
import './styles/App.css'; // استيراد ملف CSS هنا

const App = () => {
  return (
    <div>
      <h1>مرحبًا بك في تطبيق الأفلام</h1>
      <MoviesList />
    </div>
  );
};

export default App;
