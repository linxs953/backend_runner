var path = require("path")
var newman = require('newman')
runtime=require('postman-runtime')
var runner =  new runtime.Runner()
var fs = require('fs'),
    Collection = require('postman-collection').Collection,
    myCollection;

function readFileList(dir, filesList=[]) {
    const files = fs.readdirSync(dir)
    files.forEach((item, index) => {
        var fullPath = path.join(dir,item)
        const stat = fs.statSync(fullPath)
        if (stat.isDirectory()) {
            readFileList(fullPath, filesList)
        } else {
              filesList.push(__dirname + "\\" +  fullPath)
        }
    })
    return filesList
}

function write_to_log(filepath, content) {
    pathPart = filepath.split("\\")
    pathPart.pop(0)
    dir = pathPart.join("\\")
    fs.mkdirSync(dir,{recursive: true})
    date = new Date().toString()
    fs.appendFile(filepath, date.slice(0, date.length-20) + content,(error) => {
        if(error) {
            console.log(error)
        }
    })
}


// todo: 场景表单需要增加关联数据文件, 实现从库中去捞场景数据
// 获取collections下所有json文件，调用runner去执行
all_collection_files = readFileList("./collections")
for (file in all_collection_files) {
    const logFilePath =  all_collection_files[file].replace("collections", "log").replace(".json",".log")
    var myCollection = new Collection(JSON.parse(fs.readFileSync(all_collection_files[file])))
    // todo: 后面直接读库
    data_file = JSON.parse(fs.readFileSync("data2.json"))
    newman.run({
        collection: all_collection_files[file],
        reporters: ["htmlextra"],
        reporter: {
            "htmlextra": {
                "export": all_collection_files[file].replace("collections","reports").replace(".json",new Date().getTime() + ".html")
            }
        },
        iterationData: data_file,
        iterationCount: 1,
    }).on("start", function (err, args) {
        console.log("*****************************************************************************************")
        console.log("get collections: " + all_collection_files[file] + "  Successfully")
        console.log("reading data file: " + path.join(__dirname,"data2.json") + "  Successfully")
        console.log("start running collection: " + all_collection_files[file])
        if(err) {
            console.error("[ERROR] start collection error")
            write_to_log(logFilePath, "start collection error, details\n" + JSON.stringify(err))
        }
    }).on("iteration", function (err, args) {
    }).on("item", function(err,args) {
        if (err) {
            iteration = parseInt(args.cursor.iteration) + 1
            write_to_log(logFilePath, "[node: finished item] execute item failed, details: \n" + JSON.stringify(err) + "\n")
        }
    }).on("beforeItem",function (err, args){
        iteration = parseInt(args.cursor.iteration) + 1
        console.log("start execute item: " + args.item.name + " in iteration: " + iteration)
    }).on("assertion", function(err,args) {
        if(err){
            const currentIteration = parseInt(args.cursor.iteration) + 1
            var data_content = data_file[currentIteration-1]
            if(parseInt(args.cursor.iteration) > data_file.length-1) {
                data_content = data_file[data_file.length-1]
            }
            write_to_log(logFilePath,"[node: item assert] occur error in " + args.item.name + " in data iteration " +
                        currentIteration + " \ndata content: " + JSON.stringify(data_content) + "\n\n")
        }
    }).on("done", function (err, summary) {
        if(err || summary.run.error || summary.run.failures.length > 0) {
            const msg = err ||  summary.run.error || summary.run.failures
            console.log("[ERROR] [node: collection finished] running collection <" + all_collection_files[file] + ">" + " occur error")
            write_to_log(logFilePath,"[ERROR] [node：collection finished]  running collection <" + all_collection_files[file] + ">" + " occur error, details: \n" + JSON.stringify(msg) +
                    "\n\n")
        }
        console.log("collection: " + all_collection_files[file] + " execute completed")
        console.log("*****************************************************************************************")
    })
//    runner.run(myCollection,{
//            data: data_file,
//            iterationCount: data_file.length,
//            stopOnError: true,
//            stopOnFailure: true,
//            timeout: {
//                request: 30000,
//                script: 5000
//            }
//        },function(err,run) {
//            run.start({
//                request: function(err,cusor,response,request,item,cookies,history) {
//                    // 组装url
//                    write_to_log(logFilePath, "步骤: " + item.name + "\n")
//                    protocol = request.url.protocol + "://"
//                    domain = request.url.host.join(".")
//                    path = request.url.path.join("/")
//                    req_url = protocol  +  domain + "/" + path
//                    req_method = request.method
//                    req_query = decodeURI(request.url.query)
//                    req_body = request.body.raw?request.body.raw:JSON.stringify({})
//                    write_to_log(logFilePath,"--> api: " + req_url + "\n")
//                    write_to_log(logFilePath,"--> query: " + req_query  + "\n")
//                    write_to_log(logFilePath,"--> body: " + req_body + "\n")
//                },
//                response: function(err,cusor,response,request,item,cookies,history) {
//                    //  console.log("\n--------------------------response-------------------------------------------------------")
//                    write_to_log(logFilePath,"--> statusCode: " + response['code'] + "\n")
//                    write_to_log(logFilePath,"--> response size: " + response.responseSize + "\n")
//                    write_to_log(logFilePath,"--> response time: " + response.responseTime + "ms\n")
//                    if(response.code != 200) {
//                        write_to_log(logFilePath,"--> got error response: " + JSON.stringify(response.stream.toString()) + "\n")
//                    }
//                    //  console.log("--------------------------response-------------------------------------------------------\n")
//                },
//                prerequest: function(err, cusor, events, item) {},
//                assertion: function (cusor, assertion) {
//                    for(assert_idx in assertion) {
//                        if(assertion[assert_idx].passed === false) {
//                            e = assertion[assert_idx].error
//                            // 删除堆栈信息
//                            delete e.stack
//                            err = JSON.stringify(e)
//                            write_to_log(logFilePath,"--> assert error: " + JSON.stringify(err) + "\n")
//                        } else {
//                            write_to_log(logFilePath,"--> assert successfully. data: " + JSON.stringify(assertion) + "\n")
//                        }
//                    }
//
//                },
//                done: function(err) {
//                      console.log("collection: " + all_collection_files[file] + "  execute finished")
//                }
//        })
//    })

}