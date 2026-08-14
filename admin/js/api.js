function getToken() {
  const token = localStorage.getItem("admin_token");
  if (!token) window.location.href = "index.html";
  return token;
}

async function adminGet(path) {
  const res = await fetch(`${API_BASE_URL}${path}`, {
    headers: { Authorization: `Bearer ${getToken()}` },
  });
  if (res.status === 401) { localStorage.removeItem("admin_token"); window.location.href = "index.html"; }
  if (!res.ok) throw new Error(`API error ${res.status}`);
  return res.json();
}

async function adminSend(path, method, body) {
  const res = await fetch(`${API_BASE_URL}${path}`, {
    method,
    headers: { "Content-Type": "application/json", Authorization: `Bearer ${getToken()}` },
    body: body ? JSON.stringify(body) : undefined,
  });
  if (res.status === 401) { localStorage.removeItem("admin_token"); window.location.href = "index.html"; }
  if (!res.ok) throw new Error(`API error ${res.status}`);
  return res.json();
}

function logout() {
  localStorage.removeItem("admin_token");
  localStorage.removeItem("admin_role");
  localStorage.removeItem("admin_name");
  window.location.href = "index.html";
}

function getRole() {
  return localStorage.getItem("admin_role") || "staff";
}

function applyRoleGating() {
  const role = getRole();
  const navAdmins = document.getElementById("navAdmins");
  const navSettings = document.getElementById("navSettings");
  const navAuditLog = document.getElementById("navAuditLog");
  if (navAdmins && role !== "owner") navAdmins.style.display = "none";
  if (navSettings && role !== "owner") navSettings.style.display = "none";
  if (navAuditLog && role === "staff") navAuditLog.style.display = "none";

  const roleBadge = document.getElementById("roleBadge");
  if (roleBadge) roleBadge.textContent = role.charAt(0).toUpperCase() + role.slice(1);
}

function formatPrice(n) {
  return "₹" + Number(n).toLocaleString("en-IN");
}

function statusPill(status) {
  return `<span class="pill ${status.toLowerCase()}">${status}</span>`;
}
