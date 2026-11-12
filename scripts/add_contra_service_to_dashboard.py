"""
Insert Contra Service card into dashboard/index.html.
"""

path = r"D:\aria-agent\dashboard\index.html"
with open(path, "r", encoding="utf-8") as f:
    html = f.read()

target = '    <!-- TIER 3: OPEN SOURCE CONTRIBUTIONS AUDIT (NO FAKE PAYOUTS) -->'

contra_section = """    <!-- TIER 2.7: VERIFIED CLIENT SERVICES (CONTRA $150/HR) -->
    <div style="margin-top: 20px;">
      <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:14px; flex-wrap:wrap; gap:10px;">
        <div>
          <h2 style="font-size:18px; font-weight:800; display:flex; align-items:center; gap:8px;">
            <span>⚡</span> VERIFIED CLIENT SERVICE OFFERINGS (CONTRA VERIFIED)
          </h2>
          <p style="font-size:12px; color:var(--text-muted); margin-top:3px;">
            Direct Contract & Escrow Protected • 100% Commission-Free Client Engagement via Contra
          </p>
        </div>
        <a href="https://contra.com/hardik_kakkad_d2lx96u3" target="_blank" class="status-badge status-approved" style="text-decoration:none;">
          Verified Freelancer Profile ↗
        </a>
      </div>

      <div class="engine-card" style="border: 1px solid rgba(168, 85, 247, 0.35); background: linear-gradient(135deg, rgba(16, 21, 33, 0.8), rgba(88, 28, 135, 0.15));">
        <div class="engine-header">
          <div>
            <div class="engine-title" style="color: #c084fc;">⚡ Python FastAPI Webhook and API Integration</div>
            <div class="engine-subtitle">Direct Client Service by Hardik Kakkad • Standalone, Production-Grade Architecture</div>
          </div>
          <span class="engine-tag" style="background: rgba(168, 85, 247, 0.2); color: #c084fc;">STARTING AT $150 / HR</span>
        </div>

        <div class="stats-trio">
          <div class="stat-box">
            <div class="stat-val" style="color: #c084fc;">$150.00</div>
            <div class="stat-lbl">Hourly Rate (USD)</div>
          </div>
          <div class="stat-box">
            <div class="stat-val" style="color: var(--accent-emerald);">&lt; 50ms</div>
            <div class="stat-lbl">Ingestion Latency</div>
          </div>
          <div class="stat-box">
            <div class="stat-val" style="color: var(--accent-cyan);">100% Green</div>
            <div class="stat-lbl">6/6 Pytest Passing</div>
          </div>
        </div>

        <ul class="feature-list" style="margin-top: 14px;">
          <li class="feature-item">
            <span class="feat-icon" style="color: #c084fc;">✓</span>
            <div><strong>HMAC-SHA256 Signature Verification:</strong> Multi-provider authentication for Stripe (timestamp drift & replay defense), Shopify (Base64 digest), Twilio, and HubSpot.</div>
          </li>
          <li class="feature-item">
            <span class="feat-icon" style="color: #c084fc;">✓</span>
            <div><strong>Pydantic V2 Strict Validation:</strong> Automated schema typing and validation on all incoming payload bodies.</div>
          </li>
          <li class="feature-item">
            <span class="feat-icon" style="color: #c084fc;">✓</span>
            <div><strong>Idempotent Deduplication:</strong> Thread-safe SQLite / PostgreSQL storage preventing duplicate webhook processing during network replays.</div>
          </li>
          <li class="feature-item">
            <span class="feat-icon" style="color: #c084fc;">✓</span>
            <div><strong>Async Retry Queue:</strong> Exponential backoff retry queue executing heavy downstream CRM/database jobs in the background.</div>
          </li>
          <li class="feature-item">
            <span class="feat-icon" style="color: #c084fc;">✓</span>
            <div><strong>Docker & Render Ready:</strong> Complete <code>Dockerfile</code> and <code>render.yaml</code> for instant 1-click cloud container deployment.</div>
          </li>
        </ul>

        <div style="margin-top:16px; padding-top:14px; border-top:1px solid var(--border-subtle); display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px;">
          <div style="display:flex; gap:10px; flex-wrap:wrap;">
            <a href="https://contra.com/s/UsUQXXqo-python-fast-api-webhook-and-api-integration" target="_blank" style="background:#a855f7; color:#020617; font-weight:800; padding:10px 18px; border-radius:8px; text-decoration:none; font-size:13px; display:inline-flex; align-items:center; gap:6px;">
              ⚡ Hire on Contra ($150/hr) ↗
            </a>
            <a href="https://github.com/hardik4love-lang/aria-agent/tree/main/src/aria/integrations/fastapi_webhook_engine" target="_blank" style="background:rgba(255,255,255,0.08); color:#fff; font-weight:600; padding:10px 18px; border-radius:8px; text-decoration:none; font-size:13px;">
              📁 View Codebase on GitHub ↗
            </a>
          </div>
          <span class="status-badge status-approved">src/aria/integrations/fastapi_webhook_engine/</span>
        </div>
      </div>
    </div>

""" + target

if target in html:
    html = html.replace(target, contra_section)
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    print("Successfully added Contra Service section to dashboard/index.html")
else:
    print("Target not found in dashboard/index.html")
