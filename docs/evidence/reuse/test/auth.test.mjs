import test from 'node:test';
import assert from 'node:assert/strict';
import { createProbe } from '../probe.mjs';

test('real registration yields a session usable by the protected task boundary', async () => {
  const app = await createProbe({ path: ':memory:' });
  try {
    const response = await app.handle(new Request('http://localhost:4291/api/auth/sign-up/email', {
      method: 'POST',
      headers: { 'content-type': 'application/json', origin: 'http://localhost:4291' },
      body: JSON.stringify({ email: 'owner@example.test', name: 'Owner', password: 'LocalProbe!42' }),
    }));
    assert.equal(response.status, 200);
    const cookie = response.headers.getSetCookie().map(value => value.split(';')[0]).join('; ');
    assert.ok(cookie.includes('session_token'));
    const denied = await app.handle(new Request('http://localhost:4291/api/orgs/unknown/tasks'));
    assert.equal(denied.status, 401);
    const authenticated = await app.handle(new Request('http://localhost:4291/api/orgs/unknown/tasks', {
      headers: { cookie },
    }));
    assert.equal(authenticated.status, 403);
  } finally { app.close(); }
});
