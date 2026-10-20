import React from 'react';

function TestimonialCard({ name, feedback, rating }) {
  return (
    <div className="testimonial-card">
      <h4>{name}</h4>
      <p>{feedback}</p>
      <p>Rating: {rating} stars</p>
    </div>
  );
}

export default TestimonialCard;
