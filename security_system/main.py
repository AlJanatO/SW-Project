from fastapi import FastAPI
from middleware import SecurityMiddleware
from fastapi.responses import HTMLResponse
from ui import layout
import api
import os
from db import ensure_schema

app = FastAPI(title="Security Monitoring System", docs_url="/swagger")

app.add_middleware(SecurityMiddleware)

app.include_router(api.router, prefix="/api")

ENABLE_VULN_SIMULATION = os.getenv("ENABLE_VULN_SIMULATION", "false").lower() == "true"

if ENABLE_VULN_SIMULATION:
    import vulnerable
    app.include_router(vulnerable.router, prefix="/vuln")


@app.on_event("startup")
def startup():
    ensure_schema()


@app.get("/", response_class=HTMLResponse)
def root():
    return layout("""
        <h1>Security Monitoring System</h1>
        <div class="card">
            Real-time backend security monitoring and threat simulation platform.
        </div>
    """)


@app.get("/docs", response_class=HTMLResponse)
def docs_page():
    return layout("""
        <h2>API Documentation</h2>
        <div class="card">
            <iframe src="/swagger" title="Swagger Docs" style="width:100%;height:80vh;border:none;border-radius:8px;background:white;"></iframe>
        </div>
    """)


@app.get("/analyze", response_class=HTMLResponse)
def analyze_page():
    return layout("""
        <h2>Analyze a Request</h2>
        <div class="card">
            <p>Submit JSON to <code>/api/analyze</code> (POST) and view the result.</p>
            <textarea id="payload" style="width:100%;min-height:180px;padding:12px;border-radius:8px;border:1px solid #334155;background:#0b1220;color:#e2e8f0;">{"path":"/login","method":"POST","payload":{"username":"admin","password":"password123"}}</textarea>
            <div style="margin-top:12px;display:flex;gap:10px;align-items:center;">
                <button id="run" style="padding:10px 14px;border-radius:8px;border:none;background:#22c55e;color:#052e16;font-weight:700;cursor:pointer;">Analyze</button>
                <span id="status" style="opacity:.85;"></span>
            </div>
        </div>
        <div class="card">
            <h3 style="margin-top:0;">Result</h3>
            <pre id="result" style="white-space:pre-wrap;"></pre>
        </div>

        <script>
          const btn = document.getElementById("run");
          const statusEl = document.getElementById("status");
          const payloadEl = document.getElementById("payload");
          const resultEl = document.getElementById("result");

          function setStatus(text) { statusEl.textContent = text || ""; }

          btn.addEventListener("click", async () => {
            resultEl.textContent = "";

            let payload;
            try {
              payload = JSON.parse(payloadEl.value);
            } catch (e) {
              setStatus("Invalid JSON in the textarea.");
              return;
            }

            setStatus("Analyzing…");
            try {
              const res = await fetch("/api/analyze", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload),
              });

              const text = await res.text();
              let data;
              try { data = JSON.parse(text); } catch { data = text; }

              resultEl.textContent = typeof data === "string" ? data : JSON.stringify(data, null, 2);
              setStatus(res.ok ? "Done." : `Error: HTTP ${res.status}`);
            } catch (e) {
              setStatus("Request failed (is the server running?).");
              resultEl.textContent = String(e);
            }
          });
        </script>
    """)


@app.get("/dashboard", response_class=HTMLResponse)
def dashboard_page():
    return layout("""
        <h2>Live Security Dashboard</h2>
        <div class="card">
            <div><strong>Total requests (24h):</strong> <span id="total">-</span></div>
            <div><strong>Anomaly requests (24h):</strong> <span id="anomalies">-</span></div>
        </div>
        <div class="card">
            <h3 style="margin-top:0;">Top IPs (24h)</h3>
            <pre id="ips">Loading...</pre>
        </div>
        <div class="card">
            <h3 style="margin-top:0;">Recent Requests</h3>
            <pre id="recent">Loading...</pre>
        </div>
        <div class="card">
            <h3 style="margin-top:0;">Recent Anomalies</h3>
            <pre id="anomaly-list">Loading...</pre>
        </div>
        <script>
          async function refresh() {
            try {
              const res = await fetch("/api/dashboard/metrics");
              const data = await res.json();
              document.getElementById("total").textContent = String(data.total_requests_24h);
              document.getElementById("anomalies").textContent = String(data.anomaly_requests_24h);
              document.getElementById("ips").textContent = JSON.stringify(data.top_ips_24h, null, 2);
              document.getElementById("recent").textContent = JSON.stringify(data.recent_requests, null, 2);
              document.getElementById("anomaly-list").textContent = JSON.stringify(data.recent_anomalies, null, 2);
            } catch (e) {
              document.getElementById("recent").textContent = String(e);
            }
          }
          refresh();
          setInterval(refresh, 4000);
        </script>
    """)