const fs = require('fs');
const html = fs.readFileSync('D:/aria-agent/dashboard/index.html', 'utf8');

const scriptMatches = html.match(/<script>([\s\S]*?)<\/script>/gi);
console.log('Script tags count:', scriptMatches ? scriptMatches.length : 0);
let errCount = 0;
if (scriptMatches) {
  scriptMatches.forEach((s, idx) => {
    const code = s.replace(/<\/?script>/gi, '');
    try {
      new Function(code);
      console.log('Script ' + idx + ' syntax OK');
    } catch (e) {
      console.error('Script ' + idx + ' SYNTAX ERROR:', e.message);
      errCount++;
    }
  });
}
console.log('Total syntax errors:', errCount);

const tbodyMatch = html.match(/<tbody id="pin-locator-tbody">([\s\S]*?)<\/tbody>/i);
if (tbodyMatch) {
  const rowCount = (tbodyMatch[1].match(/<tr/gi) || []).length;
  console.log('Pre-rendered rows in pin-locator-tbody:', rowCount);
  console.log('Contains Loading text?:', tbodyMatch[1].includes('Loading live process'));
}
