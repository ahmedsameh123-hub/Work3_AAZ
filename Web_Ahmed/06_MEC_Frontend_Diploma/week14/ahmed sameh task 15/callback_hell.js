function fetchUserData() {
    return new Promise((resolve) => {
      setTimeout(() => {
        const userData = { id: 1, name: "John Doe" };
        resolve(userData);
      }, 2000);
    });
  }
  
  function fetchPosts(userData) {
    return new Promise((resolve) => {
      setTimeout(() => {
        const posts = ["Post 1", "Post 2", "Post 3"];
        resolve(posts);
      }, 3000);
    });
  }
  
  function fetchComments(posts) {
    return new Promise((resolve) => {
      setTimeout(() => {
        const comments = ["Comment 1", "Comment 2"];
        resolve(comments);
      }, 2000);
    });
  }
  
  fetchUserData()
    .then((userData) => fetchPosts(userData))
    .then((posts) => fetchComments(posts))
    .then((comments) => {
      displayData(userData, posts, comments);
    });
  