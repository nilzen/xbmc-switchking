import xbmc, xbmcaddon, xbmcgui
import resources.lib.switchking as SwitchKing

__addon__ = xbmcaddon.Addon(id='plugin.program.switchking')
__localize__ = __addon__.getLocalizedString
__setting__ = __addon__.getSetting

switchking = SwitchKing.SwitchKing(__setting__("host"), __setting__("port"), __setting__("username"), __setting__("password"))

scenarios = switchking.getScenarios()
names = []

for scenario in scenarios:
	names.append(scenario["name"])

select = xbmcgui.Dialog().select(__localize__(30030), names)
xbmc.log(str(len(sys.argv)))
xbmc.log(sys.argv[1])
if sys.argv[1] == "event_video_play":
	__addon__.setSetting("event_video_play", scenarios[select]["name"])
elif sys.argv[1] == "event_video_stop":
	__addon__.setSetting("event_video_stop", scenarios[select]["name"])