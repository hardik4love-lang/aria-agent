import sys

def main():
    target = 'D:/aria-agent/dashboard/index.html'
    with open(target, 'r', encoding='utf-8') as f:
        c = f.read()

    # 1. Update hero buttons
    old_actions_start = '<div class="identity-actions">'
    old_actions_end = '</div>\n      </div>\n    </div>'
    
    idx_act_start = c.find(old_actions_start)
    idx_act_end = c.find(old_actions_end, idx_act_start)
    
    if idx_act_start != -1 and idx_act_end != -1:
        new_actions = '''<div class="identity-actions">
          <button onclick="document.getElementById('skills-arsenal').scrollIntoView({behavior:'smooth'})" class="btn btn-success" style="font-size: 0.85rem; padding: 0.45rem 1.1rem; font-weight: 700; box-shadow: 0 0 15px rgba(16, 185, 129, 0.4);">
            ⚡ Test Live Skills (Code, Security, Swarm) &darr;
          </button>
          <button onclick="switchSkillTab('skill-media'); document.getElementById('skills-arsenal').scrollIntoView({behavior:'smooth'});" class="btn btn-outline" style="font-size: 0.85rem; padding: 0.45rem 1rem; border-color: #a855f7; color: #a855f7;">
            🎬 Watch 4K Documentary &amp; Hear Voice
          </button>
          <button onclick="openHireModal()" class="btn btn-outline" style="font-size: 0.85rem; padding: 0.45rem 1rem; border-color: #38bdf8; color: #38bdf8;">
            📄 Hire Aria / SOW ($25 - $250)
          </button>
          <a href="https://github.com/hardik4love-lang/aria-agent" target="_blank" class="btn" style="font-size: 0.85rem; padding: 0.45rem 1rem; background: rgba(255,255,255,0.06);">
            📦 GitHub Repo
          </a>'''
        c = c[:idx_act_start] + new_actions + c[idx_act_end:]
        print('Hero actions updated!')
    else:
        print('Could not find hero actions!')

    # 2. Update DOMContentLoaded to activate Superwoman Titan and load preset
    old_dom = "window.addEventListener('DOMContentLoaded', () => {\n      initRadar();\n      loadBounties();\n    });"
    new_dom = """window.addEventListener('DOMContentLoaded', () => {
      initRadar();
      loadBounties();
      switchAriaMode('titan');
      loadCodePreset('hydration');
    });"""
    if old_dom in c:
        c = c.replace(old_dom, new_dom, 1)
        print('DOMContentLoaded updated to default to Superwoman Titan!')
    else:
        print('Could not find old DOMContentLoaded!')

    with open(target, 'w', encoding='utf-8') as f:
        f.write(c)

    print('Successfully tuned dashboard/index.html!')

if __name__ == '__main__':
    main()
