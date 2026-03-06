window.addEventListener("DOMContentLoaded", () => {
  if (window.location.pathname.includes("auth") || window.location.pathname === "/") {
    if (getToken()) window.location.href = "dash.html";
  }
  if (window.location.pathname.includes("dash")) {
    if (!getToken()) window.location.href = "auth.html";
    document.getElementById("nav-username").textContent = getUsername();
  }
});

async function login() {
  const username = document.getElementById("login-username").value;
  const password = document.getElementById("login-password").value;
  clearMessage("auth-message");
  try {
    const resp = await fetch(`${AUTH_URL}/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password })
    });
    const data = await resp.json();
    if (!resp.ok) throw new Error(data.detail);
    localStorage.setItem("token", data.access_token);
    localStorage.setItem("username", username);
    window.location.href = "dash.html";
  } catch (e) {
    setMessage("auth-message", e.message);
  }
}

async function register() {
  const username = document.getElementById("reg-username").value;
  const password = document.getElementById("reg-password").value;
  clearMessage("auth-message");
  try {
    const resp = await fetch(`${AUTH_URL}/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password })
    });
    const data = await resp.json();
    if (!resp.ok) throw new Error(data.detail);
    setMessage("auth-message", "Account created! Please login.", false);
    switchTab("login");
  } catch (e) {
    setMessage("auth-message", e.message);
  }
}

async function logout() {
  try {
    await fetch(`${AUTH_URL}/logout`, {
      method: "POST",
      headers: { "Authorization": `Bearer ${getToken()}` }
    });
  } catch (e) {
    console.error("Logout error:", e);
  }
  localStorage.clear();
  window.location.href = "auth.html";
}