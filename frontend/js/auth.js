const AUTH_API_URL = "https://palm-mitra-2-0.onrender.com";


/* =========================
   LOGIN
========================= */

const loginForm = document.getElementById("loginForm");

if (loginForm) {

    loginForm.addEventListener("submit", async function (event) {

        event.preventDefault();

        const email = document
            .getElementById("loginEmail")
            .value
            .trim();

        const password = document
            .getElementById("loginPassword")
            .value;

        const message = document.getElementById("loginMessage");

        message.textContent = "Signing in...";

        try {

            const response = await fetch(
                `${AUTH_API_URL}/api/auth/login`,
                {
                    method: "POST",

                    headers: {
                        "Content-Type": "application/json"
                    },

                    body: JSON.stringify({
                        email: email,
                        password: password
                    })
                }
            );

            const data = await response.json();

            if (!response.ok) {

                message.textContent =
                    data.detail || "Login failed.";

                return;
            }

            /*
             * Store authentication information
             */

            localStorage.setItem(
                "palmMitraToken",
                data.access_token
            );

            localStorage.setItem(
                "palmMitraUser",
                JSON.stringify(data.user)
            );

            message.textContent =
                "Login successful. Redirecting...";

            /*
             * Redirect to the main Palm Mitra application
             */

            window.location.href = "index.html";

        } catch (error) {

            console.error("Login error:", error);

            message.textContent =
                "Unable to connect to Palm Mitra server.";
        }
    });
}


/* =========================
   SIGNUP
========================= */

const signupForm = document.getElementById("signupForm");

if (signupForm) {

    signupForm.addEventListener("submit", async function (event) {

        event.preventDefault();

        const name = document
            .getElementById("signupName")
            .value
            .trim();

        const email = document
            .getElementById("signupEmail")
            .value
            .trim();

        const password = document
            .getElementById("signupPassword")
            .value;

        const message = document.getElementById("signupMessage");

        message.textContent = "Creating your account...";

        try {

            const response = await fetch(
                `${AUTH_API_URL}/api/auth/signup`,
                {
                    method: "POST",

                    headers: {
                        "Content-Type": "application/json"
                    },

                    body: JSON.stringify({
                        name: name,
                        email: email,
                        password: password
                    })
                }
            );

            const data = await response.json();

            if (!response.ok) {

                message.textContent =
                    data.detail || "Signup failed.";

                return;
            }

            message.textContent =
                "Account created successfully. Redirecting to login...";

            setTimeout(function () {

                window.location.href = "login.html";

            }, 1000);

        } catch (error) {

            console.error("Signup error:", error);

            message.textContent =
                "Unable to connect to Palm Mitra server.";
        }
    });
}