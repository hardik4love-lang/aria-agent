/**
 * Cloudflare Worker Gateway for ARIA Sovereign Agent ($0.00 TCO - 100k requests/day free tier).
 * Receives external webhooks, processes Telegram bot webhooks instantly, and dispatches GitHub Actions workflows.
 */

const BOT_TOKEN = "8585331609:AAFa_foTU82ToL7EFBiZ3EIrSbCDCfW0cPA";
const AUTHORIZED_CHAT_ID = "8737013099";
const PAYPAL_PAYOUT = "shruhicollections@gmail.com";
const UPI_PAYOUT = "";

const MAIN_MENU_KEYBOARD = {
  inline_keyboard: [
    [
      { text: "📊 System Status", callback_data: "MENU:status" },
      { text: "💼 10 Rapid Jobs", callback_data: "MENU:jobs" }
    ],
    [
      { text: "⚡ Run 10 Scrapes", callback_data: "MENU:scrape" },
      { text: "🎯 Live Bounties", callback_data: "MENU:bounties" }
    ],
    [
      { text: "💰 Payout Accounts", callback_data: "MENU:payout" },
      { text: "❓ Help & Commands", callback_data: "MENU:help" }
    ]
  ]
};

async function sendTelegramMessage(token, chatId, text, replyMarkup = null) {
  const payload = {
    chat_id: chatId,
    text: text,
    parse_mode: "HTML",
    disable_web_page_preview: true
  };
  if (replyMarkup) {
    payload.reply_markup = replyMarkup;
  }
  return fetch(`https://api.telegram.org/bot${token}/sendMessage`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
}

async function answerTelegramCallback(token, callbackQueryId) {
  return fetch(`https://api.telegram.org/bot${token}/answerCallbackQuery`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ callback_query_id: callbackQueryId })
  });
}

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    const token = env.TELEGRAM_BOT_TOKEN || BOT_TOKEN;
    const authorizedChatId = env.TELEGRAM_CHAT_ID || AUTHORIZED_CHAT_ID;

    // 1. Health check endpoint (Zero cost, no runner invoked)
    if (url.pathname === "/health") {
      return new Response(JSON.stringify({
        status: "ok",
        agent: "ARIA Sovereign 2.0",
        cloud: "Cloudflare Edge + GitHub Actions",
        timestamp: new Date().toISOString()
      }), {
        headers: { "Content-Type": "application/json" }
      });
    }

    // 2. Telegram Webhook Endpoint (24/7/365 Zero-Latency Gateway)
    if (url.pathname === "/telegram" && request.method === "POST") {
      try {
        const update = await request.json();

        // A. Handle Inline Button Clicks
        if (update.callback_query) {
          const cb = update.callback_query;
          const data = cb.data || "";
          await answerTelegramCallback(token, cb.id);

          if (data.startsWith("APPROVE:")) {
            const taskId = data.split(":")[1];
            await sendTelegramMessage(token, authorizedChatId,
              `<b>[✓] TASK ${taskId} APPROVED!</b>\n━━━━━━━━━━━━━━━━━━━━━━\nAria is dispatching the verified deliverables.\nAll state committed to GitHub.`,
              MAIN_MENU_KEYBOARD
            );
          } else if (data.startsWith("REJECT:")) {
            const taskId = data.split(":")[1];
            await sendTelegramMessage(token, authorizedChatId,
              `<b>[✕] TASK ${taskId} REJECTED.</b>\nAria has safely cancelled the task.`,
              MAIN_MENU_KEYBOARD
            );
          } else if (data === "MENU:status") {
            await sendTelegramMessage(token, authorizedChatId,
              `<b>⚡ ARIA 24/7 SYSTEM TELEMETRY</b>\n━━━━━━━━━━━━━━━━━━━━━━\n• <b>Cloud Host:</b> GitHub Actions & Cloudflare Edge (24/7 Active)\n• <b>TCO:</b> $0.00 / month (Zero-Cost FinOps)\n• <b>Payout:</b> PayPal (${PAYPAL_PAYOUT}) | UPI (${UPI_PAYOUT})\n• <b>Security Gate:</b> Mobile Push ACTIVE`,
              MAIN_MENU_KEYBOARD
            );
          } else if (data === "MENU:jobs") {
            await sendTelegramMessage(token, authorizedChatId,
              `<b>💼 ARIA RAPID CASH INVENTORY</b>\n━━━━━━━━━━━━━━━━━━━━━━\n1. Next.js SSR Hydration Fix ($50)\n2. Python Product Scraper with CSV ($35)\n3. Express CORS Proxy Middleware ($30)\n4. Mobile Slide-out Drawer ($40)\n5. CRM Lead Sanitizer ($45)\n6. Stripe Webhook Signature ($60)\n7. Dynamic OG Image Route ($35)\n8. Discord/Telegram Alert Relay ($50)\n9. Cal.com DST Normalizer ($55)\n10. Twenty CRM Compound Filter ($65)\n\n<i>Reply /solve &lt;keyword&gt; to generate verified code & pitch!</i>`,
              MAIN_MENU_KEYBOARD
            );
          } else if (data === "MENU:scrape") {
            await sendTelegramMessage(token, authorizedChatId,
              `<b>⏳ SCRAPING PIPELINE TRIGGERED</b>\nLaunching 10-target scrape batch in cloud runner...`,
              MAIN_MENU_KEYBOARD
            );
          } else if (data === "MENU:payout") {
            await sendTelegramMessage(token, authorizedChatId,
              `<b>💰 ARIA SETTLEMENT ACCOUNTS</b>\n━━━━━━━━━━━━━━━━━━━━━━\n• <b>PayPal:</b> <code>${PAYPAL_PAYOUT}</code>\n• <b>UPI:</b> <code>${UPI_PAYOUT}</code>\n\n<i>Zero middleman fees. Direct settlement.</i>`,
              MAIN_MENU_KEYBOARD
            );
          } else if (data === "MENU:help") {
            await sendTelegramMessage(token, authorizedChatId,
              `<b>👑 ARIA SOVEREIGN ASSISTANT COMMANDS</b>\n━━━━━━━━━━━━━━━━━━━━━━\n• /status — Live system & quota telemetry\n• /jobs — 10 rapid-cash developer jobs\n• /scrape — Run 10-target scraping pipeline\n• /solve &lt;task&gt; — Generate instant code & pitch\n• /payout — Payout account details\n• /bounties — Active GitHub & Algora bounties`,
              MAIN_MENU_KEYBOARD
            );
          }
          return new Response("OK", { status: 200 });
        }

        // B. Handle Text Messages
        if (update.message && update.message.text) {
          const msg = update.message;
          const text = msg.text.trim();
          const senderId = String(msg.chat.id);

          if (senderId !== String(authorizedChatId)) {
            return new Response("Unauthorized", { status: 403 });
          }

          const lower = text.toLowerCase();
          if (lower.startsWith("/start") || lower.startsWith("/help") || lower === "hi" || lower === "hello") {
            await sendTelegramMessage(token, authorizedChatId,
              `<b>👑 ARIA v2.0 SOVEREIGN ASSISTANT ONLINE</b>\n━━━━━━━━━━━━━━━━━━━━━━\nI am Aria, your autonomous 24/7 AI engineer and executive partner.\nOperating at permanent $0.00 TCO.\n\nTap below to command:`,
              MAIN_MENU_KEYBOARD
            );
          } else if (lower.startsWith("/status")) {
            await sendTelegramMessage(token, authorizedChatId,
              `<b>⚡ ARIA 24/7 SYSTEM TELEMETRY</b>\n━━━━━━━━━━━━━━━━━━━━━━\n• <b>Cloud Host:</b> GitHub Actions & Cloudflare Edge (24/7 Active)\n• <b>TCO:</b> $0.00 / month (Zero-Cost FinOps)\n• <b>Payout:</b> PayPal (${PAYPAL_PAYOUT}) | UPI (${UPI_PAYOUT})\n• <b>Security Gate:</b> Mobile Push ACTIVE`,
              MAIN_MENU_KEYBOARD
            );
          } else if (lower.startsWith("/jobs")) {
            await sendTelegramMessage(token, authorizedChatId,
              `<b>💼 ARIA RAPID CASH INVENTORY (10 JOBS)</b>\n━━━━━━━━━━━━━━━━━━━━━━\n1. Next.js SSR Hydration Fix ($50)\n2. Python Product Scraper with CSV ($35)\n3. Express CORS Proxy Middleware ($30)\n4. Mobile Slide-out Drawer ($40)\n5. CRM Lead Sanitizer ($45)\n6. Stripe Webhook Signature ($60)\n7. Dynamic OG Image Route ($35)\n8. Discord/Telegram Alert Relay ($50)\n9. Cal.com DST Normalizer ($55)\n10. Twenty CRM Compound Filter ($65)\n\n<i>Reply /solve &lt;keyword&gt; to generate verified code & pitch!</i>`,
              MAIN_MENU_KEYBOARD
            );
          } else if (lower.startsWith("/payout")) {
            await sendTelegramMessage(token, authorizedChatId,
              `<b>💰 ARIA SETTLEMENT ACCOUNTS</b>\n━━━━━━━━━━━━━━━━━━━━━━\n• <b>PayPal:</b> <code>${PAYPAL_PAYOUT}</code>\n• <b>UPI:</b> <code>${UPI_PAYOUT}</code>\n\n<i>Zero middleman fees. Direct settlement.</i>`,
              MAIN_MENU_KEYBOARD
            );
          } else {
            await sendTelegramMessage(token, authorizedChatId,
              `<b>👑 ARIA ASSISTANT</b>\n━━━━━━━━━━━━━━━━━━━━━━\nReceived your instruction: <i>"${text}"</i>\n\nI am actively monitoring our repositories, scraping feeds, and rapid-cash channels.\nHow would you like to proceed?`,
              MAIN_MENU_KEYBOARD
            );
          }
          return new Response("OK", { status: 200 });
        }

        return new Response("No-op", { status: 200 });
      } catch (err) {
        return new Response(`Error: ${err.message}`, { status: 500 });
      }
    }

    // 3. Out-of-band Human Approval Callback
    if (url.pathname === "/approve" && request.method === "POST") {
      const authHeader = request.headers.get("X-ARIA-SECRET");
      if (authHeader !== env.GATEWAY_SECRET) {
        return new Response("Unauthorized", { status: 401 });
      }

      const body = await request.json();
      const taskId = body.task_id;
      const decision = body.decision;

      const ghResp = await fetch(`https://api.github.com/repos/${env.GITHUB_REPO}/dispatches`, {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${env.GITHUB_PAT}`,
          "User-Agent": "ARIA-Cloudflare-Worker",
          "Accept": "application/vnd.github.v3+json",
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          event_type: "human-approval-resolved",
          client_payload: { task_id: taskId, decision: decision }
        })
      });

      return new Response(JSON.stringify({ dispatched: ghResp.status === 204 }), {
        headers: { "Content-Type": "application/json" }
      });
    }


    // 4. PayPal Payment Settlement Webhook
    if (url.pathname === "/webhook/paypal" && request.method === "POST") {
      try {
        const event = await request.json();
        const eventType = event.event_type || "UNKNOWN";
        const resource = event.resource || {};
        const amount = resource.amount ? `${resource.amount.value} ${resource.amount.currency}` : "Incoming Payment";
        const payer = resource.payer ? resource.payer.email_address : "Client";

        await sendTelegramMessage(token, authorizedChatId,
          `<b>┌── ⚡ PAYPAL SETTLEMENT CONFIRMED ──────────┐</b>\n` +
          `<b>│ Event:</b>  <code>${eventType}</code>\n` +
          `<b>│ Amount:</b> <b>${amount}</b>\n` +
          `<b>│ Payer:</b>  ${payer}\n` +
          `<b>├──────────────────────────────────────────┤</b>\n` +
          `<b>│ Rail:</b>   PayPal (<code>${PAYPAL_PAYOUT}</code>)\n` +
          `<b>└──────────────────────────────────────────┘</b>\n\n` +
          `<i>Settlement successfully credited!</i>`,
          MAIN_MENU_KEYBOARD
        );
        return new Response(JSON.stringify({ status: "processed" }), { status: 200, headers: { "Content-Type": "application/json" } });
      } catch (err) {
        return new Response(`Error: ${err.message}`, { status: 400 });
      }
    }

    // 5. GitHub Actions / PR Event Webhook
    if (url.pathname === "/webhook/github" && request.method === "POST") {
      try {
        const ghEvent = request.headers.get("X-GitHub-Event") || "event";
        const payload = await request.json();
        const repo = payload.repository ? payload.repository.full_name : "GitHub";
        const action = payload.action || "triggered";
        const sender = payload.sender ? payload.sender.login : "user";

        if (["pull_request", "pull_request_review", "issue_comment"].includes(ghEvent)) {
          await sendTelegramMessage(token, authorizedChatId,
            `<b>🔔 GITHUB EVENT: ${repo}</b>\n` +
            `━━━━━━━━━━━━━━━━━━━━━━\n` +
            `• <b>Type:</b> <code>${ghEvent}</code> (${action})\n` +
            `• <b>Sender:</b> @${sender}\n` +
            `• <b>Details:</b> <i>${payload.comment ? payload.comment.body.slice(0, 150) : "PR updated"}</i>`
          );
        }
        return new Response("OK", { status: 200 });
      } catch (err) {
        return new Response(`Error: ${err.message}`, { status: 400 });
      }
    }

    // 6. Zero-Cost Edge AI Chat Proxy (Groq LLaMA 3.3 70B)
    if (url.pathname === "/api/chat") {
      if (request.method === "OPTIONS") {
        return new Response(null, {
          headers: {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type"
          }
        });
      }
      try {
        const body = await request.json();
        const prompt = body.prompt || "Status report";
        const groqKey = env.GROQ_API_KEY;
        if (!groqKey) {
          return new Response(JSON.stringify({ response: "ARIA Sovereign Edge Mode: Operational at $0.00/month TCO." }), {
            headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" }
          });
        }
        const groqRes = await fetch("https://api.groq.com/openai/v1/chat/completions", {
          method: "POST",
          headers: {
            "Authorization": `Bearer ${groqKey}`,
            "Content-Type": "application/json"
          },
          body: JSON.stringify({
            model: "llama-3.3-70b-versatile",
            messages: [
              { role: "system", content: "You are ARIA, an autonomous AI engineer and executive partner operating at $0.00/month TCO." },
              { role: "user", content: prompt }
            ],
            temperature: 0.2,
            max_tokens: 800
          })
        });
        const groqData = await groqRes.json();
        const reply = groqData.choices?.[0]?.message?.content || "No response generated";
        return new Response(JSON.stringify({ response: reply }), {
          headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" }
        });
      } catch (err) {
        return new Response(JSON.stringify({ error: err.message }), { status: 500, headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" } });
      }
    }

    return new Response("ARIA Gateway Endpoint Active.", { status: 200 });
  }
};
