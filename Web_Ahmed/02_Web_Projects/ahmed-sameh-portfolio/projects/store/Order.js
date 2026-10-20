// Order.js
export class Order {
    constructor(id, customer, products = []) {
        this.id = id;
        this.customer = customer;
        this.products = products;
    }

    addProduct(product) {
        this.products.push(product);
    }

    calcTotalPrice() {
        let total = 0;
        for (const product of this.products) {
            total += product.calcCost();
        }

        if (this.customer.discountPerc) {
            total = total * (1 - this.customer.discountPerc / 100);
        }

        return total;
    }

    displayInfo() {
        console.log(`Order ID: ${this.id}`);
        this.customer.displayInfo();
        this.products.forEach((product, index) => {
            console.log(`Product ${index + 1}:`);
            product.displayInfo();
        });
    }
}
