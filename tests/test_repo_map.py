"""Observable indexing and freshness behavior; all fixtures stay in temp dirs."""
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "repo_map.py"
SPEC = importlib.util.spec_from_file_location("repo_map", SCRIPT)
MAP = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MAP)


class ExportRegressionTests(unittest.TestCase):
    def exports(self, source, suffix=".ts"):
        with tempfile.TemporaryDirectory() as folder:
            file = Path(folder) / ("sample" + suffix)
            file.write_text(source, encoding="utf-8")
            return "\n".join(MAP.extract_exports(file))

    def test_comment_and_string_exports_are_not_symbols(self):
        symbols = self.exports('''// export function fake() {}
/* export const ghost = 1; */
const text = "export class Imaginary {}";
const template = `export interface Pretend {}`;
export const real = 1;
''')
        self.assertIn("real", symbols)
        for name in ("fake", "ghost", "Imaginary", "Pretend"):
            self.assertNotIn(name, symbols)

    def test_named_reexports_and_typed_variables_are_visible(self):
        symbols = self.exports('''export { renew, cancel as stop } from './api';
export type { Payload } from './types';
export const limit: number = 3;
export let state = 0;
''')
        for name in ("renew", "stop", "Payload", "limit", "state"):
            self.assertIn(name, symbols)

    def test_generic_function_and_default_class_are_named(self):
        symbols = self.exports('''export async function load<T>(callback: (x: T) => void): Promise<T> { }
export default class Client { }
''')
        self.assertIn("load", symbols)
        self.assertIn("Client", symbols)
        self.assertNotIn("export default class\n", symbols)

    def test_vue_indexes_only_script_blocks_with_original_lines(self):
        symbols = self.exports('''<template>export const Fake = 2;</template>
<script setup lang="ts">
export const real = 3;
</script>
<style>/* export class Styled {} */</style>
''', ".vue")
        self.assertIn("real", symbols)
        self.assertNotIn("Fake", symbols)
        self.assertNotIn("Styled", symbols)
        self.assertIn("L3", symbols)

    def test_const_enum_is_not_a_variable_named_enum(self):
        symbols = self.exports("export const enum Status { Active, Inactive }")
        self.assertIn("Status", symbols)
        self.assertNotIn("const enum\n", symbols)

    def test_generator_functions_are_visible(self):
        symbols = self.exports("export function* items() {}\nexport async function*stream() {}")
        self.assertIn("items", symbols)
        self.assertIn("stream", symbols)

    def test_vue_commented_scripts_do_not_become_symbols(self):
        symbols = self.exports('''<!-- <script>export const Ghost = 1;</script> -->
<script>
const marker = '<!--';
export const Real = 1;
</script>
''', ".vue")
        self.assertNotIn("Ghost", symbols)
        self.assertIn("Real", symbols)
        self.assertIn("L4", symbols)


class CliTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def write(self, name, content):
        file = self.root / name
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_text(content, encoding="utf-8")
        return file

    def run_map(self, *args):
        return subprocess.run(
            [sys.executable, str(SCRIPT), str(self.root), *map(str, args)],
            capture_output=True, text=True, encoding="utf-8",
            env={**os.environ, "PYTHONIOENCODING": "utf-8"},
        )

    def json_map(self, *args):
        result = self.run_map("--format", "json", *args)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(result.stdout.lstrip().startswith("{"), result.stdout)
        return json.loads(result.stdout)

    def snapshot(self):
        path = self.root / "docs" / "snapshot.json"
        result = self.run_map("--snapshot", path)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(path.exists(), "snapshot was not written")
        return path

    def test_files_without_exports_and_vue_are_in_inventory(self):
        self.write("src/side-effect.js", "window.ready = true;")
        self.write("src/Screen.vue", "<template>Hello</template>")
        self.write("node_modules/pkg/index.js", "export const ignored = 1;")
        data = self.json_map()
        self.assertEqual([f["path"] for f in data["files"]],
                         ["src/Screen.vue", "src/side-effect.js"])
        self.assertEqual(data["files"][0]["symbols"], [])

    def test_no_silent_symbol_cap_and_explicit_truncation(self):
        self.write("src/many.ts", "\n".join(f"export const item{i} = {i};" for i in range(12)))
        data = self.json_map()
        self.assertEqual(len(data["files"][0]["symbols"]), 12)
        limited = self.json_map("--max-symbols", "3")
        self.assertEqual(len(limited["files"][0]["symbols"]), 3)
        self.assertEqual(limited["files"][0]["omitted_symbols"], 9)

    def test_output_order_and_fingerprint_are_repeatable(self):
        self.write("src/z.ts", "export const z = 1;")
        self.write("src/a.ts", "export const a = 1;")
        first, second = self.json_map(), self.json_map()
        self.assertEqual(first["files"], second["files"])
        self.assertEqual(first["fingerprint"], second["fingerprint"])
        self.assertEqual([f["path"] for f in first["files"]], ["src/a.ts", "src/z.ts"])

    def test_snapshot_detects_body_change_even_when_exports_unchanged(self):
        file = self.write("src/a.ts", "export const value = 1;")
        snapshot = self.snapshot()
        self.assertEqual(self.run_map("--check", snapshot).returncode, 0)
        file.write_text("export const value = 2;", encoding="utf-8")
        result = self.run_map("--check", snapshot)
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn("stale", result.stdout.lower())

    def test_snapshot_detects_file_addition_and_deletion(self):
        first = self.write("src/a.ts", "export const a = 1;")
        snapshot = self.snapshot()
        second = self.write("src/b.ts", "export const b = 2;")
        self.assertEqual(self.run_map("--check", snapshot).returncode, 1)
        second.unlink()
        self.assertEqual(self.run_map("--check", snapshot).returncode, 0)
        first.unlink()
        self.assertEqual(self.run_map("--check", snapshot).returncode, 1)

    def test_snapshot_detects_config_change_and_root_mismatch(self):
        self.write("src/a.ts", "export const a = 1;")
        config = self.write("package.json", '{"scripts":{"build":"vite build"}}')
        snapshot = self.snapshot()
        config.write_text('{"scripts":{"build":"nuxt build"}}', encoding="utf-8")
        self.assertEqual(self.run_map("--check", snapshot).returncode, 1)
        other = self.root / "other"
        other.mkdir()
        result = subprocess.run([sys.executable, str(SCRIPT), str(other), "--check", str(snapshot)],
                                capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(result.returncode, 2, result.stderr)

    def test_missing_root_and_malformed_snapshot_fail_clearly(self):
        missing = self.root / "absent"
        result = subprocess.run([sys.executable, str(SCRIPT), str(missing)],
                                capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(result.returncode, 2)
        snapshot = self.write("snapshot.json", "not json")
        self.assertEqual(self.run_map("--check", snapshot).returncode, 2)

    def test_invalid_utf8_is_reported_and_not_a_fresh_snapshot(self):
        (self.root / "bad.ts").write_bytes(b"\xff")
        result = self.run_map("--format", "json")
        self.assertEqual(result.returncode, 2, result.stderr)
        data = json.loads(result.stdout)
        self.assertTrue(data["warnings"])

    def test_markdown_output_has_line_locations_and_limit_notice(self):
        self.write("src/a.ts", "// header\nexport const a = 1;\nexport const b = 2;")
        output = self.root / "docs" / "REPO_MAP.md"
        result = self.run_map("--output", output, "--max-symbols", "1")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(output.exists())
        text = output.read_text(encoding="utf-8")
        self.assertIn("L2", text)
        self.assertIn("omitted", text)
        self.assertIn("heuristic", text.lower())


if __name__ == "__main__":
    unittest.main()
