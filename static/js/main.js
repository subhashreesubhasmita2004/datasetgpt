const validUsername = "admin";
const validPassword = "1234";

function checkLogin(event) {
    event.preventDefault();
    const usernameInput = document.getElementById("username").value;
    const passwordInput = document.getElementById("password").value;

    
    if (usernameInput === validUsername && passwordInput === validPassword) {
        window.location.href = "app.html";
    } else {
        alert("Invalid username or password");
    }
}

document.getElementById("loginForm").addEventListener("submit", checkLogin);