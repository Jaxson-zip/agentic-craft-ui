import { createProbe } from './probe.mjs';
const app = await createProbe({ path: process.env.PROBE_DB_PATH });
try {
  const response = await app.handle(new Request(`http://localhost:4291/api/orgs/${process.env.PROBE_ORG}/tasks/${process.env.PROBE_TASK}`, {
    headers: { cookie: process.env.PROBE_COOKIE },
  }));
  console.log(JSON.stringify({ status: response.status, task: await response.json(),
    auditCount: app.db.prepare('SELECT count(*) AS n FROM audit').get().n }));
} finally { app.close(); }
