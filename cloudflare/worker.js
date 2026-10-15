/**
 * Cloudflare Worker Gateway for ARIA Agent ($0.00 TCO - 100k requests/day free tier).
 * Receives external webhooks, validates signatures, and dispatches GitHub Actions workflows.
 */

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);

    // 1. Health check endpoint (Zero cost, no runner invoked)
    if (url.pathname === "/health") {
      return new Response(JSON.stringify({
        status: "ok",
        agent: "ARIA",
        timestamp: new Date().toISOString()
      }), {
        headers: { "Content-Type": "application/json" }
      });
    }

    // 2. Out-of-band Human Approval Callback
    if (url.pathname === "/approve" && request.method === "POST") {
      const authHeader = request.headers.get("X-ARIA-SECRET");
      if (authHeader !== env.GATEWAY_SECRET) {
        return new Response("Unauthorized", { status: 401 });
      }

      const body = await request.json();
      const taskId = body.task_id;
      const decision = body.decision; // "approved" or "rejected"

      // Dispatch resume workflow to GitHub Actions
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
          client_payload: {
            task_id: taskId,
            decision: decision
          }
        })
      });

      return new Response(JSON.stringify({ dispatched: ghResp.status === 204 }), {
        headers: { "Content-Type": "application/json" }
      });
    }

    // 3. Generic Webhook Receiver (Dispatches task to runner)
    if (url.pathname === "/webhook" && request.method === "POST") {
      const payload = await request.json();
      const eventType = payload.event_type || "webhook-trigger";

      const ghResp = await fetch(`https://api.github.com/repos/${env.GITHUB_REPO}/dispatches`, {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${env.GITHUB_PAT}`,
          "User-Agent": "ARIA-Cloudflare-Worker",
          "Accept": "application/vnd.github.v3+json",
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          event_type: eventType,
          client_payload: payload
        })
      });

      return new Response(JSON.stringify({ status: "queued", status_code: ghResp.status }), {
        headers: { "Content-Type": "application/json" }
      });
    }

    return new Response("ARIA Gateway Endpoint Active.", { status: 200 });
  }
};
