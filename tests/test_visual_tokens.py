"""Check shipped palette values, using WCAG relative luminance, not screenshots."""
from pathlib import Path
import re
import unittest

CSS = Path(__file__).resolve().parents[1] / 'assets' / 'themes.css'


def ratio(a, b, backdrop='#FFFFFF'):
    def rgb(color):
        if color.startswith('#'):
            return [int(color[i:i+2], 16) / 255 for i in (1, 3, 5)]
        match = re.fullmatch(r'rgba\(([^)]+)\)', color)
        if not match:
            raise ValueError(f'unsupported color: {color}')
        r, g, blue, alpha = map(float, match[1].split(','))
        return [value / 255 * alpha + under * (1-alpha) for value, under in zip((r, g, blue), rgb(backdrop))]
    def luminance(color):
        channels = rgb(color)
        linear = [x / 12.92 if x <= .04045 else ((x + .055) / 1.055) ** 2.4 for x in channels]
        return sum(x * y for x, y in zip(linear, (.2126, .7152, .0722)))
    lo, hi = sorted((luminance(a), luminance(b)))
    return (hi + .05) / (lo + .05)


class PaletteTests(unittest.TestCase):
    def themes(self):
        source = re.sub(r'/\*.*?\*/', '', CSS.read_text(encoding='utf-8'), flags=re.S)
        base = dict(re.findall(r'(--[\w-]+):\s*([^;]+);', source.split('}', 1)[0]))
        dark = dict(base)
        block = source.split('[data-theme="dark"]', 1)[1].split('}', 1)[0]
        dark.update(re.findall(r'(--[\w-]+):\s*([^;]+);', block))
        return {'light': base, 'dark': dark}

    def test_informational_text_on_all_shipped_surfaces(self):
        for theme, tokens in self.themes().items():
            for text in ('--text-primary', '--text-secondary', '--text-muted'):
                for surface in ('--bg-page', '--bg-card', '--bg-card-hover', '--bg-muted'):
                    with self.subTest(theme=theme, text=text, surface=surface):
                        self.assertGreaterEqual(ratio(tokens[text], tokens[surface]), 4.5)

    def test_status_labels_are_readable(self):
        for theme, tokens in self.themes().items():
            for status in ('success', 'warning', 'danger', 'neutral'):
                with self.subTest(theme=theme, status=status):
                    self.assertGreaterEqual(ratio(tokens[f'--badge-{status}-text'], tokens[f'--badge-{status}-bg'], tokens['--bg-card']), 4.5)

    def test_primary_action_all_states_and_focus(self):
        for theme, tokens in self.themes().items():
            for state in ('', '-hover', '-active'):
                with self.subTest(theme=theme, state=state):
                    self.assertGreaterEqual(ratio(tokens['--on-brand'], tokens['--brand-primary' + state]), 4.5)
            for surface in ('--bg-page', '--bg-card', '--bg-muted'):
                with self.subTest(theme=theme, focus_surface=surface):
                    self.assertGreaterEqual(ratio(tokens['--focus-ring'], tokens[surface]), 3)

    def test_used_custom_properties_are_defined(self):
        source = CSS.read_text(encoding='utf-8')
        used = set(re.findall(r'var\((--[\w-]+)', source))
        for theme, tokens in self.themes().items():
            with self.subTest(theme=theme):
                self.assertTrue(used.issubset(tokens), used - tokens.keys())

    def test_control_state_foreground_background_pairs(self):
        for theme, tokens in self.themes().items():
            for foreground, background in (
                ('--control-disabled-text', '--control-disabled-bg'),
                ('--control-selected-text', '--control-selected-bg'),
                ('--field-placeholder', '--field-bg'),
                ('--text-primary', '--field-bg'),
            ):
                with self.subTest(theme=theme, foreground=foreground):
                    self.assertGreaterEqual(ratio(tokens[foreground], tokens[background]), 4.5)

    def test_field_and_selected_boundaries(self):
        for theme, tokens in self.themes().items():
            for border, surface in (
                ('--field-border', '--field-bg'),
                ('--field-invalid-border', '--field-bg'),
                ('--control-selected-border', '--control-selected-bg'),
            ):
                with self.subTest(theme=theme, border=border):
                    self.assertGreaterEqual(ratio(tokens[border], tokens[surface]), 3)

    def test_reference_calculation_and_transparency(self):
        self.assertAlmostEqual(ratio('#000000', '#FFFFFF'), 21)
        self.assertAlmostEqual(ratio('#FF0000', '#FFFFFF'), 3.99847677, places=6)
        self.assertAlmostEqual(ratio('#FFFFFF', 'rgba(0,0,0,0.5)'), ratio('#FFFFFF', '#808080'), delta=.03)


if __name__ == '__main__':
    unittest.main()
