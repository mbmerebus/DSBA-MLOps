const AUTH_URL = "http://localhost:8001";
const GATEWAY_URL = "http://localhost:8002";

function getToken() {
  return localStorage.getItem("token");
}

function getUsername() {
  return localStorage.getItem("username");
}

function setMessage(id, text, isError = true) {
  const el = document.getElementById(id);
  el.textContent = text;
  el.style.color = isError ? "#c0392b" : "#27ae60";
}

function clearMessage(id) {
  document.getElementById(id).textContent = "";
}

function switchTab(tab) {
  document.getElementById("login-form").classList.toggle("hidden", tab !== "login");
  document.getElementById("register-form").classList.toggle("hidden", tab !== "register");
  document.getElementById("tab-login").classList.toggle("active", tab === "login");
  document.getElementById("tab-register").classList.toggle("active", tab === "register");
  clearMessage("auth-message");
}