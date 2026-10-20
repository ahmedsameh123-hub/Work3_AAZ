export class Product {
    constructor(id, name, price) {
        this.id = id;
        this.name = name;
        this.price = price;
    }

    displayInfo() {
        console.log(`Product ID: ${this.id}, Name: ${this.name}, Price: ${this.price}`);
    }

    calcCost() {
        return this.price;
    }
}
