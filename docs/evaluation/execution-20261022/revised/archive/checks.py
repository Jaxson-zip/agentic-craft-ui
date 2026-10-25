import sqlite3
import tempfile
import unittest
from pathlib import Path
from service import archive, connect


class ArchiveChecks(unittest.TestCase):
    def setUp(self):
        self.conn = connect()
        self.addCleanup(self.conn.close)

    def snapshot(self):
        return [self.conn.execute('SELECT * FROM ' + table).fetchall()
                for table in ('tasks', 'audit', 'outbox')]

    def test_success_is_scoped_and_writes_related_records(self):
        self.assertEqual(archive(self.conn, 'a', 'editor', '1', 1), 200)
        tasks, audit, outbox = self.snapshot()
        self.assertEqual(tasks, [('a','1','archived',2), ('b','1','open',1)])
        self.assertEqual(audit, [('a','1','editor',2)])
        self.assertEqual(outbox, [('a','1',2)])

    def test_viewer_and_non_member_have_no_side_effects(self):
        before = self.snapshot()
        for tenant, actor in [('a','viewer'), ('b','viewer'), ('a','unknown')]:
            self.assertEqual(archive(self.conn, tenant, actor, '1', 1), 403)
            self.assertEqual(self.snapshot(), before)

    def test_missing_conflict_and_duplicate_have_no_side_effects(self):
        before = self.snapshot()
        self.assertEqual(archive(self.conn, 'a', 'editor', 'missing', 1), 404)
        self.assertEqual(archive(self.conn, 'a', 'editor', '1', 0), 409)
        self.assertEqual(self.snapshot(), before)
        self.assertEqual(archive(self.conn, 'a', 'editor', '1', 1), 200)
        after = self.snapshot()
        self.assertEqual(archive(self.conn, 'a', 'editor', '1', 1), 409)
        self.assertEqual(archive(self.conn, 'a', 'editor', '1', 2), 409)
        self.assertEqual(self.snapshot(), after)

    def test_event_failure_rolls_back_task_and_audit(self):
        self.conn.execute("CREATE TRIGGER fail_event BEFORE INSERT ON outbox BEGIN SELECT RAISE(ABORT,'event unavailable'); END")
        before = self.snapshot()
        with self.assertRaises(sqlite3.DatabaseError):
            archive(self.conn, 'a', 'editor', '1', 1)
        self.assertEqual(self.snapshot(), before)

    def test_owner_can_archive_in_their_tenant(self):
        self.assertEqual(archive(self.conn, 'b', 'editor', '1', 1), 200)
        tasks, audit, outbox = self.snapshot()
        self.assertEqual(tasks, [('a','1','open',1), ('b','1','archived',2)])
        self.assertEqual(audit, [('b','1','editor',2)])
        self.assertEqual(outbox, [('b','1',2)])

    def test_audit_failure_rolls_back_and_allows_recovery(self):
        self.conn.execute("CREATE TRIGGER fail_audit BEFORE INSERT ON audit BEGIN SELECT RAISE(ABORT,'audit unavailable'); END")
        before = self.snapshot()
        with self.assertRaises(sqlite3.DatabaseError):
            archive(self.conn, 'a', 'editor', '1', 1)
        self.assertEqual(self.snapshot(), before)
        self.assertFalse(self.conn.in_transaction)
        self.conn.execute('DROP TRIGGER fail_audit')
        self.assertEqual(archive(self.conn, 'a', 'editor', '1', 1), 200)

    def test_success_is_committed_for_another_connection(self):
        with tempfile.TemporaryDirectory() as directory:
            path = str(Path(directory) / 'archive.sqlite')
            writer = sqlite3.connect(path)
            reader = sqlite3.connect(path)
            try:
                self.conn.backup(writer)
                self.assertEqual(archive(writer, 'a', 'editor', '1', 1), 200)
                self.assertFalse(writer.in_transaction)
                self.assertEqual(reader.execute(
                    "SELECT state, version FROM tasks WHERE tenant='a' AND id='1'"
                ).fetchone(), ('archived', 2))
                self.assertEqual(reader.execute('SELECT * FROM audit').fetchall(),
                                 [('a','1','editor',2)])
                self.assertEqual(reader.execute('SELECT * FROM outbox').fetchall(),
                                 [('a','1',2)])
                self.assertEqual(archive(reader, 'a', 'editor', '1', 1), 409)
            finally:
                reader.close()
                writer.close()


if __name__ == '__main__':
    unittest.main()
