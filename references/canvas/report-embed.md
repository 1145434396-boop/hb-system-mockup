# SVG 嵌报告（仅 huoban-solution-report 场景读）

取 `<style>`＋`<div class="stage">…` 包进 `<svg><foreignObject><div xmlns="http://www.w3.org/1999/xhtml">`，尺寸取 `.stage` 实际宽高。三个必修点，漏一个整图变纯文本或不渲染：

1. 所有内嵌图标 `<svg` 必须补 `xmlns="http://www.w3.org/2000/svg"`；开头写法有 `<svg width` / `<svg class` / `<svg viewBox` 多种，按 `<svg ` 统一处理，别按前缀枚举。
2. `<br>` 转 `<br/>`（foreignObject 里是 XML）。导出后先 `xml.etree` 校验再嵌。
3. foreignObject 前垫一个全画布 `<rect>`（填报告纸色）：留透明像素，手机端 PDF 阅读器会渲成灰块。
