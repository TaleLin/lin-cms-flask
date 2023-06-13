# Lin-CMS 的腾讯云 cos 插件

基于 Lin—CMS 0.4.8 开发

[Lin-CMS 项目地址](https://github.com/TaleLin/lin-cms-flask)


## 插件使用方法

1. 然后执行初始化脚本，把插件注册到 app 的 config 文件中
```bash
flask plugin init
```
（命令行输入插件名字： cos）

2. 再次启动项目即可


## 接口描述

目前共实现了 3 个接口
- 上传单张图片
  - `POST <base_url>/plugin/cos/upload_one` 
- 上传多张图片
  - `POST <base_url>/plugin/cos/upload_multiple`
- 获取单个cos对象
  - `GET <base_url>/plugin/cos/<int:id>`
    - 返回值
      - id 
      - url （根据配置项，返回 cos 永久链接或者 cos 临时链接）
      - file_name （文件的实际名字）
      - file_key（cos 的唯一文件 key）


## 配置项

详细的插件配置见文件 `cos/config.py` 内的描述





