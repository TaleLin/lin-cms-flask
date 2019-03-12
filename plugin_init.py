"""
    :copyright: © 2019 by the Lin team.
    :license: MIT, see LICENSE for more details.
"""
import re
from importlib import import_module

import os

from app.app import create_app

"""
插件初始化流程:
1、输入要初始化的插件名称。（多个用空格隔开，*表示初始化所有）
2、python依赖的自动检测和安装
2、将插件的配置写入到项目setting.py中
3、将model中的模型插入到数据库中
4、如果有需要，将初始数据插入到数据表中
"""


class PluginInit:
    # 插件位置默认前缀
    plugin_path = 'app.plugins'

    def __init__(self, name):
        self.app = create_app(register_all=False)
        self.name = name.strip()
        # 插件相关的路径信息，包含plugin_path(插件路径)，plugin_config_path(插件的配置文件路径)，plugin_info_path(插件的基本信息路径)
        self.path_info = dict()
        # 根据name生成path，写入到path_info属性中
        self.generate_path()
        # 安装依赖
        self.auto_install_rely()
        # 将插件的配置自动写入setting
        self.auto_write_setting()
        # 创建数据表，并且向表中插入模型中的一些初始数据
        self.create_data()

    def generate_path(self):
        if self.name == '*':
            names = self.__get_all_plugins()
        else:
            names = self.name.split(" ")
        for name in names:
            exit('插件名称不能为空，请重试') if self.name == '' else print('正在初始化插件' + name + '...')
            self.path_info[name] = {
                'plugin_path': self.plugin_path + '.' + name,
                'plugin_config_path': self.plugin_path + '.' + name + '.config',
                'plugin_info_path': self.plugin_path + '.' + name + '.info'
            }

    def auto_install_rely(self):
        from subprocess import CalledProcessError
        for name in self.path_info:
            filename = 'requirements.txt'
            file_path = self.app.config.root_path + '/plugins/' + name + '/' + filename
            success_msg = '安装' + name + '插件的依赖成功'
            fail_msg = name + '插件的依赖安装失败，请[手动安装依赖]: http://doc.7yue.pro/'
            if os.path.exists(file_path):
                if (os.path.getsize(file_path)) == 0:
                    continue
                print('正在安装' + name + '插件的依赖...')

                try:
                    # 使用try except来判断使用pip管理包还是pipenv管理包，首选pipenv
                    ret = self.__execute_cmd(cmd='pipenv install -r ' + file_path)

                    if ret:
                        print(success_msg)
                    else:
                        exit(fail_msg)

                except CalledProcessError:
                    try:
                        ret = self.__execute_cmd(cmd='pip install -r ' + file_path)

                        if ret:
                            print(success_msg)
                        else:
                            exit(fail_msg)

                    except Exception as e:
                        exit((str(e)) + '\n' + fail_msg)

                except Exception as e:
                    exit((str(e)) + '\n' + fail_msg)

    def auto_write_setting(self):
        print('正在自动写入配置文件...')
        setting_text = dict()
        for name, val in self.path_info.items():
            try:
                info_mod = import_module(self.path_info[name]['plugin_info_path'])
            except ModuleNotFoundError as e:
                raise exit(str(e) + '\n未找到插件' + name + '，请检查您输入的插件名是否正确')

            res = self._generate_setting(name, info_mod)
            setting_text[name] = res

        # 正则匹配setting.py中的配置文件，将配置文件替换成新的setting_doc
        self.__update_setting(new_setting=setting_text)

    def create_data(self):
        print('正在创建基础数据...')
        for name, val in self.path_info.items():
            # 调用插件__init__模块中的initial_data方法，创建初始的数据
            try:
                plugin_module = import_module(self.path_info[name]['plugin_path'] + '.app.__init__')
                dir_info = dir(plugin_module)
            except ModuleNotFoundError as e:
                raise exit(str(e) + '\n未找到插件' + name + '，请检查您输入的插件名是否正确')
            if 'initial_data' in dir_info:
                # TODO 解决多次初始化数据重复添加的问题
                plugin_module.initial_data()
        print('插件初始化成功')

    def _generate_setting(self, name, info_mod):
        info_mod_dic = info_mod.__dict__
        ret = {
            'path': self.path_info[name]['plugin_path'],
            'enable': True,
            'version': info_mod_dic.pop("__version__", '0.0.1')  # info_mod_dic.__version__
        }
        # 向setting_doc中写入插件的配置项
        cfg_mod = import_module(self.path_info[name]['plugin_config_path'])
        dic = cfg_mod.__dict__
        for key in dic.keys():
            if not key.startswith('__'):
                ret[key] = dic[key]
        return ret

    def __update_setting(self, new_setting):
        # 得到现存的插件配置
        old_setting = self.app.config.get('PLUGIN_PATH')
        final_setting = self.__cal_setting(new_setting, old_setting)

        sub_str = 'PLUGIN_PATH = ' + self.__format_setting(final_setting)

        setting_path = self.app.config.root_path + '/config/setting.py'
        with open(setting_path, 'r') as f:
            content = f.read()
            pattern = 'PLUGIN_PATH = \{([\s\S]*)\}+.*?'
            result = re.sub(pattern, sub_str, content)

        with open(setting_path, 'w+') as f:
            f.write(result)

    def __get_all_plugins(self):
        # 返回所有插件的目录名称
        ret = []
        path = self.app.config.root_path + '/plugins'
        for file in os.listdir(path=path):
            file_path = os.path.join(path, file)
            if os.path.isdir(file_path):
                ret.append(file)
        return ret

    @classmethod
    def __execute_cmd(cls, cmd):
        import subprocess
        code = subprocess.check_call(cmd, shell=True, stdout=subprocess.PIPE)
        if code == 0:
            return True
        elif code == 1:
            return False

    @classmethod
    def __format_setting(cls, setting):
        # 格式化setting字符串
        setting_str = str(setting)
        ret = setting_str.replace('},', '},\n   ').replace('{', '{\n    ', 1)
        replace_reg = re.compile(r'\}$')
        ret = replace_reg.sub('\n}', ret)
        return ret

    @staticmethod
    def __cal_setting(new_setting, old_setting):
        # 将新旧的setting合并，返回一个字典
        # 1、对比old和new，并且将这两个配置合并
        # 2、如果新的存在，旧的不存在，就追加新的；
        # 3、如果旧的存在，新的不存在，就保留旧的；
        # 4、如果新旧都存在，那么在版本号相同的情况下，保留旧的配置项，否则新的配置覆盖旧的配置。

        final_setting = dict()
        all_keys = new_setting.keys() | old_setting.keys()  # 得到新旧配置的并集

        for key in all_keys:
            if key not in old_setting.keys():
                # 不存在，追加新的
                final_setting[key] = new_setting[key]
            else:
                # 存在，对比版本号，看看是否需要更新  TODO 优化条件判断
                if key not in new_setting:
                    # 新的不存在
                    final_setting[key] = old_setting[key]
                else:
                    # 新的存在
                    if new_setting[key]['version'] == old_setting[key]['version']:
                        # 版本号相同，使用旧的配置
                        final_setting[key] = old_setting[key]
                    else:
                        # 版本号不同，更新配置为新的
                        final_setting[key] = new_setting[key]

        return final_setting


if __name__ == '__main__':
    plugin_name = input('请输入要初始化的插件名，如果多个插件请使用空格分隔插件名，输入*表示初始化所有插件:\n')
    PluginInit(plugin_name)
