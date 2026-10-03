# ɑ 的四种声调组合

本补丁支持 `ɑ`（U+0251）及 `ɑ̄ ɑ́ ɑ̌ ɑ̀`，覆盖 8、10、12 像素、等宽和比例模式及全部语言版本。
它们与普通拉丁字母 `a ā á ǎ à` 是不同的文本编码。

## 实现

- `assets/patch-glyphs` 内新增手工像素字形：基础 `ɑ`、四个组合符号，以及四个按字号调整的组合字形。
- `assets/configs/features/ccmp.fea` 将 `U+0251` 后接 `U+0304 / U+0301 / U+030C / U+0300` 的序列替换为组合字形。原始文本、复制和搜索使用的编码不变。
- 组合符号自身的前进宽度由现有构建库按 Unicode 的 Mn 类别设为零；组合后的字形与基础 `ɑ` 等宽。
- 8 像素模式使用两行像素区分尖音符、抑扬符和重音符，最高点位于字身框顶端；不扩大现有行高。

这是对上述四个序列的定向支持，不是通用的组合附加符定位系统。其他基础字母、多重附加符，以及关闭 `ccmp` 或不支持 OpenType 字形替换的软件，不在支持范围内。推荐使用 TTF、OTF 或 WOFF2；BDF、PCF 等不携带这些 OpenType 替换规则的格式不能保证显示组合结果。

## 本地构建与预览

在仓库根目录执行（uv 会按项目配置准备 Python 和依赖）：

```sh
uv sync
uv run -m tools.build_fonts --font-formats otf.woff2 ttf
uv run -m tools.build_site
uv run -m pytest -q
uv run python -m http.server 8765 --bind 127.0.0.1 --directory build/outputs
```

打开 <http://127.0.0.1:8765/playground.html>，切换字号、宽度模式和语言；三个 Demo 页也加入了相同的对照文本。

```text
ɑ ɑ̄ ɑ́ ɑ̌ ɑ̀
mɑ̄ mɑ́ mɑ̌ mɑ̀
ɑ̄ɑ́ɑ̌ɑ̀
a ā á ǎ à
```

TTF 文件在 `build/outputs` 中，可用于本地软件测试。其字体家族名沿用上游；若已安装同名旧版，应避免两版同时安装引起缓存或字体选择混淆。

## Demo 发布

网站源码与字体位于同一仓库：`assets/templates` 是页面模板，`tools/build_site.py` 生成静态页面，`.github/workflows/pages.yaml` 构建并部署 GitHub Pages。无需另建网站项目。

Fork 后需在仓库设置中启用 GitHub Pages 并选择 GitHub Actions。当前工作流监听 `master` 分支；若改用其他分支，需要同步修改工作流。

本仓库的 Demo 地址为 <https://hitosea.github.io/fusion-pixel-font/playground.html>。项目链接已指向此 Fork，页面未使用上游的 Google Analytics 配置。

字体继续遵循 OFL 1.1，构建程序继续遵循 MIT；保留原有版权及许可证。
