const API_BASE = "http://localhost:8000";
// Tab switching
document.querySelectorAll(".tab-btn").forEach(btn => {
  btn.addEventListener("click", () => {
    const tabName = btn.dataset.tab;
    document.querySelectorAll(".tab-content").forEach(t => t.classList.remove("active"));
    document.querySelectorAll(".tab-btn").forEach(b => b.classList.remove("active"));
    document.getElementById(tabName + "-tab").classList.add("active");
    btn.classList.add("active");
  });
});

// File input listeners
document.getElementById("file-input").addEventListener("change", (e) => {
  const fileName = e.target.files[0]?.name || "No file chosen";
  document.getElementById("file-name").textContent = fileName;
});

document.getElementById("csv-input").addEventListener("change", (e) => {
  const fileName = e.target.files[0]?.name || "No file chosen";
  document.getElementById("csv-name").textContent = fileName;
});

async function analyzePaste() {
  const company = document.getElementById("paste-company").value.trim();
  const ticker = document.getElementById("paste-ticker").value.trim();
  const text = document.getElementById("paste-text").value.trim();
  const statusEl = document.getElementById("paste-status");
  
  if (!company || !ticker || !text) {
    statusEl.textContent = "❌ Please fill all fields";
    return;
  }
  
  statusEl.textContent = "📊 Analyzing...";
  
  try {
    const formData = new FormData();
    formData.append("company_name", company);
    formData.append("ticker", ticker);
    formData.append("raw_text", text);
    
    const response = await fetch(API_BASE + "/filings/analyze", {
      method: "POST",
      body: formData
    });
    
    if (response.ok) {
      statusEl.textContent = "✅ Analysis complete!";
      document.getElementById("paste-company").value = "";
      document.getElementById("paste-ticker").value = "";
      document.getElementById("paste-text").value = "";
      loadAlerts();
    } else {
      statusEl.textContent = "❌ Analysis failed";
    }
  } catch (error) {
    statusEl.textContent = "❌ Error: " + error.message;
  }
}

async function uploadFile() {
  const company = document.getElementById("file-company").value.trim();
  const ticker = document.getElementById("file-ticker").value.trim();
  const file = document.getElementById("file-input").files[0];
  const statusEl = document.getElementById("file-status");
  
  if (!company || !ticker || !file) {
    statusEl.textContent = "❌ Please fill all fields";
    return;
  }
  
  statusEl.textContent = "📤 Uploading...";
  
  try {
    const formData = new FormData();
    formData.append("company_name", company);
    formData.append("ticker", ticker);
    formData.append("file", file);
    
    const response = await fetch(API_BASE + "/filings/upload", {
      method: "POST",
      body: formData
    });
    
    if (response.ok) {
      statusEl.textContent = "✅ File uploaded!";
      document.getElementById("file-company").value = "";
      document.getElementById("file-ticker").value = "";
      document.getElementById("file-input").value = "";
      document.getElementById("file-name").textContent = "No file chosen";
      loadAlerts();
    } else {
      statusEl.textContent = "❌ Upload failed";
    }
  } catch (error) {
    statusEl.textContent = "❌ Error: " + error.message;
  }
}

async function uploadCSV() {
  const file = document.getElementById("csv-input").files[0];
  const statusEl = document.getElementById("csv-status");
  
  if (!file) {
    statusEl.textContent = "❌ Please select a CSV file";
    return;
  }
  
  statusEl.textContent = "📊 Processing CSV...";
  
  try {
    const formData = new FormData();
    formData.append("file", file);
    
    const response = await fetch(API_BASE + "/ingest/csv", {
      method: "POST",
      body: formData
    });
    
    if (response.ok) {
      const data = await response.json();
      statusEl.textContent = "✅ " + (data.message || "CSV processed!");
      document.getElementById("csv-input").value = "";
      document.getElementById("csv-name").textContent = "No file chosen";
      loadAlerts();
    } else {
      statusEl.textContent = "❌ CSV processing failed";
    }
  } catch (error) {
    statusEl.textContent = "❌ Error: " + error.message;
  }
}

async function loadAlerts() {
  const feed = document.getElementById("alert-feed");
  
  try {
    const response = await fetch(API_BASE + "/alerts");
    
    if (!response.ok) throw new Error("Failed to load alerts");
    
    const alerts = await response.json();
    
    if (!alerts || alerts.length === 0) {
      feed.innerHTML = `<div class="empty-state"><div class="empty-state-icon">📭</div><p>No filings analyzed yet. Upload a filing to get started!</p></div>`;
      return;
    }
    
    feed.innerHTML = alerts.reverse().map(alert => {
      const scoreClass = getScoreClass(alert.significance_score || 5);
      const signal = alert.signal || {};
      
      return `
        <div class="alert-item">
          <div class="alert-header">
            <div class="alert-title">${alert.ticker || 'N/A'} • ${alert.filing_type || 'FILING'} • ${alert.filed_at || ''}</div>
            <div class="score-badge ${scoreClass}">${alert.significance_score || 5}/10</div>
          </div>
          
          <div class="alert-headline">${alert.alert_headline || 'Filing Update'}</div>
          
          <div class="alert-body">${alert.alert_body || alert.summary || 'Analysis completed'}</div>
          
          ${signal.signal ? `
            <div style="margin-top: 1.2rem; padding-top: 1.2rem; border-top: 1px solid var(--border-color);">
              <div style="display: flex; align-items: center; gap: 0.8rem; margin-bottom: 0.5rem;">
                <span style="font-size: 1.3rem;">${getSignalEmoji(signal.signal)}</span>
                <span style="font-weight: 700; color: ${getSignalColor(signal.signal)}; text-transform: uppercase; letter-spacing: 1px;">
                  ${signal.signal} SIGNAL
                </span>
                <span style="background: rgba(212, 175, 55, 0.15); color: var(--primary); padding: 0.3rem 0.8rem; border-radius: 4px; font-size: 0.8rem; font-weight: 700;">
                  ${signal.confidence || 'LOW'} CONFIDENCE
                </span>
              </div>
              <div style="color: var(--text-secondary); font-size: 0.9rem;">
                ${signal.reasoning || 'No reasoning available'}
              </div>
              <div style="margin-top: 0.8rem; color: var(--primary); font-size: 0.95rem; font-weight: 600;">
                ${signal.action || 'Monitor the situation'}
              </div>
            </div>
          ` : ''}
          
          ${alert.pattern_note ? `
            <div style="margin-top: 1rem; padding: 0.8rem; background: rgba(212, 175, 55, 0.08); border-left: 3px solid var(--primary); border-radius: 4px;">
              <div style="color: var(--primary); font-size: 0.8rem; font-weight: 700; text-transform: uppercase;">Pattern Detected</div>
              <div style="color: var(--text-secondary); font-size: 0.9rem; margin-top: 0.3rem;">
                ${alert.pattern_note}
              </div>
            </div>
          ` : ''}
        </div>
      `;
    }).join("");
  } catch (error) {
    feed.innerHTML = `<div class="empty-state"><p>Error loading alerts: ${error.message}</p></div>`;
  }
}

function getScoreClass(score) {
  if (score >= 7) return "score-high";
  if (score >= 5) return "score-medium";
  return "score-low";
}

function getSignalColor(signal) {
  if (signal === "BUY") return "#06B6D4";
  if (signal === "SELL") return "#EF4444";
  return "#F59E0B";
}

function getSignalEmoji(signal) {
  if (signal === "BUY") return "🟢";
  if (signal === "SELL") return "🔴";
  return "🟡";
}

loadAlerts();
setInterval(loadAlerts, 30000);
