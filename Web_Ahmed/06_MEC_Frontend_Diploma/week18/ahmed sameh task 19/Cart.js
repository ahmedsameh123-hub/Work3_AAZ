// src/Cart.js
import React, { useState } from 'react';
import './Cart.css';

const Cart = () => {
  const [products, setProducts] = useState([
    { id: 1, name: 'Product 1', price: 20, quantity: 1, img: 'https://via.placeholder.com/80' },
    { id: 2, name: 'Product 2', price: 30, quantity: 2, img: 'https://via.placeholder.com/80' }
  ]);

  const updateQuantity = (id, amount) => {
    setProducts(products.map(product => 
      product.id === id ? { ...product, quantity: product.quantity + amount } : product
    ));
  };

  const getTotal = () => {
    return products.reduce((total, product) => total + product.price * product.quantity, 0);
  };

  return (
    <div className="cart-container">
      {products.map(product => (
        <div key={product.id} className="cart-item">
          <img src={product.img} alt={product.name} />
          <h4>{product.name}</h4>
          <div className="price">${product.price}</div>
          <div className="quantity">
            <button onClick={() => updateQuantity(product.id, -1)}>-</button>
            <input type="text" value={product.quantity} readOnly />
            <button onClick={() => updateQuantity(product.id, 1)}>+</button>
          </div>
        </div>
      ))}
      <div className="cart-total">Total: ${getTotal()}</div>
    </div>
  );
};

export default Cart;
