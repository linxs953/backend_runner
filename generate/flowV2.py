import re
import sys

sys.path.append(".")
from db.get_api_case import getAPITestCase
from db.get_domain import getDomainByType
from config.get_body import *
from config.get_query import *
from temalate.postman.collection import *
from utils.path.path_ops import createDir
from temalate.postman.action_code import *
from log.flow import *
from loguru import logger


class GenerateFlowV2:
    def __init__(self, business_name, module_name, scene_name):
        self.schema = "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
        self.root = "C:\\Users\\ds\\apitest\\collections"
        self.collection_path = f"{business_name}/{module_name}"
        self.key = scene_name
        self.response = []
        self.template = CollectionTemplate()
        self.init_testcase(business_name, module_name, scene_name)
        self.init_header()

    def init_testcase(self, business_name, module_name, scene_name):
        self.steps = getAPITestCase(business_name, module_name, scene_name)

    def init_header(self):
        self.headers = []


    """
        生成collection的入口
    """
    @logger.catch
    @flow_logger("generate collection")
    def generate(self):
        collection_template = self.template.get_collection_template()
        collection_template['info']['name'] = self.key
        collection_template['info']['schema'] = self.schema
        collection_template['item'] = self.generate_items()
        self.write_to_dis(f"{self.collection_path}/{self.key}.json", collection_template)

    """
        生成postman请求的url模块
    """

    def generate_url_part(self, step):
        url_template = self.template.get_url_template()
        url_path = step['api_case_info']['api_path']
        m_param = None

        # 用例里面加了参数，需进行参数更新
        if "?" in url_path:
            url_path, m_param = url_path.split("?")
            url_template["path"] = url_path.split("/")
            obj = {}
            for row in m_param.split("&"):
                key, value = row.split("=")
                obj[key] = value
            url_template['query'] = get_query(url_path, obj)
            url_path = f"{url_path}?"
            for q in get_query(url_path, m_param):
                param, value = q["key"], q["value"]
                url_path += f"{param}={value}"
        else:
            url_template["path"] = url_path.split("/")
            url_template['query'] = get_query(url_path) if get_query(url_path) != '' else []

        # 设置domain type，返回确定的url域名
        domain_type = step['api_case_info']['api_domain_type']
        domain_value = getDomainByType(domain_type)[0][0]

        # 根据domain type的值，设置request的row字段
        if domain_type == "GS_LOGIN":
            url_template['host'] = [domain_value]
            url_template["row"] = f"{domain_value}/{url_path}"

        elif domain_type == "GS_IM_SERVER":
            url_template['host'] = [domain_value]
            url_template["row"] = f"{domain_value}/{url_path}"

        else:
            url_template['host'] = [domain_value]
            url_template["raw"] = f"{domain_value}/{url_path.replace('?', '')}"

        return url_template

    """
        生成postman request的request模块
    """
    def generate_request(self, step, data_type="raw", data=None):
        request_template = self.template.get_request_template()
        request_template["method"] = step['api_case_info']['method']
        request_template["header"] = self.headers
        request_template["url"] = self.generate_url_part(step)
        if self.generate_body(step, data_type) != "":
            request_template['body'] = self.generate_body(step, data_type, data)
        return request_template

    """
        生成postman request的body模块
    """
    def generate_body(self, step, data_type="raw", data=None):
        body_template = self.template.get_body_template()
        body_template["mode"] = f"{data_type}"
        body_template = get_options(data_type, body_template)
        if get_body(step['api_case_info']['api_path']) != "":
            b_template = get_body(step['api_case_info']['api_path'])
            body = self.fill_body(b_template, data)
            body_template[f'{data_type}'] = body
        else:
            body_template = ""
        return body_template

    """
        生成prescript和test脚本
    """
    def generate_events(self, scripts, data):
        events = [
            self.template.get_event(self.template.get_scrpt(scripts)),
        ]
        # 生成prescript
        if data:
            events.append(self.template.get_event(self.template.get_scrpt(data), event_type="prerequest"))
        return events

    """
        1. 支持断言json类型数据，比如data.user.userAccount
        2. 支持检索并断言list类型数据，比如层级是data.roles=[{}]
            - 通过search=<field=value>字段，在list中查找符合field=value的对象
            - 断言该对象，拿对象实际值与引用的数据文件的内容相比对
    """

    def expect(self, expected_list):
        #  [{"field":"status_code","expect":200}]
        statements = []
        for expect in json.loads(str(expected_list)):
            field_name = expect['field']
            field_search = expect.get('search', '')
            field_value = expect['expect']
            operation = expect['operation']
            if field_search != "":
                #  groupName=xxx, 断言列表对象数据
                key, value = field_search.split("=")
                get_index = FOR_GET_ITEM_BY_NAME
                if "data" not in value.split(".")[0]:
                    value = f"\"{value}\""
                get_index = get_index.replace("$target_value", value).replace("$field", field_name).replace(
                    "$target_key", key)
                statements.append(get_index)
                field_name = f"{field_name}[row_index].{key}"
            statements.append(get_field_exist(field_name))
            statements.append(get_field_assert(field_name, field_value, operation))
        return statements

    """
        解析data_dependency字段，生成引用上游数据的prescripts
    """

    def parse_reference(self, data):
        # 数据格式 [{"step": "获取token","extract_field":"access_token,token_type", "location":"headers", "key":"Authorization"}]
        if data == "" or not data or len(data) == 0:
            return []
        statements = []
        for dependency in json.loads(str(data)):
            value = dependency['extract_field'].split(",")
            header_statement = self.get_headers_pre_statement(dependency['step'], dependency['location'], value,
                                                              dependency['key'])
            if header_statement:
                statements.append(header_statement)
        statements.append(PRESCRIPT_CONVERT)
        return list(statements)

    """
        根据接口body的模板，填充body内容
    """
    def fill_body(self, template, data_dependency):
        if not data_dependency:
            return json.dumps(template, ensure_ascii=False)
        new_data = copy.deepcopy(template)
        for data in json.loads(str(data_dependency)):
            if data['location'] == "body":
                # 引用数据文件
                if data.get("step", "") == "":
                    if "." in data['key']:
                        # 嵌套数据引用 a[0].b.c
                        expression = "new_data"
                        for idx, part in enumerate(data['key'].split(".")):
                            if "[" in part:
                                left, right = part.split("[")
                                index = right.split("]")[0]
                                expression = f"{expression}['{left}']"
                                expression = f"{expression}[{eval(index)}]"
                            else:
                                expression = f"{expression}['{part}']"
                        expression = f"{expression}=" + "\"{{" + data['extract_field'] + "}}\""
                        exec(expression)
                    else:
                        new_data[data['key']] = "{{" + data['extract_field'] + "}}"
                # 引用上游接口数据
                else:
                    # 嵌套数据引用 a[0].b.c
                    if "." in data['key']:
                        expression = "new_data"
                        for idx, part in enumerate(data['key'].split(".")):
                            if "[" in part:
                                left, right = part.split("[")
                                index = right.split("]")[0]
                                expression = f"{expression}['{left}']"
                                expression = f"{expression}[{eval(index)}]"
                            else:
                                expression = f"{expression}['{part}']"
                        object_type = type(eval(expression))
                        if object_type == list:
                            expression = f"{expression}.append(" + "\"{{" + f"{data['step']}-{data['extract_field']}" + "}}\")"
                        if object_type == str:
                            expression = f"{expression}=" + "\"{{" + f"{data['step']}-{data['extract_field']}" + "}}\""
                        # 执行表达式，new_data[a][b] = xxx
                        exec(expression)
                    else:
                        # 操作的对象类型是string， 赋值，是列表，追加
                        # <操作对象类型>： 写入对象位置是body.a.b.c,body[a][b][c]的类型
                        value = '{{' + f"{data['step']}-{data['extract_field']}" + '}}'
                        if type(new_data[data['key']]) == str:
                            new_data[data['key']] = value
                        if type(new_data[data['key']]) == list:
                            new_data[data['key']].append(value)

        # 对body进行额外处理，引用数据是对象类型，去除引号
        dump_obj = json.dumps(new_data, ensure_ascii=False)
        for data in json.loads(str(data_dependency)):
            if str(data['extract_type']) == "dict":
                com = re.compile(r"(\"{{$data}}\")".replace("$data", f"{data['step']}-{data['extract_field']}"))
                for f in com.findall(dump_obj):
                    new_find = str(f).replace('"', "")
                    logger.debug(f"replace {f} to {new_find}")
                    dump_obj = dump_obj.replace(f, new_find)
        return dump_obj

    """
        根据data_dependency字段解析出来的数据引用关系，生成引用脚本
    """

    def get_headers_pre_statement(self, step_name, location, values, key_name):
        if location == "headers":
            # 目前加header的场景只有token，故这里先写死
            v = ""
            for value in values:
                v += "{{" + f"{step_name}-{value}" + "}} "
            set_statement = get_auth_statement().replace("$key", key_name).replace("$value", v)
            return set_statement
        elif location == "body":
            pass

    """
        根据从表中读出来的用例，遍历生成每个请求item
    """
    @logger.catch
    @flow_logger("generate items")
    def generate_items(self):
        collection_items = []

        @logger.catch
        @flow_logger("generate item")
        def generate_item():
            for step in self.steps:
                logger.debug(f"开始生成 <{step['base_info']['step_name']}> 步骤")
                data_ = step['api_case_info']['data_dependency']
                item_template = self.template.get_sub_folder_item_template()
                item_template["name"] = step['base_info']['step_name']
                item_template["request"] = self.generate_request(step, data_type="raw", data=data_)
                item_template["response"] = self.response
                item_template["event"] = self.generate_events(
                    self.generate_scripts(step["api_case_info"]["extract"], step['api_case_info']['expect'],
                                          step['base_info']['step_name']),
                    self.parse_reference(data_)
                )
                logger.debug(f"步骤 <{step['base_info']['step_name']}> 生成成功")
                collection_items.append(item_template)
            return collection_items

        return generate_item()

    """
    生成请求item的test脚本
    """
    def generate_scripts(self, step_extract, step_expect, step_name):
        cause_template = get_env_statement()
        exec_start = get_start()
        exec_end = get_end()

        # 添加pm.test 方法起始行
        extract_causes = [exec_start.replace("$step_name", f"{step_name}")]
        extract_causes.append(get_status_to_ok(200))
        if not (step_expect == [] or step_expect == ""):
            extract_causes.extend(self.expect(str(step_expect)))

        if not (step_extract == [] or step_extract == ""):
            for ex in json.loads(str(step_extract)):
                # 数据格式  [{"field":"resp字段", "name": "", "search": "", "need_field": [], "extend_field":["field1:1"]}]
                # 接口如果有extract字段，并且指定了search， 根据某个字段搜索并组装新的对象
                if ex.get("search", "") != "" or ex.get("need_field", "") != "":
                    search_name, search_value = ex['search'].split("=")
                    extend = []
                    # 如果组装数据 需要其他字段
                    if ex.get('extend', "") != "":
                        extend = ex['extend']
                    get_custom_item = FOR_GRT_PROCESS_GROUP \
                        .replace("$field", ex['field']) \
                        .replace("$target_value", search_value) \
                        .replace("$target_key", search_name) \
                        .replace("$need_extract_fields", str(ex['need_field'])) \
                        .replace("$env_name", f"{step_name}-{ex['name']}") \
                        .replace("$ex_field", ex['field']) \
                        .replace("$priority", search_value) \
                        .replace("$group_name", search_name) \
                        .replace("$extend_extract_fields", str(extend))
                    extract_causes.append(get_custom_item)
                    continue
                value = f"{get_pm_resp()}.{RESP_JSON}"
                cause = copy.deepcopy(cause_template)

                # 生成引用数据表达式(.a.b.c)
                if "." in ex['field']:
                    for e in ex['field'].split("."):
                        value += f".{e}"
                else:
                    value += f".{ex['field']}"
                cause = cause.replace("$env_name", f"{step_name}-{ex['name']}").replace("$env_value", value)
                extract_causes.append(cause)

        # 添加pm.test结束行
        extract_causes.append(exec_end)
        return extract_causes

    """
        生成json文件
    """
    def write_to_dis(self, filepath, content):
        path_parts = filepath.split("/")
        for idx, p in enumerate(path_parts):
            if idx == 0:
                filepath = f"{self.root}"
            if "." not in p:
                filepath += f"\\{p}"
        createDir(filepath)
        filepath = f"{filepath}\\{path_parts[len(path_parts) - 1]}"
        filepath = filepath.replace("/", "\\", -1)
        with open(filepath, 'w', encoding="utf8") as file:
            json.dump(content, file, indent=4, ensure_ascii=False)
        logger.debug(f"生成json成功，路径: {filepath}")
