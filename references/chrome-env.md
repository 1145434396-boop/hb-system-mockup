# Chrome 渲染环境（skill 内置，零下载）

本 skill 在 `assets/chrome/` 内置了 Chrome for Testing 152.0.7977.54 的 chrome-headless-shell
（Linux x64，原始 zip 119,570,919 字节，按单文件 100MB 上限切成 `chs_vol_aa`＋`chs_vol_ab` 两个分卷）。
skill 文件走到哪，渲染环境就到哪，不依赖资源库，也不需要下载。

## 自动引导（默认，无需人工）

`scripts/check.py` 按以下顺序自动找 Chrome，全部落空且在 Linux 上时，
自动把内置分卷合并→解压到 `~/chrome-headless-shell-linux64/`→chmod，然后直接可用：

1. 环境变量 `CHROME_BIN`
2. macOS 本机 Chrome：`/Applications/Google Chrome.app/Contents/MacOS/Google Chrome`
3. 已解压的 chrome-headless-shell：`./chrome-headless-shell-linux64/`、`./work/…`、`~/chrome-headless-shell-linux64/`
4. PATH 里的 `chrome-headless-shell` / `google-chrome` / `chromium` / `chromium-browser`
5. **内置分卷自动解压**（仅 Linux）

PNG 导出时同样用探测到的这个二进制（解压后固定在 `~/chrome-headless-shell-linux64/chrome-headless-shell`）：

```bash
CHROME=~/chrome-headless-shell-linux64/chrome-headless-shell   # macOS 则用本机 Chrome 路径
"$CHROME" --headless --screenshot="出图@2x.png" --window-size=1704,<高度> \
  --force-device-scale-factor=2 --default-background-color=00000000 --hide-scrollbars \
  "file://$(pwd)/图.html"
```

手动引导（不走脚本时）等价操作：

```bash
cat assets/chrome/chs_vol_aa assets/chrome/chs_vol_ab > /tmp/chs.zip
unzip -q -o /tmp/chs.zip -d ~
chmod +x ~/chrome-headless-shell-linux64/chrome-headless-shell
~/chrome-headless-shell-linux64/chrome-headless-shell --version
# 应输出：Google Chrome for Testing 152.0.7977.54
```

## 注意

- 运行时若报 dbus 相关 ERROR 属正常（无头环境无 dbus），不影响渲染结果。
- 版本固定为 152.0.7977.54，无需每次查最新版；升级时重新下载 zip、按 100MB 切分替换两个分卷即可
  （`split -b 100000000 chs.zip assets/chrome/chs_vol_`）。
- 分卷完整性校验：`cat chs_vol_aa chs_vol_ab | shasum -a 256` 应为
  `11cedb5568cd374a76eb738e40bd434cd0c9956820fb406b8bd9edca53428d3e`。
- 内置分卷缺失时的备用直下地址：
  https://storage.googleapis.com/chrome-for-testing-public/152.0.7977.54/linux64/chrome-headless-shell-linux64.zip
