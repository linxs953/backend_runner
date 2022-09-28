import copy

login = {
    "username":"{{username}}",
    "password":"{{password}}",
    "client_id":"cxh",
    "grant_type":"password",
    "client_secret":"password"
}

schedule_rule_config = {
    "saturation": "0",
    "businessCode": "$first_code",
    "smartDispatch": "0",
    "business": "$first_name",
    "schedulingMethod": "$first_method",
    "allocationRule": "4"
}

schedule_group_config = {
    "details": [
        {
            "dLoss": [],
            "related": [],
            "dCaseType": [],
            "groups": [],
            "dCj": [],
            "delte": "删除"
        }
    ],
    "radtio": {
        "symbol": "$symbol",
        "pocketBottomGroups": [],
        "level": "$level",
        "minMoney": "$min",
        "mark": "$mark",
        "maxMoney": "$max"
    }
}

schedule_group_super_config = {
    "detailsg": [
        {
            "dLoss": "$dloss",
            "related": [],
            "dCaseType":"$case_type",
            "groups": [],
            "dCj": "$rule_cj",
            "delte": "删除"
        }
    ],
    "radtiog": {
            "symbol": "$symbol",
            "pocketBottomGroups": [],
            "levelg": "$level",
            "minMoneyg": "$min",
            "mark": "$mark",
            "maxMoneyg": "$max"
    }

}

repairer = {
    "groupName": "$group_name",
    "groupCode": "$group_code"
}

# 自动调度方案创建
create_schedule = {
    "groupType": "2",
    "rgdispatchStatus": "2",
    "wjdispatchStatus": "1",
    "cond": [],
    "unitId": "{{unitId}}",
    "comCode": "{{comCode}}",
    "commuteSign": "",
    "groupCode": [],
    "autonomyGroup": [],
    "group": [],
    "residual": [],
    "configuration": [],
    "conditionCode": "0",
    "switchOn": "0",
    "switchSelection": "1",
    "ordinaryList": [],
    "specializeList": [],
    "exceptionList": [],
    "exceptFlag": "0",
    "brandGrade": "2",
    "topMark": "0",
    "message": "",
    "ruleConfig": [],
    "upg": [copy.deepcopy(schedule_group_config)],
    "gdp": [copy.deepcopy(schedule_group_super_config)],
    # "upg": [],
    # "gdp": [],
    "repairers": [],
    "programName": "$program_name",
    "ruleType": "$schedule_type",
    "locationAttribution": "$belongto",
  }

