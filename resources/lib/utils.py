import re

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