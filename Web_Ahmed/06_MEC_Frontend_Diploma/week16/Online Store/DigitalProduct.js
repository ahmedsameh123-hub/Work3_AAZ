import { Product } from './Product.js';

export class DigitalProduct extends Product {
    constructor(id, name, price, subscriptionFees, subscriptionDuration) {
        super(id, name, price);
        this.subscriptionFees = subscriptionFees;
        this.subscriptionDuration = subscriptionDuration;
    }

    calcCost() {
        return this.price + this.subscriptionFees;
    }

    displayInfo() {
        console.log(`Digital Product - ID: ${this.id}, Name: ${this.name}, Price: ${this.price}, Subscription Fees: ${this.subscriptionFees}, Duration: ${this.subscriptionDuration} months`);
    }
}
