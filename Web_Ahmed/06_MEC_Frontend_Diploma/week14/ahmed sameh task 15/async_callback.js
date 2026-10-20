function fetchPostsWithCallback(callback) {
    setTimeout(() => {
      const posts = ["Post 1", "Post 2", "Post 3"];
      callback(posts);
    }, 5000);
  }
  
  fetchPostsWithCallback((posts) => {
    console.log("Posts fetched with callback:", posts);
  });
  