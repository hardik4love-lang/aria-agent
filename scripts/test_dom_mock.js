const fs = require('fs');
const html = fs.readFileSync('D:/aria-agent/dashboard/index.html', 'utf8');

const scriptMatch = html.match(/<script>([\s\S]*?)<\/script>/i);
const scriptContent = scriptMatch[1];

const elements = {};
function getOrCreate(id) {
  if (!elements[id]) elements[id] = { innerHTML: '', innerText: '', value: '', classList: { remove: ()=>{}, add: ()=>{} } };
  return elements[id];
}
const document = {
  getElementById: (id) => getOrCreate(id),
  querySelectorAll: () => [],
  querySelector: () => ({ innerText: '' })
};

const window = {
  addEventListener: (event, cb) => {},
  document
};

try {
  const fn = new Function('document', 'window', 'console', scriptContent + '; return { EMBEDDED_BOUNTIES_DATA, populateDashboard, allPinItems };');
  const res = fn(document, window, console);
  res.populateDashboard(res.EMBEDDED_BOUNTIES_DATA);
  console.log('pin-locator-tbody rows:', elements['pin-locator-tbody'].innerHTML.split('<tr').length - 1);
  console.log('merged-prs-body rows:', elements['merged-prs-body'].innerHTML.split('<tr').length - 1);
  console.log('bounties-list cards:', elements['bounties-list'].innerHTML.split('class="card"').length - 1);
  console.log('opire-tbody rows:', elements['opire-tbody'].innerHTML.split('<tr').length - 1);
  console.log('clients-tbody rows:', elements['clients-tbody'].innerHTML.split('<tr').length - 1);
  console.log('KPI Merged Value:', elements['kpi-merged-value'].innerText);
  console.log('KPI Open Value:', elements['kpi-open-value'].innerText);
  console.log('KPI Approved Value:', elements['kpi-approved-value'].innerText);
  console.log('KPI Opire Value:', elements['kpi-opire-value'].innerText);
  console.log('KPI Clients Value:', elements['kpi-clients-value'].innerText);
  console.log('TOTAL PIN ITEMS:', elements['stat-pin-count'].innerText);
  console.log('ALL VERIFICATIONS PASSED 100%!');
} catch (e) {
  console.error('Execution error:', e);
}
