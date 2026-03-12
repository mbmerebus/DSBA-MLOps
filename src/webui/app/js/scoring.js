window.addEventListener("DOMContentLoaded", () => {
  if (window.location.pathname.includes("dash")) loadHistory();
});

async function scoreProperty() {
  clearMessage("score-message");
  const body = {

    surface_reelle_bati: parseFloat(document.getElementById("surface").value),
    nombre_pieces_principales: parseFloat(document.getElementById("rooms").value),
    code_departement: document.getElementById("dept").value,
    type_local: document.getElementById("type").value,
    nombre_lots: parseFloat(document.getElementById("lots").value),
    surface_terrain: parseFloat(document.getElementById("terrain").value),

  };
  try {
    const resp = await fetch(`${GATEWAY_URL}/score`, {

      method: "POST",
      headers: { "Content-Type": "application/json", "Authorization": `Bearer ${getToken()}` },
      body: JSON.stringify(body)
    });

    const data = await resp.json();

    if (!resp.ok) throw new Error(data.detail);
    document.getElementById("result-price").textContent = `€${data.predicted_price.toLocaleString("fr-FR")}`;
    document.getElementById("result-ci").textContent = `€${data.confidence_interval.low.toLocaleString("fr-FR")} – €${data.confidence_interval.high.toLocaleString("fr-FR")}`;
    document.getElementById("score-result").classList.remove("hidden");

    loadHistory();

  } catch (e) {
    setMessage("score-message", e.message);
  }
}

async function loadHistory() {
  try {
    const resp = await fetch(`${GATEWAY_URL}/history`, {
      headers: { "Authorization": `Bearer ${getToken()}` }
    });
    const data = await resp.json();
    const list = document.getElementById("history-list");


    if (!data.history || !data.history.length) {
      list.innerHTML = `<p class="empty">No predictions yet.</p>`;
      return;
    }
    //prediction info card in the history
    list.innerHTML = data.history
      .filter(h => h.result && h.result.predicted_price)
      .map(h => `
        <div class="history-item">
          <div>
            <span class="hist-price">€${h.result.predicted_price.toLocaleString("fr-FR")}</span>
            <span class="hist-meta">${h.input.type_local} · ${h.input.surface_reelle_bati}m² · Dept. ${h.input.code_departement}</span>
            <span class="hist-date">${new Date(h.timestamp).toLocaleString("fr-FR")}</span>
          </div>
          <span class="hist-ci">€${h.result.confidence_interval.low.toLocaleString("fr-FR")} – €${h.result.confidence_interval.high.toLocaleString("fr-FR")}</span>
        </div>
      `).join("");
  } catch (e) {
    console.error("History error:", e);
  }
}

async function uploadCSV(input) {
  const file = input.files[0];
  if (!file) return;

  const formData = new FormData();
  formData.append("file", file);
  const resultsDiv = document.getElementById("batch-results");
  resultsDiv.innerHTML = `<p class="empty">Processing...</p>`;

  try {

    const resp = await fetch(`${GATEWAY_URL}/score/batch`, {
      method: "POST",
      headers: { "Authorization": `Bearer ${getToken()}` },
      body: formData
    });

    const data = await resp.json();
    if (!resp.ok) throw new Error(data.detail);
    resultsDiv.innerHTML = `
      <p class="batch-count">${data.count} properties scored</p>
      ${data.predictions.map((p, i) => `
        <div class="batch-item">
          <span>#${i + 1} — €${p.predicted_price.toLocaleString("fr-FR")}</span>
          <span class="hist-ci">€${p.confidence_interval.low.toLocaleString("fr-FR")} – €${p.confidence_interval.high.toLocaleString("fr-FR")}</span>
        </div>
      `).join("")}
    `;

  } catch (e) {
    resultsDiv.innerHTML = `<p class="message" style="color:#c0392b">${e.message}</p>`;
  }
}