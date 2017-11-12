import httplib2
from xml.etree.ElementTree import XML as xml

__author__ = 'abondoe'


class Touchline(object):
	_ip_address = ""

	def __init__(self, id=0):
		self._id = id
		self._header = {"Content-Type": "text/xml"}
		self._read_path = "/cgi-bin/ILRReadValues.cgi"
		self._write_path = "/cgi-bin/writeVal.cgi"
		self._parameter = {}
		self._xml_element_list = []
		self._xml_element_list.append(
			Parameter(name="name", desc="Name", type=Parameter.G))
		self._xml_element_list.append(
			Parameter(name="upass", desc="Password", type=Parameter.CD))
		self._xml_element_list.append(
			Parameter(name="SollTempMaxVal", desc="Setpoint max",
					  type=Parameter.G))
		self._xml_element_list.append(
			Parameter(name="SollTempMinVal", desc="Setpoint min",
					  type=Parameter.G))
		self._xml_element_list.append(
			Parameter(name="WeekProg", desc="Week program", type=Parameter.G))
		self._xml_element_list.append(
			Parameter(name="OPMode", desc="Operation mode", type=Parameter.G))
		self._xml_element_list.append(
			Parameter(name="SollTemp", desc="Setpoint", type=Parameter.G))
		self._xml_element_list.append(
			Parameter(name="RaumTemp", desc="Temperature", type=Parameter.G))
		self._xml_element_list.append(
			Parameter(name="kurzID", desc="Device ID", type=Parameter.G))
		self._xml_element_list.append(
			Parameter(name="ownerKurzID", desc="Controller ID",
					  type=Parameter.G))

	def get_number_of_devices(self, ip_address):
		Touchline._ip_address = ip_address
		number_of_devices_items = []
		number_of_devices_items.append("<i><n>totalNumberOfDevices</n></i>")
		request = self.get_touchline_request(number_of_devices_items)
		response = self.request_and_receive_xml(request)
		return self.parse_number_of_devices(response)

	def get_status(self):
		status_items = []
		status_items.append("<i><n>R0.SystemStatus</n></i>")
		request = self.get_touchline_request(status_items)
		response = self.request_and_receive_xml(request)
		return self.parse_number_of_devices(response)

	def update(self):
		device_items = self.get_touchline_device_item(self._id)
		request = self.get_touchline_request(device_items)
		response = self.request_and_receive_xml(request)
		return self.parse_device(response)

	def parse_device(self, response):
		self.devices = []
		item_list = response.find('item_list')
		for item in item_list.iterfind("i"):
			list_iterator = 0
			device_list = list(item)
			for parameter in self._xml_element_list:
				if device_list[list_iterator].tag != "n":
					list_iterator -= 1
					self._parameter[parameter.get_desc()] = "NA"
				else:
					self._parameter[parameter.get_desc()] = str(
						device_list[list_iterator + 1].text)
				list_iterator += 2

	def get_touchline_request(self, items):
		request = "<body>"
		request += "<version>1.0</version>"
		request += "<client>IMaster6_02_00</client>"
		request += "<client_ver>6.02.0006</client_ver>"
		request += "<file_name>room</file_name>"
		request += "<item_list_size>0</item_list_size>"
		request += "<item_list>"
		for item in items:
			request += item
		request += "</item_list>"
		request += "</body>"
		return request

	def request_and_receive_xml(self, req_key):
		try:
			h = httplib2.Http(".cache")
			(resp, content) = h.request(
				uri=Touchline._ip_address + self._read_path,
				method="POST",
				body=req_key,
				headers=self._header
			)
		except httplib2.ServerNotFoundError:
			print("Touchline not found")

		if resp.reason != "OK":
			exit("Network error")
		else:
			return xml(content)

	def parse_number_of_devices(self, response):
		item_list = response.find('item_list')
		item = item_list.find('i')
		return item.find('v').text

	def get_touchline_device_item(self, id):
		items = []
		parameters = ""
		for parameter in self._xml_element_list:
			if parameter.get_type() == Parameter.G:
				parameters += "<n>G%d.%s</n>" % (id, parameter.get_name())
			else:
				parameters += "<n>CD.%s</n>" % (parameter.get_name())
		items.append("<i>" + parameters + "</i>")
		return items

	def get_name(self):
		if "Name" in self._parameter:
			return self._parameter["Name"]
		else:
			return None

	def get_current_temperature(self):
		if "Temperature" in self._parameter:
			return self._parameter["Temperature"]
		else:
			return None

	def get_target_temperature(self):
		if "Setpoint" in self._parameter:
			return self._parameter["Setpoint"]
		else:
			return None


class Parameter(object):
	CD = 0
	G = 1
	R = 2

	def __init__(self, name, desc, type):
		self._name = name
		self._desc = desc
		self._type = type

	def get_name(self):
		return self._name

	def get_desc(self):
		return self._desc

	def get_type(self):
		return self._type