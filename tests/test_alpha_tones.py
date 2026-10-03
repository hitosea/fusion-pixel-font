import pytest
from fontTools.ttLib import TTFont
from pixel_font_builder import FontBuilder, Glyph, opentype
from pixel_font_knife.cmap.file import CmapGlyphFile
from pixel_font_knife.named.file import NamedGlyphFile

from tools.config import options, path_define
from tools.config.font import FontConfig


@pytest.mark.parametrize('font_size', options.FONT_SIZES)
@pytest.mark.parametrize('width_mode', options.WIDTH_MODES)
def test_alpha_tones(font_size, width_mode, tmp_path):
    """Compile actual patch assets and check substitution, spacing and bounds."""
    config = FontConfig.load(font_size)
    metric = config.layout_metrics[width_mode]
    root = path_define.PATCH_GLYPHS_DIR / str(font_size)
    builder = FontBuilder()
    builder.meta_info.family_name = 'Alpha Tone Test'
    builder.font_metric.font_size = font_size
    builder.font_metric.horizontal_layout.ascent = metric.ascent
    builder.font_metric.horizontal_layout.descent = metric.descent
    builder.glyphs.append(Glyph('.notdef', advance_width=font_size))
    for path in sorted((root / 'cmap' / width_mode).rglob('*.png')):
        glyph = CmapGlyphFile.load(path)
        if glyph.code_point not in (0x0251, 0x0300, 0x0301, 0x0304, 0x030C):
            continue
        builder.character_mapping[glyph.code_point] = glyph.glyph_name
        builder.glyphs.append(_build_glyph(glyph, font_size, metric.baseline))
    for path in sorted((root / 'named' / width_mode / 'ccmp').glob('*.png')):
        builder.glyphs.append(_build_glyph(NamedGlyphFile.load(path), font_size, metric.baseline))
    builder.opentype_config.features = opentype.FeatureProgram([
        opentype.FeatureFile(path_define.CONFIGS_FEATURES_DIR / 'ccmp.fea'),
    ])
    output = tmp_path / 'alpha.ttf'
    builder.save_ttf(output)

    with TTFont(output) as font:
        cmap = font.getBestCmap()
        assert set(cmap) == {0x0251, 0x0300, 0x0301, 0x0304, 0x030C}
        base_width = font['hmtx']['u0251'][0]
        assert base_width > 0
        substitutions = {}
        for lookup in font['GSUB'].table.LookupList.Lookup:
            assert lookup.LookupType == 4
            for table in lookup.SubTable:
                for ligature in table.ligatures['u0251']:
                    substitutions[tuple(ligature.Component)] = ligature.LigGlyph
        expected = {'u0304': 'alpha.macron', 'u0301': 'alpha.acute',
                    'u030C': 'alpha.caron', 'u0300': 'alpha.grave'}
        assert substitutions == {(mark,): name for mark, name in expected.items()}
        outlines = set()
        scale = font['head'].unitsPerEm / font_size
        for mark, name in expected.items():
            assert font['hmtx'][mark][0] == 0
            assert font['hmtx'][name][0] == base_width
            glyph = font['glyf'][name]
            assert glyph.yMax <= metric.ascent * scale
            assert glyph.yMin >= metric.descent * scale
            assert glyph.xMin >= 0 and glyph.xMax <= base_width
            outlines.add(tuple(glyph.coordinates))
        assert len(outlines) == 4


def _build_glyph(glyph, size, baseline):
    return Glyph(
        glyph.glyph_name,
        horizontal_offset=glyph.suggest_horizontal_offset(size, baseline),
        advance_width=glyph.suggest_advance_width(),
        bitmap=glyph.suggest_bitmap(),
    )
