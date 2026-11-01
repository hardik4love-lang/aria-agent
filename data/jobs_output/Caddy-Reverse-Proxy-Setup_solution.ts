const express = require('express');
const app = express();

// Universal CORS with preflight 204 handler
app.use((req, res, next) => {
  res.setHeader('Access-Control-Allow-Origin', req.headers.origin || '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');
  res.setHeader('Access-Control-Allow-Credentials', 'true');
  if (req.method === 'OPTIONS') return res.status(204).end();
  next();
});

// Transparent proxy pipeline
app.all('/api/proxy', async (req, res) => {
  const target = req.query.target;
  if (!target) return res.status(400).json({ error: 'Missing target URL' });
  try {
    const fetchRes = await fetch(target, { method: req.method, headers: req.headers });
    const data = await fetchRes.text();
    res.status(fetchRes.status).send(data);
  } catch (err) {
    res.status(502).json({ error: 'Proxy failed', details: err.message });
  }
});
