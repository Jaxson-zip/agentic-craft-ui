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
    raise NotImplementedError('Archive is not implemented')
