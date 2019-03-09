# oss 插件

## 插件模板自动生成

请在项目的根目录下运行如下命令：

```bash
python vendor/plugin_generator.py -n oss
```

即可快速生成一个名为oss的插件，`-n`表示指定插件名

## 添加requirements.txt

如果你是在插件中使用了一些第三方库，这些库在主应用中是没有的，那么请你将它添加到**requirements.txt**中。