import React from 'react';
import CourseCard from './CourseCard';

const courses = [
  { id: 1, title: 'Marion Graphics', price: '$39.99', image: 'image1.png' },
  { id: 2, title: 'Financial Analyst', price: '$45.99', image: 'image2.png' },
  { id: 3, title: 'Education Software', price: '$32.99', image: 'image3.png' },
  { id: 4, title: 'Marketing 2023', price: '$29.99', image: 'image4.png' },
  { id: 5, title: 'PHP Knowledge', price: '$33.99', image: 'image5.png' },
  { id: 6, title: '3D Modeling', price: '$35.99', image: 'image6.png' },
];

function FeaturedCourses() {
  return (
    <div className="featured-courses">
      {courses.map(course => (
        <CourseCard key={course.id} title={course.title} price={course.price} image={course.image} />
      ))}
    </div>
  );
}

export default FeaturedCourses;
