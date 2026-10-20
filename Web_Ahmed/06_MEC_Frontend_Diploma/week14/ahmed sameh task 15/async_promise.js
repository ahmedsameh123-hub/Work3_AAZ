function fetchPostsWithPromise() {
    return new Promise((resolve) => {
      setTimeout(() => {
        const posts = ["Post 1", "Post 2", "Post 3"];
        resolve(posts);
      }, 5000);
    });
  }
  
  fetchPostsWithPromise().then((posts) => {
    console.log("Posts fetched with promise:", posts);
  });
  