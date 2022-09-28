import copy
import json

import xlrd

data_map = {
    "用户名": "username",
    "密码": "password",
    "归属": "location",
    "调度方案名称": "schedule_solution",
    "调度类型": "schedule_rule_type",
    "在线定损规则": "rules",
    "外修调度规则": "outRepairerRules",
    "视频调度规则": "videoRules",
    "维修厂组": "repairers"
}

online_map = {
    "级别": "rule_level",
    "符号": "rule_sysmbol",
    "金额": "money_range",
    "维修厂组": "repairers",
    "规则类型": "is_super_rule",
    "案件类型": "rule_case_type",
    "是否拆检": "rule_cj",
    "是否估损": "rule_loss",
    "优先业务组": "priority_group",
    "兜底业务组": "bottom_group",
}

case_type = {
    "单独玻璃": "1",
    "车身划痕": "2",
    "涉水车辆": "3",
    "碰撞案件": "4",
    "大灾车辆": "5",
    "其他类型": "6",
}

schedule_type = {
    "在线定损": "13",
    "视频调度": "29",
    "外修调度": "32"
}

rule_setting = {
    "schedule_method": "",
    "allocation_rule": "",
}

def process_row_data(row):
    row['schedule_rule_type'] = schedule_type[row['schedule_rule_type']]
    count = len(row['rules'].split("\n")[0].split("/"))
    rules = [copy.deepcopy({}) for _ in range(count)]
    for idx,rule in enumerate(rules):
        for r in row['rules'].split("\n"):
            if "##" in r:
                group, gr = r[2:].split(": ")
                group_rule = gr.split("-")
                for idx2,g in enumerate(rule['priority_group']):
                    if g['name'] == group:
                        rule['priority_group'][idx2]['rule'] = copy.deepcopy(rule_setting)
                        if "分配到组" in group_rule:
                            rule['priority_group'][idx2]['rule']['schedule_method'] = "2"
                        if "分配到人" in group_rule:
                            rule['priority_group'][idx2]['rule']['schedule_method'] = "1"
                        if "忙闲分配" in group_rule:
                            rule['priority_group'][idx2]['rule']['allocation_rule'] = "1"
                        if "排班分配" in group_rule:
                            rule['priority_group'][idx2]['rule']['allocation_rule'] = "2"
                        if "在线分配" in group_rule:
                            rule['priority_group'][idx2]['rule']['allocation_rule'] = "3"
                        if "轮询调度" in group_rule:
                            rule['priority_group'][idx2]['rule']['allocation_rule'] = "4"
                        if "轮询排班调度" in group_rule:
                            rule['priority_group'][idx2]['rule']['allocation_rule'] = "5"
                        if "智能调度" in group_rule:
                            rule['priority_group'][idx2]['rule']['smartDispatch'] = "1"
                            rule['priority_group'][idx2]['rule']['smartDispatchs'] = True
                        else:
                            rule['priority_group'][idx2]['rule']['smartDispatch'] = "0"
                            rule['priority_group'][idx2]['rule']['smartDispatchs'] = False
                        for gl in group_rule:
                            if "饱和度" in gl:
                                rule['priority_group'][idx2]['rule']['saturation'] = f"{gl.split('饱和度')[1]}"
                                break
                for idx2,g in enumerate(rule['bottom_group']):
                    if g['name'] == group:
                        rule['bottom_group'][idx2]['rule'] = copy.deepcopy(rule_setting)
                        if "分配到组" in group_rule:
                            rule['bottom_group'][idx2]['rule']['schedule_method'] = "2"
                        if "分配到人" in group_rule:
                            rule['bottom_group'][idx2]['rule']['schedule_method'] = "1"
                        if "忙闲分配" in group_rule:
                            rule['bottom_group'][idx2]['rule']['allocation_rule'] = "1"
                        if "排班分配" in group_rule:
                            rule['bottom_group'][idx2]['rule']['allocation_rule'] = "2"
                        if "在线分配" in group_rule:
                            rule['bottom_group'][idx2]['rule']['allocation_rule'] = "3"
                        if "轮询调度" in group_rule:
                            rule['bottom_group'][idx2]['rule']['allocation_rule'] = "4"
                        if "轮询排班调度" in group_rule:
                            rule['bottom_group'][idx2]['rule']['allocation_rule'] = "5"
                        if "智能调度" in group_rule:
                            rule['bottom_group'][idx2]['rule']['smartDispatch'] = "1"
                            rule['bottom_group'][idx2]['rule']['smartDispatchs'] = True
                        else:
                            rule['bottom_group'][idx2]['rule']['smartDispatch'] = "0"
                            rule['bottom_group'][idx2]['rule']['smartDispatchs'] = False
                        for gl in group_rule:
                            if "饱和度" in gl:
                                rule['bottom_group'][idx2]['rule']['saturation'] = f"{gl.split('饱和度')[1]}"
                                break
                continue
            key, value = r.split(": ")
            new_key = online_map[key]
            value = value.split("/")[idx]
            if new_key == "rule_case_type":
                value = [case_type[v] for v in value.split(",")]
            if new_key == "rule_cj" or new_key == "rule_loss":
                if value == "是":
                    value = ["1"]
                else:
                    value = ["0"]
            if new_key == "is_super_rule":
                value = 0 if value == "普通" else 1
                rule['rule_mark'] = "2"
            else:
                rule['rule_mark'] = "1"
            if new_key == "money_range":
                if "-" in value:
                    min_value, max_value = value.split("-")
                    rule['rule_max_money'] = max_value
                    rule['rule_min_money'] = min_value
                else:
                    rule['rule_max_money'] = value
                    rule['rule_min_money'] = 0
                continue
            if new_key in ["priority_group", "bottom_group"]:
                if "," not in value:
                    value = [{"name": value,"rule": rule_setting}]
                else:
                    value_list = []
                    for x in value.split(","):
                        value_list.append(copy.deepcopy({"name": x,"rule": ""}))
                    value = value_list
            rule[new_key] = value

    row['rules'] = rules
    row['repairers'] = row['repairers'].split(",")
    return row


def get_row_data(keys, values):
    print(keys,values)
    if len(keys) != len(values):
        return []
    row_data = {}
    for idx, key in enumerate(keys):
        new_key = data_map[key]
        value = values[idx]
        row_data[new_key] = value
    row_data = process_row_data(row_data)
    return row_data


def get_excel(path):
    demo_xls = xlrd.open_workbook(path)
    sheet = demo_xls.sheets()[0]
    rows = sheet.nrows
    excel_all_rows = []
    for r in range(1, 3):
        row_col = sheet.row_values(r)
        data = get_row_data(sheet.row_values(0),row_col)
        excel_all_rows.append(data)
    with open("data2.json", 'w') as file:
        json.dump(excel_all_rows, file, indent=4, ensure_ascii=True)

def get_testcase_data_from_db():

    pass


def get_testdata_from_db():
    pass

path = "C:\\Users\\ds\\Desktop\\测试数据.xls"
get_excel(path)
