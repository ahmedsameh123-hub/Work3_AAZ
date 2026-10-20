function Cart() {
    const [products, setProducts] = useState([
      { name: "Product 1", price: 100, quantity: 1 },
      // More products...
    ]);
  
    const updateQuantity = (index, newQuantity) => {
      const updatedProducts = [...products];
      updatedProducts[index].quantity = newQuantity;
      setProducts(updatedProducts);
    };
  
    const addProduct = (product) => {
      setProducts([...products, product]);
    };
  
    const totalCost = products.reduce((acc, product) => acc + product.price * product.quantity, 0);
  
    return (
      <div>
        {products.map((product, index) => (
          <Product key={index} product={product} updateQuantity={updateQuantity} />
        ))}
        <h3>Total: ${totalCost}</h3>
        {/* Add Product Form */}
      </div>
    );
  }
  
  function Product({ product, updateQuantity }) {
    return (
      <div>
        <h4>{product.name} - ${product.price}</h4>
        <input
          type="number"
          value={product.quantity}
          onChange={(e) => updateQuantity(index, e.target.value)}
        />
      </div>
    );
  }
  