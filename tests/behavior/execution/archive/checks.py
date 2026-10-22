import sqlite3
import unittest
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


if __name__ == '__main__':
    unittest.main()
