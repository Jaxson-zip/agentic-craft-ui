"""
Repo Map Generator - 零依赖代码骨架与拓扑树生成器
用于在不读取完整代码的情况下，提取项目的导出函数、类型、组件与符号，极大节省 Token，防止长上下文漂移。
"""
import os
import re
import sys
from pathlib import Path

def extract_exports(file_path):
    try:
        content = file_path.read_text(encoding='utf-8')
    except Exception:
        return []

    signatures = []
    patterns = [
        r'export\s+(?:async\s+)?function\s+([a-zA-Z0-9_]+)\s*\(([^)]*)\)',
        r'export\s+const\s+([a-zA-Z0-9_]+)\s*=',
        r'export\s+(?:type|interface)\s+([a-zA-Z0-9_]+)',
        r'export\s+class\s+([a-zA-Z0-9_]+)',
        r'export\s+default\s+(?:function\s+)?([a-zA-Z0-9_]+)?',
    ]

    for p in patterns:
        for match in re.finditer(p, content):
            matched_text = match.group(0).strip()
            if len(matched_text) > 80:
                matched_text = matched_text[:77] + '...'
            signatures.append(matched_text)
            
    return list(set(signatures))

def generate_repo_map(root_dir="src"):
    target = Path(root_dir)
    if not target.exists():
        print(f"Directory {root_dir} not found.")
        return

    output = []
    output.append(f"=== REPO TOPOLOGY MAP ({root_dir}/) ===")
    
    file_count = 0
    for root, dirs, files in os.walk(target):
        dirs[:] = [d for d in dirs if d not in ['node_modules', '.git', '.next', 'dist', 'build']]
        for file in files:
            if file.endswith(('.ts', '.tsx', '.js', '.jsx')):
                p = Path(root) / file
                rel_path = p.as_posix()
                exports = extract_exports(p)
                if exports:
                    file_count += 1
                    output.append(f"\n📄 {rel_path}")
                    for exp in sorted(exports)[:8]:
                        output.append(f"   ├─ {exp}")

    output.append(f"\nTotal indexed: {file_count} files.")
    return "\n".join(output)

if __name__ == "__main__":
    scan_dir = sys.argv[1] if len(sys.argv) > 1 else "src"
    result = generate_repo_map(scan_dir)
    print(result)
