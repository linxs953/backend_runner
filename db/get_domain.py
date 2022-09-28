import pymysql


def getDomainByType(domain_type):
    conn = pymysql.connect(host='192.168.11.1',
                        user='autotest',
                        password='autotest',
                        db='jira',
                        port=3306,
                        charset='utf8'
    )

    caseDataSql = ("SELECT value "
                    "FROM jira.AO_69E499_TESTSTEP_DOMAIN where `key`='" + domain_type + "'"
                )
    cur = conn.cursor()
    cur.execute(caseDataSql)
    data = cur.fetchall()
    datalist = list(data)
    cur.close()
    conn.close()
    return datalist