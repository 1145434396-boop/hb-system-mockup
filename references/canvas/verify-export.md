# 验证与导出（步骤 6 读）

## 验证（每张图必做）

1. 浏览器打开渲染，截图核对：高度贴合、无溢出、无空白、字号层级正常。
2. 对照已读的 principles 判据自检：对齐（列数一致、不定高独占行）、状态色红绿灯、按钮分级（主/次/警示/置灰）、图表选型正确。
3. 界面里的组件名称、交互形态与结构文件（assets/c1～c4）名录一致，无自造组件。
4. **层次关系核对**：每个组件是"白卡浮在灰底"还是"透明融进容器"，逐一对照结构文件 data-measured 注释；出现"某一条工具栏/筛选条颜色和邻区不一致"的观感，先怀疑缺了容器层（如 .view-box），不要用改颜色硬凑。
5. **空隙核对**：check.py 会渲染量一遍（empty-gap），只看布局层——组件之间、组件到画布边缘不许有大片空白；组件内部（图片格、列表行数、卡片字段）的留白由数据量决定，属于产品原样，不算问题。
6. **并排栏高度核对**：check.py 的 `column-uneven` 会量同一栅格行里各栏的底部落差，超过 24px 报 Medium（阈值按肉眼实测定：37px 的落差人眼已经能看出来）。两栏之间的落差目检容易被「左右各自都很整齐」的错觉盖过去。修法是给短的那栏补数据行（分组行、明细行）或调整两栏栅格宽度，不要用固定高度硬撑。
7. **裁切与出界核对**：check.py 报 content-clipped（窗口内容比窗口高，底部被裁，整图观感偏下）或 float-out（浮层探出画布）都是 High，必须清零。回填 .stage 高度时注意鸡生蛋：详情页画布 min-height 跟着窗口高走，先把 stage 填大再量会得到虚高——以「功能区 56＋画布内容实高＋边框 2」为准，量完改高（改 --extra-style 后重跑 build.py）再复量一次确认 scrollHeight ≤ clientHeight。

## 导出 2x PNG（默认交付物）

```bash
# CHROME 取法见 references/chrome-env.md（macOS 用本机 Chrome；Linux 沙箱由 check.py 按需下载并缓存复用）
"$CHROME" \
  --headless --screenshot=out.png \
  --window-size=<宽>,<高> --force-device-scale-factor=2 \
  --hide-scrollbars "file:///路径/图.html"
```

- 产品设计类：`1640,<stage高>`；营销类：`1704,<stage高+96>` 加 `--default-background-color=00000000`（细节见各自画布文件）。
- 透明底只适用于 PNG 走 HTML 的路径；SVG/foreignObject 嵌报告管线仍须垫不透明 rect（见 [report-embed.md](report-embed.md)），否则手机端 PDF 渲成灰块。
