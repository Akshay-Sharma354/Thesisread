const API_BASE = "https://thesisread.onrender.com";

// Text form
const form = document.getElementById("filing-form");
const statusEl = document.getElementById("analyze-status");

// File form
const fileForm = document.getElementById("file-form");
const fileStatusEl = document.getElementById("file-status");

// CSV form
const csvInput = document.getElementById("csv_file");
const csvSubmitBtn = document.getElementById("csv-submit");
const csvStatusEl = document.getElementById("csv-status");

// Tab switching
document.querySelectorAll(".tab-btn").forEach(btn => {
  btn.addEventListener("click", () => {
    document.querySelectorAll(".tab-btn").forEach(b => b.classList.remove("active"));
    document.querySelectorAll(".tab-content").forEach(c => c.classList.remove("active"));
    btn.classList.add("active");
    document.getElementById(btn.dataset.tab).classList.add("active");
  });
});

// Feed
const feedEl = document.getElementById("feed");
const refreshBtn = document.getElementById("refresh-btn");

function scoreClass(score) {
  if (score >= 8) return "high";
  if (score >= 5) return "mid";
  return "low";
}

function renderCard(row) {
  const div = document.createElement("div");
  div.className = "card";
  const score = row.significance_score ?? "-";
  div.innerHTML = `
    <div class="card-top">
      <div>
        <div class="meta">${row.ticker || ""} · ${row.filing_type || ""} · ${row.filed_at || ""}</div>
      </div>
      <div class="score ${scoreClass(score)}">${score}/10</div>
    </div>
    <p class="body-text">${row.summary || ""}</p>
  `;
  return div;
}

async function loadFeed() {
  feedEl.innerHTML = `<div class="empty">Loading...</div>`;
  try {
    const res = await fetch(`${API_BASE}/alerts`);
    if (!res.ok) throw new Error(`Server returned ${res.status}`);
    const rows = await res.json();
    feedEl.innerHTML = "";
    if (!rows.length) {
      feedEl.innerHTML = `<div class="empty">No filings analyzed yet. Upload or paste one on the left.</div>`;
      return;
    }
    rows.forEach((row) => feedEl.appendChild(renderCard(row)));
  } catch (err) {
    feedEl.innerHTML = `<div class="empty">Could not reach the API. Is the backend running? (${err.message})</div>`;
  }
}

// Text form submission
form.addEventListener("submit", async (e) => {
  e.preventDefault();
  const company_name = document.getElementById("company_name").value.trim();
  const ticker = document.getElementById("ticker").value.trim();
  const raw_text = document.getElementById("raw_text").value.trim();

  statusEl.textContent = "Analyzing...";

  try {
    const res = await fetch(`${API_BASE}/filings/analyze`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ company_name, ticker, raw_text }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || `Server returned ${res.status}`);
    }
    const analysis = await res.json();
    statusEl.textContent = `✓ Done: "${analysis.alert_headline}"`;
    form.reset();
    loadFeed();
  } catch (err) {
    statusEl.textContent = `✗ Failed: ${err.message}`;
  }
});

// File form submission
fileForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const company_name = document.getElementById("file_company_name").value.trim();
  const ticker = document.getElementById("file_ticker").value.trim();
  const file = document.getElementById("filing_file").files[0];

  if (!file) {
    fileStatusEl.textContent = "Please select a file";
    return;
  }

  fileStatusEl.textContent = "Uploading & analyzing...";

  const formData = new FormData();
  formData.append("company_name", company_name);
  formData.append("ticker", ticker);
  formData.append("file", file);

  try {
    const res = await fetch(`${API_BASE}/filings/upload`, {
      method: "POST",
      body: formData,
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || `Server returned ${res.status}`);
    }
    const analysis = await res.json();
    fileStatusEl.textContent = `✓ Done: "${analysis.alert_headline}"`;
    fileForm.reset();
    loadFeed();
  } catch (err) {
    fileStatusEl.textContent = `✗ Failed: ${err.message}`;
  }
});

// CSV form submission
csvSubmitBtn.addEventListener("click", async () => {
  const file = csvInput.files[0];
  if (!file) {
    csvStatusEl.textContent = "Please select a CSV file";
    return;
  }

  csvStatusEl.textContent = "Uploading CSV...";

  const formData = new FormData();
  formData.append("file", file);

  try {
    const res = await fetch(`${API_BASE}/ingest/csv`, {
      method: "POST",
      body: formData,
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || `Server returned ${res.status}`);
    }
    const result = await res.json();
    csvStatusEl.textContent = `✓ Done: ${result.processed} filings processed from ${result.total_rows} rows`;
    csvInput.value = "";
    loadFeed();
  } catch (err) {
    csvStatusEl.textContent = `✗ Failed: ${err.message}`;
  }
});

refreshBtn.addEventListener("click", loadFeed);
loadFeed();
