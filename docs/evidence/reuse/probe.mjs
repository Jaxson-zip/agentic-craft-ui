import { DatabaseSync } from 'node:sqlite';
import { readFile } from 'node:fs/promises';
import { randomUUID } from 'node:crypto';
import { betterAuth } from 'better-auth';
import { getMigrations } from 'better-auth/db/migration';
import { organization } from 'better-auth/plugins';
import { createAccessControl } from 'better-auth/plugins/access';
import { defaultStatements, ownerAc, adminAc, memberAc } from 'better-auth/plugins/organization/access';

const origin = 'http://localhost:4291';
const ac = createAccessControl({ ...defaultStatements, task: ['read', 'create', 'update'] });
const roles = {
  owner: ac.newRole({ ...ownerAc.statements, task: ['read', 'create', 'update'] }),
  admin: ac.newRole({ ...adminAc.statements, task: ['read', 'create', 'update'] }),
  member: ac.newRole({ ...memberAc.statements, task: ['read', 'create', 'update'] }),
  viewer: ac.newRole({ task: ['read'] }),
};
const json = (data, status = 200) => Response.json(data, { status });
const valid = (body, keys) => body && typeof body === 'object' && !Array.isArray(body)
  && Object.keys(body).every(key => keys.includes(key))
  && typeof body.title === 'string' && body.title.trim().length > 0 && body.title.trim().length <= 200
  && ['todo', 'doing', 'done'].includes(body.status);

// Local compatibility probe. This fixed public secret is deliberately test-only.
export async function createProbe({ path = ':memory:' } = {}) {
  const db = new DatabaseSync(path);
  db.exec('PRAGMA foreign_keys=ON; PRAGMA busy_timeout=3000;');
  const options = {
    database: db,
    baseURL: origin,
    secret: 'LOCAL-ONLY-compatibility-probe-secret-42',
    trustedOrigins: [origin],
    emailAndPassword: { enabled: true },
    session: { cookieCache: { enabled: false } },
    plugins: [organization({ ac, roles })],
  };
  const { runMigrations } = await getMigrations(options);
  await runMigrations();
  await db.exec(await readFile(new URL('./schema.sql', import.meta.url), 'utf8'));
  const auth = betterAuth(options);
  return {
    auth,
    db,
    close() { db.close(); },
    async handle(request) {
      const url = new URL(request.url);
      if (url.pathname.startsWith('/api/auth/')) return auth.handler(request);
      const match = url.pathname.match(/^\/api\/orgs\/([^/]+)\/tasks(?:\/([^/]+))?$/);
      if (!match) return json({ code: 'NOT_FOUND' }, 404);
      const [ , orgId, taskId ] = match;
      if (!['GET', 'POST', 'PATCH'].includes(request.method)
        || (request.method === 'POST' && taskId) || (request.method === 'PATCH' && !taskId))
        return json({ code: 'METHOD_NOT_ALLOWED' }, 405);
      if (request.method !== 'GET') {
        if (request.headers.get('origin') !== origin) return json({ code: 'UNTRUSTED_ORIGIN' }, 403);
        if (!request.headers.get('content-type')?.startsWith('application/json')) return json({ code: 'UNSUPPORTED_MEDIA_TYPE' }, 415);
      }
      const session = await auth.api.getSession({ headers: request.headers, query: { disableCookieCache: true } });
      if (!session) return json({ code: 'UNAUTHENTICATED' }, 401);
      const action = request.method === 'GET' ? 'read' : request.method === 'POST' ? 'create' : 'update';
      let allowed;
      try {
        allowed = await auth.api.hasPermission({
          headers: request.headers,
          body: { organizationId: match[1], permissions: { task: [action] } },
        });
      } catch (error) {
        if (error.statusCode === 401 || error.statusCode === 403) return json({ code: 'FORBIDDEN' }, 403);
        throw error;
      }
      if (!allowed.success) return json({ code: 'FORBIDDEN' }, 403);
      const select = () => db.prepare('SELECT * FROM task WHERE organizationId=? AND id=?').get(orgId, taskId);
      if (request.method === 'GET') {
        if (!taskId) return json({ items: db.prepare('SELECT * FROM task WHERE organizationId=? ORDER BY id LIMIT 100').all(orgId) });
        const row = select();
        return row ? json(row) : json({ code: 'NOT_FOUND' }, 404);
      }
      let body;
      try { body = await request.json(); } catch { return json({ code: 'INVALID_JSON' }, 400); }
      const creating = request.method === 'POST';
      if (!valid(body, creating ? ['title', 'status', 'projectId'] : ['title', 'status', 'version'])
        || (creating ? typeof body.projectId !== 'string' : !Number.isSafeInteger(body.version) || body.version < 1))
        return json({ code: 'INVALID_INPUT' }, 422);
      if (creating && !db.prepare('SELECT id FROM project WHERE organizationId=? AND id=?').get(orgId, body.projectId))
        return json({ code: 'INVALID_PROJECT' }, 422);
      if (!creating && !select()) return json({ code: 'NOT_FOUND' }, 404);
      const id = creating ? randomUUID() : taskId;
      db.exec('BEGIN IMMEDIATE');
      try {
        // The body read above is asynchronous. Recheck mutable membership inside
        // the same SQLite write transaction, using the library's existing roles.
        const member = db.prepare('SELECT role FROM member WHERE organizationId=? AND userId=?').get(orgId, session.user.id);
        if (!member || !member.role.split(',').some(role => roles[role]?.authorize({ task: [action] }).success)) {
          db.exec('ROLLBACK');
          return json({ code: 'FORBIDDEN' }, 403);
        }
        if (creating) db.prepare('INSERT INTO task(id, organizationId, projectId, title, status) VALUES(?,?,?,?,?)')
          .run(id, orgId, body.projectId, body.title.trim(), body.status);
        else {
          const result = db.prepare('UPDATE task SET title=?, status=?, version=version+1 WHERE organizationId=? AND id=? AND version=?')
            .run(body.title.trim(), body.status, orgId, id, body.version);
          if (!result.changes) {
            db.exec('ROLLBACK');
            return json({ code: 'VERSION_CONFLICT' }, 409);
          }
        }
        const row = db.prepare('SELECT * FROM task WHERE organizationId=? AND id=?').get(orgId, id);
        db.prepare('INSERT INTO audit(id, organizationId, taskId, actorId, action, version, createdAt) VALUES(?,?,?,?,?,?,?)')
          .run(randomUUID(), orgId, id, session.user.id, creating ? 'create' : 'update', row.version, new Date().toISOString());
        db.exec('COMMIT');
        return json(row, creating ? 201 : 200);
      } catch (error) {
        db.exec('ROLLBACK');
        if (error.code === 'ERR_SQLITE_ERROR') return json({ code: 'STORAGE_FAILURE' }, 503);
        throw error;
      }
    },
  };
}
