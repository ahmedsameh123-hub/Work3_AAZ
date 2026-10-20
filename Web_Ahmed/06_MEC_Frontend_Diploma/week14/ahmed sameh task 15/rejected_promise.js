function fetchUserInfo(username) {
    return Promise.reject(new Error('User not found'));
  }
  
  fetchUserInfo("nonExistentUser")
    .catch((error) => {
      console.error("Error:", error.message);
    });
  