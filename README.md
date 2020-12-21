<!-- # Lin-CMS-Flask -->

<h1 align="center">
  <a href="https://doc.cms.talelin.com/">
  <img src="https://doc.cms.talelin.com/left-logo.png" width="250"/></a>
  <br>
  Lin-CMS-Flask
</h1>

<h4 align="center">一个简单易用的CMS后端项目 | <a href="https://doc.cms.talelin.com/" target="_blank">Lin-CMS-Flask</a></h4>

<p align="center">
  <a href="http://flask.pocoo.org/docs/1.0/" rel="nofollow">
  <img src="https://img.shields.io/badge/flask-1.1.2-green.svg" alt="flask version" data-canonical-src="https://img.shields.io/badge/flask-1.1.2-green.svg" style="max-width:100%;"></a>
  <a href="https://pypi.org/project/Lin-CMS/" rel="nofollow"><img src="https://img.shields.io/badge/lin--cms-0.3.0a7-orange.svg" alt="lin--cms version" data-canonical-src="https://img.shields.io/badge/lin--cms-0.3.0a7-orange.svge" style="max-width:100%;"></a>
  <a href="https://doc.cms.talelin.com/" rel="nofollow"><img src="https://img.shields.io/badge/license-MIT-lightgrey.svg" alt="LISENCE" data-canonical-src="https://img.shields.io/badge/license-MIT-lightgrey.svg" style="max-width:100%;"></a>
</p>

<blockquote align="center">
  <em>Lin-CMS</em> 是林间有风团队经过大量项目实践所提炼出的一套<strong>内容管理系统框架</strong>。<br>
 Lin-CMS 可以有效的帮助开发者提高 CMS 的开发效率。
</blockquote>

<p align="center">
  <a href="#简介">简介</a>&nbsp;|&nbsp;<a href="#快速开始">快速开始</a>&nbsp;|&nbsp;<a href="#下个版本开发计划">下个版本开发计划</a>
</p>

## 简介

### 什么是 Lin CMS？

Lin-CMS 是林间有风团队经过大量项目实践所提炼出的一套**内容管理系统框架**。Lin-CMS 可以有效的帮助开发者提高 CMS 的开发效率。

本项目是 Lin CMS 后端的 Flask 实现，需要前端？请访问[前端仓库](https://github.com/TaleLin/lin-cms-vue)。

### 当前最新版本

lin-cms-flask(当前示例工程)：0.3.0a7

lin-cms(核心库) ：0.3.0a7

### 文档地址

[https://doc.cms.talelin.com/](https://doc.cms.talelin.com/)

### 线上 demo

[http://face.cms.talelin.com/](http://face.cms.talelin.com/)

### QQ 交流群

QQ 群号：643205479

<img class="QR-img" width="258" height="300" src="http://i1.sleeve.talelin.com/qq-group.jpeg">

### 微信公众号

微信搜索：林间有风

<img class="QR-img" src="http://i1.sleeve.talelin.com/wechat-account.jpeg">

### Lin CMS 的特点

Lin CMS 的构筑思想是有其自身特点的。下面我们阐述一些 Lin 的主要特点。

#### Lin CMS 是一个前后端分离的 CMS 解决方案

这意味着，Lin 既提供后台的支撑，也有一套对应的前端系统，当然双端分离的好处不仅仅在于此，我们会在后续提供`Java`版本的 Lin。如果您心仪 Lin，却又因为技术栈的原因无法即可使用，没关系，我们会在后续提供更多的语言版本。为什么 Lin 要选择前后端分离的单页面架构呢？

首先，传统的网站开发更多的是采用服务端渲染的方式，需用使用一种模板语言在服务端完成页面渲染：比如 JinJa2、Jade 等。
服务端渲染的好处在于可以比较好的支持 SEO，但作为内部使用的 CMS 管理系统，SEO 并不重要。

但一个不可忽视的事实是，服务器渲染的页面到底是由前端开发者来完成，还是由服务器开发者来完成？其实都不太合适。现在已经没有多少前端开发者是了解这些服务端模板语言的，而服务器开发者本身是不太擅长开发页面的。那还是分开吧，前端用最熟悉的 Vue 写 JS 和 CSS，而服务器只关注自己的 API 即可。

其次，单页面应用程序的体验本身就要好于传统网站。

#### 框架本身已内置了 CMS 常用的功能

Lin 已经内置了 CMS 中最为常见的需求：用户管理、权限管理、日志系统等。开发者只需要集中精力开发自己的 CMS 业务即可

#### Lin CMS 本身也是一套开发规范

Lin CMS 除了内置常见的功能外，还提供了一套开发规范与工具类。换句话说，开发者无需再纠结如何验证参数？如何操作数据库？如何做全局的异常处理？API 的结构如何？前端结构应该如何组织？这些问题 Lin CMS 已经给出了解决方案。当然，如果您不喜欢 Lin 给出的架构，那么自己去实现自己的 CMS 架构也是可以的。但通常情况下，您确实无需再做出架构上的改动，Lin 可以满足绝大多数中小型的 CMS 需求。

举例来说，每个 API 都需要校验客户端传递的参数。但校验的方法有很多种，不同的开发者会有不同的构筑方案。但 Lin 提供了一套验证机制，开发者无需再纠结如何校验参数，只需模仿 Lin 的校验方案去写自己的业务即可。

还是基于这样的一个原则：Lin CMS 只需要开发者关注自己的业务开发，它已经内置了很多机制帮助开发者快速开发自己的业务。

#### 基于插件的扩展

任何优秀的框架都需要考虑到扩展。而 Lin 的扩展支持是通过插件的思想来设计的。当您需要新增一个功能时，您既可以直接在 Lin 的目录下编写代码，也可以将功能以插件的形式封装。比如，您开发了一个文章管理功能，您可以选择以插件的形式来发布，这样其他开发者通过安装您的插件就可以使用这个功能了。毫无疑问，以插件的形式封装功能将最大化代码的可复用性。您甚至可以把自己开发的插件发布，以提供给其他开发者使用。这种机制相当的棒。

#### 前端组件库支持

Lin 还将提供一套类似于 Vue Element 的前端组件库，以方便前端开发者快速开发。相比于 Vue Element 或 iView 等成熟的组件库，Lin 所提供的组件库将针对 Lin CMS 的整体设计风格、交互体验等作出大量的优化，使用 Lin 的组件库将更容易开发出体验更好的 CMS 系统。当然，Lin 本身不限制开发者选用任何的组件库，您完全可以根据自己的喜好/习惯/熟悉度，去选择任意的一个基于 Vue 的组件库，比如前面提到的 Vue Element 和 iView 等。您甚至可以混搭使用。当然，前提是这些组件库是基于 Vue 的。

#### 完善的文档

我们将提供详尽的文档来帮助开发者使用 Lin

### 所需基础

由于 Lin 采用的是前后端分离的架构，所以您至少需要熟悉 Python 和 Vue。

Lin 的服务端框架是基于 Python Flask 的，所以如果您比较熟悉 Flask 的开发模式，那将可以更好的使用 Lin。但如果您并不熟悉 Flask，我们认为也没有太大的关系，因为 Lin 本身已经提供了一套完整的开发机制，您只需要在 Lin 的框架下用 Python 来编写自己的业务代码即可。照葫芦画瓢应该就是这种感觉。

但前端不同，前端还是需要开发者比较熟悉 Vue 的。但我想以 Vue 在国内的普及程度，绝大多数的开发者是没有问题的。这也正是我们选择 Vue 作为前端框架的原因。如果您喜欢 React Or Angular，那么加入我们，为 Lin 开发一个对应的版本吧。

## 快速开始

### Server 端必备环境

- 安装`Python`环境(version： 3.6+)

### 获取工程项目

打开您的命令行工具（terminal），在其中键入:

```bash
git clone https://github.com/TaleLin/lin-cms-flask.git -b 0.3.x starter
```

> **Tips:** 当前分支不是默认分支，所以需要分支切换到`0.3.x`
>
> 我们以 `starter` 作为工程名，当然您也可以以任意您喜爱的名字作为工程名。
>
> 如果您想以某个版本，如`0.0.1`版，作为起始项目，那么请在 github 上的版本页下载相应的版本即可。

### 安装依赖包

进入项目目录，调用环境中的 pip 来安装依赖包:

```bash
pip install -r requirements-${env}.txt
```

### 数据库配置

#### 默认使用 Sqlite3

Lin 默认启用 Sqlite3 数据库，打开项目根目录下的.env 文件(我们提供了开发环境的`.development.env`和生产环境的`.production.env`)，配置其`SQLALCHEMY_DATABASE_URI`

> Tips: 下面我们用{env}指代配置对应的环境

```conf
# 数据库配置示例
    SQLALCHEMY_DATABASE_URI='sqlite:///relative/path/to/file.db'

    or

    SQLALCHEMY_DATABASE_URI='sqlite:////absolute/path/to/file.db'
```

这将在项目的最外层目录生成名为`lincms${env}.db`的 Sqlite3 数据库文件。

#### 使用 MySQL

**Tips:** 默认的依赖中不包含 Python 的 Mysql 库，如有需要，请自行在您的运行环境中安装它（如`pymysql`或`cymysql`等）。

Lin 需要您自己在 MySQL 中新建一个数据库，名字由您自己决定(例如`lincms`)。

创建数据库后，打开项目根目录下的`.${env}.env`文件，配置对应的`SQLALCHEMY_DATABASE_URI`。

如下所示：

```conf
# 数据库配置示例: '数据库+驱动库://用户名:密码@主机:端口/数据库名'
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:123456@localhost:3306/lincms'
```

> 您所使用的数据库账号必须具有创建数据表的权限，否则 Lin 将无法为您自动创建数据表

### 初始化

如果您是第一次使用 **`Lin-CMS`**，需要初始化数据库。

请先进入项目根目录，然后执行`flask db init`,用来添加超级管理员 root(默认密码 123456), 以及新建其他必要的分组

> **Tips:**
> 如果您需要一些业务样例数据，可以执行脚本`flask db fake`添加它

### 运行

一切就绪后，再次从命令行中执行

```bash
flask run
```

如果一切顺利，您将在命令行中看到项目成功运行的信息。如果您没有修改代码，Lin 将默认在本地启动一个端口号为 5000 的端口用来监听请求。此时，我们访问`http://localhost:5000`，将看到一组字符：

“心上无垢，林间有风"

点击“心上无垢”，将跳转到`Redoc`页面；点击“林间有风”，跳转到`Swagger`页面。

这证明您已经成功的将服务运行起来了，Congratulations！

## 后续开发计划

- [ ] 新增 `websocket`模块
- [ ] 七牛 文件上传支持
- [ ] 启用插件机制
- [ ] 限流限频 功能
- [ ] 图形验证码
- [ ] 优化核心库逻辑
