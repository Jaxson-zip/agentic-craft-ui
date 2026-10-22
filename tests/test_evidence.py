"""Frozen instruction bytes must survive checkout without invalidating evidence."""
import hashlib
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class EvidenceTests(unittest.TestCase):
    def test_frozen_instruction_fingerprints(self):
        for manifest, folder in (
            ('docs/evaluation/reuse-gate/before-manifest.json',
             'docs/evaluation/reuse-gate/before'),
            ('docs/evaluation/execution-20261022/before/manifest.json',
             'docs/evaluation/execution-20261022/before'),
        ):
            expected = json.loads((ROOT / manifest).read_text(encoding='utf-8'))
            for name, fingerprint in expected.items():
                with self.subTest(file=folder + '/' + name):
                    self.assertEqual(hashlib.sha256((ROOT / folder / name).read_bytes()).hexdigest(), fingerprint)


if __name__ == '__main__':
    unittest.main()
