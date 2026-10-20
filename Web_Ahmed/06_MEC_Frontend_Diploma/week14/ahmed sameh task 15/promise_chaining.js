function fetchUserDataPromise() {
    return new Promise((resolve) => {
      setTimeout(() => {
        const userData = { id: 1, name: "John Doe" };
        resolve(userData);
      }, 2000);
    });
  }
  
  function fetchPostsPromise(userId) {
    return new Promise((resolve) => {
      setTimeout(() => {
        const posts = ["Post 1", "Post 2", "Post 3"];
        resolve(posts);
      }, 3000);
    });
  }
  
  fetchUserDataPromise()
    .then((userData) => {
      console.log("User data:", userData);
      return fetchPostsPromise(userData.id);
    })
    .then((posts) => {
      console.log("Posts fetched after user data:", posts);
    });
  