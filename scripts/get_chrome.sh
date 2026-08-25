#!/usr/bin/env bash
# 一键装 chrome-headless-shell（Linux）：已装即退，否则按镜像顺序下载→校验→解压→chmod。
# 国内首选 npmmirror（路径必须带完整 /-/binary/chrome-for-testing/，裸域名会 302 跳走限速），googleapis 仅兜底。
set -euo pipefail

VER=152.0.7977.54
SHA=11cedb5568cd374a76eb738e40bd434cd0c9956820fb406b8bd9edca53428d3e
DEST="$HOME/chrome-headless-shell-linux64"
BIN="$DEST/chrome-headless-shell"
URLS=(
  "https://registry.npmmirror.com/-/binary/chrome-for-testing/$VER/linux64/chrome-headless-shell-linux64.zip"
  "https://cdn.npmmirror.com/binaries/chrome-for-testing/$VER/linux64/chrome-headless-shell-linux64.zip"
  "https://storage.googleapis.com/chrome-for-testing-public/$VER/linux64/chrome-headless-shell-linux64.zip"
)

if [ -x "$BIN" ]; then
  echo "已存在：$BIN（$("$BIN" --version)）"
  exit 0
fi

ZIP=$(mktemp -d)/chs.zip
for u in "${URLS[@]}"; do
  echo "下载：$u"
  if curl -sL --fail --connect-timeout 10 -o "$ZIP" "$u"; then
    got=$(shasum -a 256 "$ZIP" | cut -d' ' -f1)
    [ "$got" = "$SHA" ] && break
    echo "校验不符（$got），换下一个源"
  fi
done
[ -s "$ZIP" ] && [ "$(shasum -a 256 "$ZIP" | cut -d' ' -f1)" = "$SHA" ] || { echo "!! 所有源都失败"; exit 1; }

unzip -q -o "$ZIP" -d "$HOME"
rm -f "$ZIP"
chmod +x "$BIN"
echo "完成：$BIN（$("$BIN" --version)）"
