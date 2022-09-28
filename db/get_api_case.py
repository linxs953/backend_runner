import pymysql
from loguru import logger
# 通过module name获取一组用例
"""
- 所属系统：国寿
- 用例所属模块：估损
- 用例场景名称：发起调度方案
- 用例名称：api1/api2/api3/api/4
- 用例编号: 1/2/3/4
- 接口域名: https://apirestpre.com
- 接口地址: sso/oauth/token
- 请求方法: post
- 上游数据（输入数据）:  [{from: 111, to: 222}]
- 提取字段（输出数据）: [{access_token: "token"}]
- 预期结果: [{code: 200, test.0.token_type: "bearer"}]
- 重试次数: 5
- 用例超时时间: 5
"""

def map_data(data):
    api_form_keys = [
        "case_no",
        "system_name",
        "module_name",
        "scene_name",
        "step_name",
        "api_domain_type",
        "api_path",
        "method",
        "data_dependency",
        "extract",
        "expect"
    ]
    for index, d in enumerate(data):
        data_obj = {
            "base_info": {},
            "api_case_info": {}
        }
        for idx, key in enumerate(api_form_keys):
            if key in ["case_no", "system_name","module_name","scene_name","step_name"]:
                data_obj['base_info'][key] = d[idx] if d[idx] is not None else []
            else:
                data_obj['api_case_info'][key] = d[idx] if d[idx] is not None else []
        data[index] = data_obj
    return data

def getAPITestCase(business_name,module_name,scene_name):
    # 设置连接地址，用户账号密码，连接的数据库，连接端口，编码方式，创建连接
    conn = pymysql.connect(host='192.168.1.1',
                        user='autotest',
                        password='autotest',
                        db='jira',
                        port=3306,
                        charset='utf8'
    )

    caseDataSql = ("SELECT * "
                    "FROM jira.AO_69E499_TEST_API_FORM "
                    "where system_name = '" + business_name +"'" + " and module_name = '" +
                     module_name + "'" + " and scene_name = '" + scene_name + "'"
                )

    cur = conn.cursor()
    cur.execute(caseDataSql)
    data = cur.fetchall()
    datalist = list(data)
    logger.debug(f"getAPICase:  {datalist}")
    cur.close()
    conn.close()
    return map_data(datalist)

def get_all_system():
    conn = pymysql.connect(host='192.168.1.1',
                        user='autotest',
                        password='autotest',
                        db='jira',
                        port=3306,
                        charset='utf8'
    )
    caseDataSql = """
        select system_name from jira.AO_69E499_TEST_API_FORM group by system_name
    """
    cur = conn.cursor()
    cur.execute(caseDataSql)
    data = cur.fetchall()
    datalist = list(data)
    cur.close()
    conn.close()
    return datalist

def get_all_module(system_name):
    conn = pymysql.connect(host='192.168.11.197',
                        user='autotest',
                        password='cxh123456',
                        db='jira',
                        port=3306,
                        charset='utf8'
    )
    caseDataSql = f"""
        select module_name from jira.AO_69E499_TEST_API_FORM where system_name="{system_name}" group by module_name 
    """
    cur = conn.cursor()
    cur.execute(caseDataSql)
    data = cur.fetchall()
    datalist = list(data)
    cur.close()
    conn.close()
    return datalist

def get_all_scene(system_name, module_name):
    conn = pymysql.connect(host='192.168.11.1',
                        user='autotest',
                        password='autotest',
                        db='jira',
                        port=3306,
                        charset='utf8'
    )
    caseDataSql = f"""
        select scene_name from jira.AO_69E499_TEST_API_FORM where system_name="{system_name}" and module_name="{module_name}" group by scene_name 
    """
    cur = conn.cursor()
    cur.execute(caseDataSql)
    data = cur.fetchall()
    datalist = list(data)
    cur.close()
    conn.close()
    return datalist
