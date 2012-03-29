import xbmc, xbmcaddon
import resources.lib.switchking as SwitchKing

__addon__ = xbmcaddon.Addon(id='plugin.program.switchking')
__setting__ = __addon__.getSetting

class PlayerEvents(xbmc.Player):
	
	def __init__(self):
		self.switchking = SwitchKing.SwitchKing(__setting__("host"), __setting__("port"), __setting__("username"), __setting__("password"))
	
	def activateScenarioByName(self, name):

		selected_scenario = None

		scenarios = self.switchking.getScenarios()

		for scenario in scenarios:
			if scenario["name"] == name:
				selected_scenario = scenario

		if not selected_scenario is None:
			self.switchking.setScenario(selected_scenario["id"])

	def onPlayBackStarted(self):
		if __setting__("event_enabled") == "true":
			self.activateScenarioByName(__setting__("event_video_play"))

	def onPlayBackStopped(self):
		if __setting__("event_enabled") == "true":
			self.activateScenarioByName(__setting__("event_video_stop"))

	def onPlayBackEnded(self):
		if __setting__("event_enabled") == "true":
			self.activateScenarioByName(__setting__("event_video_stop"))

	def onPlayBackPaused(self):
		if __setting__("event_enabled") == "true":
			self.activateScenarioByName(__setting__("event_video_stop"))

	def onPlayBackResumed(self):
		if __setting__("event_enabled") == "true":
			self.activateScenarioByName(__setting__("event_video_play"))

player=PlayerEvents()

while (not xbmc.abortRequested):
	xbmc.sleep(10)