#!/usr/bin/env python3
"""界面示意图产出物静态检查。纯标准库，不依赖浏览器。

用法：
    python3 scripts/check.py 图.html            # 人读的分级报告
    python3 scripts/check.py 图.html --json     # 机读

检查的是"该由机器判定、肉眼容易漏"的项：色值有没有写死、有没有用不存在的
组件类、导出前置条件、以及几条踩过坑的结构禁令。看得见的对齐和观感仍然要
自己看截图，见 references/canvas-spec.md 的验证清单。

退出码：有 Blocker 返回 1，其余返回 0。
"""
import json
import re
import sys
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent
ASSETS = SKILL / "assets"

# 允许写死颜色的地方：皮肤文件自己定义 token，以及 #fff 这种中性值
HEX = re.compile(r'#[0-9A-Fa-f]{3,8}\b')
RGB = re.compile(r'\brgba?\(')
ALLOW_LITERAL = {"#fff", "#ffffff", "#000", "#000000"}


def load_known_classes():
    """base.css 里定义过的 class，作为"组件是否存在"的判据。"""
    css = (ASSETS / "base.css").read_text(encoding="utf-8")
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    return set(re.findall(r"\.([A-Za-z][\w-]*)", css))


def load_known_icons():
    svg = (ASSETS / "icons.svg").read_text(encoding="utf-8")
    return set(re.findall(r'<symbol id="i-([\w-]+)"', svg))


def split_doc(text):
    """拆成 <style> 段和 body 段：style 里出现色值是正常的，body 里不是。"""
    styles = re.findall(r"<style[^>]*>(.*?)</style>", text, flags=re.S)
    body = re.sub(r"<style[^>]*>.*?</style>", "", text, flags=re.S)
    body = re.sub(r"<!--.*?-->", "", body, flags=re.S)
    return "\n".join(styles), body


def line_of(text, idx):
    return text.count("\n", 0, idx) + 1


def check(path):
    text = Path(path).read_text(encoding="utf-8")
    styles, body = split_doc(text)
    findings = []

    def add(level, rule, msg, line=None):
        findings.append({"level": level, "rule": rule, "msg": msg, "line": line})

    # ── Blocker：色值写死 ───────────────────────────────────────────
    # body 里的 fill/stroke/color/background 属性值
    for m in re.finditer(r'(?:fill|stroke|stop-color)="([^"]+)"', body):
        v = m.group(1).strip()
        if v.lower() in ALLOW_LITERAL or v in ("none", "currentColor") or v.startswith("url("):
            continue
        if HEX.match(v) or RGB.match(v):
            add("Blocker", "hardcoded-color",
                f'SVG 属性写死颜色 {v}，应改 var(--...)；换皮肤时这里不会跟着变', line_of(body, m.start()))
    # body 里 style="" 中的颜色
    for m in re.finditer(r'style="([^"]*)"', body):
        for cm in re.finditer(r"(?:background|color|fill|stroke|border)[^;:]*:\s*([^;\"]+)", m.group(1)):
            v = cm.group(1).strip()
            if v.lower() in ALLOW_LITERAL or v.startswith("var(") or v.startswith("url("):
                continue
            if HEX.search(v) or RGB.search(v):
                add("Blocker", "hardcoded-color",
                    f'行内 style 写死颜色 {v}，应改 var(--...)', line_of(body, m.start()))
    # 本图补充样式段（最后一个 style 块）里的裸色值
    tail = styles.split("/* ── 本图布局 ── */")[-1] if "/* ── 本图布局 ── */" in styles else ""
    for m in re.finditer(r"(?:background|color|fill|stroke)\s*:\s*([^;{}]+)", tail):
        v = m.group(1).strip()
        if v.lower() in ALLOW_LITERAL or "var(" in v or v.startswith("url("):
            continue
        if HEX.search(v) or RGB.search(v):
            add("High", "hardcoded-color",
                f'本图补充样式里写死颜色 {v}；确属一次性微调可忽略，否则应加进皮肤 token')

    # ── 组件存在性：base.css 有 / 只在本图样式里有 / 哪都没有 ──────
    known = load_known_classes()
    local = set(re.findall(r"\.([A-Za-z][\w-]*)", styles))
    used = set()
    for m in re.finditer(r'class="([^"]+)"', body):
        used.update(c for c in m.group(1).split() if c)
    for c in sorted(used):
        if c.startswith(("i-", "sw-", "c-", "tint-")) or c in known:
            continue
        if c in local:
            add("Nit", "local-only-class",
                f'.{c} 只在本图补充样式里定义：一次性布局可以，但若多张图都要用应沉淀进 base.css')
        else:
            add("High", "unknown-component",
                f'.{c} 在 base.css 和本图样式里都没有定义：自造组件（违反硬约束）或漏写样式')

    # ── High：引用了不存在的图标 ───────────────────────────────────
    icons = load_known_icons()
    for m in re.finditer(r'<use href="#i-([\w-]+)"', body):
        if m.group(1) not in icons:
            add("High", "unknown-icon",
                f'#i-{m.group(1)} 不在 icons.svg 里', line_of(body, m.start()))
    if "<use href=" in body and 'id="i-' not in text:
        add("Blocker", "missing-sprite",
            "用了 <use> 但没把 assets/icons.svg 拼进文件，图标会全部空白")

    # ── SVG 导出前置条件（嵌报告时必踩；导出脚本会统一补，这里聚合提示） ──
    n_noxmlns = len(re.findall(r"<svg(?![^>]*xmlns)[^>]*>", body))
    if n_noxmlns:
        add("Medium", "svg-no-xmlns",
            f"{n_noxmlns} 处内嵌 <svg> 缺 xmlns：出 PNG 无影响；走 SVG/foreignObject 嵌报告前须按 canvas-spec 统一补齐")
    n_br = len(re.findall(r"<br\s*>", body))
    if n_br:
        add("Medium", "br-not-closed",
            f"{n_br} 处 <br> 未自闭合：嵌报告导出前须转 <br/>（foreignObject 是 XML）")

    # ── Medium：结构禁令（踩过的坑） ───────────────────────────────
    if re.search(r'class="[^"]*\bico\b[^"]*"[^>]*>\s*<path', body):
        add("Medium", "inline-icon-path",
            "图标仍在内联 path，应改 <use href=\"#i-...\"/>（icons.svg 已收 63 个）")
    if "■" in body or "●" in body:
        add("Medium", "legend-char",
            "图例用了 ■/● 字符：字符只能着文字色，无法与系列色一致，应改 <rect>/<circle>")
    if re.search(r'class="[^"]*\bstage\b', body) and "class=\"window\"" in body:
        if not re.search(r"\.stage\s*\{[^}]*height", "\n".join([styles])):
            add("High", "stage-no-height",
                ".stage 没设 height：画布高度必须按渲染实测回填，否则导出会截断或留白")

    # ── 汇总 ───────────────────────────────────────────────────────
    order = {"Blocker": 0, "High": 1, "Medium": 2, "Nit": 3}
    findings.sort(key=lambda f: (order[f["level"]], f["rule"], f["line"] or 0))
    return findings


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    as_json = "--json" in sys.argv
    if not args:
        print(__doc__)
        return 2
    findings = check(args[0])
    if as_json:
        print(json.dumps(findings, ensure_ascii=False, indent=2))
    else:
        if not findings:
            print("✓ 静态检查通过（颜色 token、组件存在性、导出前置、结构禁令）")
            print("  注意：对齐与观感仍需看截图，见 canvas-spec.md 验证清单")
        else:
            counts = {}
            for f in findings:
                counts[f["level"]] = counts.get(f["level"], 0) + 1
            print("　".join(f"{k} {v}" for k, v in counts.items()))
            print()
            for f in findings:
                loc = f"  第{f['line']}行" if f["line"] else ""
                print(f"[{f['level']}] {f['rule']}{loc}\n    {f['msg']}")
    return 1 if any(f["level"] == "Blocker" for f in findings) else 0


if __name__ == "__main__":
    sys.exit(main())
