# Chrome 渲染环境（按需下载）

skill 本体不带 Chrome。渲染用的 chrome-headless-shell（Chrome for Testing 152.0.7977.54，Linux x64，
约 120MB）在真正需要渲染且本机没有 Chrome 时，才由脚本从官方 CDN 下载一次，
解压到 `~/chrome-headless-shell-linux64/`，同一会话内缓存复用。

## 自动引导（默认，无需人工）

`scripts/check.py` 按以下顺序自动找 Chrome，全部落空且在 Linux 上时自动下载：

1. 环境变量 `CHROME_BIN`
2. macOS 本机 Chrome：`/Applications/Google Chrome.app/Contents/MacOS/Google Chrome`
3. 已解压的 chrome-headless-shell：`./chrome-headless-shell-linux64/`、`./work/…`、`~/chrome-headless-shell-linux64/`
4. PATH 里的 `chrome-headless-shell` / `google-chrome` / `chromium` / `chromium-browser`
5. **官方 CDN 自动下载**（仅 Linux）

PNG 导出时同样用探测到的这个二进制：

```bash
CHROME=~/chrome-headless-shell-linux64/chrome-headless-shell   # macOS 则用本机 Chrome 路径
"$CHROME" --headless --screenshot="出图@2x.png" --window-size=1704,<高度> \
  --force-device-scale-factor=2 --default-background-color=00000000 --hide-scrollbars \
  "file://$(pwd)/图.html"
```

手动引导（不走脚本时）等价操作：

```bash
curl -sL -o /tmp/chs.zip \
  https://storage.googleapis.com/chrome-for-testing-public/152.0.7977.54/linux64/chrome-headless-shell-linux64.zip
unzip -q -o /tmp/chs.zip -d ~
chmod +x ~/chrome-headless-shell-linux64/chrome-headless-shell
~/chrome-headless-shell-linux64/chrome-headless-shell --version
# 应输出：Google Chrome for Testing 152.0.7977.54
```

## 注意

- 运行时若报 dbus 相关 ERROR 属正常（无头环境无 dbus），不影响渲染结果。
- 版本固定为 152.0.7977.54，无需每次查最新版；升级时改脚本里的 `CHS_URL` 版本号即可。
- zip 完整性校验：`shasum -a 256 /tmp/chs.zip` 应为
  `11cedb5568cd374a76eb738e40bd434cd0c9956820fb406b8bd9edca53428d3e`。
