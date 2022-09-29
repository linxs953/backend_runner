use database api_test
create table `api_case_form` (
    `case_no` bigint(20) NOT NULL COMMENT '用例编号',
    `step_no` bigint(20) NOT NULL COMMENT '当前场景的步骤编号',
    `system_name` varchar(100) NOT NULL COMMENT '系统名称',
    `module_name` varchar(100) NOT NULL COMMENT '模块名称',
    `scene_id` varchar(32) NOT NULL COMMENT '场景id,关联数据文件id',
    `scene_name` varchar(100) NOT NULL COMMENT '场景名称',
    `step_name` varchar(100) NOT NULL COMMENT '步骤名称',
    `api_domain_type` varchar(100) NOT NULL COMMENT '接口域名类型',
    `api_path` longtext NOT NULL COMMENT '接口地址',
    `method` varchar(100) NOT NULL COMMENT '请求方法',
    `data_dependency` longtext NOT NULL COMMENT '数据依赖',
    `extract` longtext NOT NULL COMMENT '字段提取',
    `expect` longtext NOT NULL COMMENT '预期结果',
    `skipped` varchar(2) NOT NULL COMMENT '是否跳过',
    PRIMARY KEY (`case_no`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT="接口测试用例维护表"

create table `api_case_data` (
    `scene_id` bigint(20) NOT NULL COMMENT="场景id",
    `data_id`  bigint(20) NOT NULL COMMENT="数据id, 一个场景绑定一个数据文件",
    `data_type` varchar(100) NOT NULL COMMENT="数据文件类型，标识哪条业务线",
    `data_content` longtext NOT NULL COMMENT="数据文件内容",
    PRIMARY KEY (`scene_id`,`data_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT="场景数据维护表"

create table `api_system` (
    `id` varchar(32) NOT NULL COMMENT="业务线id",
    `name` varchar(100) NOT NULL COMMENT="业务线名称",
    PRIMARY KEY(`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT="业务线信息维护表"

create table `api_module` (
    `id` varchar(32) NOT NULL COMMENT="模块id",
    `system_id` varchar(32) NOT NULL COMMENT="业务线id"
    `name` varchar(100) NOT NULL COMMENT="模块名称",
    `system_name` varchar(100) NOT NULL COMMENT="系统名称",
    PRIMARY KEY(`id`,`system_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT="模块信息维护表"

create table `api_case_scene` (
    `id` varchar(32) NOT NULL COMMENT="场景id",
    `system_id` varchar(32) NOT NULL COMMENT="业务线名称",
    `module_id` varchar(32) NOT NULL COMMENT="模块名称",
    `name` varchar(100) NOT NULL COMMENT="场景名称",
    `system_name` varchar(100) NOT NULL COMMENT="系统名称",
    `module_name` varchar(100) NOT NULL COMMENT="模块名称"
    PRIMARY KEY(`id`,`system_id`,`module_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT="接口场景维护表"