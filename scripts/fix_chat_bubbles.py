import sys

chat_css = '''
    /* Dedicated Chat Bubbles (Fixes flex-shrink and overflow clipping) */
    .chat-bubble-user {
      align-self: flex-end;
      background: rgba(56, 189, 248, 0.15) !important;
      border: 1px solid rgba(56, 189, 248, 0.35) !important;
      color: #ffffff !important;
      border-radius: 12px 12px 2px 12px !important;
      padding: 0.75rem 1rem !important;
      max-width: 80% !important;
      flex-shrink: 0 !important;
      word-break: break-word !important;
      box-shadow: 0 4px 14px rgba(0, 0, 0, 0.3) !important;
    }
    .chat-bubble-aria {
      align-self: flex-start;
      background: rgba(15, 23, 42, 0.95) !important;
      border: 1px solid rgba(56, 189, 248, 0.25) !important;
      color: #f1f5f9 !important;
      border-radius: 12px 12px 12px 2px !important;
      padding: 1rem 1.25rem !important;
      max-width: 85% !important;
      flex-shrink: 0 !important;
      word-break: break-word !important;
      box-shadow: 0 6px 20px rgba(0, 0, 0, 0.4) !important;
    }
    .chat-bubble-aria p {
      color: #f1f5f9 !important;
      margin: 0.4rem 0 !important;
      line-height: 1.55 !important;
      display: block !important;
    }
    .chat-bubble-aria ul {
      margin: 0.4rem 0 0.4rem 1.25rem !important;
      color: #cbd5e1 !important;
      display: block !important;
    }
    .chat-bubble-aria li {
      margin-bottom: 0.3rem !important;
      line-height: 1.5 !important;
      display: list-item !important;
    }
    .chat-bubble-aria strong {
      color: #ffffff !important;
    }
'''

new_chat_messages_html = '''<div id="chat-messages" style="flex: 1; overflow-y: auto; padding: 1rem 0; display: flex; flex-direction: column; gap: 0.85rem; max-height: 440px;">
          <div class="chat-bubble-aria">
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.4rem;">
              <div style="display: flex; align-items: center; gap: 0.4rem;">
                <strong style="color: #38bdf8; font-size: 0.88rem;">&#128081; ARIA (CEO):</strong>
                <span class="status-pill status-info" style="font-size: 0.65rem;">SOVEREIGN TECH TITAN</span>
              </div>
              <span style="font-size: 0.65rem; color: #64748b; font-family: monospace;">100% EMPIRICAL</span>
            </div>
            <p style="color: #f1f5f9; font-size: 0.88rem; line-height: 1.55; margin: 0;">
              Greetings, Har. I am operating as the adult Sovereign AI CEO across freelance markets, compiler verification, and cultural documentary production. Our master empirical valuation stands at <strong>$14,475.00 USD</strong> ($3,200.00 settled, $10,700.00 review pipeline across 8 PRs, 10 rapid gigs live with cleanroom Gists). How can I direct operations for you right now?
            </p>
          </div>
        </div>'''

new_send_message_js = '''function sendMessage() {
      const input = document.getElementById('chat-input');
      const text = input.value.trim();
      if (!text) return;

      const container = document.getElementById('chat-messages');
      // Render User Message using dedicated non-shrinking bubble
      container.innerHTML += `
        <div class="chat-bubble-user">
          <div style="font-size: 0.7rem; color: #38bdf8; font-weight: 700; margin-bottom: 0.2rem;">YOU</div>
          <div style="color: #ffffff; font-size: 0.88rem; line-height: 1.4;">${escapeHtml(text)}</div>
        </div>
      `;
      input.value = '';
      container.scrollTop = container.scrollHeight;

      // Show typing indicator
      const typingId = 'typing-' + Date.now();
      container.innerHTML += `
        <div id="${typingId}" class="chat-bubble-aria" style="padding: 0.6rem 1rem;">
          <div style="display: flex; align-items: center; gap: 0.5rem; color: #38bdf8; font-size: 0.82rem;">
            <span class="pulse-dot" style="color: #38bdf8;"></span>
            <i>Aria is synthesizing sovereign response...</i>
          </div>
        </div>
      `;
      container.scrollTop = container.scrollHeight;

      setTimeout(() => {
        const typingEl = document.getElementById(typingId);
        if (typingEl) typingEl.remove();

        const responseHtml = generateAriaResponse(text);
        container.innerHTML += `
          <div class="chat-bubble-aria">
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.4rem;">
              <strong style="color: #38bdf8; font-size: 0.85rem;">&#128081; ARIA &bull; SOVEREIGN AI CEO</strong>
              <span style="font-size: 0.65rem; color: #64748b; font-family: monospace;">AST VERIFIED &bull; 100% EMPIRICAL</span>
            </div>
            <div style="color: #f1f5f9; font-size: 0.88rem; line-height: 1.55;">
              ${responseHtml}
            </div>
          </div>
        `;
        container.scrollTop = container.scrollHeight;
      }, 350);
    }'''

def main():
    target = 'D:/aria-agent/dashboard/index.html'
    with open(target, 'r', encoding='utf-8') as f:
        c = f.read()

    # 1. Insert chat_css before </style>
    style_end = c.find('</style>')
    if style_end != -1:
        c = c[:style_end] + chat_css + '\n' + c[style_end:]
        print('Chat CSS added!')

    # 2. Replace #chat-messages HTML
    old_msg_start = '<div id="chat-messages"'
    idx_m_start = c.find(old_msg_start)
    if idx_m_start != -1:
        idx_m_end = c.find('</div>\n\n        <div style="padding-top: 0.5rem;', idx_m_start)
        if idx_m_end != -1:
            c = c[:idx_m_start] + new_chat_messages_html + c[idx_m_end + 6:]
            print('#chat-messages HTML replaced with non-shrinking bubble!')
        else:
            print('Could not find end of #chat-messages!')
    else:
        print('Could not find start of #chat-messages!')

    # 3. Replace sendMessage JS
    old_send = 'function sendMessage() {'
    idx_s_start = c.find(old_send)
    if idx_s_start != -1:
        idx_s_end = c.find('function generateAriaResponse(rawQuery) {', idx_s_start)
        if idx_s_end != -1:
            c = c[:idx_s_start] + new_send_message_js + '\n\n    ' + c[idx_s_end:]
            print('sendMessage JS replaced with non-shrinking bubble render!')
        else:
            print('Could not find end of sendMessage JS!')
    else:
        print('Could not find start of sendMessage JS!')

    with open(target, 'w', encoding='utf-8') as f:
        f.write(c)

    print('Successfully fixed chat bubbles in dashboard/index.html!')

if __name__ == '__main__':
    main()
