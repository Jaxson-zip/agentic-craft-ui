"""Zero-dependency, heuristic JS/TS/Vue symbol inventory and freshness check.

Not an AST, call graph, architecture generator, or dead-code detector. Ordinary
comments/strings are masked; regex literals, JSX text, complex templates and
destructuring are not fully parsed. Confirm any inference by reading source.
"""
import argparse
from datetime import datetime, timezone
import fnmatch
import hashlib
import json
import os
from pathlib import Path
import re
import sys

SCHEMA_VERSION = 1
EXTENSIONS = {".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs", ".mts", ".cts", ".vue"}
EXCLUDED = {"node_modules", ".git", ".next", ".nuxt", "dist", "build", "coverage",
            ".venv", "venv", "__pycache__", ".cache", ".output"}
CONFIG_PATTERNS = ("package.json", "package-lock.json", "pnpm-lock.yaml", "yarn.lock",
                   "bun.lock", "bun.lockb", "tsconfig*.json", "jsconfig*.json",
                   "biome.json", "biome.jsonc", ".eslintrc*", "pyproject.toml",
                   "Cargo.toml", "go.mod", "go.sum")
IDENTIFIER = r"[A-Za-z_$][\w$]*"


def blank(text):
    return "".join("\n" if char == "\n" else " " for char in text)


def mask_non_code(source):
    """Preserve positions while masking comments and quoted/template strings."""
    chars = list(source)
    index = 0
    while index < len(source):
        start = index
        if source.startswith("//", index):
            end = source.find("\n", index)
            index = len(source) if end < 0 else end
        elif source.startswith("/*", index):
            end = source.find("*/", index + 2)
            index = len(source) if end < 0 else end + 2
        elif source[index] in "\"'`":
            quote = source[index]
            index += 1
            while index < len(source):
                if source[index] == "\\":
                    index += 2
                elif source[index] == quote:
                    index += 1
                    break
                else:
                    index += 1
            index = min(index, len(source))
        else:
            index += 1
            continue
        chars[start:index] = blank(source[start:index])
    return "".join(chars)


def symbols_from_source(source, suffix):
    if suffix.lower() == ".vue":
        script_only = list(blank(source))
        # Consume whole HTML comments before they can expose fake script tags.
        # Script bodies are consumed as a unit, so '<!--' inside JS stays intact.
        blocks = r"<!--[\s\S]*?(?:-->|$)|<script\b[^>]*>(.*?)</script\s*>"
        for match in re.finditer(blocks, source, re.I | re.S):
            if match.group(1) is not None:
                script_only[match.start(1):match.end(1)] = match.group(1)
        source = "".join(script_only)
    masked = mask_non_code(source)
    symbols = []

    def add(name, kind, position):
        symbols.append({"name": name, "kind": kind,
                        "line": source.count("\n", 0, position) + 1})

    declaration = re.compile(
        rf"\bexport\s+(?:declare\s+)?(?:(default)\s+)?(?:async\s+)?"
        rf"(abstract\s+class|const\s+enum|function|class|const|let|var|type|interface|enum)"
        rf"(?:\s*\*\s*|\s+)({IDENTIFIER})"
    )
    covered_defaults = set()
    for match in declaration.finditer(masked):
        kind = " ".join(match.group(2).split())
        if match.group(1):
            kind = "default " + kind
            covered_defaults.add(match.start())
        add(match.group(3), kind, match.start())
    for match in re.finditer(r"\bexport\s+(?:type\s+)?\{([^}]*)\}", masked, re.S):
        for item in match.group(1).split(","):
            item = re.sub(r"^\s*type\s+", "", item).strip()
            name = re.split(r"\s+as\s+", item)[-1].strip()
            if re.fullmatch(IDENTIFIER, name):
                add(name, "named export", match.start())
    for match in re.finditer(rf"\bexport\s+(?:type\s+)?\*(?:\s+as\s+({IDENTIFIER}))?", masked):
        add(match.group(1) or "*", "re-export", match.start())
    for match in re.finditer(r"\bexport\s+default\b", masked):
        if match.start() not in covered_defaults:
            add("default", "default export", match.start())
    return sorted(symbols, key=lambda item: (item["line"], item["name"], item["kind"]))


def extract_exports(file_path):
    """Compatibility helper; read failures propagate rather than looking empty."""
    path = Path(file_path)
    source = path.read_text(encoding="utf-8-sig")
    return [f"L{s['line']} {s['kind']} {s['name']}"
            for s in symbols_from_source(source, path.suffix)]


def collect(root_dir, max_symbols=0):
    root = Path(root_dir).resolve()
    if not root.is_dir():
        raise ValueError(f"Project directory does not exist: {root}")
    files, configs, warnings = [], [], []
    candidates = []
    for directory, dirs, names in os.walk(root, onerror=lambda err: warnings.append(str(err))):
        dirs[:] = sorted(d for d in dirs if d not in EXCLUDED
                         and not (Path(directory) / d).is_symlink())
        for name in sorted(names):
            path = Path(directory) / name
            is_source = path.suffix.lower() in EXTENSIONS
            is_config = any(fnmatch.fnmatch(name, pattern) for pattern in CONFIG_PATTERNS)
            if not (is_source or is_config):
                continue
            if path.is_symlink():
                warnings.append(f"Skipped symlink: {path.relative_to(root).as_posix()}")
                continue
            candidates.append((path, is_source))
    for path, is_source in sorted(candidates, key=lambda item: item[0].relative_to(root).as_posix()):
        relative = path.relative_to(root).as_posix()
        try:
            content = path.read_bytes()
            digest = hashlib.sha256(content).hexdigest()
            entry = {"path": relative, "sha256": digest}
            if is_source:
                symbols = symbols_from_source(content.decode("utf-8-sig"), path.suffix)
                kept = symbols[:max_symbols] if max_symbols else symbols
                entry.update(symbols=kept, omitted_symbols=len(symbols) - len(kept))
                files.append(entry)
            else:
                configs.append(entry)
        except (OSError, UnicodeError) as error:
            warnings.append(f"Cannot index {relative}: {error}")
    manifest = sorted((entry["path"], entry["sha256"]) for entry in files + configs)
    fingerprint = hashlib.sha256(json.dumps(manifest, ensure_ascii=True).encode("utf-8")).hexdigest()
    return {"schema_version": SCHEMA_VERSION, "root": str(root),
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "indexer": "heuristic JS/TS/Vue exports; not an AST or dependency graph",
            "max_symbols": max_symbols, "fingerprint": fingerprint,
            "files": files, "configs": configs, "warnings": warnings}


def render_markdown(data):
    lines = ["# Repository Symbol Map", "", f"Root: `{data['root']}`",
             f"Generated (UTC): {data['generated_at']}",
             f"Fingerprint: `{data['fingerprint']}`", "",
             "Heuristic inventory, not an AST or dependency graph. Confirm symbols in source.", "",
             "Scope: JS/TS/Vue files and selected project manifests/lockfiles; "
             "excluded dependency/build directories are not watched.", ""]
    for entry in data["files"]:
        lines.extend([f"## {entry['path']}", ""])
        if not entry["symbols"]:
            lines.append("- No recognized exports; file still indexed.")
        for symbol in entry["symbols"]:
            lines.append(f"- L{symbol['line']}: {symbol['kind']} `{symbol['name']}`")
        if entry["omitted_symbols"]:
            lines.append(f"- {entry['omitted_symbols']} symbols omitted by --max-symbols.")
        lines.append("")
    lines.append(f"Indexed: {len(data['files'])} source files, {len(data['configs'])} config/lockfiles.")
    for warning in data["warnings"]:
        lines.append(f"WARNING: {warning}")
    return "\n".join(lines) + "\n"


def generate_repo_map(root_dir="src"):
    return render_markdown(collect(root_dir))


def write_utf8(path, text):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", default=".", help="project root (default: current directory)")
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown")
    parser.add_argument("--output", type=Path, help="write inventory as UTF-8 instead of stdout")
    parser.add_argument("--snapshot", type=Path, help="also save JSON fingerprint inventory")
    parser.add_argument("--check", type=Path, help="check an existing JSON snapshot without updating it")
    parser.add_argument("--max-symbols", type=int, default=0, help="per-file cap; 0 shows all")
    args = parser.parse_args(argv)
    if args.max_symbols < 0:
        parser.error("--max-symbols must be nonnegative")
    if args.check and (args.output or args.snapshot):
        parser.error("--check cannot be combined with --output or --snapshot")
    try:
        data = collect(args.root, args.max_symbols)
        if args.check:
            old = json.loads(args.check.read_text(encoding="utf-8-sig"))
            if not isinstance(old, dict) or old.get("schema_version") != SCHEMA_VERSION:
                raise ValueError("Invalid snapshot schema; regenerate the snapshot")
            if old.get("root") != data["root"] or not isinstance(old.get("fingerprint"), str):
                raise ValueError("Snapshot belongs to a different root or lacks a fingerprint")
            if data["warnings"] or old.get("warnings"):
                raise ValueError("Incomplete inventory cannot be certified fresh")
            fresh = old["fingerprint"] == data["fingerprint"]
            print("Snapshot fresh (within indexed scope)." if fresh else "Snapshot stale; regenerate and review architecture.")
            return 0 if fresh else 1
        rendered = (json.dumps(data, ensure_ascii=False, indent=2) + "\n"
                    if args.format == "json" else render_markdown(data))
        if args.output:
            write_utf8(args.output, rendered)
        else:
            print(rendered, end="")
        if args.snapshot and not data["warnings"]:
            write_utf8(args.snapshot, json.dumps(data, ensure_ascii=False, indent=2) + "\n")
        if data["warnings"]:
            for warning in data["warnings"]:
                print(warning, file=sys.stderr)
            return 2
        return 0
    except (OSError, ValueError) as error:
        print(f"repo_map: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    sys.exit(main())
