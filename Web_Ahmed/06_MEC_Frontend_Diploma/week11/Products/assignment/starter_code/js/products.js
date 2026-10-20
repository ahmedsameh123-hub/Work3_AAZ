// Function to filter products by price range
function filterProductsByPrice(products, minPrice, maxPrice) {
    return products.filter(product => product.price >= minPrice && product.price <= maxPrice);
  }
  
  // Function to map products to their display text
  function getProductsDisplayText(products) {
    return products.map(product => `
      <h4>
        <a href='#'>${product.name}</a> - $${product.price} 
        ${product.discount ? "<img src='./images/discount.png' width=30/>" : ""}
      </h4>
      <p>${product.description}</p>
    `);
  }
  
  // Function to calculate the total price
  function calculateTotalPrice(selectedProducts) {
    return selectedProducts.reduce((total, product) => total + product.price, 0).toFixed(2);
  }
  
  // Function to get product by its id
  function getProductById(products, productID) {
    return products.find(product => product.id === productID);
  }
  
  // Filter products by name
  function searchForProductsByName(products, searchText) {
    return products.filter(product => product.name.toLowerCase().includes(searchText.toLowerCase()));
  }
  
  // Function to filter products that have discount
  function getProductsWithDiscounts(products) {
    return products.filter(product => product.discount);
  }
  
  // Function to sort products from lowest price to highest (ASC)
  function sortProductsByPriceLowToHigh(products) {
    return products.sort((a, b) => a.price - b.price);
  }
  
  // Function to sort products from highest price to lowest (DESC)
  function sortProductsByPriceHighToLow(products) {
    return products.sort((a, b) => b.price - a.price);
  }
  