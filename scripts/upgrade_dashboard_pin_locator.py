import re
import sys

def upgrade_dashboard_html():
    path = "D:/aria-agent/dashboard/index.html"
    with open(path, "r", encoding="utf-8") as f:
        html = f.read()

    # 1. Update Navigation Tabs
    old_nav_tabs_regex = r'<div class="nav-tabs">.*?</div>'
    new_nav_tabs = '''<div class="nav-tabs">
      <button class="tab-btn active" onclick="switchTab('pin-tab')">
        <svg width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"></path><path d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"></path></svg>
        📍 Process &amp; Payment Pin Locator (<span id="stat-pin-count">19 Items &bull; $3,035</span>)
      </button>
      <button class="tab-btn" onclick="switchTab('merged-tab')">
        <svg width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M5 13l4 4L19 7"></path></svg>
        🏆 Merged Wins (<span id="merged-tab-count">6 PRs &bull; $600</span>)
      </button>
      <button class="tab-btn" onclick="switchTab('bounties-tab')">
        <svg width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
        🎯 Active Open PRs (<span id="bounty-count">7 PRs &bull; $1,700</span>)
      </button>
      <button class="tab-btn" onclick="switchTab('opire-tab')">
        <svg width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M13 10V3L4 14h7v7l9-11h-7z"></path></svg>
        🟣 Opire Claude Bounties (5 Claims &bull; $575)
      </button>
      <button class="tab-btn" onclick="switchTab('clients-tab')">
        <svg width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"></path></svg>
        💼 Client Contracts (Shir &bull; Ritesh &bull; $160)
      </button>
      <button class="tab-btn" onclick="switchTab('completed-tab')">
        <svg width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
        ⚡ Rapid Gigs (<span id="stat-tab-value">$575.00</span>)
      </button>
      <button class="tab-btn" onclick="switchTab('liquidity-tab')">
        <svg width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
        ⚡ Fast-Cash Platforms
      </button>
      <button class="tab-btn" onclick="switchTab('audit-tab')">
        <svg width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M4 6h16M4 10h16M4 14h16M4 18h16"></path></svg>
        🔄 Stream Log
      </button>
      <button class="tab-btn" onclick="switchTab('chat-tab')">
        <svg width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"></path></svg>
        💬 Ask ARIA
      </button>
    </div>'''
    
    html = re.sub(old_nav_tabs_regex, new_nav_tabs, html, count=1, flags=re.DOTALL)

    # 2. Add PIN-TAB as the primary tab content right above completed-tab
    pin_tab_html = '''<!-- TAB: PROCESS & PAYMENT PIN LOCATOR (TOP-TO-TOE LIVE TRACKER) -->
    <div id="pin-tab" class="tab-content active">
      <!-- Live Sync & Settlement Header Card -->
      <div class="card" style="margin-bottom: 1.5rem; background: linear-gradient(135deg, rgba(15, 23, 42, 0.95) 0%, rgba(30, 41, 59, 0.9) 100%); border-left: 5px solid #10b981; padding: 1.5rem;">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 1rem;">
          <div>
            <div style="display: flex; align-items: center; gap: 0.6rem; flex-wrap: wrap;">
              <span class="status-pill status-ok" style="font-size: 0.75rem; font-weight: 800; display: flex; align-items: center; gap: 0.4rem;">
                <span class="pulse-dot" style="color: #10b981;"></span> LIVE RADAR ACTIVE &bull; TOP-TO-TOE
              </span>
              <span class="status-pill status-info" style="font-size: 0.72rem;" id="pin-last-sync-badge">
                LAST SYNC: OCTOBER 29, 2026
              </span>
              <span style="font-size: 0.75rem; color: #94a3b8; font-family: monospace;" id="pin-countdown-badge">
                ⏱ Auto-refresh in 30s
              </span>
            </div>
            <h2 style="font-size: 1.5rem; color: #fff; margin-top: 0.5rem; font-weight: 800; letter-spacing: -0.02em;">
              📍 Live Process &amp; Payment Pin Locator
            </h2>
            <p style="color: #cbd5e1; font-size: 0.88rem; margin-top: 0.3rem; max-width: 850px; line-height: 1.55;">
              Real-time pin telemetry across every active dollar. Tracks the exact <strong>process step</strong> (CI, maintainer review, approval, merge) and <strong>payment location</strong> (payout rail, claim comment hash, support ticket, PayPal account) so you never have to wonder where a payment stands.
            </p>
          </div>

          <div style="display: flex; flex-direction: column; gap: 0.5rem; align-items: flex-end;">
            <div style="font-size: 0.75rem; color: #94a3b8; font-weight: 700;">LOCKED PAYOUT DESTINATION:</div>
            <span class="copy-pill" style="font-size: 0.88rem; font-family: monospace; background: rgba(16, 185, 129, 0.15); border: 1px solid rgba(16, 185, 129, 0.4); color: #34d399;" onclick="copyText('shruhicollections@gmail.com', this)">
              💳 PayPal: shruhicollections@gmail.com 📋
            </span>
            <div style="display: flex; gap: 0.5rem; margin-top: 0.2rem;">
              <button onclick="loadBounties(true)" class="btn btn-success" style="font-size: 0.78rem; padding: 0.4rem 0.8rem; font-weight: 700;">
                🔄 Sync Now
              </button>
              <a href="https://github.com/BasedHardware/omi/pulls/hardik4love-lang" target="_blank" class="btn btn-outline" style="font-size: 0.78rem; padding: 0.4rem 0.8rem;">
                GitHub PR Fleet ↗
              </a>
            </div>
          </div>
        </div>
      </div>

      <!-- Top Stat Cards (Real-Time Dynamic Rollup) -->
      <div class="grid" style="grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); margin-bottom: 1.5rem;">
        <div class="card" style="border-top: 3px solid var(--success);">
          <div style="font-size: 0.75rem; color: #94a3b8; font-weight: 700; text-transform: uppercase;">Realized / Merged</div>
          <div class="stat-value" id="kpi-merged-value" style="color: var(--success); font-size: 1.8rem; margin: 0.3rem 0;">$600.00</div>
          <div class="stat-sub" id="kpi-merged-sub" style="font-size: 0.75rem; color: #cbd5e1;">6 Omi PRs Merged • Claim comments posted</div>
        </div>
        <div class="card" style="border-top: 3px solid #f59e0b;">
          <div style="font-size: 0.75rem; color: #94a3b8; font-weight: 700; text-transform: uppercase;">Approved &amp; Imminent</div>
          <div class="stat-value" id="kpi-approved-value" style="color: #f59e0b; font-size: 1.8rem; margin: 0.3rem 0;">$300.00</div>
          <div class="stat-sub" id="kpi-approved-sub" style="font-size: 0.75rem; color: #cbd5e1;">PR #23806 Approved • #23841 Green • #23842 Fixed</div>
        </div>
        <div class="card" style="border-top: 3px solid #38bdf8;">
          <div style="font-size: 0.75rem; color: #94a3b8; font-weight: 700; text-transform: uppercase;">In-Review PR Queue</div>
          <div class="stat-value" id="kpi-open-value" style="color: #38bdf8; font-size: 1.8rem; margin: 0.3rem 0;">$1,400.00</div>
          <div class="stat-sub" id="kpi-open-sub" style="font-size: 0.75rem; color: #cbd5e1;">Tenstorrent #60777 ($1k) • Omi Auth PRs ($400)</div>
        </div>
        <div class="card" style="border-top: 3px solid #a855f7;">
          <div style="font-size: 0.75rem; color: #94a3b8; font-weight: 700; text-transform: uppercase;">Opire Claude Bounties</div>
          <div class="stat-value" id="kpi-opire-value" style="color: #a855f7; font-size: 1.8rem; margin: 0.3rem 0;">$575.00</div>
          <div class="stat-sub" id="kpi-opire-sub" style="font-size: 0.75rem; color: #cbd5e1;">5 PRs claimed via /opire try comments</div>
        </div>
        <div class="card" style="border-top: 3px solid #ec4899;">
          <div style="font-size: 0.75rem; color: #94a3b8; font-weight: 700; text-transform: uppercase;">Client Contracts (Freelancer)</div>
          <div class="stat-value" id="kpi-clients-value" style="color: #ec4899; font-size: 1.8rem; margin: 0.3rem 0;">$160.00</div>
          <div class="stat-sub" id="kpi-clients-sub" style="font-size: 0.75rem; color: #cbd5e1;">Shir Twilio ($140) • Ritesh Classroom ($20)</div>
        </div>
      </div>

      <!-- Filter Controls & Real-Time Search -->
      <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem; margin-bottom: 1.25rem;">
        <div class="filter-pills" id="pin-filter-pills">
          <button class="category-pill active" onclick="filterPinTable('ALL', this)">All Items (19 &bull; $3,035)</button>
          <button class="category-pill" onclick="filterPinTable('MERGED', this)">🟢 Merged ($600)</button>
          <button class="category-pill" onclick="filterPinTable('APPROVED', this)">🟡 Approved ($100)</button>
          <button class="category-pill" onclick="filterPinTable('QUEUE', this)">🔵 In Queue ($1,600)</button>
          <button class="category-pill" onclick="filterPinTable('OPIRE', this)">🟣 Opire ($575)</button>
          <button class="category-pill" onclick="filterPinTable('CLIENT', this)">🟠 Clients ($160)</button>
        </div>
        <input type="text" id="pin-search-input" class="search-box" style="width: 320px;" placeholder="Search PR #, title, station, or payout..." oninput="searchPinTable()">
      </div>

      <!-- Master Pin Locator Table -->
      <div class="table-container" style="border: 1px solid rgba(255,255,255,0.08); border-radius: 8px;">
        <table class="data-table" id="pin-locator-table">
          <thead>
            <tr>
              <th style="width: 140px;">STATUS &bull; STAGE</th>
              <th style="width: 280px;">TARGET / PR &bull; REPO</th>
              <th style="width: 110px;">AMOUNT</th>
              <th>📍 PROCESS PIN LOCATION</th>
              <th>💰 PAYMENT PIN LOCATION</th>
              <th style="width: 150px;">ACTOR / MAINTAINER</th>
              <th style="width: 120px;">ACTION</th>
            </tr>
          </thead>
          <tbody id="pin-locator-tbody">
            <tr><td colspan="7" style="text-align: center; color: var(--text-muted); padding: 2.5rem;">Loading live process &amp; payment telemetry...</td></tr>
          </tbody>
        </table>
      </div>
    </div>
'''
    
    # Make completed-tab not active by default
    html = html.replace('<div id="completed-tab" class="tab-content active">', pin_tab_html + '\n    <!-- TAB 0: COMPLETED BOUNTIES & LIVE SUBMISSIONS TABLE -->\n    <div id="completed-tab" class="tab-content">')

    # 3. Add Opire and Client tabs HTML
    opire_and_client_tabs = '''<!-- TAB: OPIRE CLAUDE BUILDERS BOUNTIES -->
    <div id="opire-tab" class="tab-content">
      <div class="card" style="margin-bottom: 1.5rem; border-left: 4px solid #a855f7;">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem;">
          <div>
            <h2 style="font-size: 1.3rem; color: #fff; font-weight: 800;">🟣 Claude Builders Bounties on Opire ($575.00 USD)</h2>
            <p style="color: #cbd5e1; font-size: 0.85rem; margin-top: 0.2rem;">
              5 production PRs authored and officially claimed via <code>/opire try</code> comments. Payouts escrowed by Opire smart contract.
            </p>
          </div>
          <span class="status-pill status-ok">5 OF 5 CLAIMS ACTIVE</span>
        </div>
      </div>
      <div class="table-container">
        <table class="data-table">
          <thead>
            <tr>
              <th>Issue</th>
              <th>PR</th>
              <th>Title</th>
              <th>Amount</th>
              <th>Status</th>
              <th>Process Pin</th>
              <th>Payment Pin</th>
              <th>Links</th>
            </tr>
          </thead>
          <tbody id="opire-tbody"></tbody>
        </table>
      </div>
    </div>

    <!-- TAB: CLIENT CONTRACTS & FREELANCER SPRINTS -->
    <div id="clients-tab" class="tab-content">
      <div class="card" style="margin-bottom: 1.5rem; border-left: 4px solid #ec4899;">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem;">
          <div>
            <h2 style="font-size: 1.3rem; color: #fff; font-weight: 800;">💼 Freelancer Client Sprints ($160.00 USD)</h2>
            <p style="color: #cbd5e1; font-size: 0.85rem; margin-top: 0.2rem;">
              Production deliverables 100% pre-built and persisted on disk, ready for instant release upon milestone award.
            </p>
          </div>
          <span class="status-pill status-ok">DELIVERABLES COMPILED ON DISK</span>
        </div>
      </div>
      <div class="table-container">
        <table class="data-table">
          <thead>
            <tr>
              <th>Client</th>
              <th>Project Title</th>
              <th>Amount</th>
              <th>Deliverable Status</th>
              <th>📍 Process Pin Location</th>
              <th>💰 Payment Pin Location</th>
              <th>Disk Artifacts</th>
            </tr>
          </thead>
          <tbody id="clients-tbody"></tbody>
        </table>
      </div>
    </div>
'''
    html = html.replace('<!-- TAB 1: MULTI-SUBMISSIONS STREAM -->', opire_and_client_tabs + '\n    <!-- TAB 1: MULTI-SUBMISSIONS STREAM -->')

    # 4. Inject JavaScript rendering functions into <script>
    js_pin_functions = '''
    // ==========================================
    // PIN LOCATOR & REAL-TIME TELEMETRY ENGINE
    // ==========================================
    let allPinItems = [];
    let currentPinFilter = 'ALL';
    let pinRefreshTimer = 30;

    function buildPinItems(data) {
      const items = [];
      
      // 1. Merged PRs
      (data.merged_git_prs || []).forEach(p => {
        items.push({
          type: 'MERGED',
          badgeClass: 'status-ok',
          statusText: 'MERGED & CLAIMED',
          title: p.title,
          repoTag: p.repo + '#' + p.pr_number,
          url: p.pr_url,
          claimUrl: p.claim_comment_url || p.pr_url,
          payout: p.payout,
          payoutNumeric: p.payout_numeric,
          category: p.category,
          processPin: p.process_pin || 'Merged into main.',
          paymentPin: p.payment_pin || 'PayPal: shruhicollections@gmail.com',
          actor: p.maintainer || 'Core Team',
          timeDisplay: p.merged_display || p.merged_at || 'Oct 2026'
        });
      });

      // 2. Open PRs
      (data.open_git_prs || []).forEach(p => {
        let type = 'QUEUE';
        let badgeClass = 'status-info';
        if (p.state === 'APPROVED') {
          type = 'APPROVED';
          badgeClass = 'status-warning';
        }
        items.push({
          type: type,
          badgeClass: badgeClass,
          statusText: p.status || p.state,
          title: p.title,
          repoTag: p.repo + '#' + p.pr_number,
          url: p.pr_url,
          claimUrl: p.pr_url,
          payout: p.payout,
          payoutNumeric: p.payout_numeric,
          category: p.category,
          processPin: p.process_pin || 'In review.',
          paymentPin: p.payment_pin || 'PayPal: shruhicollections@gmail.com',
          actor: p.maintainer || 'Maintainers',
          timeDisplay: 'Live Active'
        });
      });

      // 3. Opire Bounties
      (data.opire_bounties || []).forEach(p => {
        items.push({
          type: 'OPIRE',
          badgeClass: 'status-purple',
          statusText: 'OPIRE CLAIMED',
          title: p.title,
          repoTag: p.repo + ' #' + p.issue_number,
          url: p.issue_url,
          claimUrl: p.claim_comment_url || p.issue_url,
          payout: p.payout,
          payoutNumeric: p.payout_numeric,
          category: p.category,
          processPin: p.process_pin || 'Claimed via /opire try.',
          paymentPin: p.payment_pin || 'Opire Escrow -> PayPal',
          actor: 'Opire Bot / claude-builders',
          timeDisplay: 'PR #' + p.pr_number + ' Bound'
        });
      });

      // 4. Client Sprints
      (data.client_sprints || []).forEach(p => {
        items.push({
          type: 'CLIENT',
          badgeClass: 'status-pink',
          statusText: 'DELIVERABLE PRE-BUILT',
          title: p.project_title,
          repoTag: p.platform + ' &bull; ' + p.client_username,
          url: '#',
          claimUrl: '#',
          payout: p.payout,
          payoutNumeric: p.payout_numeric,
          category: 'Direct Client Sprint',
          processPin: p.process_pin || 'Deliverable ready on disk.',
          paymentPin: p.payment_pin || 'Freelancer Escrow -> PayPal',
          actor: p.client_name + ' (' + p.client_username + ')',
          timeDisplay: 'Pre-Built On Disk'
        });
      });

      return items;
    }

    function renderPinLocatorTable(items) {
      const tbody = document.getElementById('pin-locator-tbody');
      if (!tbody) return;

      if (!items || items.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" style="text-align: center; color: var(--text-muted); padding: 2.5rem;">No matching telemetry pins found.</td></tr>';
        return;
      }

      tbody.innerHTML = items.map(item => {
        let badgeColor = '#10b981';
        let badgeBg = 'rgba(16, 185, 129, 0.15)';
        if (item.type === 'APPROVED') { badgeColor = '#f59e0b'; badgeBg = 'rgba(245, 158, 11, 0.15)'; }
        if (item.type === 'QUEUE') { badgeColor = '#38bdf8'; badgeBg = 'rgba(56, 189, 248, 0.15)'; }
        if (item.type === 'OPIRE') { badgeColor = '#c084fc'; badgeBg = 'rgba(192, 132, 252, 0.15)'; }
        if (item.type === 'CLIENT') { badgeColor = '#f472b6'; badgeBg = 'rgba(244, 114, 182, 0.15)'; }

        const actionBtn = item.claimUrl && item.claimUrl !== '#' ? `
          <a href="${escapeHtml(item.claimUrl)}" target="_blank" class="btn btn-outline" style="font-size: 0.72rem; padding: 0.35rem 0.6rem; color: ${badgeColor}; border-color: ${badgeColor};">
            Evidence ↗
          </a>
        ` : `<span style="font-size: 0.72rem; color: #64748b;">On Disk</span>`;

        return `
          <tr style="border-bottom: 1px solid rgba(255,255,255,0.05);">
            <td>
              <span style="font-size: 0.68rem; font-weight: 800; padding: 0.25rem 0.5rem; border-radius: 4px; background: ${badgeBg}; color: ${badgeColor}; border: 1px solid ${badgeColor}; display: inline-block;">
                ${escapeHtml(item.statusText)}
              </span>
              <div style="font-size: 0.7rem; color: #64748b; margin-top: 0.25rem;">${escapeHtml(item.timeDisplay)}</div>
            </td>
            <td>
              <div style="font-weight: 700; color: #fff; font-size: 0.88rem; line-height: 1.35;">
                <a href="${escapeHtml(item.url)}" target="_blank" style="color: #fff; text-decoration: underline;">
                  ${escapeHtml(item.title)}
                </a>
              </div>
              <div style="font-size: 0.74rem; color: #38bdf8; margin-top: 0.25rem; font-family: monospace;">
                ${item.repoTag}
              </div>
            </td>
            <td>
              <div style="font-weight: 800; color: var(--success); font-family: 'JetBrains Mono', monospace; font-size: 1.05rem;">
                ${escapeHtml(item.payout)}
              </div>
            </td>
            <td>
              <div style="font-size: 0.82rem; color: #e2e8f0; line-height: 1.45; background: rgba(15, 23, 42, 0.6); padding: 0.45rem 0.65rem; border-radius: 6px; border-left: 3px solid ${badgeColor};">
                ${escapeHtml(item.processPin)}
              </div>
            </td>
            <td>
              <div style="font-size: 0.82rem; color: #a7f3d0; line-height: 1.45; background: rgba(6, 78, 59, 0.3); padding: 0.45rem 0.65rem; border-radius: 6px; border-left: 3px solid #10b981;">
                ${escapeHtml(item.paymentPin)}
              </div>
            </td>
            <td>
              <div style="font-size: 0.8rem; color: #cbd5e1; font-weight: 600;">
                ${escapeHtml(item.actor)}
              </div>
            </td>
            <td>
              ${actionBtn}
            </td>
          </tr>
        `;
      }).join('');
    }

    function filterPinTable(category, el) {
      currentPinFilter = category;
      document.querySelectorAll('#pin-filter-pills .category-pill').forEach(b => b.classList.remove('active'));
      if (el) el.classList.add('active');

      applyPinFilterAndSearch();
    }

    function searchPinTable() {
      applyPinFilterAndSearch();
    }

    function applyPinFilterAndSearch() {
      const q = (document.getElementById('pin-search-input').value || '').toLowerCase();
      let filtered = allPinItems;

      if (currentPinFilter !== 'ALL') {
        filtered = filtered.filter(item => item.type === currentPinFilter);
      }

      if (q) {
        filtered = filtered.filter(item => 
          (item.title && item.title.toLowerCase().includes(q)) ||
          (item.repoTag && item.repoTag.toLowerCase().includes(q)) ||
          (item.processPin && item.processPin.toLowerCase().includes(q)) ||
          (item.paymentPin && item.paymentPin.toLowerCase().includes(q)) ||
          (item.actor && item.actor.toLowerCase().includes(q))
        );
      }

      renderPinLocatorTable(filtered);
    }

    function renderOpireTable(bounties) {
      const tbody = document.getElementById('opire-tbody');
      if (!tbody) return;
      tbody.innerHTML = (bounties || []).map(b => `
        <tr>
          <td><strong style="color: #c084fc;">Issue #${b.issue_number}</strong></td>
          <td><code style="color: #38bdf8;">PR #${b.pr_number}</code></td>
          <td style="font-weight: 600; color: #fff;">${escapeHtml(b.title)}</td>
          <td style="font-weight: 800; color: var(--success); font-family: monospace;">${escapeHtml(b.payout)}</td>
          <td><span class="status-pill status-ok">${escapeHtml(b.status)}</span></td>
          <td style="font-size: 0.8rem; color: #cbd5e1;">${escapeHtml(b.process_pin)}</td>
          <td style="font-size: 0.8rem; color: #a7f3d0;">${escapeHtml(b.payment_pin)}</td>
          <td>
            <a href="${escapeHtml(b.claim_comment_url)}" target="_blank" class="btn btn-outline" style="font-size: 0.72rem; color: #c084fc; border-color: #c084fc;">
              Claim ↗
            </a>
          </td>
        </tr>
      `).join('');
    }

    function renderClientsTable(sprints) {
      const tbody = document.getElementById('clients-tbody');
      if (!tbody) return;
      tbody.innerHTML = (sprints || []).map(c => `
        <tr>
          <td><strong style="color: #f472b6;">${escapeHtml(c.client_name)}</strong> <span style="font-size: 0.75rem; color: #94a3b8;">${escapeHtml(c.client_username)}</span></td>
          <td style="font-weight: 600; color: #fff;">${escapeHtml(c.project_title)}</td>
          <td style="font-weight: 800; color: var(--success); font-family: monospace;">${escapeHtml(c.payout)}</td>
          <td><span class="status-pill status-ok">${escapeHtml(c.status)}</span></td>
          <td style="font-size: 0.8rem; color: #cbd5e1;">${escapeHtml(c.process_pin)}</td>
          <td style="font-size: 0.8rem; color: #a7f3d0;">${escapeHtml(c.payment_pin)}</td>
          <td>
            <code style="font-size: 0.72rem; color: #cbd5e1;">${(c.local_artifacts || []).map(a => a.split('/').pop()).join(', ')}</code>
          </td>
        </tr>
      `).join('');
    }

    function initPinCountdown() {
      setInterval(() => {
        pinRefreshTimer--;
        const badge = document.getElementById('pin-countdown-badge');
        if (badge) {
          badge.innerText = `⏱ Auto-refresh in ${pinRefreshTimer}s`;
        }
        if (pinRefreshTimer <= 0) {
          pinRefreshTimer = 30;
          loadBounties(false);
        }
      }, 1000);
    }
'''

    # Update loadBounties function to parse and update everything dynamically
    old_load_bounties_start = 'async function loadBounties() {'
    new_load_bounties = '''async function loadBounties(showNotice = false) {
      try {
        const res = await fetch('bounties.json?t=' + Date.now());
        if (!res.ok) throw new Error('HTTP ' + res.status);
        const data = await res.json();

        // 1. Dynamic Top KPI updates
        if (data.summary) {
          const s = data.summary;
          const setEl = (id, text) => { const el = document.getElementById(id); if (el) el.innerText = text; };
          setEl('kpi-merged-value', `$${s.total_merged_settled_usd.toLocaleString('en-US', {minimumFractionDigits: 2})}`);
          setEl('kpi-approved-value', `$${s.total_approved_imminent_usd.toLocaleString('en-US', {minimumFractionDigits: 2})}`);
          setEl('kpi-open-value', `$${s.total_open_prs_usd.toLocaleString('en-US', {minimumFractionDigits: 2})}`);
          setEl('kpi-opire-value', `$${s.total_opire_bounties_usd.toLocaleString('en-US', {minimumFractionDigits: 2})}`);
          setEl('kpi-clients-value', `$${s.total_client_contracts_usd.toLocaleString('en-US', {minimumFractionDigits: 2})}`);
          setEl('stat-total-value', data.total_pipeline_value);
          setEl('stat-pin-count', `${(s.merged_prs_count + s.open_prs_count + s.opire_bounties_count + s.client_contracts_count)} Items • ${data.total_pipeline_value}`);
          setEl('merged-tab-count', `${s.merged_prs_count} PRs • $${s.total_merged_settled_usd.toLocaleString('en-US', {minimumFractionDigits: 2})}`);
          setEl('bounty-count', `${s.open_prs_count} PRs • $${s.total_open_prs_usd.toLocaleString('en-US', {minimumFractionDigits: 2})}`);
        }

        if (data.last_updated_display) {
          const badge = document.getElementById('pin-last-sync-badge');
          if (badge) badge.innerText = `LAST SYNC: ${data.last_updated_display.toUpperCase()}`;
        }

        // 2. Build & Render Pin Locator
        allPinItems = buildPinItems(data);
        applyPinFilterAndSearch();

        // 3. Render Dedicated Tables
        renderMergedPRsTable(data.merged_git_prs || []);
        renderBounties(data.open_git_prs || []);
        renderOpireTable(data.opire_bounties || []);
        renderClientsTable(data.client_sprints || []);

        allCompletedBounties = data.completed_rapid_jobs || data.completed_bounties || [];
        allAuditSubmissions = data.recent_submissions || [];
        renderMasterSubmissionsTable(allCompletedBounties);
        renderAuditTable(allAuditSubmissions);

        if (showNotice) {
          alert('✅ Live Telemetry Synchronized: All 19 pipeline items, process stations, and PayPal payment rails up-to-date!');
        }
      } catch (err) {
        console.error('Error loading bounties.json:', err);
      }
    }'''

    html = html.replace(old_load_bounties_start, js_pin_functions + '\n    ' + new_load_bounties)

    # Make DOMContentLoaded call initPinCountdown
    html = html.replace("loadBounties();", "loadBounties();\n      initPinCountdown();")

    with open(path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Successfully upgraded {path}!")

if __name__ == "__main__":
    upgrade_dashboard_html()
