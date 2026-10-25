"""Keep the skill small and its links valid; fail if it starts to bloat again."""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
# 运行时会被 Agent 读进上下文的文件，以及各自的字节上限（UTF-8 中文约 3 字节一个字）
BUDGET = {'SKILL.md': 6_000, 'references/ui.md': 14_000, 'references/delivery.md': 7_000}


class SkillTests(unittest.TestCase):
    def test_frontmatter_has_name_and_description(self):
        text = (ROOT / 'SKILL.md').read_text(encoding='utf-8')
        self.assertTrue(text.startswith('---\n'))
        head = text.split('---', 2)[1]
        self.assertIn('name: agentic-craft-ui', head)
        self.assertRegex(head, r'description: ".{50,}"')

    def test_context_budget(self):
        for name, limit in BUDGET.items():
            with self.subTest(file=name):
                self.assertLessEqual((ROOT / name).stat().st_size, limit)
        references = sorted(p.name for p in (ROOT / 'references').glob('*.md'))
        self.assertEqual(references, ['delivery.md', 'ui.md'], '新增参考文件前先想想能不能并进现有两篇')

    def test_relative_links_resolve(self):
        for md in [ROOT / 'SKILL.md', ROOT / 'README.md', *(ROOT / 'references').glob('*.md')]:
            for target in re.findall(r'\]\(([^)#\s]+)', md.read_text(encoding='utf-8')):
                if target.startswith(('http://', 'https://', 'mailto:')):
                    continue
                with self.subTest(file=md.name, link=target):
                    self.assertTrue((md.parent / target).exists())

    def test_patterns_page_is_self_contained(self):
        html = (ROOT / 'assets' / 'patterns.html').read_text(encoding='utf-8')
        self.assertNotRegex(html, r'<link[^>]+stylesheet')
        self.assertNotRegex(html, r'<script[^>]+src=')
        used = set(re.findall(r'var\((--[\w-]+)', html)) - {'--c', '--k'}
        defined = set(re.findall(r'(--[\w-]+)\s*:', html))
        self.assertTrue(used <= defined, used - defined)


if __name__ == '__main__':
    unittest.main()
