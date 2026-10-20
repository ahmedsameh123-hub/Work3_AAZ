import React from 'react';
import CategoryCard from './CategoryCard';

const categories = [
  { id: 1, name: 'Digital Marketing', courses: '25 Courses' },
  { id: 2, name: 'Web Development', courses: '35 Courses' },
  { id: 3, name: 'Art & Humanities', courses: '20 Courses' },
  { id: 4, name: 'Personal Development', courses: '15 Courses' },
  { id: 5, name: 'IT & Software', courses: '30 Courses' },
  { id: 6, name: 'Graphic Design', courses: '10 Courses' },
];

function TopCategories() {
  return (
    <div className="top-categories">
      <h2>Top Categories</h2>
      {categories.map(category => (
        <CategoryCard key={category.id} name={category.name} courses={category.courses} />
      ))}
    </div>
  );
}

export default TopCategories;
