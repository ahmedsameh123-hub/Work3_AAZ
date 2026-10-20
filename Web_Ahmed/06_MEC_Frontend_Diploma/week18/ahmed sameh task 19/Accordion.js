// src/Accordion.js
import React, { useState } from 'react';
import './Accordion.css'; // تأكد من إنشاء ملف CSS مخصص

const AccordionItem = ({ question, answer }) => {
  const [isActive, setIsActive] = useState(false);

  return (
    <div className={`accordion-item ${isActive ? 'active' : ''}`}>
      <div className="accordion-header" onClick={() => setIsActive(!isActive)}>
        <h4>{question}</h4>
        <div className="icon">{isActive ? '-' : '+'}</div>
      </div>
      <div className="accordion-content">
        <p>{answer}</p>
      </div>
    </div>
  );
};

const Accordion = () => {
  const data = [
    { question: 'What is React?', answer: 'React is a JavaScript library for building user interfaces.' },
    { question: 'Why use React?', answer: 'React allows for fast, efficient rendering and state management.' },
  ];

  return (
    <div className="accordion-container">
      {data.map((item, index) => (
        <AccordionItem key={index} {...item} />
      ))}
    </div>
  );
};

export default Accordion;
