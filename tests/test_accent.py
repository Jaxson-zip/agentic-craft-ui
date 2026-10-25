"""The accent generator must produce readable text and focus colors for any brand hue."""
from pathlib import Path
import subprocess
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import accent  # noqa: E402

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts' / 'accent.py'


class AccentTests(unittest.TestCase):
    def test_reference_brand_colors_all_pass(self):
        # visual-style.md 选色表里的全部颜色，以及很浅的黄色这类难例
        for brand in ('#4772FA', '#5B5BD6', '#30CF79', '#14B8A6', '#FF5C00', '#E8A100', '#7B61FF', '#D946EF',
                      '#0033FF', '#5672CD', '#E8590C', '#4969ED', '#FFD60A', '#000000'):
            with self.subTest(brand=brand):
                _, _, checks = accent.build(brand)
                for name, value, target in checks:
                    self.assertGreaterEqual(value, target, name)

    def test_round_trip_keeps_hue(self):
        lightness, chroma, hue = accent.to_oklch('#4772FA')
        back = accent.to_oklch(accent.from_oklch(lightness, chroma, hue))
        self.assertAlmostEqual(back[0], lightness, places=2)
        self.assertAlmostEqual(back[2], hue, delta=1)

    def test_avoid_flags_close_hues_only(self):
        # 小红书红和橙色太近；和蓝色、灰色都能共存
        self.assertLess(accent.hue_distance('#FF5C00', '#FF2442'), 30)
        self.assertGreater(accent.hue_distance('#4772FA', '#FF2442'), 30)
        self.assertIsNone(accent.hue_distance('#4772FA', '#777777'))
        clash = subprocess.run([sys.executable, '-X', 'utf8', str(SCRIPT), '#FF5C00', '--avoid', '#FF2442'], capture_output=True, text=True, encoding='utf-8')
        self.assertEqual(clash.returncode, 1)
        self.assertIn('冲突', clash.stdout)
        fine = subprocess.run([sys.executable, '-X', 'utf8', str(SCRIPT), '#4772FA', '--avoid', '#FF2442,#07C160'], capture_output=True, text=True, encoding='utf-8')
        self.assertEqual(fine.returncode, 0, fine.stdout)

    def test_cli_prints_tokens_and_rejects_bad_input(self):
        ok = subprocess.run([sys.executable, '-X', 'utf8', str(SCRIPT), '#30CF79'], capture_output=True, text=True, encoding='utf-8')
        self.assertEqual(ok.returncode, 0, ok.stderr)
        self.assertIn('--accent-text', ok.stdout)
        bad = subprocess.run([sys.executable, '-X', 'utf8', str(SCRIPT), 'green'], capture_output=True, text=True, encoding='utf-8')
        self.assertEqual(bad.returncode, 2)


if __name__ == '__main__':
    unittest.main()
