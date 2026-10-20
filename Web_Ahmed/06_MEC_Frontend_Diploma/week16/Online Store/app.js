import { DigitalProduct } from './DigitalProduct.js';
import { PhysicalProduct } from './PhysicalProduct.js';
import { Customer } from './Customer.js';
import { Order } from './Order.js';

const products = [
    new DigitalProduct(1, "Digital Service 1", 49.99, 5.99, 12),
    new DigitalProduct(2, "Digital Service 2", 29.99, 3.99, 6),
    new PhysicalProduct(3, "Physical Item 1", 19.99, 2, 8.99),
    new PhysicalProduct(4, "Physical Item 2", 39.99, 3, 12.99),
    new DigitalProduct(5, "Digital Service 3", 59.99, 6.99, 24),
    new PhysicalProduct(6, "Physical Item 3", 49.99, 5, 15.99),
];

const customer = new Customer(101, "John Doe", "john@example.com", "123 Main St");

const order = new Order(1001, customer);

const productContainer = document.getElementById('product-container');
const cartList = document.getElementById('cart-list');
const checkoutButton = document.getElementById('checkout');
const totalPriceElement = document.getElementById('total-price');

function updateTotalPrice() {
    const total = order.calcTotalPrice();
    totalPriceElement.textContent = `Total: $${total.toFixed(2)}`;
}

function updateCartView() {
    cartList.innerHTML = ''; 
    order.products.forEach((product, index) => {
        const listItem = document.createElement('li');
        listItem.textContent = `${product.name} - $${product.calcCost().toFixed(2)}`;
        cartList.appendChild(listItem);
    });

    checkoutButton.disabled = order.products.length === 0;
    updateTotalPrice();
}

function addToCart(product) {
    order.addProduct(product);
    updateCartView();
}

function displayProducts() {
    products.forEach((product) => {
        const productItem = document.createElement('div');
        productItem.classList.add('product-item');
        
        productItem.innerHTML = `
            <h3>${product.name}</h3>
            <p>Price: $${product.price}</p>
            <p>${product instanceof DigitalProduct ? `Subscription: $${product.subscriptionFees}` : `Shipping: $${product.shippingCost}`}</p>
            <button>Add to Cart</button>
        `;

        productItem.querySelector('button').addEventListener('click', () => addToCart(product));
        productContainer.appendChild(productItem);
    });
}

displayProducts();
