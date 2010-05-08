"""
PropertySet.py

Created by Chris Sutton on 2007-08-11.
Copyright (c) 2007 Chris Sutton. All rights reserved.
"""
from logging import error, warning, info, debug

class PropertySet(set):

	def __init__(self, shortname, propertyURI, validTypes, allowLits):
		set.__init__(self)
		self.shortname = shortname
		self.propertyURI = propertyURI
		self.validTypes = validTypes
		self.allowLits = allowLits
		self.Lits = (str, unicode, int, float) # Any more ? 
	#
	# Set functions :
	#	
	def add(self, o):
		# type check :
		#print "type checking against : "+str(self.validTypes)
		#if self.allowLits:
		#	print "(lits allowed)"
		if not ((self.allowLits and isinstance(o, self.Lits))\
				or (self.validTypes != None and isinstance(o, self.validTypes))\
				or self.validTypes == None):
			msg = "Invalid type for "+self.shortname+" property ! Got "+str(type(o))+" but expected one of : "+str(self.validTypes)
			if self.allowLits:
				msg+= " (or a literal)"
			raise TypeError(msg)
		set.add(self,o)
	
	def get(self):
		#print "in custom get()"
		return self

	def set(self, v):
		self.clear()
		self.add(v)

def protector(self, item, value):
	if (not self.__dict__.has_key("_initialised"))\
		   or self._initialised == False \
	       or hasattr(self,item):
		object.__setattr__(self,item,value)
	else:
		raise AttributeError("Not allowed add new attributes to classes ! Typo ?")
