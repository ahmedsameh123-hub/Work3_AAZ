import React from 'react';
import ReactDOM from 'react-dom/client'; // تأكد من أنك تستورد من 'react-dom/client'
import App from './App';

const container = document.getElementById('root'); // تأكد من أن العنصر هنا هو 'root'
const root = ReactDOM.createRoot(container); // استخدم createRoot
root.render(<App />);
