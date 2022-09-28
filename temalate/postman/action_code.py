import copy

FOR_GET_ITEM_BY_NAME = """
row_index = 0
for(row in pm.response.json().$field) {
    if($target_value === pm.response.json().$field[row].$target_key) {
        row_index = row
        break
    }
}
"""

FOR_GET_ITEM_WITH_CUSTOM_FIELD = """
// 根据条件查找列表元素并组装成对象
for(row in pm.response.json().$field) {
    if($target_value === pm.response.json().$field[row].$target_key) {
        r = {}
        need_list = $need_extract_fields
        for(need in need_list) {
            parts = need_list[need].split(":")
            if (parts.length === 1) {
                 r[parts[0]] =  pm.response.json().$field[row][parts[0]]
            } else {
                resp_field = parts[0]
                new_field = parts[1]
                r[new_field] =  pm.response.json().$field[row][resp_field]
            }
        }
        pm.environment.set("$env_name",JSON.stringify(r))
        console.log(pm.environment.get("$env_name"))
    }
}
"""

FOR_GRT_PROCESS_GROUP = """
{FOR_GET_ITEM_WITH_CUSTOM_FIELD}
// 根据extend字段组装另一个对象, 通过<step_name>.<field_name>_extend访问
for(row in pm.response.json().$ex_field) {
    if($priority === pm.response.json().$field[row].$group_name) {
        rule = {}
        if(rule === undefined) {
            return
        }
        need_list = $need_extract_fields
        for(need in need_list) {
            parts = need_list[need].split(":")
            if (parts.length === 1) {
                 rule[parts[0]] =  pm.response.json().$ex_field[row][parts[0]]
            } else {
                resp_field = parts[0]
                new_field = parts[1]
                rule[new_field] =  pm.response.json().$ex_field[row][resp_field]
            }
        }
        extend_list = $extend_extract_fields
        for(extend in extend_list) {
            extend_field_name = extend_list[extend].split(":")[0]
            extend_field_value = extend_list[extend].split(":")[1]
            // if (extend_field_name == "smartDispatchs") {
            //    rule[extend_field_name] = true
            // } else{
            rule[extend_field_name] = extend_field_value
            //}
            
        }
        pm.environment.set("$env_name_extend",JSON.stringify(rule))
        console.log(pm.environment.get("$env_name_extend"))
    }
}
""".replace("{FOR_GET_ITEM_WITH_CUSTOM_FIELD}", FOR_GET_ITEM_WITH_CUSTOM_FIELD)

PRESCRIPT_CONVERT = """
body = pm.request.body
if(body.raw !== undefined) {
    const regex = /("{{data\.(.*?)}}")/g
    raw = pm.request.body.raw
    myreg=regex.exec(raw)
    while(true) {
        if(myreg === null) {
            break
        }
        value = eval(myreg[1])
        pm.request.body.raw = pm.request.body.raw.replace(myreg[1], JSON.stringify(eval(value)))
        myreg = regex.exec(raw)
    }
}
"""

SET_ENV = "set(\"$env_name\",$env_value)"

GET_ENV = "get(\"$env_name\")"

ADD_HEADER = "add(\"$value\",\"$key\")"

STATUS_OK = "to.have.status($status_code)"

FIELD_EXIST = "$pm_object.expect($field).to.ok"

FIELD_ASSERT = "$pm_object.expect($field).to.$ops($value)"

RESP_JSON = "json()"

REQUEST = "request"

HEADERS = "headers"

RESPONSE = "pm.response"

POSTMAN_OBJECT = "pm"

GLOBAL = "globals"

ENVIROMENT = "environment"

TEST_START = "pm.test(\"$step_name\",function(){\r"

TEST_END = "})"


def get_field_exist(field):
    s = f"{FIELD_EXIST}".replace("$pm_object", POSTMAN_OBJECT).replace("$field", f"{RESPONSE}.{RESP_JSON}.{field}")
    return s


def get_field_assert(field, value, ops):
    if type(value) == str and "data" not in value.split(".")[0]:
        value = f"\"{value}\""
    else:
        if type(value) == bool:
            if value:
                value = "true"
            else:
                value = "false"
        else:
            value = f"{value}"
    s = f"{FIELD_ASSERT}".replace("$pm_object", POSTMAN_OBJECT)\
            .replace("$field",f"{RESPONSE}.{RESP_JSON}.{field}")\
            .replace("$value", value).replace("$ops", ops)
    return s


def get_status_to_ok(code):
    s = f"{RESPONSE}.{STATUS_OK}".replace("$status_code", str(code))
    return s


def get_env_var():
    s = f"{POSTMAN_OBJECT}.{ENVIROMENT}.{GET_ENV}"
    return s


# 增加headers语句
def get_auth_statement():
    s = f"{POSTMAN_OBJECT}.{REQUEST}.{HEADERS}.{ADD_HEADER}"
    return s


def get_pm_resp():
    return copy.deepcopy(RESPONSE)


# 设置环境变量
def get_env_statement(t="env"):
    if t == "env":
        return f"{copy.deepcopy(POSTMAN_OBJECT)}.{ENVIROMENT}.{copy.deepcopy(SET_ENV)}"
    else:
        return f"{copy.deepcopy(POSTMAN_OBJECT)}.{GLOBAL}.{copy.deepcopy(SET_ENV)}"


def get_start():
    return copy.deepcopy(TEST_START)


def get_end():
    return copy.deepcopy(TEST_END)
