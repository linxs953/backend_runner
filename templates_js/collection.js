

class PostmanCollection {
    constructor() {
        this.collectionName = "111"
        this.collectionSchema = "https{//schema.getpostman.com/json/collection/v2.1.0/collection.json"
        this.cases = []
    }

    generate() {
        return {
            info: this.getCollectionInfo(),
            items: this.getItems()
        }
    }
    
    getCollectionInfo() {
        return {
            name: this.collectionName,
            schema: this.collectionSchema
        }
    }
    
    getItems() {
        let itemList = []
        for (let case_ in this.cases) {
            item = this.getItem(case_.base_info.scene_name)
            itemList.push(item)
        }
        return itemList
    }

    getItem(item_name) {
        item = {
            name: item_name,
            request: this.getItemRequest(),
            response: this.getItemResponse(),
            events: this.getItemEvents(),
            event: this.getItemEvents()
        }
        return item
    }

    getItemRequest(api, method) {
        itemRequestMeta = {
            method: String(method).toUpperCase(),
            header: this.getItemRequestHeaders(),
            url: this.getItemUrlPart(api),
            body: this.getItemRequestBody()
        }
        return itemRequestMeta
    }

    // api: v2/1/2/3?a=2&b=3
    getItemUrlPart(api) {
        var urlMeta = {
            raw: api,
            row: api,
            host: api.split("//")[1].split("/")[0].split(".")
        }
        if (String(api).includes("?")){
            let url_path = api.split("?")[0]
            let m_param = api.split("?")[1]
            let pathList = url_path.split("//")[1].split("/")
            urlMeta["path"] = pathList.slice(1,pathList.length)
            let queryList = []
            for (let row of m_param.split("&")){
                let obj = {}
                let key = row.split("=")[0]
                let value = row.split("=")[1]
                obj['key'] = key
                obj['value'] = value
                queryList.push(obj)
            }
            urlMeta['query'] = queryList
            // for (row in m_param.split("&")){
            //     key, value = row.split("=")
            //     obj[key] = value
            //     urlMeta['query'] = get_query(url_path, obj)
            //     url_path = url_path + "?"
            //     for (q in get_query(url_path, m_param)) {
            //         param, value = q["key"], q["value"]
            //         url_path += "{param}={value}"
            //     }
            // }
        }
        else {
            let pathList = api.split("//")[1].split("/")
            urlMeta["path"] = pathList.slice(1,pathList.length)
            urlMeta['query'] = []
            // if (get_query(url_path) != '') {
            //     urlMeta['query'] = get_query(url_path)
            // } else{
            //     urlMeta['query'] = []
            // }
        }

        return urlMeta
    }
    getItemRequestBody() {}
    getItemRequestHeaders() {
        return []
    }
    
    getItemResponse() {
        return []
    }
    
    getItemEvents() {}
    getItemEvent(evt_type) {}
}


console.log(new PostmanCollection().getItemUrlPart("https://apirestpre.chexinhui.com/v2/rest/org/user?userId={{username}}"))