import xbmc, xbmcplugin, xbmcaddon, xbmcgui

import re, htmlentitydefs
import httplib, urllib
import base64
from xml.dom.minidom import parse, parseString

__settings__ = xbmcaddon.Addon(id='plugin.program.switchking')
__language__ = __settings__.getLocalizedString

MODE_DEVICE_LIST = "devicelist"
MODE_SCENARIO_SELECT = "scenarioselect"
MODE_DEVICE_GROUP_LIST = "devicegrouplist"
MODE_DEVICE_TOGGLE_SELECT = "devicetoggleselect"
MODE_DEVICE_DIM_SELECT = "devicedimselect"

class SwitchKing:

	def __init__(self, host, port, user, password):
		self.utils = Utils()
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

class Utils:

	def unescape(self, text):
	    def fixup(m):
	        text = m.group(0)
	        if text[:2] == "&#":
	            # character reference
	            try:
	                if text[:3] == "&#x":
	                    return unichr(int(text[3:-1], 16))
	                else:
	                    return unichr(int(text[2:-1]))
	            except ValueError:
	                pass
	        else:
	            # named entity
	            try:
	                text = unichr(htmlentitydefs.name2codepoint[text[1:-1]])
	            except KeyError:
	                pass
	        return text # leave as is
	    return re.sub("&#?\w+;", fixup, text)


	def paramStringToDictionary(self, str):

		params = {}

		if str:
			pairs = str[1:].split("&")

			for pair in pairs:
				split = pair.split('=')

				if (len(split)) == 2:
					params[split[0]] = split[1]
		
		return params

class XbmcSwitchking():

	def __init__(self):
		self.switchking = SwitchKing(__settings__.getSetting("host"), __settings__.getSetting("port"), __settings__.getSetting("username"), __settings__.getSetting("password"))
		self.utils = Utils()

	def addDirectoryItem(self, name, params={}, isFolder=True, infoLabels=None):

		cm = []
		li = xbmcgui.ListItem(name)
		
		if isFolder == True:
			url = sys.argv[0] + '?' + urllib.urlencode(params)
		else:
			url = params["url"]

			if not infoLabels:
				infoLabels = { "Title": name }
			
			li.setInfo(type="executable", infoLabels=infoLabels)

		li.addContextMenuItems( cm, replaceItems=False )
			
		return xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=li, isFolder=isFolder)

	def getDeviceList(self):
		for device in self.switchking.getDevices():
			if device["dim"]:
				mode = MODE_DEVICE_DIM_SELECT
			else:
				mode = MODE_DEVICE_TOGGLE_SELECT

			self.addDirectoryItem(device["name"], { "mode": mode, "id": device["id"], "name": device["name"] })

	def scenarioSelect(self):

		scenarios = self.switchking.getScenarios()
		names = []

		for scenario in scenarios:
			names.append(scenario["name"])

		select = xbmcgui.Dialog().select(__language__(30030), names)

		self.switchking.setScenario(scenarios[select]["id"])

		xbmcsk.getActionList()

	def deviceToggle(self, id, name):
		select = xbmcgui.Dialog().select(name, [__language__(30010), __language__(30011), __language__(30012)])

		if select == 0:
			self.switchking.sendDeviceCommand(id, "turnon")

		if select == 1:
			self.switchking.sendDeviceCommand(id, "turnoff")

		if select == 2:
			self.switchking.sendDeviceCommand(id, "cancelsemiauto")

		xbmcsk.getDeviceList()

	def deviceDim(self, id, name):
		select = xbmcgui.Dialog().select(name, [__language__(30010), __language__(30011), __language__(30050), __language__(30051), __language__(30052), __language__(30053), __language__(30054), __language__(30055), __language__(30056), __language__(30057), __language__(30058), __language__(30012)])

		if select == 0:
			self.switchking.sendDeviceCommand(id, "turnon")

		if select == 1:
			self.switchking.sendDeviceCommand(id, "turnoff")

		if select == 2:
			self.switchking.sendDeviceCommand(id, "dim/10")

		if select == 3:
			self.switchking.sendDeviceCommand(id, "dim/20")

		if select == 4:
			self.switchking.sendDeviceCommand(id, "dim/30")

		if select == 5:
			self.switchking.sendDeviceCommand(id, "dim/40")

		if select == 6:
			self.switchking.sendDeviceCommand(id, "dim/50")

		if select == 7:
			self.switchking.sendDeviceCommand(id, "dim/60")

		if select == 8:
			self.switchking.sendDeviceCommand(id, "dim/70")

		if select == 9:
			self.switchking.sendDeviceCommand(id, "dim/80")

		if select == 10:
			self.switchking.sendDeviceCommand(id, "dim/90")

		if select == 11:
			self.switchking.sendDeviceCommand(id, "cancelsemiauto")
	
		xbmcsk.getDeviceList()

	def getActionList(self):
		self.addDirectoryItem(__language__(30000), { "mode": MODE_DEVICE_LIST })
		self.addDirectoryItem(__language__(30002), { "mode": MODE_SCENARIO_SELECT })
		#self.addDirectoryItem(__language__(30001), { "mode": MODE_DEVICE_GROUP_LIST })

utils = Utils()	
params = utils.paramStringToDictionary(sys.argv[2])
xbmcsk = XbmcSwitchking()

mode = params.get("mode", None)
name = params.get("name", "")
id = int(params.get("id", "0"))

if len(sys.argv) < 2 or not sys.argv[2] or not mode:
	xbmcsk.getActionList()
elif mode == MODE_DEVICE_LIST:
	xbmcsk.getDeviceList()
elif mode == MODE_DEVICE_TOGGLE_SELECT and id > 0:
	xbmcsk.deviceToggle(id, name)
elif mode == MODE_DEVICE_DIM_SELECT and id > 0:
	xbmcsk.deviceDim(id, name)
elif MODE_SCENARIO_SELECT:
	xbmcsk.scenarioSelect()
else:
	print "unknown mode: " + mode
	xbmcsk.getActionList()

xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True, cacheToDisc=True)