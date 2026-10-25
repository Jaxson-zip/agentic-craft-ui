# 平台与组件库

新产品选栈或新项目建界面时读。已有项目沿用它现在的框架和组件库，不为“更好看”换栈。

## 默认步骤

1. 确定平台：网页、微信小程序、App，或需要同时覆盖几种。
2. 按下表选框架和组件库；用户或项目已有选择时以其为准。
3. 用 [视觉规范](visual-style.md) 的 tokens 覆盖组件库的默认主题（颜色、圆角、字体、阴影、动效）。
4. 只在组件库没有的地方自己写组件，并沿用同一套 tokens。

## 怎么选

| 平台 | 推荐起点 | 组件库 | 说明 |
| --- | --- | --- | --- |
| 网页（React） | Vite 或 Next.js | 个人项目：shadcn/ui + Tailwind，或 AI 应用用 Lobe UI；企业后台：Ant Design、Arco Design、Semi Design | shadcn/ui 是复制到项目里的源码，改起来最自由（Cherry Studio 官网就是这类风格）；Ant Design 最成熟，偏后台和数据密集。动效用 Motion（原 Framer Motion） |
| 网页（Vue） | Vite + Vue 3 | Arco Design Vue、TDesign Vue Next、Element Plus | 已用 Vue 的项目继续用 Vue |
| 微信小程序 | 原生小程序 | TDesign 小程序、Vant Weapp | 只做小程序时原生最稳，包体小、兼容好 |
| 小程序 + 网页 + App 多端 | uni-app（Vue）或 Taro（React） | uni-ui、NutUI 等对应框架的组件库 | 一套代码出多端，但每个端都要分别实测 |
| 手机 App | uni-app、Taro、React Native、Flutter | 框架自带或配套组件库 | 已有 Web 技术栈时优先 uni-app 或 React Native；需要大量自定义动画时 Flutter 更顺手 |
| 鸿蒙原生 | ArkTS + ArkUI | 系统组件 | HarmonyOS NEXT 不再运行安卓 APK，只有用户明确需要时才做 |

小型个人工具也可以不用框架：原生 HTML、CSS、JS 加 [themes.css](../assets/themes.css) 就能做出来，[示例页面](../assets/demo.html) 就是这样写的。

## 用组件库但不要“一眼组件库”

组件库解决的是“好用、稳定、可访问”，不自动解决“好看”。原样使用时，Ant Design 的默认蓝、Element Plus 的默认样式一眼就能认出来。

- **改主题，不改组件**：用组件库自己的主题机制注入 tokens，例如 Ant Design 的 `ConfigProvider` token、Arco 和 TDesign 的 CSS 变量、Vant 的 CSS 变量。不要到处写覆盖样式。
- **至少改这几项**：主色、页面底色、圆角、字体、阴影、动效时长与曲线，数值来自 [视觉规范](visual-style.md)。
- **版式自己设计**：组件库给的是零件。首屏放什么、核心对象怎么呈现，仍按视觉规范和 [艺术方向与动效](art-direction-motion.md) 决定。
- **只装需要的**：按需引入组件，图标库只用一套。

## 各平台要注意

- **网页**：手机和桌面都要看；要在微信内置浏览器里打开测一次（见 [中国用户](china.md)）。
- **小程序**：
  - 没有 DOM，不能直接用网页组件库。
  - 主包有大小限制（目前 2MB），图片尽量放到网络。
  - 动画用 CSS 或小程序动画接口。
  - 用户信息和手机号要按微信的授权流程获取。
  - 提交审核前在真机预览一次。
- **App**：
  - 权限申请（相机、定位、通知）要写清用途，用到时再申请。
  - 适配刘海屏和安全区。
  - 安卓机型多，至少在一台中低端机上看动效是否流畅。

## 怎么验证

- **网页**：浏览器实测，加一个 375px 宽的手机视图。
- **小程序**：微信开发者工具预览。没有工具时，标为 `not-run` 并说明。
- **App**：模拟器或真机。只用浏览器预览过的 H5 版本，不能当作 App 已经验证。
