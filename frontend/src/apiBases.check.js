import assert from 'node:assert/strict';
import { isPersistedTemplateId, resolveApiBases, SKD_API } from './apiBases.js';

const vercelToday = resolveApiBases({
  primary: 'https://certificate-generator2-1.onrender.com',
  secondary: 'https://certificate-generator2skd.onrender.com',
  legacy: 'https://certificate-generator2-1.onrender.com',
});
assert.deepEqual(vercelToday, [SKD_API], 'dead dash1 host must not be used even if Vercel lists it first');

assert.deepEqual(
  resolveApiBases({ primary: 'https://certificate-generator2-1.onrender.com' }),
  [SKD_API],
  'only-dead-host env falls back to SKD',
);

assert.deepEqual(
  resolveApiBases({ isDev: true }),
  ['http://localhost:8000'],
  'local dev with no env uses localhost',
);

assert.ok(isPersistedTemplateId(34));
assert.ok(!isPersistedTemplateId(Date.now()));

console.log('OK: apiBases checks passed');
