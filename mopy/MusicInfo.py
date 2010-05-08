"""
MusicInfo.py

Holds a collection of Music Ontology objects

Created by Chris Sutton on 2007-08-13.
Copyright (c) 2007 Chris Sutton. All rights reserved.
"""

from logging import log, error, warning, info, debug
from mopy import model
import random

class MusicInfoException(Exception):
	def __init__(self, message) :
		self.message = message
	def __str__(self) :
		return self.message

class MusicInfo(object):
	def __init__(self, objects=None, namespaceBindings = model.namespaceBindings):
		if objects==None:
			objects = []
		self.MainIdx = {}
		for obj in objects:
			self.add(obj)
		self.namespaceBindings = namespaceBindings

	def add(self, obj, URI=None):
		if URI == None:
			# See if we have an existing blind node object :
			if hasattr(obj, "URI") == False or obj.URI == None or isBlind(obj):
				#raise MusicInfoException("Tried to add object "+str(obj)+" with no URI !")
				found = self.findExistingBlindObj(obj)
				if found == None:
					if not isBlind(obj):
						debug(" Assigning a blind URI for "+str(obj).replace("\n","|"))
						obj.URI = getBlindURI()
				else:
					debug("Already know blind obj "+str(obj).replace("\n","|"))
					obj.URI = found.URI # Update other references to this blind node
					return
					
			URI = obj.URI

		if not self.haveURI(URI):
			# Add object :
			self.MainIdx[URI] = obj
			if not hasattr(obj, "shortname"):
				raise MusicInfoException("No shortname property for object " + str(obj) + ", did it come from the MO model ?")
			if not hasattr(self, obj.shortname+"Idx"):
				setattr(self, obj.shortname+"Idx", {})
			getattr(self, obj.shortname+"Idx")[URI] = obj
		else:
			existing = self.MainIdx[URI]
			if isinstance(obj, type(existing)):
				keep = obj # The (possibly) more specific subclass
				add = existing
			elif isinstance(existing, type(obj)):
				keep = existing
				add = obj
			else:
				raise MusicInfoException("Tried to add two objects for the same URI and classes are a mismatch !"\
										 +"\n Existing : "+str(existing)+"\nAdding : "+str(obj))
			debug("Merging Existing : "+str(existing)+"\nAdding : "+str(obj))
			for propName in keep._props.keys():
				 if add._props.has_key(propName):
					for v in add._props[propName]:
						#debug("Adding "+str(v).replace("\n","|")+" to "+str(keep).replace("\n","|")+" as "+propName)
						keep._props[propName].add(v)

			# Update references
			self.MainIdx[URI] = keep
			if not hasattr(self, keep.shortname+"Idx"):
				setattr(self, keep.shortname+"Idx", {})
			getattr(self, keep.shortname+"Idx")[URI] = keep
			
			if keep != existing:
				del getattr(self, existing.shortname+"Idx")[URI]
				for obj in self.MainIdx.values():
					for propSet in obj._props.values():
						outdatedRefs = [v for v in propSet if v==existing]
						for v in outdatedRefs:
							debug("Updating reference in "+str(obj).replace("\n","|"))
							propSet.remove(v)
							propSet.add(keep)
	
	def haveURI(self, uri):
		return self.MainIdx.has_key(uri)
		
	def findExistingBlindObj(self, o):
		if not hasattr(o, "shortname"):
			raise MusicInfoException("No shortname property for object " + str(o) + ", did it come from the MO model ?")
		if not hasattr(self, o.shortname+"Idx"):
			return None
			
		idx = getattr(self, o.shortname+"Idx")
		for obj in idx.values():
			if obj.URI.startswith("blind:"):
				# test properties
				match = True
				try:
					for propName in obj._props.keys():
						if obj._props[propName] != o._props[propName]:
							#print("Disregarding "+str(obj).replace("\n","|")+" due to property "+propName+" differing.\n")
							match = False
				except:
					match = False
					
				if match == True:
					info("Found object "+str(obj).replace("\n","|")+" to match "+str(o).replace("\n","|"))
					return obj
					
		return None
		
def isBlind(obj):
	return hasattr(obj,"URI") and obj.URI != None and obj.URI.startswith("blind:")

def getBlindURI(s=None):
	if s==None:
		s=str(hex(random.getrandbits(64))[2:-1])
	return "blind:"+s
