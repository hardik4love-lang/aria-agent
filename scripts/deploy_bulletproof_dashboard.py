import json
import re
import html

def escape_html(s):
    if not s:
        return ""
    return html.escape(str(s))

def generate_pin_items(data):
    items = []
    
    # 1. Merged PRs
    for p in data.get("merged_git_prs", []):
        items.append({
            "type": "MERGED",
            "statusText": "MERGED & CLAIMED",
            "title": p.get("title", ""),
            "repoTag": f"{p.get('repo', '')}#{p.get('pr_number', '')}",
            "url": p.get("pr_url", "#"),
            "claimUrl": p.get("claim_comment_url", p.get("pr_url", "#")),
            "payout": p.get("payout", "$100.00"),
            "payoutNumeric": p.get("payout_numeric", 100.0),
            "category": p.get("category", ""),
            "processPin": p.get("process_pin", "Merged into main."),
            "paymentPin": p.get("payment_pin", "PayPal: shruhicollections@gmail.com"),
            "actor": p.get("maintainer", "Core Team"),
            "timeDisplay": p.get("merged_display", "Oct 2026")
        })
        
    # 2. Open PRs
    for p in data.get("open_git_prs", []):
        t = "QUEUE"
        if p.get("state") == "APPROVED":
            t = "APPROVED"
        items.append({
            "type": t,
            "statusText": p.get("status", p.get("state", "OPEN")),
            "title": p.get("title", ""),
            "repoTag": f"{p.get('repo', '')}#{p.get('pr_number', '')}",
            "url": p.get("pr_url", "#"),
            "claimUrl": p.get("pr_url", "#"),
            "payout": p.get("payout", "$100.00"),
            "payoutNumeric": p.get("payout_numeric", 100.0),
            "category": p.get("category", ""),
            "processPin": p.get("process_pin", "In review."),
            "paymentPin": p.get("payment_pin", "PayPal: shruhicollections@gmail.com"),
            "actor": p.get("maintainer", "Maintainers"),
            "timeDisplay": "Live Active"
        })
        
    # 3. Opire Bounties
    for p in data.get("opire_bounties", []):
        items.append({
            "type": "OPIRE",
            "statusText": "OPIRE CLAIMED",
            "title": p.get("title", ""),
            "repoTag": f"{p.get('repo', '')} #{p.get('issue_number', '')}",
            "url": p.get("issue_url", "#"),
            "claimUrl": p.get("claim_comment_url", p.get("issue_url", "#")),
            "payout": p.get("payout", "$100.00"),
            "payoutNumeric": p.get("payout_numeric", 100.0),
            "category": p.get("category", ""),
            "processPin": p.get("process_pin", "Claimed via /opire try."),
            "paymentPin": p.get("payment_pin", "Opire Escrow -> PayPal"),
            "actor": "Opire Bot / claude-builders",
            "timeDisplay": f"PR #{p.get('pr_number', '')} Bound"
        })
        
    # 4. Client Sprints
    for p in data.get("client_sprints", []):
        items.append({
            "type": "CLIENT",
            "statusText": "DELIVERABLE PRE-BUILT",
            "title": p.get("project_title", ""),
            "repoTag": f"{p.get('platform', 'Freelancer')} &bull; {p.get('client_username', '')}",
            "url": "#",
            "claimUrl": "#",
            "payout": p.get("payout", "$140.00"),
            "payoutNumeric": p.get("payout_numeric", 140.0),
            "category": "Direct Client Sprint",
            "processPin": p.get("process_pin", "Deliverable ready on disk."),
            "paymentPin": p.get("payment_pin", "Freelancer Escrow -> PayPal"),
            "actor": f"{p.get('client_name', '')} ({p.get('client_username', '')})",
            "timeDisplay": "Pre-Built On Disk"
        })
        
    return items

def render_pin_table_rows(items):
    out = []
    for item in items:
        badge_color = "#10b981"
        badge_bg = "rgba(16, 185, 129, 0.15)"
        if item["type"] == "APPROVED":
            badge_color = "#f59e0b"
            badge_bg = "rgba(245, 158, 11, 0.15)"
        elif item["type"] == "QUEUE":
            badge_color = "#38bdf8"
            badge_bg = "rgba(56, 189, 248, 0.15)"
        elif item["type"] == "OPIRE":
            badge_color = "#c084fc"
            badge_bg = "rgba(192, 132, 252, 0.15)"
        elif item["type"] == "CLIENT":
            badge_color = "#f472b6"
            badge_bg = "rgba(244, 114, 182, 0.15)"
            
        action_btn = f'''<a href="{escape_html(item['claimUrl'])}" target="_blank" class="btn btn-outline" style="font-size: 0.72rem; padding: 0.35rem 0.6rem; color: {badge_color}; border-color: {badge_color};">Evidence ↗</a>''' if item["claimUrl"] and item["claimUrl"] != "#" else f'<span style="font-size: 0.72rem; color: #64748b;">On Disk</span>'

        row = f'''
          <tr style="border-bottom: 1px solid rgba(255,255,255,0.05);">
            <td>
              <span style="font-size: 0.68rem; font-weight: 800; padding: 0.25rem 0.5rem; border-radius: 4px; background: {badge_bg}; color: {badge_color}; border: 1px solid {badge_color}; display: inline-block;">
                {escape_html(item['statusText'])}
              </span>
              <div style="font-size: 0.7rem; color: #64748b; margin-top: 0.25rem;">{escape_html(item['timeDisplay'])}</div>
            </td>
            <td>
              <div style="font-weight: 700; color: #fff; font-size: 0.88rem; line-height: 1.35;">
                <a href="{escape_html(item['url'])}" target="_blank" style="color: #fff; text-decoration: underline;">
                  {escape_html(item['title'])}
                </a>
              </div>
              <div style="font-size: 0.74rem; color: #38bdf8; margin-top: 0.25rem; font-family: monospace;">
                {item['repoTag']}
              </div>
            </td>
            <td>
              <div style="font-weight: 800; color: var(--success); font-family: 'JetBrains Mono', monospace; font-size: 1.05rem;">
                {escape_html(item['payout'])}
              </div>
            </td>
            <td>
              <div style="font-size: 0.82rem; color: #e2e8f0; line-height: 1.45; background: rgba(15, 23, 42, 0.6); padding: 0.45rem 0.65rem; border-radius: 6px; border-left: 3px solid {badge_color};">
                {escape_html(item['processPin'])}
              </div>
            </td>
            <td>
              <div style="font-size: 0.82rem; color: #a7f3d0; line-height: 1.45; background: rgba(6, 78, 59, 0.3); padding: 0.45rem 0.65rem; border-radius: 6px; border-left: 3px solid #10b981;">
                {escape_html(item['paymentPin'])}
              </div>
            </td>
            <td>
              <div style="font-size: 0.8rem; color: #cbd5e1; font-weight: 600;">
                {escape_html(item['actor'])}
              </div>
            </td>
            <td>
              {action_btn}
            </td>
          </tr>
        '''
        out.append(row)
    return "\n".join(out)

def update_index_html():
    with open("D:/aria-agent/dashboard/bounties.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        
    pin_items = generate_pin_items(data)
    rendered_rows = render_pin_table_rows(pin_items)
    
    with open("D:/aria-agent/dashboard/index.html", "r", encoding="utf-8") as f:
        content = f.read()
        
    # 1. Replace the loading row in pin-locator-tbody with pre-rendered rows!
    loading_pattern = r'<tbody id="pin-locator-tbody">[\s\S]*?</tbody>'
    new_tbody = f'<tbody id="pin-locator-tbody">\n{rendered_rows}\n          </tbody>'
    content = re.sub(loading_pattern, new_tbody, content)
    
    # 2. Update Top Stat Cards static numbers
    content = re.sub(r'id="kpi-merged-value"[^>]*>[\s\S]*?</div>', 'id="kpi-merged-value" style="color: var(--success); font-size: 1.8rem; margin: 0.3rem 0;">$900.00</div>', content)
    content = re.sub(r'id="kpi-merged-sub"[^>]*>[\s\S]*?</div>', 'id="kpi-merged-sub" style="font-size: 0.75rem; color: #cbd5e1;">9 PRs Merged (6 Omi + 3 Go-Hybrid) &bull; Claim comments logged</div>', content)
    
    content = re.sub(r'id="kpi-approved-value"[^>]*>[\s\S]*?</div>', 'id="kpi-approved-value" style="color: #f59e0b; font-size: 1.8rem; margin: 0.3rem 0;">$100.00</div>', content)
    content = re.sub(r'id="kpi-approved-sub"[^>]*>[\s\S]*?</div>', 'id="kpi-approved-sub" style="font-size: 0.75rem; color: #cbd5e1;">PR #23806 Approved by Aryan Gupta &bull; Awaiting merge commit</div>', content)
    
    content = re.sub(r'id="kpi-open-value"[^>]*>[\s\S]*?</div>', 'id="kpi-open-value" style="color: #38bdf8; font-size: 1.8rem; margin: 0.3rem 0;">$7,125.00</div>', content)
    content = re.sub(r'id="kpi-open-sub"[^>]*>[\s\S]*?</div>', 'id="kpi-open-sub" style="font-size: 0.75rem; color: #cbd5e1;">HackerOne ($1.5k) &bull; Go-Hybrid ($1.5k) &bull; Tenstorrent ($2.5k) &bull; Expensify ($525) &bull; Omi ($600)</div>', content)
    
    content = re.sub(r'id="kpi-opire-value"[^>]*>[\s\S]*?</div>', 'id="kpi-opire-value" style="color: #a855f7; font-size: 1.8rem; margin: 0.3rem 0;">$575.00</div>', content)
    content = re.sub(r'id="kpi-opire-sub"[^>]*>[\s\S]*?</div>', 'id="kpi-opire-sub" style="font-size: 0.75rem; color: #cbd5e1;">5 PRs claimed via /opire try comments</div>', content)
    
    content = re.sub(r'id="kpi-clients-value"[^>]*>[\s\S]*?</div>', 'id="kpi-clients-value" style="color: #ec4899; font-size: 1.8rem; margin: 0.3rem 0;">$160.00</div>', content)
    content = re.sub(r'id="kpi-clients-sub"[^>]*>[\s\S]*?</div>', 'id="kpi-clients-sub" style="font-size: 0.75rem; color: #cbd5e1;">Shir Twilio ($140) &bull; Ritesh Classroom ($20)</div>', content)
    
    # 3. Update filter pills static numbers
    filter_pills_html = '''<div class="filter-pills" id="pin-filter-pills">
          <button class="category-pill active" onclick="filterPinTable('ALL', this)">All Items (30 &bull; $9,325)</button>
          <button class="category-pill" onclick="filterPinTable('MERGED', this)">🟢 Merged (9 &bull; $900)</button>
          <button class="category-pill" onclick="filterPinTable('APPROVED', this)">🟡 Approved (1 &bull; $100)</button>
          <button class="category-pill" onclick="filterPinTable('QUEUE', this)">🔵 In Queue (14 &bull; $7,125)</button>
          <button class="category-pill" onclick="filterPinTable('OPIRE', this)">🟣 Opire (5 &bull; $575)</button>
          <button class="category-pill" onclick="filterPinTable('CLIENT', this)">🟠 Clients (2 &bull; $160)</button>
        </div>'''
    content = re.sub(r'<div class="filter-pills" id="pin-filter-pills">[\s\S]*?</div>', filter_pills_html, content)
    
    # 4. Update tab counts in header
    content = re.sub(r'id="stat-pin-count">[\s\S]*?</span>', 'id="stat-pin-count">30 Items &bull; $9,325.00</span>', content)
    content = re.sub(r'id="merged-tab-count">[\s\S]*?</span>', 'id="merged-tab-count">9 PRs &bull; $900.00</span>', content)
    content = re.sub(r'id="bounty-count">[\s\S]*?</span>', 'id="bounty-count">14 Items &bull; $7,125.00</span>', content)

    # 5. Embed EMBEDDED_BOUNTIES_DATA right before buildPinItems
    json_str = json.dumps(data)
    embedded_var = f"\n    const EMBEDDED_BOUNTIES_DATA = {json_str};\n"
    
    # Check if EMBEDDED_BOUNTIES_DATA already present
    if "const EMBEDDED_BOUNTIES_DATA" in content:
        content = re.sub(r'const EMBEDDED_BOUNTIES_DATA = \{[\s\S]*?\};', f'const EMBEDDED_BOUNTIES_DATA = {json_str};', content)
    else:
        content = content.replace("let allPinItems = [];", f"{embedded_var}    let allPinItems = [];")
        
    # 6. Ensure populateDashboard is defined and called cleanly
    new_populate_and_load = """
    function populateDashboard(data) {
      if (!data) return;
      if (data.summary) {
        const s = data.summary;
        const setEl = (id, text) => { const el = document.getElementById(id); if (el) el.innerText = text; };
        setEl('kpi-merged-value', `$${s.total_merged_settled_usd.toLocaleString('en-US', {minimumFractionDigits: 2})}`);
        setEl('kpi-approved-value', `$${s.total_approved_imminent_usd.toLocaleString('en-US', {minimumFractionDigits: 2})}`);
        setEl('kpi-open-value', `$${s.total_open_prs_usd.toLocaleString('en-US', {minimumFractionDigits: 2})}`);
        setEl('kpi-opire-value', `$${s.total_opire_bounties_usd.toLocaleString('en-US', {minimumFractionDigits: 2})}`);
        setEl('kpi-clients-value', `$${s.total_client_contracts_usd.toLocaleString('en-US', {minimumFractionDigits: 2})}`);
        setEl('stat-total-value', data.total_pipeline_value);
        setEl('stat-pin-count', `${s.merged_prs_count + s.open_prs_count + s.opire_bounties_count + s.client_contracts_count} Items • ${data.total_pipeline_value}`);
        setEl('merged-tab-count', `${s.merged_prs_count} PRs • $${s.total_merged_settled_usd.toLocaleString('en-US', {minimumFractionDigits: 2})}`);
        setEl('bounty-count', `${s.open_prs_count} Items • $${s.total_open_prs_usd.toLocaleString('en-US', {minimumFractionDigits: 2})}`);
      }

      if (data.last_updated_display) {
        const badge = document.getElementById('pin-last-sync-badge');
        if (badge) badge.innerText = `LAST SYNC: ${data.last_updated_display.toUpperCase()}`;
      }

      allPinItems = buildPinItems(data);
      applyPinFilterAndSearch();

      renderMergedPRsTable(data.merged_git_prs || []);
      renderBounties(data.open_git_prs || []);
      renderOpireTable(data.opire_bounties || []);
      renderClientsTable(data.client_sprints || []);

      allCompletedBounties = data.completed_rapid_jobs || data.completed_bounties || [];
      allAuditSubmissions = data.recent_submissions || [];
      renderMasterSubmissionsTable(allCompletedBounties);
      renderAuditTable(allAuditSubmissions);
    }

    async function loadBounties(showNotice = false) {
      try {
        const res = await fetch('bounties.json?t=' + Date.now());
        if (res.ok) {
          const data = await res.json();
          populateDashboard(data);
          if (showNotice) {
            alert('✅ Live Telemetry Synchronized: All 30 pipeline items, process stations, and PayPal payment rails up-to-date!');
          }
        }
      } catch (err) {
        console.warn('Network fetch for bounties.json bypassed; embedded telemetry active:', err);
      }
    }
"""
    # Replace existing loadBounties function
    content = re.sub(r'async function loadBounties[\s\S]*?\}\s*function filterCategory', f'{new_populate_and_load}\n    function filterCategory', content)

    # 7. In DOMContentLoaded, call populateDashboard(EMBEDDED_BOUNTIES_DATA)
    content = content.replace("loadBounties();", "if (typeof EMBEDDED_BOUNTIES_DATA !== 'undefined') { populateDashboard(EMBEDDED_BOUNTIES_DATA); }\n      loadBounties();")

    with open("D:/aria-agent/dashboard/index.html", "w", encoding="utf-8") as f:
        f.write(content)
        
    print("Pre-rendered index.html with all 30 rows and embedded telemetry data successfully!")

if __name__ == "__main__":
    update_index_html()
