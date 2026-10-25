import unittest
from ledger import for_day


class CalendarChecks(unittest.TestCase):
    def test_local_midnight_and_half_open_end(self):
        rows = [{'id': i, 'at': at} for i, at in enumerate([
            '2026-10-20T15:59:59Z', '2026-10-20T16:00:00Z',
            '2026-10-21T15:59:59Z', '2026-10-21T16:00:00Z'])]
        self.assertEqual([r['id'] for r in for_day(rows, '2026-10-21')], [1, 2])

    def test_offsets_and_input_order(self):
        rows = [{'id': 1, 'at': '2026-10-21T23:00:00+08:00'},
                {'id': 2, 'at': '2026-10-20T09:00:00-07:00'}]
        self.assertEqual(for_day(rows, '2026-10-21'), rows)

    def test_empty_and_month_boundary(self):
        self.assertEqual(for_day([], '2026-11-01'), [])
        rows = [{'at': '2026-10-31T16:00:00Z'}]
        self.assertEqual(for_day(rows, '2026-11-01'), rows)

    def test_year_boundary_with_fractional_seconds(self):
        rows = [{'id': i, 'at': at} for i, at in enumerate([
            '2026-12-31T15:59:59.999999Z', '2026-12-31T16:00:00Z',
            '2027-01-01T15:59:59.999999Z', '2027-01-01T16:00:00Z'])]
        result = for_day(rows, '2027-01-01')
        self.assertEqual([row['id'] for row in result], [1, 2])
        self.assertIs(result[0], rows[1])
        self.assertEqual(rows[1]['at'], '2026-12-31T16:00:00Z')

    def test_naive_storage_timestamps_are_utc(self):
        rows = [{'at': '2026-10-20T16:00:00'},
                {'at': '2026-10-21T16:00:00'}]
        self.assertEqual(for_day(rows, '2026-10-21'), rows[:1])


if __name__ == '__main__':
    unittest.main()
