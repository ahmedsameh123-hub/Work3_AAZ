// === 1. Async function with callback ===
function fetchPostsWithCallback(callback) {
    setTimeout(() => {
        const posts = ["Post 1", "Post 2", "Post 3"];
        callback(posts);
    }, 5000);
}

function runCallbackExample() {
    document.getElementById('output').innerText = "Fetching posts using callback...";
    fetchPostsWithCallback((posts) => {
        document.getElementById('output').innerText = "Posts fetched with callback: " + posts.join(", ");
    });
}

// === 2. Async Function with Promise ===
function fetchPostsWithPromise() {
    return new Promise((resolve) => {
        setTimeout(() => {
            const posts = ["Post 1", "Post 2", "Post 3"];
            resolve(posts);
        }, 5000);
    });
}

function runPromiseExample() {
    document.getElementById('output').innerText = "Fetching posts using promise...";
    fetchPostsWithPromise().then((posts) => {
        document.getElementById('output').innerText = "Posts fetched with promise: " + posts.join(", ");
    });
}

// === 3. Promise Chaining ===
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

function runPromiseChainingExample() {
    document.getElementById('output').innerText = "Fetching user data and posts...";
    fetchUserDataPromise()
        .then((userData) => {
            document.getElementById('output').innerText = "User data: " + JSON.stringify(userData);
            return fetchPostsPromise(userData.id);
        })
        .then((posts) => {
            document.getElementById('output').innerText += "\nPosts: " + posts.join(", ");
        });
}

// === 5. Rejected Promise Handling ===
function fetchUserInfo(username) {
    return Promise.reject(new Error('User not found'));
}

function runRejectedPromiseExample() {
    document.getElementById('output').innerText = "Fetching user info...";
    fetchUserInfo("nonExistentUser")
        .catch((error) => {
            document.getElementById('output').innerText = "Error: " + error.message;
        });
}
