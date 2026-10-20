// Function to filter products by name
function filterProductsByName(products, searchTerm) {
  return searchForProductsByName(products, searchTerm);
}

// Function to filter products by price range
function filterProductsByPriceRange(products, minPrice, maxPrice) {
  const minPriceNumber = parseFloat(minPrice || "0");
  const maxPriceNumber = parseFloat(maxPrice || Infinity.toString());
  return filterProductsByPrice(products, minPriceNumber, maxPriceNumber);
}

// Function to filter products by discount
function filterProductsByDiscount(products, discountOnly) {
  return discountOnly ? getProductsWithDiscounts(products) : products;
}

// Function to sort products
function sortProducts(products, sortBy) {
  if (sortBy === "price-low-to-high") {
    return sortProductsByPriceLowToHigh([...products]);
  } else if (sortBy === "price-high-to-low") {
    return sortProductsByPriceHighToLow([...products]);
  }
  return products;
}

function getDefaultProductsDisplay(products) {
  return products.map((product) => {
    return product.name;
  });
}

// Function to generate the HTML for product listing
function getProductsHTML(products) {
  let newProducts = getProductsDisplayText(products);

  if (!newProducts) newProducts = getDefaultProductsDisplay(products);
  return newProducts
    .map((product, index) => {
      return `<div class='product-wrapper'>
                <input type="checkbox" class="product-checkbox" value="${products[index].id}">
                <div>
                    ${product}
                </div>
             </div> `;
    })
    .join("");
}

// Function to handle rendering the product listing
function renderProducts(products) {
  const productContainer = document.getElementById("product-container");
  productContainer.innerHTML = getProductsHTML(products);
}
// Function to get the selected products
function getSelectedProducts() {
  const checkboxes = document.getElementsByClassName("product-checkbox");
  const selectedProducts = [];
  for (let i = 0; i < checkboxes.length; i++) {
    if (checkboxes[i].checked) {
      const productId = parseInt(checkboxes[i].value);
      selectedProducts.push(getProductById(products, productId));
    }
  }
  return selectedProducts;
}

// Function to update the selected products list
function updateSelectedProducts(selectedProducts) {
  const selectedProductsContainer =
    document.getElementById("selected-products");
  selectedProductsContainer.innerHTML = selectedProducts
    .map((product) => {
      return `<li>${product.name} - $${product.price}</li>`;
    })
    .join("");
}

// Function to update the total price
function updateTotalPrice(totalPrice) {
  const totalPriceContainer = document.getElementById("total-price");
  totalPriceContainer.textContent = `Total Price: $${totalPrice}`;
}
// Event listener for checkout button
const checkoutBtn = document.getElementById("checkout-btn");
checkoutBtn.addEventListener("click", function () {
  const selectedProducts = getSelectedProducts();
  const totalPrice = calculateTotalPrice(selectedProducts);
  updateSelectedProducts(selectedProducts);
  updateTotalPrice(totalPrice);
});

// Initial product listing
let filteredProducts = products.slice();
renderProducts(filteredProducts);

// Event listener for search field
const searchField = document.getElementById("search-field");
searchField.addEventListener("input", function (event) {
  const searchTerm = event.target.value;
  filteredProducts = filterProductsByName(products, searchTerm);
  renderProducts(filteredProducts);
});

// Event listener for min price field
const minPriceField = document.getElementById("min-price");
minPriceField.addEventListener("input", function (event) {
  const minPrice = event.target.value;
  filteredProducts = filterProductsByPriceRange(
    products,
    minPrice,
    maxPriceField.value
  );
  renderProducts(filteredProducts);
});

// Event listener for max price field
const maxPriceField = document.getElementById("max-price");
maxPriceField.addEventListener("input", function (event) {
  const maxPrice = event.target.value;
  filteredProducts = filterProductsByPriceRange(
    products,
    minPriceField.value,
    maxPrice
  );
  renderProducts(filteredProducts);
});

// Event listener for discount checkbox
const discountCheckbox = document.getElementById("discount-checkbox");
discountCheckbox.addEventListener("change", function (event) {
  const discountOnly = event.target.checked;
  filteredProducts = filterProductsByDiscount(products, discountOnly);
  renderProducts(filteredProducts);
});

// Event listener for sort by dropdown
const sortByDropdown = document.getElementById("sort-by");
sortByDropdown.addEventListener("change", function (event) {
  const sortBy = event.target.value;
  const sortedProducts = sortProducts(filteredProducts, sortBy);
  renderProducts(sortedProducts);
});
