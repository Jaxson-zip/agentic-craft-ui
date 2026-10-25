"""Exercise actual installs in temporary folders; no user installation is touched."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts' / 'sync_skill.py'
REPO = SCRIPT.parent.parent


class SyncTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / 'source'
        self.target = self.root / 'installed'
        self.backups = self.root / 'backups'
        self.source.mkdir()
        self.write(self.source, 'SKILL.md', '---\nname: sample\ndescription: Use for sample work\n---\n# Sample\n')
        self.write(self.source, 'references/ui.md', '中文 current rules\n')

    def write(self, root, relative, value):
        file = root / relative
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_text(value, encoding='utf-8')
        return file

    def run_sync(self, *args, source=None, target=None):
        return subprocess.run([sys.executable, '-X', 'utf8', str(SCRIPT),
                               str(target or self.target), '--source', str(source or self.source),
                               *map(str, args)], capture_output=True, text=True, encoding='utf-8')

    def apply(self, *args):
        return self.run_sync('--apply', '--backup-dir', self.backups, *args)

    def test_default_is_read_only_and_reports_missing(self):
        result = self.run_sync()
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertFalse(self.target.exists())
        self.assertIn('SKILL.md', json.loads(result.stdout)['missing'])

    def test_apply_backs_up_verifies_hashes_and_is_idempotent(self):
        self.write(self.target, 'SKILL.md', 'old rules')
        result = self.apply()
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        backup = Path(report['backup'])
        self.assertEqual((backup / 'SKILL.md').read_text(encoding='utf-8'), 'old rules')
        manifest_path = self.target / '.craft-install.json'
        manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
        for name, digest in manifest['files'].items():
            self.assertEqual(hashlib.sha256((self.target / name).read_bytes()).hexdigest(), digest)
        manifest_bytes = manifest_path.read_bytes()
        backup_count = len(list(self.backups.iterdir()))
        second = self.apply()
        self.assertEqual(second.returncode, 0, second.stderr)
        self.assertIsNone(json.loads(second.stdout)['backup'])
        self.assertEqual(len(list(self.backups.iterdir())), backup_count)
        self.assertEqual(manifest_path.read_bytes(), manifest_bytes)
        self.assertEqual(self.run_sync().returncode, 0)

    def test_extra_file_is_preserved_unless_prune_is_explicit(self):
        self.write(self.target, 'custom.txt', 'keep this')
        self.assertEqual(self.apply().returncode, 2)
        self.assertFalse((self.target / 'SKILL.md').exists())
        result = self.apply('--prune')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse((self.target / 'custom.txt').exists())
        self.assertEqual((Path(json.loads(result.stdout)['backup']) / 'custom.txt').read_text(), 'keep this')

    def test_nested_skill_in_source_fails_before_writes(self):
        self.write(self.source, 'docs/history/SKILL.md', 'old entry')
        result = self.apply('--with-dev')
        self.assertEqual(result.returncode, 2)
        self.assertFalse(self.target.exists())
        self.assertIn('SKILL.md', result.stderr)

    def test_old_nested_entry_in_target_is_backed_up_and_pruned(self):
        self.write(self.target, 'docs/history/SKILL.md', 'old entry')
        result = self.apply('--prune')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual([p.relative_to(self.target).as_posix() for p in self.target.rglob('SKILL.md')], ['SKILL.md'])
        backup = Path(json.loads(result.stdout)['backup'])
        self.assertEqual((backup / 'docs/history/SKILL.md').read_text(), 'old entry')

    def test_overlapping_source_and_destination_are_refused(self):
        for target in (self.source, self.source / 'installed', self.root):
            result = self.run_sync('--apply', target=target)
            self.assertEqual(result.returncode, 2, result.stderr)

    def test_existing_changes_require_external_backup_location(self):
        self.write(self.target, 'SKILL.md', 'old')
        self.assertEqual(self.run_sync('--apply').returncode, 2)
        result = self.run_sync('--apply', '--backup-dir', self.target / 'backup')
        self.assertEqual(result.returncode, 2)
        self.assertEqual((self.target / 'SKILL.md').read_text(), 'old')

    def test_git_checkout_is_not_an_install_destination(self):
        self.write(self.target, '.git', 'gitdir: elsewhere')
        result = self.apply()
        self.assertEqual(result.returncode, 2)
        self.assertFalse((self.target / 'SKILL.md').exists())

    def test_file_directory_collision_is_rejected_before_writes(self):
        self.write(self.target, 'references', 'local file')
        result = self.apply('--prune')
        self.assertEqual(result.returncode, 2)
        self.assertFalse((self.target / 'SKILL.md').exists())

    def test_manifest_directory_collision_is_rejected_before_writes(self):
        (self.target / '.craft-install.json').mkdir(parents=True)
        result = self.apply()
        self.assertEqual(result.returncode, 2)
        self.assertFalse((self.target / 'SKILL.md').exists())

    def test_manifest_only_install_is_backed_up_before_overwrite(self):
        self.write(self.target, '.craft-install.json', 'old manifest')
        self.assertEqual(self.run_sync('--apply').returncode, 2)
        result = self.apply()
        self.assertEqual(result.returncode, 0, result.stderr)
        backup = Path(json.loads(result.stdout)['backup'])
        self.assertEqual((backup / '.craft-install.json').read_text(), 'old manifest')

    @unittest.skipUnless(os.name == 'nt', 'Windows case-insensitive filesystem regression')
    def test_windows_case_alias_is_not_pruned_after_update(self):
        self.write(self.target, 'References/UI.md', 'old content')
        result = self.apply('--prune')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual((self.target / 'references/ui.md').read_bytes(), (self.source / 'references/ui.md').read_bytes())
        self.assertEqual(self.run_sync().returncode, 0)

    def test_check_does_not_trust_saved_manifest(self):
        result = self.apply()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.write(self.target, 'references/ui.md', 'tampered')
        check = self.run_sync()
        self.assertEqual(check.returncode, 1)
        self.assertIn('references/ui.md', json.loads(check.stdout)['changed'])

    def test_only_package_resources_are_installed_and_caches_are_ignored(self):
        self.write(self.source, '.env', 'private')
        self.write(self.source, '.git/config', 'private')
        self.write(self.source, 'scripts/__pycache__/sample.pyc', 'cache')
        self.write(self.source, '.github/workflows/check.yml', 'ci')
        result = self.apply()
        self.assertEqual(result.returncode, 0, result.stderr)
        for name in ('.env', '.git', 'scripts/__pycache__', '.github'):
            self.assertFalse((self.target / name).exists())

    def test_default_install_skips_maintenance_folders(self):
        self.write(self.source, 'docs/CASE.md', 'case study')
        self.write(self.source, 'tests/test_sample.py', 'regression')
        result = self.apply()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((self.target / 'references/ui.md').exists())
        self.assertFalse((self.target / 'docs').exists())
        self.assertFalse((self.target / 'tests').exists())
        dev = self.apply('--with-dev')
        self.assertEqual(dev.returncode, 0, dev.stderr)
        self.assertTrue((self.target / 'docs/CASE.md').exists())
        self.assertTrue(json.loads((self.target / '.craft-install.json').read_text(encoding='utf-8'))['with_dev'])
        # Going back to the runtime package treats maintenance files as extra.
        self.assertIn('tests/test_sample.py', json.loads(self.run_sync().stdout)['extra'])

    def test_link_in_package_is_refused(self):
        external = self.write(self.root, 'external.txt', 'external')
        link = self.source / 'references' / 'linked.md'
        try:
            link.symlink_to(external)
        except OSError as error:
            self.skipTest('symlinks unavailable: ' + str(error))
        result = self.apply()
        self.assertEqual(result.returncode, 2)
        self.assertFalse(self.target.exists())

    @unittest.skipUnless(os.name == 'nt', 'Windows junction regression')
    def test_windows_junction_in_package_is_refused(self):
        external = self.root / 'external'
        external.mkdir()
        link = self.source / 'assets'
        created = subprocess.run(['cmd', '/c', 'mklink', '/J', str(link), str(external)],
                                 capture_output=True)
        if created.returncode:
            self.skipTest('junction creation unavailable')
        result = self.apply()
        self.assertEqual(result.returncode, 2)
        self.assertIn('Linked paths', result.stderr)
        self.assertFalse(self.target.exists())

    def test_current_repository_has_no_nested_discovery_entry(self):
        result = self.run_sync(source=REPO)
        self.assertEqual(result.returncode, 1, result.stderr)
        missing = json.loads(result.stdout)['missing']
        self.assertIn('SKILL.md', missing)
        self.assertIn('scripts/sync_skill.py', missing)


if __name__ == '__main__':
    unittest.main()
