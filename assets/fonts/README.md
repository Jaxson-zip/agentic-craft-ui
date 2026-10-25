# 字体

`misans/` 是 [MiSans](https://hyperos.mi.com/font) 的一小部分字形，只包含 [示例页面](../demo.html) 和 [组件配方](../patterns.html) 用到的字符，供示例离线展示。

- MiSans 由小米发布，官方声明可免费商用；以小米官方页面的最新条款为准。
- 这里的分片来自 npm 包 [`misans`](https://www.npmjs.com/package/misans)（按小米官方切片范围拆分），又用 fontTools 裁剪到示例用到的字符。
- 新项目不要复制这些文件，而是安装完整包：`npm install misans`，再引入 `misans/lib/Normal/MiSans-Regular.min.css` 等需要的字重。浏览器只会下载页面实际用到的分片。
