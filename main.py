import sys
from generate.flow import GenerateCollections
from generate.flowV2 import GenerateFlowV2
from db.get_api_case import *

def run(args):
    for system in get_all_system():
        for module in get_all_module(system[0]):
            for scene in get_all_scene(system[0],module[0]):

                obj = GenerateFlowV2(system[0], module[0], scene[0])
                obj.generate()
    # if len(args) <= 1:
    #     raise Exception("args list is required ")
    # if len(args) > 1:
    #     args = args[1:]
    #
    # domain_type = args[0]
    #
    # # 获取jiraid
    # jira_id = args[1]
    # # 获取issue no
    # issue_no = args[2]
    #
    # # 获取文件存储路径
    # json_file_path = args[3]
    #
    # # 获取生成文件名
    # filename = args[4]
    #
    # # 创建Collection类，调用generate方法生成json
    # obj = GenerateCollections(domain_type,jira_id,issue_no,json_file_path,filename)
    # obj.generate()


if __name__ == '__main__':
    run(sys.argv)