from collections.abc import Callable

import pytest
from pixel_font_knife.cmap.context import CmapContext

from tools.config import options
from tools.config.options import FontSize, GlyphScope


PATCHED_BY_SCOPE = {
    'common': '灬纟饣㇏讷鹭',
    'monospaced': '›−≠ɡˉˊˇˋếềḿ',
    'proportional': '›−≠ɡˉˊˇˋếềḿ',
}


@pytest.mark.parametrize('font_size', (10, 12))
@pytest.mark.parametrize('glyph_scope', options.GLYPH_SCOPES)
def test_missing_glyph_patches_are_loaded(
        load_cmap_context: Callable[[FontSize, GlyphScope], CmapContext],
        font_size: FontSize,
        glyph_scope: GlyphScope,
) -> None:
    context = load_cmap_context(font_size, glyph_scope)
    expected = PATCHED_BY_SCOPE[glyph_scope]
    if font_size == 10 and glyph_scope == 'common':
        expected = '灬纟饣㇏讷峤曈鹂爫犭礻'
    if font_size == 12 and glyph_scope == 'common':
        expected = '㇏鹭'
    if glyph_scope != 'common' and font_size == 12:
        expected = '›−≠ɡˉˊˇˋếềḿ'
    for character in expected:
        assert ord(character) in context, f'{font_size}px {glyph_scope}: U+{ord(character):04X}'
