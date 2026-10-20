import React from 'react';

function CourseCard({ title, price, image }) {
  return (
    <div className="course-card">
      <img src={image} alt={title} />
      <h3>{title}</h3>
      <p>{price}</p>
    </div>
  );
}

export default CourseCard;
