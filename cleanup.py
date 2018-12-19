import re
import utilities

# need to do this as a class so it can retain loaded settings from file
class CleanerAgent:
	
	def __init__(self):
		self.updateRules()
	
	def updateRules(self):
		raw = utilities.parseAllTSV("rules","string","string","string")
		self.rules_belongtogether = [b for [a,b,c] in raw if a=="belongtogether"]
		self.rules_notanartist = [b for [a,b,c] in raw if a=="notanartist"]
		self.rules_replacetitle = {b:c for [a,b,c] in raw if a=="replacetitle"}
		self.rules_replaceartist = {b:c for [a,b,c] in raw if a=="replaceartist"}
			
	
	
	def fullclean(self,artist,title):
		artists = self.parseArtists(self.removespecial(artist))
		title = self.parseTitle(self.removespecial(title))
		(title,moreartists) = self.parseTitleForArtists(title)
		artists += moreartists
		
		return (list(set(artists)),title)

	def removespecial(self,s):
		return s.replace("\t","").replace("␟","").replace("\n","")


	delimiters_feat = ["ft.","ft","feat.","feat","featuring","Ft.","Ft","Feat.","Feat","Featuring"]			#Delimiters used for extra artists, even when in the title field
	delimiters = ["vs.","vs","&"]											#Delimiters in informal artist strings, spaces expected around them
	delimiters_formal = ["; ",";","/"]										#Delimiters used specifically to tag multiple artists when only one tag field is available, no spaces used


	def parseArtists(self,a):

		if a.strip() == "":
			return []
			
		if a.strip() in self.rules_notanartist:
			return []
			
		if " performing " in a.lower():
			return self.parseArtists(re.split(" [Pp]erforming",a)[0])
			
		if a.strip() in self.rules_belongtogether:
			return [a.strip()]
		if a.strip() in self.rules_replaceartist:
			return self.rules_replaceartist[a.strip()].split("␟")
			
		
		
		for d in self.delimiters_feat:
			if re.match(r"(.*) \(" + d + " (.*)\)",a) is not None:
				return self.parseArtists(re.sub(r"(.*) \(" + d + " (.*)\)",r"\1",a)) + self.parseArtists(re.sub(r"(.*) \(" + d + " (.*)\)",r"\2",a))
		
		for d in self.delimiters_formal:
			if (d in a):
				ls = []
				for i in a.split(d):
					ls += self.parseArtists(i)
				return ls
		
		for d in (self.delimiters_feat + self.delimiters):
			if ((" " + d + " ") in a):
				ls = []
				for i in a.split(" " + d + " "):
					ls += self.parseArtists(i)
				return ls
				
		
			
		
			
		return [a.strip()]

	def parseTitle(self,t):
		if t.strip() in self.rules_replacetitle:
			return self.rules_replacetitle[t.strip()]
	
		t = t.replace("[","(").replace("]",")")
		
		t = re.sub(r" \(as made famous by .*?\)","",t)
		t = re.sub(r" \(originally by .*?\)","",t)
		t = re.sub(r" \(.*?Remaster.*?\)","",t)
		
		return t.strip()

	def parseTitleForArtists(self,t):
		for d in self.delimiters_feat:
			if re.match(r"(.*) \(" + d + " (.*?)\)",t) is not None:
				(title,artists) = self.parseTitleForArtists(re.sub(r"(.*) \(" + d + " (.*?)\)",r"\1",t))
				artists += self.parseArtists(re.sub(r"(.*) \(" + d + " (.*?)\).*",r"\2",t))
				return (title,artists)
			if re.match(r"(.*) - " + d + " (.*)",t) is not None:
				(title,artists) = self.parseTitleForArtists(re.sub(r"(.*) - " + d + " (.*)",r"\1",t))
				artists += self.parseArtists(re.sub(r"(.*) - " + d + " (.*).*",r"\2",t))
				return (title,artists)
			if re.match(r"(.*) " + d + " (.*)",t) is not None:
				(title,artists) = self.parseTitleForArtists(re.sub(r"(.*) " + d + " (.*)",r"\1",t))
				artists += self.parseArtists(re.sub(r"(.*) " + d + " (.*).*",r"\2",t))
				return (title,artists)
		
		return (t,[])
		
		

#this is for all the runtime changes (counting Trouble Maker as HyunA for charts etc)		
class CollectorAgent:
	
	def __init__(self):
		self.updateRules()
	
	def updateRules(self):
		raw = utilities.parseAllTSV("rules","string","string","string")
		self.rules_countas = {b:c for [a,b,c] in raw if a=="countas"}
		self.rules_include = {} #Twice the memory, double the performance! (Yes, we're saving redundant information here, but it's not unelegant if it's within a closed object!)
		for a in self.rules_countas:
			self.rules_include[self.rules_countas[a]] = self.rules_include.setdefault(self.rules_countas[a],[]) + [a]
	
	# this agent needs to be aware of the current id assignment in the main program. unelegant, but the best way i can think of	
	def updateIDs(self,artistlist):
		self.rules_countas_id = {artistlist.index(a):artistlist.index(self.rules_countas[a]) for a in self.rules_countas}
		#self.rules_include_id = {artistlist.index(a):artistlist.index(self.rules_include[a]) for a in self.rules_include}
		#this needs to take lists into account
		
	def getCredited(self,artist):
		if artist in self.rules_countas_id:
			return self.rules_countas_id[artist]
		if artist in self.rules_countas:
			return self.rules_countas[artist]
		else:
			return artist
	
		
	def getCreditedList(self,artists):
		updatedArtists = []
		for artist in artists:
			updatedArtists.append(self.getCredited(artist))
		return list(set(updatedArtists))
		
	def getAllAssociated(self,artist):
		return self.rules_include.get(artist,[])
		
		
		
		
		
		
		
def flatten(lis):

	newlist = []
		
	for l in lis:
		if isinstance(l, str):
			newlist.append(l)
		else:
			newlist = newlist + l
				
	return list(set(newlist))
