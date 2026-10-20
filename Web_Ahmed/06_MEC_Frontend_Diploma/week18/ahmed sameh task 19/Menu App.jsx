const menuItems = [
    { id: 1, name: "Pancakes", category: "breakfast", price: "$5", image: "path_to_image" },
    { id: 2, name: "Burger", category: "lunch", price: "$8", image: "path_to_image" },
    // more items
  ];
  
  function MenuApp() {
    const [filteredItems, setFilteredItems] = useState(menuItems);
  
    const filterItems = (category) => {
      if (category === "all") {
        setFilteredItems(menuItems);
      } else {
        setFilteredItems(menuItems.filter(item => item.category === category));
      }
    };
  
    return (
      <div>
        <button onClick={() => filterItems("all")}>All</button>
        <button onClick={() => filterItems("breakfast")}>Breakfast</button>
        <button onClick={() => filterItems("lunch")}>Lunch</button>
        <div>
          {filteredItems.map(item => (
            <div key={item.id}>
              <img src={item.image} alt={item.name} />
              <h4>{item.name}</h4>
              <p>{item.price}</p>
            </div>
          ))}
        </div>
      </div>
    );
  }
  