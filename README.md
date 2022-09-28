# 后端接口自动化解决方案

## 技术方案

- ##### 通过协作平台录入用例和测试数据到数据库
- ##### 读取数据并做处理生成collection
- ##### 使用 `postman runner`　去执行


## 目录结构

- ##### `collections`: 存放生成的collection文件
- ##### `log`: 存放运行collection后的日志文件
- ##### `reports`: 存放测试报告 
- ##### `config`: 存放配置相关的东西,比如url与body,query的映射,以及一些域名的配置
- ##### `db`: 存放和db相关的操作,比如获取jira的信息,获取测试数据
- ##### `generate`: 生成collection和测试脚本的工具类
- ##### `template`: 存放模板,包括collection以及测试脚本
- ##### `utils`: 存放一些公共操作
- ##### `main.py`： 主入口

