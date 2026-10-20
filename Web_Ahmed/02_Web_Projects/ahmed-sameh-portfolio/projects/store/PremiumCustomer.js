import { Customer } from './Customer.js';

export class PremiumCustomer extends Customer {
    constructor(id, name, email, address, discountPerc) {
        super(id, name, email, address);
        this.discountPerc = discountPerc;
    }

    displayInfo() {
        console.log(`Premium Customer - ID: ${this.id}, Name: ${this.name}, Email: ${this.email}, Address: ${this.address}, Discount: ${this.discountPerc}%`);
    }
}
