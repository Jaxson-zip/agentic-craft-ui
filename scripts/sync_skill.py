"""Check or install this skill with content hashes and an external backup.

Python standard library only. Exit 0: identical/installed, 1: drift (read-only),
2: invalid input or failure. Not a concurrent installer or an atomic tree swap.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import stat
import sys
import tempfile

ROOT_FILES = ('SKILL.md', 'README.md', 'LICENSE')
ROOT_DIRS = ('references', 'assets', 'scripts', 'agents')
# Case studies, evidence and regressions are for maintaining the skill, not running it.
DEV_DIRS = ('docs', 'tests')
IGNORED = {'.git', '__pycache__', '.pytest_cache', 'node_modules'}
MANIFEST = '.craft-install.json'


def assert_plain(path):
    """Reject symlinks and Windows junction/reparse points before resolving."""
    for part in (path, *path.parents):
        if part.is_symlink() or (part.exists() and getattr(part.lstat(), 'st_file_attributes', 0)
                                 & getattr(stat, 'FILE_ATTRIBUTE_REPARSE_POINT', 0x400)):
            raise ValueError('Linked paths are unsupported: ' + str(part))


def overlaps(left, right):
    return left == right or left in right.parents or right in left.parents


def walk_files(root):
    if not root.exists():
        return {}
    result = {}
    for folder, dirs, files in os.walk(root, followlinks=False):
        dirs[:] = sorted(name for name in dirs if name not in IGNORED)
        for name in dirs + files:
            assert_plain(Path(folder) / name)
        for name in sorted(files):
            path = Path(folder) / name
            if path.suffix in {'.pyc', '.pyo'}:
                continue
            result[path.relative_to(root).as_posix()] = path
    return result


def package_files(source, with_dev=False):
    if not (source / 'SKILL.md').is_file():
        raise ValueError('Source must contain SKILL.md')
    files = {}
    for name in ROOT_FILES:
        path = source / name
        if path.exists():
            assert_plain(path)
            if not path.is_file():
                raise ValueError('Expected a file: ' + str(path))
            files[name] = path
    for name in ROOT_DIRS + (DEV_DIRS if with_dev else ()):
        path = source / name
        assert_plain(path)
        if path.exists() and not path.is_dir():
            raise ValueError('Expected a directory: ' + str(path))
        files.update({name + '/' + rel: file for rel, file in walk_files(path).items()})
    nested = [name for name in files if Path(name).name.lower() == 'skill.md' and name != 'SKILL.md']
    if nested:
        raise ValueError('Nested SKILL.md would create duplicate discovery: ' + ', '.join(nested))
    return dict(sorted(files.items()))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def path_key(name):
    # Windows opens differently cased names as the same actual file.
    return os.path.normcase(name.replace('/', os.sep))


def atomic_write(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix='.craft-', dir=path.parent)
    try:
        with os.fdopen(descriptor, 'wb') as stream:
            stream.write(content)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def synchronize(source, destination, apply=False, prune=False, backup_dir=None, with_dev=False):
    for path in (source, destination):
        assert_plain(path)
    source, destination = source.resolve(), destination.resolve()
    if overlaps(source, destination):
        raise ValueError('Source and destination must not overlap')
    if destination.exists() and not destination.is_dir():
        raise ValueError('Destination must be a directory')
    if (destination / '.git').exists():
        raise ValueError('Refusing to overwrite a Git checkout')
    manifest_path = destination / MANIFEST
    if manifest_path.is_dir():
        raise ValueError('Manifest path is a directory: ' + str(manifest_path))
    files = package_files(source, with_dev)
    installed = walk_files(destination)
    installed.pop(MANIFEST, None)
    by_key = {path_key(name): name for name in installed}
    source_keys = {path_key(name) for name in files}
    # Reject file/directory collisions before backing up or writing any files.
    for name in files:
        target = destination / name
        if target.is_dir() or any(parent.is_file() for parent in target.parents if parent != destination):
            raise ValueError('File/directory collision: ' + str(target))
    hashes = {name: digest(path) for name, path in files.items()}
    missing = sorted(name for name in files if path_key(name) not in by_key)
    changed = sorted(name for name in files if path_key(name) in by_key
                     and digest(installed[by_key[path_key(name)]]) != hashes[name])
    extra = sorted(name for name in installed if path_key(name) not in source_keys)
    report = {'source': str(source), 'destination': str(destination), 'missing': missing,
              'changed': changed, 'extra': extra, 'backup': None,
              'files': len(files), 'applied': False}
    drift = bool(missing or changed or extra)
    if not apply:
        return report, int(drift)
    if extra and not prune:
        raise ValueError('Destination has extra files; inspect them and use --prune to archive then remove: ' + ', '.join(extra))
    has_existing = bool(installed) or manifest_path.exists()
    if drift and has_existing and backup_dir is None:
        raise ValueError('Existing changes require --backup-dir outside source and destination')
    if backup_dir is not None:
        assert_plain(backup_dir)
        backup_dir = backup_dir.resolve()
        if overlaps(backup_dir, source) or overlaps(backup_dir, destination):
            raise ValueError('Backup directory must not overlap source or destination')
    if drift and has_existing:
        backup_dir.mkdir(parents=True, exist_ok=True)
        backup = Path(tempfile.mkdtemp(prefix=destination.name + '-' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '-', dir=backup_dir))
        # Only plain, already-inspected files; keep their relative paths.
        for name, path in installed.items():
            target = backup / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, target)
            if digest(path) != digest(target):
                raise OSError('Backup verification failed: ' + str(target))
        manifest = destination / MANIFEST
        if manifest.is_file():
            shutil.copy2(manifest, backup / MANIFEST)
        report['backup'] = str(backup)
        print('Verified backup: ' + str(backup), file=sys.stderr)
    for name in missing + changed:
        atomic_write(destination / name, files[name].read_bytes())
    for name in extra:
        path = destination / name
        assert_plain(path)
        if destination not in path.resolve().parents:
            raise ValueError('Prune path escaped destination: ' + str(path))
        path.unlink()  # Full inspected file content is in the verified backup.
    actual = walk_files(destination)
    actual.pop(MANIFEST, None)
    actual_by_key = {path_key(name): path for name, path in actual.items()}
    if actual_by_key.keys() != source_keys or any(digest(actual_by_key[path_key(name)]) != expected for name, expected in hashes.items()):
        raise OSError('Post-install verification failed; use the reported backup to recover')
    manifest = {'schema': 1, 'source': str(source), 'with_dev': with_dev, 'files': hashes,
                'content_sha256': hashlib.sha256(json.dumps(hashes, sort_keys=True).encode()).hexdigest()}
    manifest_bytes = (json.dumps(manifest, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
    manifest_path = destination / MANIFEST
    if not manifest_path.exists() or manifest_path.read_bytes() != manifest_bytes:
        atomic_write(manifest_path, manifest_bytes)
    report.update(applied=True, verified_files=len(files))
    return report, 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('destination', type=Path)
    parser.add_argument('--source', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--apply', action='store_true', help='Install; default is a read-only comparison')
    parser.add_argument('--prune', action='store_true', help='With --apply, remove extra files after a verified backup')
    parser.add_argument('--backup-dir', type=Path, help='Existing changes require a backup outside source and destination')
    parser.add_argument('--with-dev', action='store_true', help='Also include docs/ and tests/ for maintaining the skill')
    args = parser.parse_args()
    try:
        report, code = synchronize(args.source, args.destination, args.apply, args.prune, args.backup_dir, args.with_dev)
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return code
    except (OSError, ValueError) as error:
        print('sync failed: ' + str(error), file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
