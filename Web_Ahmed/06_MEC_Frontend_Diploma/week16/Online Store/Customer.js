export class Customer {
    constructor(id, name, email, address) {
        this.id = id;
        this.name = name;
        this.email = email;
        this.address = address;
    }

    displayInfo() {
        console.log(`Customer ID: ${this.id}, Name: ${this.name}, Email: ${this.email}, Address: ${this.address}`);
    }
}
