// src/MenuApp.js
import React, { useState } from 'react';
import './MenuApp.css';

const MenuApp = () => {
  const allMenuItems = [
    { id: 1, name: 'Pancakes', category: 'breakfast', price: 5, img: 'https://via.placeholder.com/150' },
    { id: 2, name: 'Burger', category: 'lunch', price: 8, img: 'https://via.placeholder.com/150' },
    { id: 3, name: 'Milkshake', category: 'shakes', price: 4, img: 'https://via.placeholder.com/150' },
  ];

  const [menuItems, setMenuItems] = useState(allMenuItems);

  const filterMenu = (category) => {
    if (category === 'all') {
      setMenuItems(allMenuItems);
    } else {
      setMenuItems(allMenuItems.filter(item => item.category === category));
    }
  };

  return (
    <div className="menu-container">
      <div className="menu-categories">
        <button onClick={() => filterMenu('all')}>All</button>
        <button onClick={() => filterMenu('breakfast')}>Breakfast</button>
        <button onClick={() => filterMenu('lunch')}>Lunch</button>
        <button onClick={() => filterMenu('shakes')}>Shakes</button>
      </div>
      <div className="menu-items">
        {menuItems.map(item => (
          <div key={item.id} className="menu-item">
            <img src={item.img} alt={item.name} />
            <h4>{item.name}</h4>
            <div className="price">${item.price}</div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default MenuApp;
