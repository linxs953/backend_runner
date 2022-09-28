import pymysql


#  通过表单类型获取数据
"""
    :type=gs, 国寿测试数据表单
    :type=dssp, 协作平台测试数据表单
"""
def getTestCaseDataContent(form_type):
    # 设置连接地址，用户账号密码，连接的数据库，连接端口，编码方式，创建连接
    conn = pymysql.connect(host='192.168.11.1',
                        user='autotest',
                        password='autotest',
                        db='jira',
                        port=3306,
                        charset='utf8'
    )

    #测试用例查询sql
    caseDataSql = ("SELECT * "
                    "FROM jira.AO_69E499_TESTSTEP_DATA "
                    "where data_type = '"+ form_type +"'")


    # 创建游标
    cur = conn.cursor()
    # 使用sql语句进行游标定位
    cur.execute(caseDataSql)
    # 游标定位后的数据抓取（抓取返回的是一系列元组）
    data = cur.fetchall()
    #转换成list
    datalist = list(data)

    # 关闭游标
    cur.close()
    # 关闭连接
    conn.close()

    return datalist