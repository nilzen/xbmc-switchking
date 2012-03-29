import utils as Utils
import base64
from xml.dom.minidom import parseString
import httplib

class SwitchKing:

	def __init__(self, host, port, user, password):
		self.utils = Utils.Utils()
		self.user = user
		self.password = password
		self.host = host
		self.port = port
		self.headers = {}
		self.headers["Authorization"] = "Basic {0}".format(base64.b64encode("{0}:{1}".format(user, password)))
		self.headers["Connection"] = "Keep-Alive"

	def getServerResponse(self, url):
		conn = httplib.HTTPConnection(self.host + ":" + self.port)
		conn.request("GET", "/" + url, None, self.headers)
		resp = conn.getresponse()
		return resp.read()

	def getDevices(self):
		
		dom = parseString(self.getServerResponse("devices"))
		devices = dom.getElementsByTagName("RESTDevice")

		result = []

		for device in devices:
			result.append({
				"name": self.utils.unescape(device.getElementsByTagName("Name")[0].childNodes[0].data).encode('utf-8'),
				"id": int(device.getElementsByTagName("ID")[0].childNodes[0].data),
				"dim": (device.getElementsByTagName("SupportsAbsoluteDimLvl")[0].childNodes[0].data == "true"),
				"state": int(device.getElementsByTagName("CurrentStateID")[0].childNodes[0].data)
			})

		return result

	def getDeviceGroups(self):

		dom = parseString(self.getServerResponse("devicegroups"))
		devicegroups = dom.getElementsByTagName("RESTDeviceGroup")

		result = []

		for devicegroup in devicegroups:

			if(devicegroup.getElementsByTagName("ID")[0].childNodes[0].data == "-1"):
				continue

			result.append({
				"name": self.utils.unescape(devicegroup.getElementsByTagName("Name")[0].childNodes[0].data).encode('utf-8'),
				"id": int(devicegroup.getElementsByTagName("ID")[0].childNodes[0].data)
			})

		return result


	def getScenarios(self):

		dom = parseString(self.getServerResponse("scenarios"))
		scenarios = dom.getElementsByTagName("RESTScenario")

		result = []

		for scenario in scenarios:
			result.append({
				"name": self.utils.unescape(scenario.getElementsByTagName("Name")[0].childNodes[0].data).encode('utf-8'),
				"id": int(scenario.getElementsByTagName("ID")[0].childNodes[0].data)
			})

		return result
			
	def getDataSources(self):

		dom = parseString(getServerResponse("datasources"))
		datasources = dom.getElementsByTagName("RESTDataSource")

		for datasource in datasources:
			result.append({
				"name": self.utils.unescape(datasource.getElementsByTagName("Name")[0].childNodes[0].data).encode('utf-8'),
				"id": int(datasource.getElementsByTagName("ID")[0].childNodes[0].data)
			})

		return result

	def sendDeviceCommand(self, id, command):
		conn = httplib.HTTPConnection(self.host + ":" + self.port)
		conn.request("GET", "/devices/" + str(id) + "/" + command, None, self.headers)

	def sendDeviceGroupCommand(self, id, command):
		conn = httplib.HTTPConnection(self.host + ":" + self.port)
		conn.request("GET", "/devicegroups/" + str(id) + "/" + command, None, self.headers)

	def setScenario(self, id):
		conn = httplib.HTTPConnection(self.host + ":" + self.port)
		conn.request("GET", "/commandqueue?operation=changescenario&target=" + str(id) + "&param1=&param2=&param3=", None, self.headers)

	def setDataSourceValue(self, id, value):
		conn = httplib.HTTPConnection(self.host + ":" + self.port)
		conn.request("GET", "/datasources/" + str(id) + "/addvalue?value=" + value, None, self.headers)