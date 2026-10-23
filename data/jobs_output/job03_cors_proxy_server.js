const express = require("express");
const http = require("http");
const https = require("https");
const { URL } = require("url");

const app = express();
const PORT = process.env.PORT || 8080;

app.use((req, res, next) => {
  const origin = req.headers.origin || "*";
  res.setHeader("Access-Control-Allow-Origin", origin);
  res.setHeader("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS, PATCH");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type, Authorization, X-Requested-With");
  res.setHeader("Access-Control-Allow-Credentials", "true");
  if (req.method === "OPTIONS") return res.status(204).end();
  next();
});

app.all("/api/proxy", (req, res) => {
  const targetUrlStr = req.query.url;
  if (!targetUrlStr) return res.status(400).json({ error: "Missing ?url= query parameter" });

  try {
    const targetUrl = new URL(targetUrlStr);
    const transport = targetUrl.protocol === "https:" ? https : http;
    const clientReq = transport.request(targetUrl, { method: req.method }, (clientRes) => {
      res.status(clientRes.statusCode);
      for (const [k, v] of Object.entries(clientRes.headers)) {
        if (!k.toLowerCase().startsWith("access-control-")) res.setHeader(k, v);
      }
      clientRes.pipe(res);
    });
    clientReq.on("error", (err) => res.status(502).json({ error: err.message }));
    req.pipe(clientReq);
  } catch (err) {
    res.status(400).json({ error: "Invalid target URL" });
  }
});

app.listen(PORT, () => console.log(`CORS Proxy active on port ${PORT}`));
