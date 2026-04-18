---
sidebarDepth: 2
---

# 使用数据库

::: tip
本节所介绍的内容需要你安装一个数据库支持。如果你暂时不打算使用数据库，可以略过本节。
:::

对于几乎所有大型机器人项目，数据库的使用都是不可或缺的。但如果每个插件都使用了自己的数据库，这将导致插件之间的兼容性非常差——用户要么选择同时安装多个数据库，要么只能放弃一些功能或者重复造轮子。为此，Koishi 设计了一整套对象关系映射（ORM）接口，它易于扩展并广泛地运用于各种插件中。同时，我们也提供了一些常用数据库的官方插件，足以应对绝大部分使用场景。

## 安装数据库

为了保证纯粹性，Koishi 的核心库 koishi-core 并不希望写入对某个具体的数据库的支持。因此，Koishi 的数据库采取了注入的方法。如果你是插件开发者，你可能不需要关心具体的数据库实现。但是如果你是 Koishi 的使用者，只有在安装了数据库之后，你才能正常使用所有的特性，包括下一节中的用户管理系统。首先你需要安装数据库依赖：

::: code-group manager
```npm
# 我们以 mysql 数据库为例
npm i koishi-plugin-mysql -D
```
```yarn
# 我们以 mysql 数据库为例
yarn add koishi-plugin-mysql -D
```
:::

然后与你添加插件同样的方法配置你的数据库：

```js koishi.config.js
module.exports = {
  plugins: {
    mysql: {
      host: '[host]',
      port: 3306,
      user: 'root',
      password: '[password]',
      database: '[database]',
    },
  },
}
```

运行程序后，你就可以通过访问 `ctx.database` 来调用数据库接口了：

```js
// 获取用户数据
const user = await ctx.database.getUser(type, id)

// 修改群数据
await ctx.database.setChannel(type, id, { assignee: 123456789 })
```

你可以在后面的 API 文档中看到全部内置的 [数据库方法](../api/database.md)。

## 使用会话 API

对于 Koishi 内部的两个抽象表 User 和 Channel，我们在 [会话对象](../api/session.md) 中封装了几个高级方法：

```js
// 中间增加了一个第二参数，表示默认情况下的权限等级
// 如果找到该用户，则返回该用户本身
// 否则创建一个新的用户数据，权限为 authority
// 如果 authority 大于 0，则将新的用户数据添加到表中
session.getUser(id, authority, fields)

// 在当前会话上绑定一个可观测用户实例
// 也就是所谓的 session.user
session.observeUser(fields)

// 中间增加了一个第二参数，表示默认情况下的 assignee
// 如果找到该频道，则不修改任何数据，返回该频道本身
// 如果未找到该频道，则创建一个新的频道，代理者为 selfId
// 如果 selfId 大于 0，则将新的频道数据添加到表中
session.getChannel(id, selfId, fields)

// 在当前会话上绑定一个可观测频道实例
// 也就是所谓的 session.channel
session.observeChannel(fields)
```

## 使用 ORM API

Koishi 设计了一套 **对象关系映射（ORM）** 接口，它易于扩展并广泛地运用于各种插件中。

### 获取和删除数据

使用 `database.get()` 方法以获取特定表中的数据。下面是一个最基本的形式：

```js
// 获取 schedule 表中 id 为 1234 或 5678 的数据行，返回一个数组
const rows = await ctx.database.get('schedule', [1234, 5678])
```

对于复杂的数据表，如果你只需要获取少数字段，你可以通过第三个参数手动指定要获取的字段：

```js
// 返回的数组中每个元素只会包含 command, lastCall 属性
const rows = await ctx.database.get('schedule', [1234], ['command', 'lastCall'])
```

你还可以向第二个参数传入一个对象，用来查询非主键上的数据或者同时指定多列的值：

```js
// 获取名为 schedule 的表中 assignee 为 onebot:123456 的数据行
const rows = await ctx.database.get('schedule', { assignee: ['onebot:123456'] })
```

对于需要进行复杂的数据库搜索的，ORM 也提供了相对应的方法：

```js
// 获取名为 schedule 的表中 id 大于 2 但是小于等于 5 的数据行
const rows = await ctx.database.get('schedule', { id: { $gt: 2, $lte: 5 } })
```

> 你可以在 [这里](../api/database.md#db-get-table) 看到更多相关的 API。

删除数据的语法与获取数据类似：

```js
// 从 schedule 表中删除特定 id 的数据行
// 第二个参数也可以使用上面介绍的对象语法
await ctx.database.remove('schedule', [id])
```

### 添加和修改数据

除了获取和删除数据，常用的需求还有添加和修改数据。

```js
// 向 schedule 表中添加一行数据，row 是要添加的数据行
// 返回值是添加的行的完整数据（包括自动生成的 id 和默认属性等）
await ctx.database.create('schedule', row)
```

修改数据的逻辑稍微有些不同，需要你传入一个数组：

```js
// 用 rows 来对数据进行更新，你需要确保每一个元素都拥有 id 属性
// 修改时只会用 rows 中出现的键进行覆盖，不会影响未记录在 data 中的字段
await ctx.database.update('schedule', rows)
```

如果想以非主键来索引要修改的数据，可以使用第三个参数：

```js
// 用 rows 来对数据进行更新，你需要确保每一个元素都拥有 onebot 属性
await ctx.database.update('user', rows, 'onebot')
```

## 使用 ORM API 扩展数据库

你也可以使用 ORM API 扩展数据库中的已有表，或者新建数据表。

### 扩展表

向内置的 User 表中注入字段的方式如下：

::: code-group language
```js
const { Tables } = require('koishi')

Tables.extend('user', {
  fields: {
    // 向用户表中注入字符串字段 foo
    foo: { type: 'string' },
    // 你还可以配置默认值为 'bar'
    foo: { type: 'string',  initial: 'bar', nullable: true },
  }
})
```
```ts
import { Tables } from 'koishi'

// TypeScript 用户需要进行类型合并
declare module 'koishi' {
  interface User {
    foo: string
  }
}

Tables.extend('user', {
  fields: {
    // 向用户表中注入字符串字段 foo
    foo: { type: 'string' },
    // 你还可以配置默认值为 'bar'
    foo: { type: 'string',  initial: 'bar', nullable: true },
  }
})
```
:::

向 Channel 注入字段同理。

::: warning
实际上，在 Koishi v3 中还有以下的扩展方法：

```js
// 向用户表中注入字符串字段 foo，简写形式
foo: 'string'
```

但是这个方法和下面的方法都会导致新增的字段不可为空（Not Nullable）：

```js
// 拓展定义的完整形式，配置了初始值 (initial)，但是没有指定可空 (nullable)
foo: { type: 'string', initial: 'bar' }
```

这样会导致一个问题：在使用 koishi-plugin-mysql 时，如果你安装了用这样的方法扩展了数据库的插件，之后又因为一些原因卸载了它，那么数据库会因为新增行时 Koishi 没有对不可为空的字段赋值而报错。([#414](https://github.com/koishijs/koishi/issues/414))

如果你使用的是 mysql 数据库，或者你想让更多的人使用你的插件，那么，为了避免这个问题，在对已有数据库进行扩展的时候，不应该使用上面的两种写法，以确保新增的字段均可空。

如果你已经遇到了这个问题，则需要手动将这些字段修改为可空字段。关于 mysql 的基础操作在这里就不多做赘述了。

在这一节的稍后，我们会介绍可以使用这些扩展方法的场景。
:::

::: warning
在安装了使用 ORM 对数据库扩展 JSON 类型的字段的插件后，可能会出现这个错误：

```
SyntaxError: Unexpected end of JSON input
```

在大部分情况下，这是因为 Koishi v3 的 ORM JSON 解析虽然能正常解析 `NULL` 和 `{}` （或其他正常的 JSON 字符串），但不能正常解析空字符串。([#382](https://github.com/koishijs/koishi/issues/382))

这一问题的诱因之一就是上文提到的“不可为空”（Not Nullable）问题。如果：

- 插件在扩展数据库时使用了 JSON 类型，但没有设置可空；
- 插件是在机器人开发中途被安装，在此之前，数据库中已经产生了数据行，

那么，在安装插件后，在解析既有数据行的 JSON 字段时就会出现这个错误。([#415](https://github.com/koishijs/koishi/issues/415))

如果你已经遇到了这个问题，除了将相关字段手动设置为可空，还需要将已有的数据手动初始化为 `NULL`。
:::

### 定义新表

和扩展已有的表类似，定义新表也需要用到 `Tables` 接口。不过除了 `fields` 属性，我们还需要指定一些其他的属性。下面的例子取自 `koishi-plugin-schedule` 中对新表的定义：

:::code-group language
```js
const { Tables } = require('koishi')

// 表的名字为 schedule
Tables.extend('schedule', {
  // 设置主键为字段 id
  primary: 'id'
  // 设置主键自增
  type: 'incremental'
  // 设置各字段类型
  fields: {
    id: 'unsigned',
    assignee: 'string',
    time: 'timestamp',
    lastCall: 'timestamp',
    interval: 'integer',
    command: 'text',
    session: 'json',
  }
})
```
```ts
import { Tables, Session } from 'koishi'

// TypeScript 用户需要进行类型合并
declare module 'koishi' {
  interface Tables {
    schedule: Schedule
  }
}

export interface Schedule {
  id: number
  assignee: string
  time: Date
  lastCall: Date
  interval: number
  command: string
  session: Partial<Session>
}

// 表的名字为 schedule
Tables.extend('schedule', {
  // 设置主键为字段 id
  primary: 'id'
  // 设置主键自增
  type: 'incremental'
  // 设置各字段类型
  fields: {
    id: 'unsigned',
    assignee: 'string',
    time: 'timestamp',
    lastCall: 'timestamp',
    interval: 'integer',
    command: 'text',
    session: 'json',
  }
})
```
:::

你也可以对每个字段使用上文中描述过的方法进行更加详细的定义。关于定义新表时的各个配置项请参考 [API 文档](../api/database.md#tables-extend-name-config)。

::: tip
在定义新表时，就不需要关注前文中提到的“不可为空”（Not Nullable）问题了。因为，不论是安装插件还是卸载插件，新表均独立运作，不会给其他表带来不可空的字段，从而引发上述问题。
:::

::: warning
另一方面，如果你的插件的功能是对其他用户开发的插件进行增强，其中你需要扩展其他用户定义的数据库，那么你仍然会受到上文中提到的“不可为空”制约。
:::

## 对单一数据库的支持

::: warning
下列方法都会导致你的代码只能用于单一数据库。使用下列方法代表你完全理解这一前提所带来的后果。
:::

在一些特殊的情况下，ORM 可能无法满足你的使用需求。以下的方法能过作为面对这种情形的最终手段。

### 扩展数据库方法

要为已有的数据库添加新的自定义方法，需要调用 `Database.extend()`：

::: code-group language
```js
const { Database } = require('koishi-core')

// 第一个参数声明这个方法依赖于 mysql 数据库
// 第二个参数表明这次调用注入的是 user 表
Database.extend('koishi-plugin-mysql', {
  // 要扩展的方法实现
  myMethod(...args) {
    // 此时这里的 this 实际上是一个 MysqlDatabase 对象
    return this.query(sql)
  },
})

ctx.database.myMethod(...args)
```
```ts
// 你应该将 koishi-plugin-mysql 作为插件的 devDependency
// 这个空的导入在编译中会自然消失，但会提供必要的类型注入
import {} from 'koishi-plugin-mysql'
import { Database } from 'koishi-core'

declare module 'koishi-core' {
  interface Database {
    myMethod(...args): Promise<SomeType>
  }
}

// 第一个参数声明这个方法依赖于 mysql 数据库
// 第二个参数表明这次调用注入的是 user 表
Database.extend('koishi-plugin-mysql', {
  myMethod(...args) {
    // 此时这里的 this 实际上是一个 MysqlDatabase 对象
    return this.query(sql)
  },
})
```
:::

这么做并不需要引入 koishi-plugin-mysql 作为插件的依赖。

实际上，编写数据库支持时也需要进行类似的方法定义，区别在于数据库支持中需要定义各个标准方法，而此处定义的则是用户的自定义方法。关于编写数据库支持的更多详情请参考 [编写数据库支持](./database-support)。

### 使用原始方案 <Badge text="不推荐" type="danger"/>

如果你需要调用原始的数据库接口而不是使用 ORM，你可以利用 Database 对象的特殊属性，它只在你使用了特定的数据库插件的时候有效：

```ts
// TypeScript 用户需要手动引入模块，否则将产生类型错误
import {} from '@koishijs/plugin-database-mysql'

// 直接发送 SQL 语句
ctx.database.mysql.query('select * from user')
```

其他数据库也有类似接口，例如 MongoDB 的原始接口可以通过 `ctx.database.mongo` 访问到。