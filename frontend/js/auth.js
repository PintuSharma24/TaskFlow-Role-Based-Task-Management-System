
const loginForm = document.getElementById("loginForm");

loginForm.addEventListener("submit", async function (event) {
    event.preventDefault();

    const role = document.getElementById("role").value;
    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value;

    const loginMessage = document.getElementById("loginMessage");
    const loginButton = document.getElementById("loginButton");

    loginMessage.textContent = "";
    loginButton.disabled = true;
    loginButton.textContent = "Signing in...";

    try {
        const data = await apiRequest("/auth/login", {
            method: "POST",
            body: JSON.stringify({
                email: email,
                password: password,
                role: role
            })
        });

        // Store authentication information
        localStorage.setItem("access_token", data.access_token);
        localStorage.setItem("user", JSON.stringify(data.user));

        loginMessage.style.color = "green";
        loginMessage.textContent = "Login successful! Redirecting...";

        // Redirect according to verified backend role
        const userRole = data.user.role;

        if (userRole === "admin") {
            window.location.href = "admin/dashboard.html";
        } else if (userRole === "manager") {
            window.location.href = "manager/dashboard.html";
        } else if (userRole === "employee") {
            window.location.href = "employee/dashboard.html";
        } else {
            throw new Error("Invalid user role");
        }

    } catch (error) {
        loginMessage.style.color = "red";
        loginMessage.textContent = error.message;
    } finally {
        loginButton.disabled = false;
        loginButton.textContent = "Sign In";
    }
});
