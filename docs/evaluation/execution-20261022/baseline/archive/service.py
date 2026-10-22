"""Existing SQLite domain service; caller provides an authenticated actor."""
import sqlite3


def connect():
    conn = sqlite3.connect(':memory:')
    conn.executescript('''
    CREATE TABLE members(tenant TEXT, actor TEXT, role TEXT, PRIMARY KEY(tenant, actor));
    CREATE TABLE tasks(tenant TEXT, id TEXT, state TEXT, version INTEGER,
                       PRIMARY KEY(tenant, id));
    CREATE TABLE audit(tenant TEXT, task TEXT, actor TEXT, version INTEGER);
    CREATE TABLE outbox(tenant TEXT, task TEXT, version INTEGER);
    INSERT INTO members VALUES ('a','editor','editor'),('a','viewer','viewer'),('b','editor','owner');
    INSERT INTO tasks VALUES ('a','1','open',1),('b','1','open',1);
    ''')
    return conn


def archive(conn, tenant, actor, task_id, expected_version):
    """Return 200, 403, 404 or 409. Audit and event commit with the update."""
    with conn:
        member = conn.execute(
            'SELECT role FROM members WHERE tenant = ? AND actor = ?',
            (tenant, actor),
        ).fetchone()
        if member is None or member[0] not in ('owner', 'editor'):
            return 403

        task = conn.execute(
            'SELECT state, version FROM tasks WHERE tenant = ? AND id = ?',
            (tenant, task_id),
        ).fetchone()
        if task is None:
            return 404
        if task[0] != 'open' or task[1] != expected_version:
            return 409

        updated = conn.execute(
            "UPDATE tasks SET state = 'archived', version = version + 1 "
            "WHERE tenant = ? AND id = ? AND state = 'open' AND version = ?",
            (tenant, task_id, expected_version),
        )
        if updated.rowcount != 1:
            return 409

        new_version = task[1] + 1
        conn.execute(
            'INSERT INTO audit (tenant, task, actor, version) VALUES (?, ?, ?, ?)',
            (tenant, task_id, actor, new_version),
        )
        conn.execute(
            'INSERT INTO outbox (tenant, task, version) VALUES (?, ?, ?)',
            (tenant, task_id, new_version),
        )
    return 200
