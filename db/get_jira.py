# 安装pip install pymysql
# 导入pysql包
import pymysql


def getTestCaseContent(projectCode, issueNumber):
    # 设置连接地址，用户账号密码，连接的数据库，连接端口，编码方式，创建连接
    conn = pymysql.connect(host='192.168.11.1',
                        user='autotest',
                        password='autotest',
                        db='jira',
                        port=3306,
                        charset='utf8'
    )

    # 测试用例查询sql
    caseDataSql = ("SELECT "
                   "ji.SUMMARY ,"
                   "a6t.STEP ,"
                   "a6t.STEP_DATA ,"
                   "a6t.EXPECTED_RESULT ,"
                   "p.pkey ,"
                   "ji.issuenum "
                   "FROM jira.AO_69E499_TESTSTEP a6t "
                   "left join jira.jiraissue ji on ji.ID = a6t.TC_ID "
                   "left join jira.project p on p.ID = ji.PROJECT "
                   "where p.pkey = '" + projectCode + "' "
                                                      "and ji.issuenum = '" + issueNumber + "' "
                                                                                            "ORDER BY a6t.ID asc")

    # 创建游标
    cur = conn.cursor()
    # 使用sql语句进行游标定位
    cur.execute(caseDataSql)
    # 游标定位后的数据抓取（抓取返回的是一系列元组）
    data = cur.fetchall()
    # 转换成list
    # datalist = list(data)

    # 关闭游标
    cur.close()
    # 关闭连接
    conn.close()

    return convert_testcas(data)


def convert_testcas(data):
    testcases = []
    for d in data:
        jira_case = {}
        jira_case['title'] = d[0]
        jira_case['step'] = map_step(d[1])
        jira_case['data'] = d[2]
        jira_case['expect'] = d[3]
        testcases.append(jira_case)
    return testcases

def map_step(step_obj):
    mult_stepes = str(step_obj).split("\n")
    if len(mult_stepes) < 3:
        return {}
    for i,s in enumerate(mult_stepes):
        content = s[2:]
        mult_stepes[i] = content
    if len(mult_stepes) < 4:
        return {
            "step_name": mult_stepes[0],
            "url_path": mult_stepes[1],
            "method": str(mult_stepes[2]).upper(),
        }
    return {
        "step_name": mult_stepes[0],
        "url_path":mult_stepes[1],
        "method":str(mult_stepes[2]).upper(),
        "extract":mult_stepes[3]
    }
# caseDataList = getTestCaseContent("DSTEST540", "7")

# # 步骤
# STEP = ""
# # 测试数据
# STEP_DATA = ""
# # 预期结果
# EXPECTED_RESULT = ""
#
# i = 0
# for caseData in caseDataList:
#     STEP = caseData[0]  # 获取步骤的值
#     STEP_DATA = caseData[1]  # 获取测试数据的值
#     EXPECTED_RESULT = caseData[2]  # 获取预期结果的值
#     print(str(i) + ': ' + STEP + ', ' + STEP_DATA + ', ' + EXPECTED_RESULT)
#     i += 1
# i = 0
