import React from 'react';
import TestimonialCard from './TestimonialCard';

const testimonials = [
  { id: 1, name: 'Ronald Richards', feedback: 'Great platform!', rating: 5 },
  { id: 2, name: 'Wade Warren', feedback: 'Excellent courses.', rating: 4 },
  { id: 3, name: 'Jacob Jones', feedback: 'Highly recommend.', rating: 5 },
];

function Testimonials() {
  return (
    <div className="testimonials">
      <h2>Testimonials</h2>
      {testimonials.map(testimonial => (
        <TestimonialCard key={testimonial.id} name={testimonial.name} feedback={testimonial.feedback} rating={testimonial.rating} />
      ))}
    </div>
  );
}

export default Testimonials;
