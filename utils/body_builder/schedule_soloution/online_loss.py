import json
import requests

gs_login_api = "https://ssopre.chexinhui.com/sso/oauth/token"
repairer_api = "https://apirestpre.chexinhui.com/v2/gsoc/rest/rule/DmsGroupService/queryGroup?page=1&rows=10000&ruleType=13"
business_group_api = "https://apirestpre.chexinhui.com/v2/gsoc/rest/rule/DmsPersonService/querybusiness?page=1&rows=100000"
company_api = "https://apirestpre.chexinhui.com/v2/gsoc/rest/rule/DmsPersonService/queryMapUser"
conutry_api = "https://apirestpre.chexinhui.com/v2/gsoc/rest/rule/DmsPersonService/queryCounty"
query_person_api = "https://apirestpre.chexinhui.com/v2/gsoc/rest/rule/DmsPersonService/queryPerson?groupCodes={}"
video_group_api = "https://apirestpre.chexinhui.com/v2/gsoc/rest/rule/DmsPersonService/queryOrg?groupType=2&groupName"
accessory_api = "https://apirestpre.chexinhui.com/rest/modelfacade/StdPartService/findPartByEnter?enterParam={}"
factory_groups_api = "https://apirestpre.chexinhui.com/v2/gsoc/rest/rule/DmsGroupService/queryFactoryListWx?page=1&rows=10000&groupName="
user_api = "https://apirestpre.chexinhui.com/v2/rest/org/user"
query_wx_api = "https://apirestpre.chexinhui.com/v2/rest/dstenant/DsspTenantRelationService/query?tenantSource=&audit=0&queryType=page&queryName=queryRelationly&valid=Y&page=1&rows=10000&toTenantType=6&tenantName=&ordId={ordid}&unitId={unitid}"

def get_unitId(province,header):
    resp = requests.request("GET",conutry_api, headers=header).text
    respJson = json.loads(resp)
    for row in respJson:
        if province == row['text']:
            return row['id']
    return ""

def get_org_id(header):
    resp = requests.request("GET", user_api, headers=header).text
    orgid = json.loads(resp)['orgId']
    return orgid

def get_provice_by_name(province,param,header):
    url = conutry_api
    if param != "":
        url = f"{conutry_api}?{param}"
    resp = requests.request("GET",url,headers=header).text
    respJson = json.loads(resp)
    for row in respJson:
        if row['text'] == province:
            return row['id']
    return ""

def get_wx_repairers(repairers, province, headers):
    wx_repairers = []
    wx_url = query_wx_api.replace("{ordid}",get_org_id(headers)).replace("{unitid}",get_unitId(province,headers))
    print(f"wx url: {wx_url}")
    resp = requests.request("GET",wx_url,headers=headers).text
    respJson = json.loads(resp)
    for repairer in repairers:
        for row in respJson['rows']:
            if repairer == row['toTenantName']:
                wx_repairer = {
                    "foreignRepairerName": row['toUnitName'],
                    "foreignRepairerCode": row['factoryCode'],
                    "toUnitId": row['toUnitId'],
                    "toOrgId": row['toOrgId'],
                }
                wx_repairers.append(wx_repairer)
    return wx_repairers

def get_factory_groups(groups,header):
    resp = requests.request("GET", factory_groups_api, headers=header).text
    factory_groups = []
    for group in groups:
        for row in json.loads(resp)['rows']:
            if row['groupName'] == group:
                obj = {
                    "groupName": row['groupName'],
                    "groupCode": row['groupCode']
                }
                factory_groups.append(obj)
    return factory_groups

def get_ordniary(ord_list,location, header):
    ordinary_list = []
    area_list = []
    for ord in ord_list:
        ordinary_info = {}
        for area in ord['areas']:
            area_info = {}
            province, city = area.split("-")
            province_id = get_provice_by_name(province, "", header)
            city_code = get_provice_by_name(city, f"parentCode={province_id}", header)
            area_info['areaName'] = city
            area_info['areaCode'] = city_code
            area_list.append(area_info)
        ordinary_info['areaList'] = area_list
        ordinary_info['foreignRepairers'] = get_wx_repairers(ord['foreignRepairers'],location, header)
        ordinary_list.append(ordinary_info)
    print(ordinary_list)
    return ordinary_list

def get_exception(ex_list,location, header):
    exception_list = []
    for ex in ex_list:
        exception_info = {'groups': get_factory_groups(ex['groups'], header),
                          'foreignRepairers': get_wx_repairers(ex['foreignRepairers'], location, header)}
        exception_list.append(exception_info)
    return exception_list

def get_specialize(spec_list, location, header):
    specialize_list = []
    area_list = []
    for spec in spec_list:
        spec_info = {
            "foreignRepairers": get_wx_repairers(spec['foreignRepairers'], location, header)
        }
        for area in spec['areas']:
            area_info = {}
            province, city = area.split("-")
            province_id = get_provice_by_name(province, "", header)
            city_code = get_provice_by_name(city, f"parentCode={province_id}", header)
            area_info['areaName'] = city
            area_info['areaCode'] = city_code
            area_list.append(area_info)
        spec_info['areaList'] = area_list
        spec_info['accessories'] = spec['accessories']
        specialize_list.append(spec_info)
    return specialize_list

def get_company(com_list, header):
    company_list = []
    resp = requests.request("GET", company_api, headers=header).text
    respJson = json.loads(resp)
    for com in com_list:
        for row in respJson:
            if row['unitName'] == com:
                obj = {}
                obj['comCodeName'] = row['unitName']
                obj['comCode'] = row['unitCode']
                company_list.append(obj)
    return company_list

def get_country(can_use_list, header):
    can_use_area = []
    resp = requests.request("GET", conutry_api, headers=header).text
    respJson = json.loads(resp)
    for u in can_use_list:
        for row in respJson:
            if row['text'] == u:
                obj = {}
                obj['applicableAreaName'] = row['text']
                obj['applicableAreaCode'] = row['id']
                can_use_area.append(obj)
    return can_use_area

def query_business_groups(group_list,header):
    resp = requests.request("GET",video_group_api,headers=header)
    business_groups = []
    for name in group_list:
        for row in json.loads(resp.text):
            if row['groupName'] == name:
                obj = {
                    "groupName": row['groupName'],
                    "groupCode": row["groupCode"]
                }
                business_groups.append(obj)
    return business_groups

def get_groups(group_list, header):
    resp = query_business_groups(group_list, header=header)
    groups = json.loads(json.dumps(resp).replace("business","groupName",1).replace("business","group",1))
    return groups

def query_user_info(business_group_list, header):
    userList = []
    for business in business_group_list:
        name = business['groupName']
        canUserArea = business['canUseArea']
        resp = get_business_group([name], business_group_api, headers=header)
        resp = requests.request("GET", query_person_api.replace("{}", resp[0]['businessCode']), headers=header).text
        person = json.loads(resp)[0]
        user_info = {"userName": person['userName'], "userAccount": person['userAccount'],
                   "groupCode": person['groupCode'], 'applicableAreas': get_country(canUserArea, header)}
        userList.append(user_info)
    return userList

def login(url,data,content):
    data['username'] = content['username']
    data['password'] = content['password']
    resp = requests.request("POST",url, data=data).text
    return json.loads(resp)

def get_repairers(repairers,url,headers):
    resp = requests.request("GET",url,headers=headers).text
    respJson = json.loads(resp)
    repairer_data = []
    for re in repairers:
        re_data = {}
        for f in respJson['rows']:
            if f['groupName'] == re:
                re_data['groupName'] = f['groupName']
                re_data['groupCode'] = f['groupCode']
                repairer_data.append(re_data)
    return repairer_data

def get_business_group(group_list,url,headers):
    resp = requests.request("GET", url, headers=headers).text
    respJson = json.loads(resp)
    business_group_list = []
    for business in group_list:
        group_data = {}
        for f in respJson['rows']:
            if f['groupName'] == business:
                group_data['business'] = f['groupName']
                group_data['businessCode'] = f['groupCode']
                business_group_list.append(group_data)
    return business_group_list

# 目前只支持单条件
def get_upg(rule_setting,header):
    priority_groups = get_business_group([x['name'] for x in rule_setting['priority_group']],business_group_api,header)
    bottom_groups = get_business_group([x['name'] for x in rule_setting['bottom_group']],business_group_api,header)
    priority_groups = json.loads(json.dumps(priority_groups).replace("businessCode","groupCode",-1).replace("business","groupName",-1))
    bottom_groups = json.loads(json.dumps(bottom_groups).replace("businessCode","groupCode",-1).replace("business","groupName",-1))
    print(rule_setting)
    upg = {
        "details": [{
            "dCaseType": rule_setting['rule_case_type'],
            "dCj":rule_setting['rule_cj'],
            "dLoss": rule_setting['rule_loss'],
            "delte": "删除",
            "groups":priority_groups
        }],
        "radtio": {
            "level": rule_setting['rule_level'],
            "mark": rule_setting['rule_mark'],
            "symbol": rule_setting['rule_sysmbol'],
            "minMoney": rule_setting['rule_min_money'],
            "maxMoney": rule_setting['rule_max_money'],
            "pocketBottomGroups": bottom_groups
        }
    }
    return upg

def get_gdp(rule_setting,header):
    priority_groups = get_business_group([x['name'] for x in rule_setting['priority_group']], business_group_api,
                                         header)
    bottom_groups = get_business_group([x['name'] for x in rule_setting['bottom_group']], business_group_api, header)
    priority_groups = json.loads(
        json.dumps(priority_groups).replace("business", "groupName", 1).replace("business", "group", 1))
    bottom_groups = json.loads(
        json.dumps(bottom_groups).replace("business", "groupName", 1).replace("business", "group", 1))
    gdp = {
        "detailsg": [{
            "dCaseType": rule_setting['rule_case_type'],
            "dCj": rule_setting['rule_cj'],
            "dLoss": rule_setting['rule_loss'],
            "delte": "删除",
            "groups": priority_groups
        }],
        "radtiog": {
            "levelg": rule_setting['rule_level'],
            "mark": rule_setting['rule_mark'],
            "symbol": rule_setting['rule_sysmbol'],
            "minMoneyg": rule_setting['rule_min_money'],
            "maxMoneyg": rule_setting['rule_max_money'],
            "pocketBottomGroups": bottom_groups
        }
    }
    return gdp

def get_rule_setting(content,header):
    rule_setting_map = {
        "upg": [],
        "gdp": []
    }
    for rule in content['rules']:
        if rule['is_super_rule']:
            rule_setting = get_gdp(rule,header)
            rule_setting_map['gdp'].append(rule_setting)
        else:
            rule_setting = get_upg(rule,header)
            rule_setting_map['upg'].append(rule_setting)
    return rule_setting_map

def get_rule_config(content,headers):
    rule_config_list = []
    rules = content['rules']
    rule_set = set()
    for r in rules:
        for pg in r['priority_group']:
            if pg['name'] in rule_set:
                continue
            rule_form = {}
            repairer = get_business_group([pg['name']],business_group_api,headers=headers)
            business_code = repairer[0]['businessCode']
            if pg['rule']['schedule_method'] == "2":
                rule_form['saturation'] = pg['rule']['saturation']
                rule_form['smartDispatch'] = pg['rule']['smartDispatch']
            rule_form['business'] = pg['name']
            rule_form['businessCode'] = business_code
            rule_form['schedulingMethod'] = pg['rule']['schedule_method']
            rule_form['allocationRule'] = pg['rule']['allocation_rule']
            rule_config_list.append(rule_form)
            rule_set.add(pg['name'])
        for bg in r['bottom_group']:
            if bg['name'] in rule_set:
                continue
            rule_form = {}
            repairer = get_business_group([bg['name']],business_group_api,headers=headers)
            business_code = repairer[0]['businessCode']
            if bg['rule']['schedule_method'] == "2":
                rule_form['saturation'] = bg['rule']['saturation']
                rule_form['smartDispatch'] = bg['rule']['smartDispatch']
            rule_form['business'] = bg['name']
            rule_form['businessCode'] = business_code
            rule_form['schedulingMethod'] = bg['rule']['schedule_method']
            rule_form['allocationRule'] = bg['rule']['allocation_rule']
            rule_config_list.append(rule_form)
            rule_set.add(bg['name'])
    return rule_config_list

def schedule_auto_builder(loginform,content,body):
    token = login(gs_login_api,loginform,content)['access_token']
    body['programName'] = "{{schedule_solution}}"
    body['ruleType'] = "{{schedule_rule_type}}"
    body['locationAttribution'] = "{{location}}"
    schedule_type = content['schedule_rule_type']
    if schedule_type == "13":
        body['programName'] = "{{schedule_solution}}"
        body['ruleType'] = "{{schedule_rule_type}}"
        body['locationAttribution'] = "{{location}}"
        body['repairers'] = get_repairers(content['repairers'], repairer_api, {"Authorization": f"bearer {token}"})
        body['ruleConfig'] = get_rule_config(content, headers={"Authorization": f"bearer {token}"})
        body['upg'] = get_rule_setting(content, header={"Authorization": f"bearer {token}"})['upg']
        body['gdp'] = get_rule_setting(content,header={"Authorization": f"bearer {token}"})['gdp']

    elif schedule_type == "29" and content['videoRules'] != "":
        body['group'] = get_groups(content["videoRules"]['business_groups'],header={"Authorization": f"bearer {token}"})
        body['comList'] = get_company(content['videoRules']['company'],header={"Authorization": f"bearer {token}"})
        body['userList'] = query_user_info(content['videoRules']['businessGroups'],header={"Authorization": f"bearer {token}"})

    elif schedule_type == "32" and content['outRepairerRules'] != "":
        body['ordinaryList'] = get_ordniary(content['outRepairerRules']['ordinary'],content['location'],header={"Authorization": f"bearer {token}"})
        body['specializeList'] = get_specialize(content['outRepairerRules']['specialize'], content['location'],header={"Authorization": f"bearer {token}"})
        body['exceptionList'] = get_exception(content['outRepairerRules']['exception'],content['location'],header={"Authorization": f"bearer {token}"})
        body['exceptFlag'] = "1"
        body['conditionCode'] = content['outRepairerRules']['wx_repairer_range_control']
        body['switchSelection'] = content['outRepairerRules']['switchSelection']
        body['switchOn'] = content['outRepairerRules']['switch_related']
    return body

def get_builded_body(api_path,loginform,content,body):
    if "token" in api_path:
        return body
    if "v2/gsoc/rest/rule/GisControlRunSystemService/addupdateProgram" in api_path:
        return body