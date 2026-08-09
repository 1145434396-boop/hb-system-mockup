// 画布自适应。两种模式：
// 全屏模式（body.fullbleed，产品设计类默认）：画布缩放到正好等于窗口宽（可放大可缩小），像真实产品一样撑满，竖向超出走正常滚动。
// 画布模式（营销类，带衬底和浮层留白）：窗口窄于画布时整体等比缩小，打开即看全图；不放大。
// 用 zoom 而非 transform：zoom 参与布局，缩放后不残留滚动条。截图管线按 1:1 窗口尺寸导出，缩放系数为 1，不影响导出。
(function () {
  function fit() {
    var full = document.body.classList.contains('fullbleed');
    var w = document.documentElement.clientWidth - (full ? 0 : 64);
    var k = w / 1640;
    if (!full) k = Math.min(1, k);
    document.querySelectorAll('.stage').forEach(function (s) { s.style.zoom = k; });
  }
  fit();
  addEventListener('resize', fit);
})();
