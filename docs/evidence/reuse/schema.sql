CREATE TABLE IF NOT EXISTS project (
  id TEXT PRIMARY KEY,
  organizationId TEXT NOT NULL REFERENCES organization(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  UNIQUE(organizationId, id)
);
CREATE TABLE IF NOT EXISTS task (
  id TEXT PRIMARY KEY,
  organizationId TEXT NOT NULL REFERENCES organization(id) ON DELETE CASCADE,
  projectId TEXT NOT NULL,
  title TEXT NOT NULL CHECK(length(trim(title)) BETWEEN 1 AND 200),
  status TEXT NOT NULL CHECK(status IN ('todo', 'doing', 'done')),
  version INTEGER NOT NULL DEFAULT 1 CHECK(version > 0),
  UNIQUE(organizationId, id),
  FOREIGN KEY(organizationId, projectId) REFERENCES project(organizationId, id)
);
CREATE INDEX IF NOT EXISTS task_org_project ON task(organizationId, projectId);
CREATE TABLE IF NOT EXISTS audit (
  id TEXT PRIMARY KEY,
  organizationId TEXT NOT NULL,
  taskId TEXT NOT NULL,
  actorId TEXT NOT NULL REFERENCES user(id),
  action TEXT NOT NULL CHECK(action IN ('create', 'update')),
  version INTEGER NOT NULL,
  createdAt TEXT NOT NULL,
  FOREIGN KEY(organizationId, taskId) REFERENCES task(organizationId, id)
);
