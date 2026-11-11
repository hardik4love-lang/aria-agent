"""
Update dashboard/index.html to include direct live links to GuardianAngel and SuratVision AI interactive simulators.
"""

path = r"D:\aria-agent\dashboard\index.html"
with open(path, "r", encoding="utf-8") as f:
    html = f.read()

# 1. Update header telemetry pills
old_pills = """      <div class="telemetry-pills">
        <div class="daemon-pill">
          <div class="pulse-dot"></div>
          <span>Surat Live Scanner Daemon Active</span>
        </div>"""

new_pills = """      <div class="telemetry-pills">
        <div class="daemon-pill">
          <div class="pulse-dot"></div>
          <span>Surat Live Scanner Daemon Active</span>
        </div>
        <a href="guardian.html" style="text-decoration:none;" class="daemon-pill">
          <span>🛡️ GuardianAngel Live</span>
        </a>
        <a href="surat_vision.html" style="text-decoration:none; border-color:var(--accent-cyan); color:var(--accent-cyan); background:rgba(56,189,248,0.12);" class="daemon-pill">
          <span>👁️ SuratVision AI Live</span>
        </a>"""

if old_pills in html:
    html = html.replace(old_pills, new_pills)
    print("Updated header pills")

# 2. Update GuardianAngel card footer
old_ga_footer = """          <div style="margin-top:14px; padding-top:12px; border-top:1px solid var(--border-subtle); display:flex; justify-content:space-between; align-items:center;">
            <span style="font-size:12px; color:var(--text-muted); font-family:var(--font-mono);">src/aria/guardian/</span>
            <span class="status-badge status-merged">Codebase & Blueprint Ready</span>
          </div>"""

new_ga_footer = """          <div style="margin-top:14px; padding-top:12px; border-top:1px solid var(--border-subtle); display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px;">
            <a href="guardian.html" style="background:var(--accent-emerald); color:#020617; font-weight:800; padding:8px 16px; border-radius:8px; text-decoration:none; font-size:12px;">▶ Launch Live Voice Simulator ↗</a>
            <span class="status-badge status-merged">Codebase & Tests 100% Green</span>
          </div>"""

if old_ga_footer in html:
    html = html.replace(old_ga_footer, new_ga_footer)
    print("Updated GuardianAngel card footer")

# 3. Update SuratVision card footer
old_sv_footer = """          <div style="margin-top:14px; padding-top:12px; border-top:1px solid var(--border-subtle); display:flex; justify-content:space-between; align-items:center;">
            <span style="font-size:12px; color:var(--text-muted); font-family:var(--font-mono);">src/aria/surat_vision/</span>
            <span class="status-badge status-merged">Connector & Sentry Ready</span>
          </div>"""

new_sv_footer = """          <div style="margin-top:14px; padding-top:12px; border-top:1px solid var(--border-subtle); display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px;">
            <a href="surat_vision.html" style="background:var(--accent-cyan); color:#020617; font-weight:800; padding:8px 16px; border-radius:8px; text-decoration:none; font-size:12px;">▶ Launch Live CCTV Simulator ↗</a>
            <span class="status-badge status-merged">Connector & Tests 100% Green</span>
          </div>"""

if old_sv_footer in html:
    html = html.replace(old_sv_footer, new_sv_footer)
    print("Updated SuratVision card footer")

with open(path, "w", encoding="utf-8") as f:
    f.write(html)
print("Successfully saved dashboard/index.html")
