# Markdowm2ing Pro 插件

超级无敌免外置浏览器加强版本，一个强大的AI对话Markdown消息转图片插件，能够自动识别和转换AI回复中的Markdown格式内容为精美的图片。


![开发群聊](https://img.shields.io/badge/开发群聊-472263434-blue)

![LangBot版本](https://img.shields.io/badge/LangBot-4.3+-blue)

![Python版本](https://img.shields.io/badge/Python-3.10+-blue)


## 功能特性

- 🔄 **智能识别**: 自动检测AI回复中的Markdown语法
- 🎨 **样式定制**: 支持自定义Markdown渲染样式
- 📱 **异步处理**: 采用异步渲染，避免事件循环冲突
- 🔗 **链接提取**: 可选提取Markdown中的链接信息
- 🚫 **消息拦截**: 可配置阻止未处理的Markdown消息回复
- 📊 **权重控制**: 灵活的转换触发权重设置

## 配置说明

### 样式配置

样式文件应为ZIP格式，包含以下结构：
```
style.zip
├── elements.yml    # 元素样式配置
├── setting.yml     # 全局设置
└── imgs/
    └── background.png  # 背景图片
```

### 参数详解

- **Markdown style**: 上传包含样式配置的ZIP文件（必需）
- **提取Markdown中的链接**: 布尔值，控制是否提取Markdown中的链接（默认关闭）
- **markdown转义触发量**: 整数值，设置触发转换的Markdown元素数量阈值（默认2）
- **阻止未处理的markdown消息回复**: 布尔值，控制是否阻止未处理的Markdown消息回复（默认开启）

## 使用说明

插件会自动监听AI的回复消息，当检测到Markdown内容时：

1. 分析消息中的Markdown语法元素
2. 根据配置的样式渲染为图片
3. 将图片转换为Base64格式发送
4. 可选提取并显示链接信息

### 支持的Markdown语法

- 标题 (#, ##, ###)
- 粗体 (**text**)
- 斜体 (*text*)
- 行内代码 (`code`)
- 列表 (-, *, +, 数字.)
- 引用块 (>)
- 链接 ([text](url))
- 图片 (![alt](src))
- 分割线 (---, ***)
- 代码块 (```)

## 技术实现

### 核心组件

- **事件监听器**: 监听`NormalMessageResponded`事件
- **Markdown分析器**: 识别标题、列表、链接、代码块等语法
- **异步渲染器**: 使用`pillowmd`库进行图片渲染
- **Base64转换**: 将图片转换为Base64格式发送

## 故障排除

### 常见问题

1. **事件循环错误**: 确保使用最新版本，已修复异步渲染问题
2. **样式加载失败**: 检查ZIP文件格式和内容结构
3. **渲染失败**: 验证Markdown内容格式是否正确

## 特别感谢

本项目基于 [Monody-S/CustomMarkdownImage](https://github.com/Monody-S/CustomMarkdownImage) 项目开发，特别感谢该项目提供的强大渲染能力：

- **基于pillow的可自定义markdown风格的渲染器**
- **支持LaTeX渲染**
- **相比playwright有更快的渲染速度（pillow直绘）**
- **更简单的自定义方式（直接修改配置文件，无需写CSS）**

## 支持与贡献

如有问题或建议，欢迎提交Issue或Pull Request。

---

**注意**: 请确保上传的样式ZIP文件格式正确，包含必要的配置文件。