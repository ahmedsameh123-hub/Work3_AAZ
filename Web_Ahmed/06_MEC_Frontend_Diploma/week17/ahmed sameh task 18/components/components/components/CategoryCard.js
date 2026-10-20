import React from 'react';

function CategoryCard({ name, courses }) {
  return (
    <div className="category-card">
      <h4>{name}</h4>
      <p>{courses}</p>
    </div>
  );
}

export default CategoryCard;
