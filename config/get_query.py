
query_map = {
    "v2/rest/org/user": ["userID:{{username}}"],
    "gsimserver/rest/dsspnetty/IMService/getUserSign": ["userID:{{username}}"],
    "v2/gsoc/rest/onlineclaim/OcTasksFlowService/ipageAllTaskApi":["page:1","rows:10000","taskStatus:1"],
    "v2/gsoc/rest/onlineclaim/OcTasksFlowService/TaskManageMentListXp":["page:1","rows:10000","taskStatus:1"],
    "v2/gsoc/rest/rule/GisControlRunSystemService/queryProgram":["page:1","rows:1000","ruleType:{{schedule_rule_type}}","flag:1"],
    "v2/gsoc/rest/rule/DmsGroupService/queryGroup": ["page:1","rows:10000","ruleType:{{schedule_rule_type}}"],
    "v2/gsoc/rest/rule/DmsPersonService/querybusiness": ["page:1","rows:10000"],
    "v2/gsoc/rest/rule/DmsPersonService/queryMapUser": []
}

def get_query(url_path,extend_param=None):
    query = query_map.get(url_path,"")
    if query == "":
        return query
    queryList = []
    for q in query:
        # e.g page:1
        # 解析query params, 生成key:value形式的dict, 转成列表
        # 根据url path后面的带的参数, 更新原有的默认参数
        queryMap = {}
        param_name, param_value = q.split(":")
        queryMap['key'] = param_name
        queryMap['value'] = param_value
        if extend_param:
            # {field: value}
            for k,v in extend_param.items():
                if param_name == k:
                    queryMap['key'] = k
                    queryMap['value'] = str(v)
                    break
        queryList.append(queryMap)
    return queryList