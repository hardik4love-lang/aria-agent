async function check() {
  const res = await fetch('https://hardik4love-lang.github.io/aria-agent/?cache_bust=' + Date.now());
  const t = await res.text();
  console.log('HTTP Status:', res.status);
  console.log('Total HTML Bytes:', t.length);
  console.log('Has 32 Items:', t.includes('32 Items'));
  console.log('Has $9,925.00:', t.includes('$9,925.00'));
  console.log('Has HackerOne #4115591:', t.includes('HackerOne #4115591'));
  console.log('Has Video & Multimedia Module:', t.includes('Cleanroom Video & Multimedia'));
  console.log('Has Loading live process row:', t.includes('Loading live process & payment telemetry...'));
  console.log('Has Cache-Control meta:', t.includes('Cache-Control'));
  const rows = t.split('<tr style="border-bottom: 1px solid rgba(255,255,255,0.05);">').length - 1;
  console.log('Count of pre-rendered static rows in HTML:', rows);
}
check();
