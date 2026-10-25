"""Generate the four accent tokens for one brand color, light and dark, with contrast checks.

Python standard library only. Usage: python scripts/accent.py "#4772FA"
Prints a CSS block to paste into themes.css; exit 1 if a required pair misses its target.
"""
import argparse
import math
import sys


def srgb_to_linear(x):
    return x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4


def linear_to_srgb(x):
    x = min(1.0, max(0.0, x))
    return 12.92 * x if x <= 0.0031308 else 1.055 * x ** (1 / 2.4) - 0.055


def hex_to_rgb(value):
    value = value.strip().lstrip('#')
    if len(value) == 3:
        value = ''.join(ch * 2 for ch in value)
    if len(value) != 6 or any(ch not in '0123456789abcdefABCDEF' for ch in value):
        raise ValueError('Expected a hex color such as #4772FA')
    return [int(value[i:i + 2], 16) / 255 for i in (0, 2, 4)]


def rgb_to_hex(rgb):
    return '#%02X%02X%02X' % tuple(round(linear_to_srgb(c) * 255) for c in rgb)


def to_oklch(hexcolor):
    r, g, b = (srgb_to_linear(c) for c in hex_to_rgb(hexcolor))
    l_ = (0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b) ** (1 / 3)
    m_ = (0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b) ** (1 / 3)
    s_ = (0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b) ** (1 / 3)
    lightness = 0.2104542553 * l_ + 0.7936177850 * m_ - 0.0040720468 * s_
    a = 1.9779984951 * l_ - 2.4285922050 * m_ + 0.4505937099 * s_
    bb = 0.0259040371 * l_ + 0.7827717662 * m_ - 0.8086757660 * s_
    return lightness, math.hypot(a, bb), math.degrees(math.atan2(bb, a)) % 360


def from_oklch(lightness, chroma, hue):
    """OKLCH to hex; chroma is reduced until the color fits in sRGB."""
    while True:
        a, b = chroma * math.cos(math.radians(hue)), chroma * math.sin(math.radians(hue))
        l_ = (lightness + 0.3963377774 * a + 0.2158037573 * b) ** 3
        m_ = (lightness - 0.1055613458 * a - 0.0638541728 * b) ** 3
        s_ = (lightness - 0.0894841775 * a - 1.2914855480 * b) ** 3
        rgb = (4.0767416621 * l_ - 3.3077115913 * m_ + 0.2309699292 * s_,
               -1.2684380046 * l_ + 2.6097574011 * m_ - 0.3413193965 * s_,
               -0.0041960863 * l_ - 0.7034186147 * m_ + 1.7076147010 * s_)
        if all(-0.001 <= c <= 1.001 for c in rgb) or chroma < 0.002:
            return rgb_to_hex(rgb)
        chroma *= 0.95


def luminance(hexcolor):
    r, g, b = (srgb_to_linear(c) for c in hex_to_rgb(hexcolor))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a, b):
    hi, lo = sorted((luminance(a), luminance(b)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)


def darkest_passing(chroma, hue, background, target, start, step):
    """Walk lightness from `start` by `step` until text on `background` reaches `target`."""
    lightness = start
    while 0 < lightness < 1:
        color = from_oklch(lightness, chroma, hue)
        if contrast(color, background) >= target:
            return color
        lightness += step
    return from_oklch(lightness - step, chroma, hue)


def build(brand):
    lightness, chroma, hue = to_oklch(brand)
    light_page, light_card, dark_card = '#FAFAF9', '#FFFFFF', '#1C1917'
    soft = from_oklch(0.965, min(chroma, 0.035), hue)
    light = {
        '--accent': brand.upper() if brand.startswith('#') else '#' + brand.upper(),
        '--accent-text': darkest_passing(chroma, hue, soft, 4.5, min(lightness, 0.6), -0.01),
        '--accent-soft': soft,
        '--focus-ring': darkest_passing(chroma, hue, light_page, 3.0, min(lightness, 0.7), -0.01),
    }
    dark_soft = from_oklch(0.28, min(chroma, 0.07), hue)
    dark = {
        '--accent': from_oklch(max(lightness, 0.7), chroma, hue),
        '--accent-text': darkest_passing(chroma, hue, dark_soft, 4.5, max(lightness, 0.72), 0.01),
        '--accent-soft': dark_soft,
        '--focus-ring': darkest_passing(chroma, hue, dark_card, 3.0, max(lightness, 0.7), 0.01),
    }
    checks = [
        ('浅色 accent-text / 白卡片', contrast(light['--accent-text'], light_card), 4.5),
        ('浅色 accent-text / accent-soft', contrast(light['--accent-text'], soft), 4.5),
        ('浅色 focus-ring / 页面', contrast(light['--focus-ring'], light_page), 3.0),
        ('深色 accent-text / 卡片', contrast(dark['--accent-text'], dark_card), 4.5),
        ('深色 accent-text / accent-soft', contrast(dark['--accent-text'], dark_soft), 4.5),
        ('深色 focus-ring / 卡片', contrast(dark['--focus-ring'], dark_card), 3.0),
    ]
    return light, dark, checks


def hue_distance(a, b):
    """Smallest OKLCH hue difference in degrees; near-gray colors have no meaningful hue."""
    la, ca, ha = to_oklch(a)
    lb, cb, hb = to_oklch(b)
    if ca < 0.04 or cb < 0.04:
        return None
    d = abs(ha - hb) % 360
    return min(d, 360 - d)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('brand', help='Brand or accent color, e.g. "#4772FA"')
    parser.add_argument('--avoid', default='', help='Comma-separated colors already prominent on the page (platform tags, key brand icons)')
    args = parser.parse_args()
    try:
        light, dark, checks = build(args.brand)
        avoid = [c.strip() for c in args.avoid.split(',') if c.strip()]
        clashes = [(c, hue_distance(args.brand, c)) for c in avoid]
    except ValueError as error:
        print('accent: ' + str(error), file=sys.stderr)
        return 2
    print('/* :root, [data-theme="light"] */')
    for key, value in light.items():
        print(f'  {key}: {value};')
    print('/* [data-theme="dark"] */')
    for key, value in dark.items():
        print(f'  {key}: {value};')
    print('/* 对比度检查 */')
    ok = True
    for name, value, target in checks:
        passed = value >= target
        ok &= passed
        print(f'/* {"通过" if passed else "未达标"} {name}: {value:.2f} (≥ {target}) */')
    for color, distance in clashes:
        if distance is None:
            print(f'/* 避让 {color}：接近中性色，不冲突 */')
        elif distance < 30:
            ok = False
            print(f'/* 冲突 {color}：色相只差 {distance:.0f}°（< 30°），换成该领域的第二选择 */')
        else:
            print(f'/* 避让 {color}：色相差 {distance:.0f}°，可以共存 */')
    print('/* --accent 本身只用于色块、图表和小圆点；正文里的强调文字用 --accent-text */')
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
