import test from 'node:test';
import assert from 'node:assert/strict';
import { randomUUID } from 'node:crypto';
import { mkdtemp, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { execFileSync } from 'node:child_process';
import { createProbe } from '../probe.mjs';

const base = 'http://localhost:4291';
async function send(app, cookie, path, method = 'GET', body, origin = base) {
  return app.handle(new Request(base + path, {
    method,
    headers: { cookie, origin, ...(body === undefined ? {} : { 'content-type': 'application/json' }) },
    ...(body === undefined ? {} : { body: JSON.stringify(body) }),
  }));
}
async function user(app, name) {
  const r = await send(app, '', '/api/auth/sign-up/email', 'POST', {
    email: `${name}@example.test`, name, password: 'LocalProbe!42',
  });
  assert.equal(r.status, 200);
  return { data: (await r.json()).user, cookie: r.headers.getSetCookie().map(v => v.split(';')[0]).join('; ') };
}
async function fixture(path = ':memory:') {
  const app = await createProbe({ path });
  try {
    const owner = await user(app, 'owner');
    const other = await user(app, 'other');
    const viewer = await user(app, 'viewer');
    const editor = await user(app, 'editor');
    const org = async (who, name) => {
      const r = await send(app, who.cookie, '/api/auth/organization/create', 'POST', { name, slug: name });
      assert.equal(r.status, 200);
      return r.json();
    };
    const a = await org(owner, 'alpha');
    const b = await org(other, 'beta');
    for (const [person, role] of [[viewer, 'viewer'], [editor, 'member']]) {
      // Official server-only provisioning API, not exposed as a browser route.
      await app.auth.api.addMember({ body: { organizationId: a.id, userId: person.data.id, role } });
    }
    const pa = randomUUID(), pb = randomUUID();
    app.db.prepare('INSERT INTO project(id, organizationId, name) VALUES(?,?,?)').run(pa, a.id, 'Alpha Project');
    app.db.prepare('INSERT INTO project(id, organizationId, name) VALUES(?,?,?)').run(pb, b.id, 'Beta Project');
    return { app, owner, other, viewer, editor, a, b, pa, pb };
  } catch (error) { app.close(); throw error; }
}
const create = (f, cookie = f.owner.cookie, org = f.a.id, project = f.pa) =>
  send(f.app, cookie, `/api/orgs/${org}/tasks`, 'POST', { title: 'Review release scope', projectId: project, status: 'todo' });
async function createdTask(f) {
  const r = await create(f);
  assert.equal(r.status, 201);
  return r.json();
}
const patch = (f, cookie, org, id, body) => send(f.app, cookie, `/api/orgs/${org}/tasks/${id}`, 'PATCH', body);
const counts = app => [app.db.prepare('SELECT count(*) AS n FROM task').get().n,
  app.db.prepare('SELECT count(*) AS n FROM audit').get().n];

test('owner creates and member updates a persisted task with an audit record', async () => {
  const f = await fixture();
  try {
    const r = await create(f);
    assert.equal(r.status, 201);
    const task = await r.json();
    assert.equal(task.organizationId, f.a.id);
    assert.equal(task.version, 1);
    const saved = await patch(f, f.editor.cookie, f.a.id, task.id, { title: 'Scope approved', status: 'done', version: 1 });
    assert.equal(saved.status, 200);
    assert.equal((await saved.json()).version, 2);
    const list = await send(f.app, f.viewer.cookie, `/api/orgs/${f.a.id}/tasks`);
    assert.equal(list.status, 200);
    assert.equal((await list.json()).items[0].title, 'Scope approved');
    assert.deepEqual(counts(f.app), [1, 2]);
  } finally { f.app.close(); }
});

test('cross-tenant list, guessed task reads and writes disclose no data and change no rows', async () => {
  const f = await fixture();
  try {
    const a = await createdTask(f);
    assert.equal((await create(f, f.other.cookie, f.b.id, f.pb)).status, 201);
    const before = counts(f.app);
    assert.equal((await send(f.app, f.other.cookie, `/api/orgs/${f.a.id}/tasks`)).status, 403);
    const own = await send(f.app, f.other.cookie, `/api/orgs/${f.b.id}/tasks`);
    assert.equal(own.status, 200);
    const ownItems = (await own.json()).items;
    assert.equal(ownItems.length, 1);
    assert.ok(ownItems.every(t => t.organizationId === f.b.id));
    assert.equal((await send(f.app, f.other.cookie, `/api/orgs/${f.b.id}/tasks/${a.id}`)).status, 404);
    assert.equal((await patch(f, f.other.cookie, f.b.id, a.id, { title: 'intrusion', status: 'done', version: 1 })).status, 404);
    assert.equal((await patch(f, f.other.cookie, f.a.id, a.id, { title: 'intrusion', status: 'done', version: 1 })).status, 403);
    assert.deepEqual(counts(f.app), before);
  } finally { f.app.close(); }
});

test('viewer cannot create or update, and membership revocation applies to an existing session', async () => {
  const f = await fixture();
  try {
    const task = await createdTask(f);
    const before = counts(f.app);
    assert.equal((await create(f, f.viewer.cookie)).status, 403);
    assert.equal((await patch(f, f.viewer.cookie, f.a.id, task.id, { title: 'viewer write', status: 'done', version: 1 })).status, 403);
    const removed = await send(f.app, f.owner.cookie, '/api/auth/organization/remove-member', 'POST', {
      organizationId: f.a.id, memberIdOrEmail: f.editor.data.email,
    });
    assert.equal(removed.status, 200);
    assert.equal((await patch(f, f.editor.cookie, f.a.id, task.id, { title: 'revoked write', status: 'done', version: 1 })).status, 403);
    assert.deepEqual(counts(f.app), before);
  } finally { f.app.close(); }
});

test('cross-tenant project links, invalid status, blank title and forged actor are rejected', async () => {
  const f = await fixture();
  try {
    const before = counts(f.app);
    assert.equal((await create(f, f.owner.cookie, f.a.id, f.pb)).status, 422);
    for (const body of [
      { title: ' ', projectId: f.pa, status: 'todo' },
      { title: 'x', projectId: f.pa, status: 'closed' },
      { title: 'x', projectId: f.pa, status: 'todo', actorId: f.other.data.id },
    ]) assert.equal((await send(f.app, f.owner.cookie, `/api/orgs/${f.a.id}/tasks`, 'POST', body)).status, 422);
    assert.deepEqual(counts(f.app), before);
  } finally { f.app.close(); }
});

test('a stale edit is rejected without overwriting the first committed edit or adding audit', async () => {
  const f = await fixture();
  try {
    const task = await createdTask(f);
    const [r1, r2] = await Promise.all([
      patch(f, f.owner.cookie, f.a.id, task.id, { title: 'First', status: 'doing', version: 1 }),
      patch(f, f.editor.cookie, f.a.id, task.id, { title: 'Second', status: 'done', version: 1 }),
    ]);
    assert.deepEqual([r1.status, r2.status].sort(), [200, 409]);
    const winner = await (r1.status === 200 ? r1 : r2).json();
    const persisted = await (await send(f.app, f.owner.cookie, `/api/orgs/${f.a.id}/tasks/${task.id}`)).json();
    assert.equal(persisted.title, winner.title);
    assert.equal(persisted.version, 2);
    assert.deepEqual(counts(f.app), [1, 2]);
  } finally { f.app.close(); }
});

test('audit storage failure rolls back a task update and its version', async () => {
  const f = await fixture();
  try {
    const task = await createdTask(f);
    f.app.db.exec("CREATE TRIGGER reject_audit BEFORE INSERT ON audit BEGIN SELECT RAISE(ABORT, 'simulated audit failure'); END;");
    const r = await patch(f, f.owner.cookie, f.a.id, task.id, { title: 'Must roll back', status: 'done', version: 1 });
    assert.equal(r.status, 503);
    const stored = await (await send(f.app, f.owner.cookie, `/api/orgs/${f.a.id}/tasks/${task.id}`)).json();
    assert.equal(stored.title, task.title);
    assert.equal(stored.version, 1);
    assert.deepEqual(counts(f.app), [1, 1]);
  } finally { f.app.close(); }
});

test('task, audit and a valid session survive opening the database in a new Node process', async () => {
  const directory = await mkdtemp(join(tmpdir(), 'craft-reuse-'));
  let f;
  try {
    const path = join(directory, 'probe.sqlite');
    f = await fixture(path);
    const task = await createdTask(f);
    f.app.close();
    f = { ...f, app: null };
    const output = execFileSync(process.execPath, ['verify-reopen.mjs'], {
      cwd: new URL('..', import.meta.url),
      env: { ...process.env, PROBE_DB_PATH: path, PROBE_COOKIE: f.owner.cookie, PROBE_ORG: f.a.id, PROBE_TASK: task.id },
      encoding: 'utf8',
    });
    const result = JSON.parse(output);
    assert.equal(result.status, 200);
    assert.equal(result.task.id, task.id);
    assert.equal(result.auditCount, 1);
  } finally { f?.app?.close(); await rm(directory, { recursive: true, force: true }); }
});

test('cross-origin business writes are rejected and browser callers cannot provision members', async () => {
  const f = await fixture();
  try {
    const before = counts(f.app);
    const r = await send(f.app, f.owner.cookie, `/api/orgs/${f.a.id}/tasks`, 'POST', {
      title: 'cross-site', status: 'todo', projectId: f.pa,
    }, 'https://untrusted.example');
    assert.equal(r.status, 403);
    assert.equal((await send(f.app, f.viewer.cookie, '/api/auth/organization/add-member', 'POST', {
      userId: f.viewer.data.id, role: 'owner', organizationId: f.a.id,
    })).status, 404);
    assert.deepEqual(counts(f.app), before);
  } finally { f.app.close(); }
});

test('revocation while a write body is being read cannot commit a previously authorized edit', async () => {
  const f = await fixture();
  try {
    const task = await createdTask(f);
    let enter, release;
    const reading = new Promise(resolve => { enter = resolve; });
    const gate = new Promise(resolve => { release = resolve; });
    const request = new Request(`${base}/api/orgs/${f.a.id}/tasks/${task.id}`, {
      method: 'PATCH', headers: { origin: base, cookie: f.editor.cookie, 'content-type': 'application/json' },
      body: JSON.stringify({ title: 'Late edit', status: 'done', version: 1 }),
    });
    const parse = request.json.bind(request);
    request.json = async () => { enter(); await gate; return parse(); };
    const pending = f.app.handle(request);
    await reading;
    try {
      const removed = await send(f.app, f.owner.cookie, '/api/auth/organization/remove-member', 'POST', {
        organizationId: f.a.id, memberIdOrEmail: f.editor.data.email,
      });
      assert.equal(removed.status, 200);
    } finally { release(); }
    assert.equal((await pending).status, 403);
    const saved = await (await send(f.app, f.owner.cookie, `/api/orgs/${f.a.id}/tasks/${task.id}`)).json();
    assert.equal(saved.title, task.title);
    assert.equal(saved.version, 1);
    assert.deepEqual(counts(f.app), [1, 1]);
  } finally { f.app.close(); }
});
