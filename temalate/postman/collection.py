from copy import deepcopy
collection = {
	"info": {
		"name": "{collection_name}",
		"schema": "{schema}"
	},
	"item": [

	]
}

event = {
	"listen": "$event_type",
	"script": {}
}

script = {
	"type":"text/javascript",
	"exec": []
}

sub_folder = {
	"name": "{sub_folder_name}",
	"item": []
}

sub_folder_item = {
	"name": "{item_name}",
	"request": {},
	"response": [],
	"events": []
}


request = {
	"method": "{api method}",
	"header": [],
	"url": {},
	"body": {}
}

request_url = {
	"raw": "{url}",
	"host": [],
	"path": [],
	"query": []
}



request_body_raw = {
	"mode":"raw",
	"raw": "{body_string}"
}

request_body_form = {
	"mode": "formdata",
	"formdata": []
}


class CollectionTemplate:
	def __init__(self):
		pass

	def get_collection_template(self):
		self.collection = collection
		return deepcopy(collection)

	def get_sub_folder_template(self):
		self.sub_folder = sub_folder
		return deepcopy(sub_folder)

	def get_sub_folder_item_template(self):
		self.sub_folder_item = sub_folder_item
		return deepcopy(sub_folder_item)

	def get_request_template(self):
		self.request = request
		return deepcopy(request)

	def get_url_template(self):
		self.url_object = request_url
		return deepcopy(request_url)

	def get_body_template(self,data_type="raw"):
		if data_type == "raw":
			self.req_body = request_body_raw
			return deepcopy(request_body_raw)
		self.req_body = request_body_form
		return deepcopy(request_body_form)

	"""
		获取单个event对象模板
	"""
	def get_event(self,scripts,event_type="test"):
		e = deepcopy(event)
		e['listen'] = e['listen'].replace("$event_type",event_type)
		e['script'] = scripts
		return e

	def get_scrpt(self,exec_list):
		s = deepcopy(script)
		s['exec'] = exec_list
		return s