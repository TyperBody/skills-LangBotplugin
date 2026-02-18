---
name: astr2lang
description: astrbot插件到langbot插件的转换逻辑,是转换AstrBot插件的步骤,同时有调试插件步骤,自主生成插件
license: Apache-2.0
trigger_keywords:
  - AstrBot转LangBot
  - AstrBot to LangBot
  - astrbot转langbot
  - astrbot插件转langbot插件
  - astrbot to langbot
  - astrbot plugin to langbot plugin
  - astr plugin to lang plugin
  - lang插件调试
  - LangBot插件调试
  - langbot插件调试
  - 插件调试
  - 调试
  - LangBot插件
  - 创建插件
metadata:
  author: TwperBody
  version: "0.1 Beta"
---

# Astrtolangplugin

你现在是「LangBot核心开发者rockqinQ」
或者你是「LangBot插件大手子「sheetung」
你现在精通LangBot和LangBot runtime还有LangBot CIL

## 指令
1. 目录构建以及组件添加必须使用lbp提供的组件
2. 必须要使用 lbp run 进行测试
3. 必须保证`manifest.yaml`的注册的组件有效符合文档归档
4. 如果目录不符合规范要修改
5. example里有示例插件，必要时参考成熟插件
6. 不要在完成构建langbot插件步骤之前创建插件，会有步骤创建插件
7. 交互式创建插件除了插件名字可以提前命令，交互式创建时将剩下的交互留给用户
8. 如果用户提交告知使用lbp工具创建好，则不需要自己创建目录
9. lbp init <pluginname> 会自己创建pluginname的目录，你不需要自己创建这个同名目录
10. 如果用户没有告诉你插件名字，或者没有创建目录，你需要提前警告用户 
11. 如果遇到交互问题则提示用户手动输入lbp命令
12. 如果发现插件构建完成，则直接进行测试，如果测试发现插件没有完成，则到未完成的步骤重新补全插件
13. DEBUG_RUNTIME_WS_URL is not set in .env file则说明阅读 templates/lbpfunction.md 并设置DEBUG_RUNTIME_WS_URL
14. 要在 生成 下载 等关键部分使用 langbot 日志类型，以便后续调试
15. 在 async generator 中，yield CommandReturn 之后的代码需要等待下一次迭代才会执行。如果框架只消费一次 yield 就停止，后续代码就不会运行
16. 如果用户没有提供任何astrbot插件的信息或说要生成一个某某某插件，则默认原生生成，没有参考，跳过所有关于astr的步骤
17. examples提供了一些用例，你可以参考这些用例
18. 如果遇到组件冲突，或者组件混同，比如说命令设置特定功能 则需单独规范并重新设计功能
19. 如果命令没有正确触发，例如用户没有正确发送命令，必须进行正确命令发送提示用户
20. 如果所给的astrbot插件是zip格式的，请先解压
21. 如果关于进展，则不进行总结，若关于文档或规划，则一定要总结
22. 时刻明确你写的是LangBot插件而不是astrbot，不要使用astrbot的包，哪怕插件名字里有astr也不要使用astrbot的包
23. 在插件 requirements.txt 文件里是插件的依赖，如果更新了依赖，请同步更新插件的 requirements.txt

## 了解 LangBot 插件开发类型与可用组件
请先阅读官方文档参考 templates/lbpfunction.md ，熟悉 LangBot 插件可使用的各类组件。
此时不要创建插件

## 了解 AstrBot 插件开发类型与可用组件
请先阅读官方文档参考

- references/astrguide/ai.md
- references/astrguide/env.md
- references/astrguide/html-to-pic.md
- references/astrguide/listen-message-event.md
- references/astrguide/other.md
- references/astrguide/plugin-config.md
- references/astrguide/send-message.md
- references/astrguide/session-control.md
- references/astrguide/simple.md
- references/astrguide/storage.md

熟悉 AstrBot 插件可使用的各类组件。

## 分析将要转换插件 astr 插件表达式
拆解并理解 astr 插件中的表达式，将其映射为 LangBot 插件所需的类型定义，此时不是写真正的插件。
分析这个插件可能需要的langbot组件，但是此时不要创建插件

## 分析 astr 插件配置文件
对照官方配置规范 references/astrguide/plugin-config.md
回看astrbot插件的配置项，但是不要创建langbot插件
分析astr原插件的配置项有什么，哪些是必须的，哪些是可选的
但是此时不要创建插件

## 分析 langbot example 插件文件
文件夹 examples 提供多种插件参考各各组件的调用方式，可以通过这些插件基本了解插件原理
但是不要创建langbot插件
- examples/Typer_Body-Markdowm2ing_Pro-1.1.0 提供了事件监听器组件的基本使用方法
- examples/langbot-team-RAGFlowRetriever-0.1.0 提供了知识检索组件的基本使用方法
- examples/langbot-team-DifyDatasetsRetriever-0.1.1 提供了知识检索组件的基本使用方法
- examples/Aizbend-DickRabbit-1.3.3 提供了两个命令组件和一个事件监听器组件的基本使用方法
- examples/langbot-team-ScheNotify-0.2.0 提供了两个工具组件和两个命令组件的基本使用方法
- examples/langbot-team-TavilySearch-0.1.0 提供了一个工具组件的基本使用方法
- examples/RockChinQ-HelloPlugin-0.1.0 提供了一个事件监听器组件一个工具组件一个命令组件的基本使用方法

## 初始化 LangBot 插件目录
如果创建过插件目录，跳过这一步
如果遇到交互问题则提示用户手动输入lbp命令
1. 在任意目录下新建插件目录，确定插件名字，替换 <HelloPlugin>
2. 进入该目录，执行
   ```bash
   lbp init <HelloPlugin>
   ```
3. 根据提示填写 Author（作者）、Description（插件描述）等信息，完成初始化。

## 确定目录规范
遵循官方推荐的 references/langbotguide/dev/tutor.md references/langbotguide/dev/directory-structure.md 组织源码与资源文件。
该步骤不要修改插件，甚至文件夹

## 构建 LangBot 插件配置
参考 references/langbotguide/dev/basic-info.md 只调整插件的 `manifest.yaml` 配置文件。
此时不要构建components字段，在下一阶段使用工具构建组件，文件夹，只修改配置，不编写插件

## 构建插件所需组件
根据功能需求，在插件中引入并配置各类组件，详见 references/langbotguide/dev/components/add.md
如果遇到交互问题则提示用户手动输入lbp命令

## 编写迁移代码
将 astr 插件的核心逻辑迁移至 LangBot 插件框架，完成适配与测试。
- references/langbotguide/dev/basic-info.md
- references/langbotguide/dev/directory-structure.md
- references/langbotguide/dev/migration.md
- references/langbotguide/dev/style.md
- references/langbotguide/dev/tutor.md
- references/langbotguide/dev/apis/common.md
- references/langbotguide/dev/apis/messages.md
- references/langbotguide/dev/apis/pipeline-events.md
- references/langbotguide/dev/apis/tech-details.md
- references/langbotguide/dev/components/add.md
- references/langbotguide/dev/components/command.md
- references/langbotguide/dev/components/event-listener.md
- references/langbotguide/dev/components/knowledge-retriever.md
- references/langbotguide/dev/components/tool.md
- references/langbotguide/dev/publish/github.md
- references/langbotguide/dev/publish/market.md
务必确认包导入方式正确，不要在langbot插件中调用不可能出现的astrbot的包

## 日志规划化
正确导入 import logging 包
在插件中请使用`logging`模块记录日志，不要使用`print`语句（这将导致容器环境中无法输出日志）。

```python
import logging

logger = logging.getLogger(__name__)

logger.info('This is an info message')
logger.warning('This is a warning message')
logger.error('This is an error message')
```


## 测试
1. 阅读 templates/lbpfunction.md 修改或添加 DEBUG_RUNTIME_WS_URL
2. 运行lbp run进行插件测试，直到第一测试阶段结束
3. 修复用户从其他或前端获取的报错进行修复
4. examples提供了一些用例，你可以参考这些用例进行修复
5. 通过文档去反向检查功能是否完善 一个bug是否影响其他功能或者这个bug在其他功能上有体现
6. 直到用户回复没有问题结束开发，否则结束一个问题后继续等待用户新问题
