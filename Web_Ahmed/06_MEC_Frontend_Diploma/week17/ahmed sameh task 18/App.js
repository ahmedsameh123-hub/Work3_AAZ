import React from 'react';
import FeaturedCourses from './components/FeaturedCourses';
import TopCategories from './components/TopCategories';
import Testimonials from './components/Testimonials';

function App() {
  return (
    <div className="App">
      <header>
        <h1>Featured Courses</h1>
        <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit.</p>
      </header>
      <FeaturedCourses />
      <TopCategories />
      <Testimonials />
    </div>
  );
}

export default App;
