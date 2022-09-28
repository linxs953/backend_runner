import sys
sys.path.append(".")
from db.get_jira import getTestCaseContent
from config.url_domain import *
from config.get_body import *
from config.get_headers import *
from config.get_query import *
from temalate.postman.collection import *
from utils.path.path_ops import createDir
from temalate.postman.action_code import *
import json


class GenerateCollections:
    def __init__(self, domain_type, title, no, path, filename):
        self.domain = domain_type
        self.root = "C:\\Users\\ds\\apitest\\collections"
        self.collection_path = path
        self.key = filename
        self.schema = "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
        self.template = CollectionTemplate()
        self.jira_title = title
        self.issue_no = no
        self.init_testcase()
        self.init_header()
        self.init_response()

    def init_testcase(self):
        self.steps = getTestCaseContent(self.jira_title, self.issue_no)

    def init_response(self):
        self.response = []

    def init_header(self):
        self.headers = get_default_headers()

    def extract(self, raw):
        step = raw['step']
        if step.get("extract","") == "":
            return []
        step_extract = step['extract']
        cause_template = get_env_statement()
        exec_start = get_start()
        exec_end = get_end()
        extract_causes = [exec_start.replace("$step_name",f"{step['step_name']}")]
        for ex in step_extract.split(","):
            value = f"{get_pm_resp()}.{RESP_JSON}"
            cause = copy.deepcopy(cause_template)
            if "." in ex:
                for e in ex.split("."):
                    value += f".{e}"
            else:
                value += f".{ex}"
            cause = cause.replace("$env_name", f"{ex}").replace("$env_value", value)
            extract_causes.append(cause)
        extract_causes.append(exec_end)
        return extract_causes

    def generate_body(self, step, data_type="raw"):
        body_template = self.template.get_body_template()
        body_template["mode"] = f"{data_type}"
        body_template = get_options(data_type, body_template)
        if get_body(step['url_path']) != "":
            body_template[f'{data_type}'] = get_body(step['url_path'])
        else:
            body_template = ""
        return body_template

    def generate_request(self, step, data_type="raw"):
        request_template = self.template.get_request_template()
        request_template["method"] = step['method']
        request_template["header"] = self.headers
        request_template["url"] = self.generate_url_part(step)
        if self.generate_body(step, data_type) != "":
            request_template['body'] = self.generate_body(step, data_type)
        return request_template

    def generate_events(self, scripts,prescripts):
        events = [
            self.template.get_event(self.template.get_scrpt(scripts)),
        ]
        if prescripts:
            events.append(self.template.get_event(self.template.get_scrpt(prescripts),event_type="prerequest"))
        return events

    def get_sub_folder_name(self, step):
        title = step['step_name']
        parts = title.split("-")
        return parts[0]

    def get_api_item_name(self, step):
        title = step['step_name']
        parts = title.split("-")
        return parts[1]

    def generate_sub_folder(self, title,data):
        folder_name = title.split("-")[0]
        sub_folder_item = []
        sub_folder_template = self.template.get_sub_folder_template()
        sub_folder_template["name"] = folder_name
        for step in self.steps:
            datas = step['data']
            folder = self.get_sub_folder_name(step['step'])
            if folder == folder_name:
                item_template = self.template.get_sub_folder_item_template()
                item_template["name"] = self.get_api_item_name(step['step'])
                item_template["request"] = self.generate_request(step['step'], data_type="raw")
                item_template["response"] = self.response
                item_template["events"] = self.generate_events(self.extract(step),self.parse_reference(datas,step['step']['step_name']))
                sub_folder_item.append(item_template)
        sub_folder_template["item"] = sub_folder_item
        return sub_folder_template

    def generate(self):
        collection_template = self.template.get_collection_template()
        collection_template['info']['name'] = self.key
        collection_template['info']['schema'] = self.schema
        collection_template['item'] = self.generate_folders()
        self.write_to_dis(f"{self.collection_path}/{self.key}.json", collection_template)

    def get_statement(self,env,location,step):
        if location == "header":
            get_env_statement = get_env_var().replace("$env_name",env)
            set_statement = get_auth_statement().replace("$value",AUTH_VALUE.replace("$step_name.","",-1))
            return [get_env_statement,set_statement]
        elif location == "body":
            pass
    def parse_reference(self,data,step_name):
        if data == "":
            return
        statements = []
        data_part = str(data[2:]).split("#")
        env_name = data_part[0]
        location = data_part[1].split(".")[0]
        key = data_part[1].split(".")[1]
        statements.extend(self.get_statement(env_name, location, step_name))
        return statements

    def generate_folders(self):
        has_generate = set()
        collection_folders = []
        for row in self.steps:
            step = row['step']
            folder = step['step_name'].split("-")[0]
            refer_data = row['data']
            refer_statement = self.parse_reference(refer_data,step['step_name'])
            if folder in has_generate:
                continue
            sub_folder = self.generate_sub_folder(step['step_name'],refer_statement)
            collection_folders.append(sub_folder)
            has_generate.add(folder)
        return collection_folders

    def write_to_dis(self, filepath, content):
        path_parts = filepath.split("/")
        if "." in path_parts[0]:
            path_parts[0] = self.root
            filepath = "/".join(path_parts)
        else:
            filepath = f"{self.root}\\{path_parts[0]}"
            createDir(filepath)
            filepath = f"{filepath}\\{path_parts[1]}"
        filepath = filepath.replace("/", "\\", -1)
        with open(filepath, 'w') as file:
            json.dump(content, file, indent=4, ensure_ascii=True)
        print(f"生成json成功，路径: {filepath}")

    def generate_url_part(self, step, domain_type="login"):
        url_template = self.template.get_url_template()
        url_path = step['url_path']
        m_param = None
        if "," in url_path:
            url_path = step['url_path'].split(",")[0]
            m_param = step['url_path'].split(",")[1]
        url_template["path"] = url_path.split(',')[0].split("/")
        if get_query(url_path) != "":
            url_template['query'] = get_query(url_path,m_param)
            url_path = f"{url_path}?"
            for q in get_query(url_path,m_param):
                param, value = q["key"], q["value"]
                url_path += f"{param}={value}"
        if "sso" not in url_path:
            domain_type = self.domain
        if "gsimserver" in url_path:
            domain_type = "gs_im_server"
        if domain_type == "login":
            url_template['host'] = [login_domain]
            url_template["row"] = f"{login_domain}/{url_path}"
        elif domain_type == "gs_im_server":
            url_template['host'] = [gs_im_server]
            url_template["row"] = f"{gs_im_server}/{url_path}"
        else:
            url_template['host'] = [gs]
            url_template["raw"] = f"{gs}/{url_path}"
        return url_template
