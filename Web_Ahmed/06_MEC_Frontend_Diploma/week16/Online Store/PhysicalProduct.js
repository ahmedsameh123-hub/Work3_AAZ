import { Product } from './Product.js';

export class PhysicalProduct extends Product {
    constructor(id, name, price, weight, shippingCost) {
        super(id, name, price);
        this.weight = weight;
        this.shippingCost = shippingCost;
    }

    calcCost() {
        return this.price + this.shippingCost;
    }

    displayInfo() {
        console.log(`Physical Product - ID: ${this.id}, Name: ${this.name}, Price: ${this.price}, Weight: ${this.weight}kg, Shipping Cost: ${this.shippingCost}`);
    }
}
