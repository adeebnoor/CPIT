// Test helper: seal a throwaway STRESS payload with a test code, the same way tools/seal_stress.py
// seals the real ones (PBKDF2-SHA256 -> AES-256-GCM, AAD "chapter|version"). Real codes never appear here.
const {webcrypto} = require('crypto');
const TEST_CODE = 'TEST-CODE-2026';
const norm = code => String(code).toUpperCase().replace(/[^A-Z0-9]/g, '');
const b64 = bytes => Buffer.from(bytes).toString('base64');

async function sealForTest(chapter, version, body, code = TEST_CODE, iter = 1000) {
  const subtle = webcrypto.subtle, enc = new TextEncoder();
  const salt = webcrypto.getRandomValues(new Uint8Array(16)), iv = webcrypto.getRandomValues(new Uint8Array(12));
  const base = await subtle.importKey('raw', enc.encode(norm(code)), 'PBKDF2', false, ['deriveKey']);
  const key = await subtle.deriveKey({name: 'PBKDF2', salt, iterations: iter, hash: 'SHA-256'}, base,
    {name: 'AES-GCM', length: 256}, false, ['encrypt']);
  const ct = await subtle.encrypt({name: 'AES-GCM', iv, additionalData: enc.encode(String(chapter) + '|' + version)},
    key, enc.encode(JSON.stringify(body)));
  return {chapter: String(chapter), version, label: 'STRESS · new evidence',
    sealed: {v: 1, alg: 'AES-256-GCM', kdf: 'PBKDF2-SHA256', iter, salt: b64(salt), iv: b64(iv), ct: b64(new Uint8Array(ct))}};
}

// Give a jsdom window the Web Crypto API that browsers provide.
function withWebCrypto(w) {
  Object.defineProperty(w, 'crypto', {value: webcrypto, configurable: true});
  if (!w.TextEncoder) w.TextEncoder = TextEncoder;
  if (!w.TextDecoder) w.TextDecoder = TextDecoder;
}

// Enter the unlock code in the page and wait until the STRESS text is shown.
async function unlock(w, text, code = TEST_CODE, timeout = 5000) {
  const d = w.document, start = Date.now();
  while (!d.getElementById('stressCode')) {
    if (Date.now() - start > timeout) throw new Error('Unlock form did not appear');
    await new Promise(r => setTimeout(r, 10));
  }
  d.getElementById('stressCode').value = code;
  d.getElementById('unlockStress').click();
  while (!d.getElementById('partB').textContent.includes(text)) {
    if (Date.now() - start > timeout) throw new Error('STRESS did not unlock: ' + d.getElementById('partB').textContent.slice(0, 200));
    await new Promise(r => setTimeout(r, 10));
  }
}

function assertSealed(payload, where) {
  if ('text' in payload || 'principle' in payload || !payload.sealed || !payload.sealed.ct)
    throw new Error(where + ': published STRESS payload must be sealed');
}

module.exports = {TEST_CODE, sealForTest, withWebCrypto, unlock, assertSealed};
