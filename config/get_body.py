import copy
from utils.body_builder.schedule_soloution.online_loss import *
from config.body import *
from utils.data.get_json import *

form_map = {
    "sso/oauth/token": login,
    "v2/gsoc/rest/rule/GisControlRunSystemService/addupdateProgram":copy.deepcopy(create_schedule),
}


def get_body(url_path):
    path = "C:\\Users\\ds\\apitest\\data2.json"
    content = json.loads(get_data(path))
    if form_map.get(url_path,"") == "":
        return ""
    body_template = form_map.get(url_path)
    for idx, c in enumerate(content):
        content[idx][f"{url_path}_body"] = json.dumps(get_builded_body(url_path, copy.deepcopy(login), c, body_template))
        with open(path, 'w') as f:
            json.dump(content, f, indent=4, ensure_ascii=True)
    rs = "{{" + url_path + "_body}}"
    return body_template


def get_options(data_type,body):
    if data_type == "raw":
        body['options'] = {
            f"{data_type}": {
                "language": "json"
            }
        }
    return body
