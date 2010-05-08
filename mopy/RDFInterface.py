"""
RDFInterface.py

Functions to transform an RDF document into Python MO objects, and vice-versa.

Created by Chris Sutton on 2007-08-12.
Copyright (c) 2007 Chris Sutton. All rights reserved.
"""

# Python 2.4.4 (#1, Oct 18 2006, 10:34:39) 
# [GCC 4.0.1 (Apple Computer, Inc. build 5341)] on darwin
# Type "help", "copyright", "credits" or "license" for more information.
# >>> from RDFInterface import *
# >>> mi = importRDFFile("L1 tiny.n3","n3")
# >>> for sma in mi.SoloMusicArtistIdx.values():
# ...     print sma
# ... 
# -- SoloMusicArtist @ http://zitgist.com/music/artist/2f58d07c-4ed6-4f29-8b10-95266e16fe1b --
# wikipedia : <class 'model.Document'> @ http://en.wikipedia.org/wiki/Dave_Mustaine
# name : Dave Mustaine
# member_of : <class 'model.MusicGroup'> @ http://zitgist.com/music/artist/65f4f0c5-ef9e-490c-aee3-909e7ae6b2ab


from mopy import model
from mopy import time
from mopy.MusicInfo import MusicInfo, getBlindURI, isBlind
from mopy.rdfs import Resource
import rdflib; from rdflib import URIRef, Literal, BNode, RDF, RDFS, ConjunctiveGraph
from logging import log, error, warning, info, debug

class ImportException(Exception):
	def __init__(self, message) :
		self.message = message
	def __str__(self) :
		return self.message

class ExportException(Exception):
	def __init__(self, message) :
		self.message = message
	def __str__(self) :
		return self.message

def importRDFFile(filename, format="xml", strict=True):
	g = ConjunctiveGraph()
	g.load(filename, format=format)
	return importRDFGraph(g, strict)

def importRDFGraph(g, strict=True):
	objs = {}
	modelAttrs = [model.__dict__[c] for c in model.__dict__.keys()]
	knownTypes = dict([(c.classURI, c) for c in modelAttrs if hasattr(c, "classURI") and type(c) == type])
	knownInstances = dict([(i.URI, i) for i in modelAttrs if hasattr(i, "URI")])
	
	#
	# Replace blind nodes with local names
	#
	for bn in [s for s,p,o in set(g.triples((None,None,None))) if type(s) == BNode]:
		for p,o in set(g.predicate_objects(bn)):
			g.remove((bn, p, o))
			g.add((URIRef(getBlindURI(bn)), p, o))
	for bn in [o for s,p,o in set(g.triples((None,None,None))) if type(o) == BNode]:
		for s,p in set(g.subject_predicates(bn)):
			g.remove((s,p,bn))
			g.add((s, p, URIRef(getBlindURI(bn))))
	
	#
	# Create Python objects to model triple subjects
	#
	for s in set(g.subjects()):
		s_type = None
		try:
			s_type = g.objects(s, RDF.type).next()
		except StopIteration, e:
			if strict:
				raise ImportException("NO TYPE SPECIFIED for "+ str(s)+" !")
			else:
				error("NO TYPE SPECIFIED for "+ str(s)+" ! Ignoring...")
				continue
		# FIXME : Definately want some type inference here
	
		if str(s_type) not in knownTypes.keys():
			if strict:
				raise ImportException("NO CLASS TO MODEL TYPE : "+str(s_type)+" OF URI "+str(s)+" !")
			else:
				error("NO CLASS TO MODEL TYPE : "+str(s_type)+" OF URI "+str(s)+" ! Ignoring...")
				continue
			# FIXME : Maybe use a Resource ?
		
		objs[str(s)] = knownTypes[str(s_type)](URI=str(s))
	
	#
	# Set object properties to model RDF properties
	#
	for s in objs.keys():
		for (p, o) in g.predicate_objects(URIRef(s)):
			if p == RDF.type:
				continue # This is modelled above.
			s_propnames = objs[s]._props.keys()
			s_propURIs = [objs[s]._props[s_propname].propertyURI for s_propname in s_propnames]
			s_propdict = dict(zip(s_propURIs, s_propnames))
			
			#print "Trying to find "+str(p)+" amongst : "+str(s_propURIs)
			
			if str(p) in s_propURIs:
				# find object
				if type(o) == URIRef:
					if str(o) in objs.keys():
						obj = objs[str(o)]
					elif str(o) in knownInstances.keys():
						obj = knownInstances[str(o)]
					else:
						warning("Unknown URI "+str(o)+" as object of "+str(s)+", using a Resource to model.")
						obj = Resource(str(o))
						objs[str(o)] = obj
				elif type(o) == Literal:
					# FIXME : this needs some more careful thought.
					typeMapping = {"http://www.w3.org/2001/XMLSchema#integer" : int,\
								   "http://www.w3.org/2001/XMLSchema#int" : int,\
								   "http://www.w3.org/2001/XMLSchema#decimal" : float,\
								   "http://www.w3.org/2001/XMLSchema#float" : float,\
								   "http://www.w3.org/2001/XMLSchema#nonNegativeInteger" : int,\
								   "http://www.w3.org/2001/XMLSchema#duration": str,\
								   "http://www.w3.org/2001/XMLSchema#date" : str,\
								   "http://www.w3.org/2001/XMLSchema#dateTime" : str,\
							   	   "http://www.w3.org/2001/XMLSchema#gYear" : int,\
								   "http://www.w3.org/2001/XMLSchema#gYearMonth" : str,\
								   "http://www.w3.org/2001/XMLSchema#gMonth" : int,\
								   "http://www.w3.org/2001/XMLSchema#gDay" : int}
					if (str(o.datatype) in typeMapping.keys()):
						obj = typeMapping[str(o.datatype)](o)
					else:
						obj = str(o)
					
				else:
					if strict:
						raise ImportException("Found object "+str(o)+" of "+str(s)+" whose type isn't URIRef or Literal ! What to do ?")
					else:
						error("Found object "+str(o)+" of "+str(s)+" whose type isn't URIRef or Literal ! What to do ?")
						continue
						
				# set object for property :
				try:
					getattr(objs[s], s_propdict[str(p)]).add(obj)
				except TypeError, e:
					if strict:
						raise ImportException("Exception when adding "+str(o)+" type "+str(type(obj))\
						+" to "+str(s)+" type "+str(type(objs[s]))\
						+" for property "+str(s_propdict[str(p)])+" : \n" + str(e))
					else:
						warning("Exception when adding "+str(o)+" type "+str(type(obj))\
						+" to "+str(s)+" type "+str(type(objs[s]))\
						+" for property "+str(s_propdict[str(p)])+"...\n" + str(e) +"\nIgnoring...\n")
						continue
					
			else:
				if strict:
					raise ImportException("NO PROPERTY TO MODEL "+str(p)+" in class "+str(type(objs[s]))+"\nKnown properties : "+str(s_propURIs))
				else:
					error("NO PROPERTY TO MODEL "+str(p)+" in class "+str(type(objs[s])))
					continue
	
	mi = MusicInfo(objs.values())
	# Add any namespaces mentioned in the file which we didn't already know :
	mi.namespaceBindings.update(dict([(NSName, str(NSURI)) for NSName, NSURI in g.namespaces()]))
	return mi

 
# Python 2.4.4 (#1, Oct 18 2006, 10:34:39) 
# [GCC 4.0.1 (Apple Computer, Inc. build 5341)] on darwin
# Type "help", "copyright", "credits" or "license" for more information.
# >>> from RDFInterface import *
# >>> mi = importRDFFile("L1 tiny.n3","n3")
# >>> mi.SoloMusicArtistIdx.values()[0].name
# PropertySet(['Dave Mustaine'])
# >>> mi.SoloMusicArtistIdx.values()[0].name = "Davy Crockett"
# >>> mi.SoloMusicArtistIdx.values()[0].name
# PropertySet(['Davy Crockett'])
# >>> exportRDFFile(mi, "out_tiny.n3", "n3")
# Constructing graph...
# Added <class 'model.SoloMusicArtist'> @ http://zitgist.com/music/artist/2f58d07c-4ed6-4f29-8b10-95266e16fe1b
# Added <class 'model.Document'> @ http://en.wikipedia.org/wiki/Dave_Mustaine
# Added <class 'model.MusicGroup'> @ http://zitgist.com/music/artist/65f4f0c5-ef9e-490c-aee3-909e7ae6b2ab
# Writing to file...
# >>> mi = importRDFFile("out_tiny.n3","n3")
# >>> mi.SoloMusicArtistIdx.values()[0].name
# PropertySet(['Davy Crockett'])


def exportRDFGraph(mi):
	g = ConjunctiveGraph()
	bnodes = {}
	for NSName, NSuriStr in mi.namespaceBindings.iteritems():
		g.namespace_manager.bind(NSName, URIRef(NSuriStr))

	modelAttrs = [model.__dict__[c] for c in model.__dict__.keys()]
	knownTypes = dict([(c.classURI, c) for c in modelAttrs if hasattr(c, "classURI")])
	knownInstances = dict([(i.URI, i) for i in modelAttrs if hasattr(i, "URI")])

	# Assign blind nodes :
	for s in mi.MainIdx.values():
		if s.URI == None or isBlind(s):
			snode = BNode()
			bnodes[s.URI] = snode
		for propName, propSet in s._props.iteritems():
			for v in propSet:
				if type(v) not in propSet.Lits and isBlind(v):
					if not bnodes.has_key(v.URI):
						vnode = BNode()
						bnodes[v.URI] = vnode
					

	for s in mi.MainIdx.values():
		if not hasattr(s, "classURI") or s.classURI not in knownTypes.keys():
			raise ExportException("Object "+str(s)+" has no classURI, or classURI is not known in the MO model.")
			# FIXME : Maybe use a Resource ?
		
		if s.URI == None or isBlind(s):
			snode = bnodes[s.URI]
		else:
			snode = URIRef(s.URI)

		g.add((snode, RDF.type, URIRef(s.classURI)))

		for propName, propSet in s._props.iteritems():
			for v in propSet:
				if not hasattr(propSet, "propertyURI"):
					raise ExportException("Property "+str(propName)+" on object "+str(s)+" has no propertyURI !")
				
				if type(v) not in propSet.Lits:
					if not hasattr(v, "URI"):
						raise ExportException("Property value "+str(v)+" is not a Literal, but has no URI !")
					if isBlind(v):
						g.add((snode, URIRef(propSet.propertyURI), bnodes[v.URI]))
					else:
						g.add((snode, URIRef(propSet.propertyURI), URIRef(v.URI)))
				else:
					g.add((snode, URIRef(propSet.propertyURI), Literal(v)))
		
		info("Added "+str(type(s))+" @ "+str(snode))
		
	return g

def exportRDFFile(mi, filename, format="xml"):
	info("Constructing graph...")
	g = exportRDFGraph(mi)
	info("Writing to file...")
	out = open(filename,'w')
	out.write(g.serialize(format=format))
	out.close()
