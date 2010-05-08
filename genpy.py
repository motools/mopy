#!/usr/bin/env python
# encoding: utf-8
"""
genpy.py

Generate model.py, which defines a Python class for each class in the Music Ontology.

Created by Chris Sutton on 2007-08-10.
Copyright (c) 2007 Chris Sutton. All rights reserved.
"""

import sys
import time
import os
from os import mkdir
import rdflib; from rdflib import RDF, RDFS, BNode, URIRef, Literal
from rdflib.Collection import Collection

OWL = rdflib.Namespace("http://www.w3.org/2002/07/owl#")
DC = rdflib.Namespace("http://purl.org/dc/elements/1.1/")

class Generator:
	def __init__(self, graph, target_class, excludeClasses = None):
		self.graph = graph
		self.c = target_class
		[self.ns, self.name] = self.graph.qname(self.c).split(":")
		self.pyname = ClassQNameToPyClassName(self.graph.qname(self.c))
		self.filename = "model.py"
		self.out = []
		self.write = self.out.append
		self.hdr = ""
		self.classDef=""
		self.init ="\tdef __init__(self,URI=None):\n"
		self.props = ""
		self.utils = ""
		self.excludeClasses = excludeClasses or []

		# Do we have any non-inherited properties ?
		self.properties = self.getProperties()
		self.haveProperties = len(self.properties) > 0

	def printAll(self):
		self.addHeader()
		self.addClassDef()
		self.addInit()
		self.addProperties()
		self.addUtils()
		self.write(self.classDef)
		self.write(self.hdr)
		self.write(self.init)
		self.write(self.props)
		self.write(self.utils)
		self.out = "".join(self.out)


	def addHeader(self):
		self.hdr = '\t"""\n'
		self.hdr+="\t"+self.ns+":"+self.name+"\n"
		for comment in self.graph.objects(self.c, RDFS.comment):
			self.hdr+="\t"+comment+"\n"
		self.hdr+= '\t"""\n'

	def addClassDef(self):
		cd=""
		parentURIs = self.getParents()
		parentqnames = [self.graph.qname(p) for p in parentURIs]
		parentpynames = [ClassQNameToPyClassName(q) for q in parentqnames]
		parentpynames.sort() # For consistency across runs
		self.classDef+="\nclass "+self.pyname+"("
		if len(parentpynames)==0:
			cd+="object"
		else:
			cd+=", ".join(parentpynames)
		cd+="):\n"
		self.classDef += cd
		

	def addInit(self):
		parentURIs = self.getParents()
		parentqnames = [self.graph.qname(p) for p in parentURIs]
		parentpynames = [ClassQNameToPyClassName(q) for q in parentqnames]
		if len(parentpynames)>0:
			self.init+="\t\t# Initialise parents\n"
		for p in parentpynames:
			self.init+="\t\t"+p+".__init__(self)\n"
		
		self.init+="\t\tself._initialised = False\n"
		self.init+="\t\tself.shortname = \""+self.name+"\"\n"
		self.init+="\t\tself.URI = URI\n"
		if self.haveProperties:
			self.init+="\t\tself._props = getattr(self,\"_props\",{}) # Initialise if a parent class hasn't already\n"

			
	def addProperties(self):
		self.props+="\tclassURI = \""+str(self.c)+"\"\n"
		if self.haveProperties:
			self.props+="\n\n\t# Python class properties to wrap the PropertySet objects\n"
		for prop in self.properties:
				propname = PropQNameToPyName(self.graph.qname(prop))
				URIstr = str(prop)
				validTypes = ""
				rTypes = list(self.graph.objects(prop, RDFS.range))
				
				# Add the range types of any parent properties
				for parent in self.graph.objects(prop,RDFS.subPropertyOf):
					#print "Added range types from parent property "+str(parent)+" to subproperty "+str(prop)
					rTypes.extend(self.graph.objects(parent, RDFS.range))
				
				# Add the domain types of any inverse properties
				for invProp in self.graph.objects(prop, OWL.inverseOf):
					print "Adding domain types of "+str(invProp)+" inverse of "+str(prop)
					rTypes.extend(self.graph.objects(invProp, RDFS.domain))
				
				rTypeNames = []
				allowLits=False
				for rT in rTypes:
					if isinstance(rT, BNode):
						try:
							un = (self.graph.objects(rT,OWL["unionOf"])).next()
							col = Collection(self.graph, un)
							for c in col:
								rTypeNames.append(self.TypeToPyTypeName(c))
						except StopIteration:
							print "Unhandled Blind Node in addProperties ! No unionOf found. Triples :"
							print "\n".join(list(self.graph.triples(rT,None,None)))
							raise Exception("Unhandled Blind Node in addProperties !")
					else:
						rTypeNames.append(self.TypeToPyTypeName(rT))
				
				rTypeNames = list(set(rTypeNames)) # remove dupes
				if "rdfs___Literal" in rTypeNames:
					allowLits=True
					rTypeNames.remove("rdfs___Literal")
				if len(rTypeNames) > 1:
					validTypes="("+",".join(rTypeNames)+")"
				elif len(rTypeNames) == 1:
					validTypes=rTypeNames[0]
				else:
					validTypes="None"

				self.init+="\t\tself._props[\""+propname+"\"] = PropertySet(\""+propname+"\",\""+URIstr+"\", "+validTypes
				self.init+=", "+str(allowLits)+")\n"
				# Wrap the PropertySet up to be usable and protected :
				self.props+="\t" + propname + " = property(fget=lambda x: x._props[\"" + propname + "\"].get()"\
														", fset=lambda x,y : x._props[\"" + propname + "\"].set(y)"\
														", fdel=None, doc=propDocs[\""+propname+"\"])\n"
		self.init+="\t\tself._initialised = True\n"
		
	def addUtils(self):
		self.utils+="\n\t# Utility methods\n" # TODO : serialisation routine here ?
		self.utils+="\t__setattr__ = protector\n"
		self.utils+="\t__str__ = objToStr\n"
	
	def getProperties(self):
		props=[]
		graph_props = list(self.graph.subjects(RDF.type, RDF.Property))
		for subType in self.graph.subjects(RDFS.subClassOf, RDF.Property):
			graph_props.extend(list(self.graph.subjects(RDF.type, subType)))
			
		for prop in graph_props:
			# Simple case : Named explicitly in property's domain
			if len(list(self.graph.triples((prop,RDFS.domain,self.c)))) > 0:
				props.append(prop)
			# Harder case : Named in a property's range and we know of an inverseProperty
			if len(list(self.graph.triples((prop,RDFS.range,self.c)))) > 0:
				inverses = list(self.graph.objects(prop,OWL.inverseOf)) + list(self.graph.subjects(OWL.inverseOf,prop))
				props.extend(inverses)
			 
			# Harder case : Named in a collection in property's domain
			for bn in (o for (s,p,o) in self.graph.triples((prop,RDFS.domain,None)) if isinstance(o, BNode)):
				try:
					un = (self.graph.objects(bn,OWL["unionOf"])).next()
					domain = Collection(self.graph, un)
					if self.c in domain:
						props.append(prop)
				except StopIteration:
					print "Unhandled Blind Node in getProperties ! No unionOf found. Triples :"
					print "\n".join(list(self.graph.triples(bn,None,None)))
					raise Exception("Unhandled Blind Node in getProperties")
		
		# Then need to add the known subproperties for properties we've found
		for prop in props:
			for child in self.graph.subjects(RDFS.subPropertyOf, prop):
				#print "Adding child property "+str(child)+" because we have the parent property "+str(prop)
				props.append(child)
		
		# Handle owl:sameAs links
		for x in set(list(self.graph.objects(self.c, OWL.sameAs)) + list(self.graph.subjects(OWL.sameAs, self.c))):
			if x not in self.excludeClasses:
				#print "Adding properties from "+str(x)+" sameAs "+str(self.c)
				#print " exclude classes : "+str(self.excludeClasses)
				g = Generator(self.graph, x, excludeClasses = self.excludeClasses + [self.c])
				props.extend(g.getProperties())
		
		removeDeprecated(self.graph, props)
		props = list(set(props)) # Remove duplicates
		props.sort() # Aid consistency of generated code
		#print str(self.c)+" has properties : "+str(props)
		return props

	def getParents(self):
		p = []
		for parent in self.graph.objects(self.c, RDFS.subClassOf):
			if not isinstance(parent, BNode):
				p.append(parent)
			else:
				try:
					un = (self.graph.objects(parent,OWL["unionOf"])).next()
					parents = Collection(self.graph, un)
					print "WARNING : Ignoring union of parents !" # FIXME
					#p.extend(parents) # FIXME : If the union'd nodes are themselves complicated, we will fail
				except StopIteration:
					parentTypeList = list(self.graph.objects(parent, RDF.type))
					if len(parentTypeList) > 0 and parentTypeList[0] == OWL.Restriction:
						print "WARNING : Ignoring owl:Restriction on parents of "+str(self.c)
					else:
						print "Unhandled Blind Node in getParents ! No unionOf found. Triples :"
						print "\n".join(list(str(trip) for trip in self.graph.triples((parent,None,None))))
						raise Exception("Unhandled Blind Node in getParents")
				
		# Handle owl:sameAs links
		for x in set(list(self.graph.objects(self.c, OWL.sameAs)) + list(self.graph.subjects(OWL.sameAs, self.c))):
			if x not in self.excludeClasses:
				#print "Adding parents from "+str(x)+" sameAs "+str(self.c)
				g = Generator(self.graph, x, excludeClasses=self.excludeClasses + [self.c])
				their_parents = g.getParents()
				if their_parents != [RDFS.Resource]:
					p.extend(their_parents)

		# Handle orphan classes
		if (self.c != OWL.Thing) and (len(p) == 0):
			if self.c == RDFS.Resource:
				p.append(OWL.Thing)
			else:
				p.append(RDFS.Resource)
				
		removeDeprecated(self.graph, p)
		p = list(set(p)) # Remove duplicates
		p.sort()
		return p

	def addImportForClass(self):
		nsInit = open(os.path.join("mopy",self.ns,"__init__.py"), 'a')
#		nsInit.write("from mopy.model import "+self.name+"\n")
		nsInit.write("from mopy.model import "+ClassQNameToPyClassName(self.graph.qname(self.c))+" as "+self.name+"\n")
		nsInit.close()

	def TypeToPyTypeName(self, t):
		# FIXME : One day it might be nice to actually model these and restrict as appropriate O_o
		typeMapping = {"http://www.w3.org/2001/XMLSchema#integer" : "int",\
					   "http://www.w3.org/2001/XMLSchema#int" : "int",\
					   "http://www.w3.org/2001/XMLSchema#decimal" : "float",\
					   "http://www.w3.org/2001/XMLSchema#float" : "float",\
					   "http://www.w3.org/2001/XMLSchema#nonNegativeInteger" : "int",\
					   "http://www.w3.org/2001/XMLSchema#duration": "str",\
					   "http://www.w3.org/2001/XMLSchema#date" : "str",\
					   "http://www.w3.org/2001/XMLSchema#dateTime" : "str",\
				   	   "http://www.w3.org/2001/XMLSchema#gYear" : "int",\
					   "http://www.w3.org/2001/XMLSchema#gYearMonth" : "str",\
					   "http://www.w3.org/2001/XMLSchema#gMonth" : "int",\
					   "http://www.w3.org/2001/XMLSchema#gDay" : "int",
					   "http://www.w3.org/2001/XMLSchema#string" : "str"}
		if not str(t).startswith("http://www.w3.org/2001/XMLSchema#"):
			return (ClassQNameToPyClassName(self.graph.qname(t)))
		elif str(t) in typeMapping.keys(): #FIXME handle others
			return typeMapping[str(t)]
		else:
			raise Exception("Got an unknown xmls type : " + t)
			
def PropQNameToPyName(qname):
#	return qname.replace(":","_") # Probably don't need namespace in property names
	return qname.split(":")[1]
	
def ClassQNameToPyModuleName(qname):
	return qname.replace(":",".")
def ClassQNameToPyClassName(qname):
#	return qname.split(":")[1]
	return qname.replace(":", "___")
def PyClassNameToClassQName(pyname):
	return pyname.replace("___",":")

def setupNamespace(ns, fromScratch=True):
	if not os.path.exists(os.path.join("mopy",ns)):
		mkdir(os.path.join("mopy",ns))
		fromScratch = True # If we've had to create the directory, we better start from scratch
	if fromScratch:
		nsInit = open(os.path.join("mopy",ns,"__init__.py"), 'w')
		nsInit.write("import mopy.model\n\n")
		nsInit.close()
		packageInit = open(os.path.join("mopy","__init__.py"),'a')
		packageInit.write("import "+ns+"\n")
		packageInit.close()

def addImportForInstance(ns, i):
	nsInit = open(os.path.join("mopy",ns,"__init__.py"), 'a')
	nsInit.write("from mopy.model import "+i+" as " + PyClassNameToClassQName(i).split(":")[1] + "\n")
	nsInit.close()
	
def removeDeprecated(g, xs):
	for x in xs:
		status = list(g.objects(x, URIRef("http://www.w3.org/2003/06/sw-vocab-status/ns#term_status")))
		if Literal("deprecated") in status:
			print "DEPRECATED : "+str(x)
			xs.remove(x)
			
def main():
	spec_g = rdflib.ConjunctiveGraph()
	print "Loading ontology documents..."
	# add mew ontologies here...
	spec_g.load("owl.rdfs")
	spec_g.load("time.owl")
	spec_g.load("classicalmusicnav.owl")
	spec_g.load("musicontology.rdfs")
	spec_g.load("extras.rdfs")
	spec_g.load("foaf.rdfs")
	spec_g.load("chordontology.rdfs")
	spec_g.load("timeline.rdf")
	spec_g.load("event.rdf")
	spec_g.load("myspace.owl")

	# FIXME : Why do these get lost in loading ?
	spec_g.namespace_manager.bind("owl",rdflib.URIRef('http://www.w3.org/2002/07/owl#'))
	spec_g.namespace_manager.bind("classicalmusicnav", rdflib.URIRef("http://grasstunes.net/ontology/classicalmusicnav.owl#"))
	spec_g.namespace_manager.bind("timeline",rdflib.URIRef('http://purl.org/NET/c4dm/timeline.owl#'))
	spec_g.namespace_manager.bind("time", rdflib.URIRef("http://www.w3.org/2006/time#"))
	spec_g.namespace_manager.bind("myspace", rdflib.URIRef("http://grasstunes.net/ontology/myspace.owl#"))

	classes = list(set(s for s in spec_g.subjects(RDF.type, OWL.Class) if type(s) != BNode)) # rdflib says rdfs:Class is a subClass of owl:Class - check !
	removeDeprecated(spec_g, classes)
	classes.sort() # Ensure serialisation order is reasonably consistent across runs
	classtxt = {}
	parents = {}
	
	packageInit = open(os.path.join("mopy","__init__.py"),'w')
	packageInit.write("import model\n")
	packageInit.write("from MusicInfo import MusicInfo\n")
	packageInit.write("from RDFInterface import importRDFGraph, importRDFFile, exportRDFGraph, exportRDFFile\n\n")
	packageInit.close()
	
	for ns in set([spec_g.qname(c).split(":")[0] for c in classes]):
		setupNamespace(ns)
					
	model = open(os.path.join("mopy","model.py"), "w")
	model.write("""
# ===================================================================
# = model.py - Core and External Classes of the Music Ontology 
# =            Generated automatically on """+time.asctime()+"""
# ===================================================================\n\n\n""")
	model.write("import sys\n")
	model.write("from mopy.PropertySet import PropertySet, protector\n\n")
	
	objToStr = """
def objToStr(c):
	s = "-- "+c.shortname
	if c.URI != None :
		s+=" @ "+unicode(c.URI)
	s+=" --\\n"
	for p in c._props.keys():
		for v in c._props[p]:
			s+=c._props[p].shortname + " : "
			if isinstance(v, c._props[p].Lits):
				s+=unicode(v)
			else:
				s+=str(type(v))
				if hasattr(v,"URI") and v.URI != None:
					s+=" @ "+v.URI
			s +="\\n"
	return s.encode(sys.getdefaultencoding(), 'replace')
"""
	model.write(objToStr)
	model.write("\n# ======================== Property Docstrings ====================== \n\n")
	model.write("propDocs = {}\n")
	graph_props = list(spec_g.subjects(RDF.type, RDF.Property))
	for subType in spec_g.subjects(RDFS.subClassOf, RDF.Property):
		graph_props.extend(list(spec_g.subjects(RDF.type, subType)))
	removeDeprecated(spec_g, graph_props)
	graph_props.sort()
	print "properties : " + str(graph_props)
	for p in graph_props:
		doc = "\n".join(spec_g.objects(p, RDFS.comment))
		if len(doc) > 0:
			if doc[-1] == '"':
				doc = doc+"." # or python gets confused.
			model.write("propDocs[\""+PropQNameToPyName(spec_g.qname(p))+"\"]=\\\n\"\"\""+doc.strip()+"\"\"\"\n")
		else:
			model.write("propDocs[\""+PropQNameToPyName(spec_g.qname(p))+"\"]=\"\"\n")
		
	model.write("\n\n\n\n# ========================  Class Definitions  ====================== \n")

	for c in classes:
		print "processing " + str(c)
		g = Generator(spec_g, c)
		g.printAll()
		classtxt[str(c)] = g.out
		parents[str(c)] = [str(p) for p in g.getParents()]
		g.addImportForClass() # Add the class to the right namespace

	#
	# Serialise classes in an appropriate order
	#
	remclasses = [str(c) for c in classes]
	n=1; lastlen = len(remclasses)+1
	while (len(remclasses) > 0) and len(remclasses) < lastlen:
		lastlen = len(remclasses)
		print("pass "+ str(n))
		for c in remclasses:
			if len(parents[c]) == 0: # Write out orphans immediately
				model.write(classtxt[c])
				print(" wrote "+c)
				remclasses.remove(c)
				for k in remclasses:    # And abandon any classes who were waiting for us
					if c in parents[k]:
						parents[k].remove(c)
		n+=1

	if len(remclasses) > 0:
		raise Exception("Couldn't find a serialisation order ! Remaining classes : " + "\n".join(remclasses))
		

	#
	# Ontology-defined Instances
	#
	# FIXME : Properties aren't handled !
	model.write("\n\n# ======================= Instance Definitions ======================= \n")
	for c in classes:
		if c == RDFS.Class:
			continue
		instances = [s for s in spec_g.subjects(RDF.type, c) if type(s) != BNode]
		removeDeprecated(spec_g, instances)
		instances.sort()
		for ns in set([spec_g.qname(i).split(":")[0] for i in instances]):
			setupNamespace(ns, False)
		if len(instances)>0:
			classname= ClassQNameToPyClassName(spec_g.qname(c))
			model.write("\n")
			for i in instances:
				print "Instance of "+classname+" : "+str(i)
				instancename = ClassQNameToPyClassName(spec_g.qname(i))
				model.write(instancename+" = "+ classname+"(\""+str(i)+"\")\n")
				descrip="\n".join([d.strip() for d in spec_g.objects(i, DC.description)])
				if len(descrip)>0:
					if descrip[-1] == '"':
						descrip = descrip+"." # or python gets confused.
					model.write(instancename+".description = \\\n\"\"\""+descrip+"\"\"\"\n")
				addImportForInstance(spec_g.qname(i).split(":")[0], instancename)
	
	NamespaceBindings = ",".join(["\"" + NSName + "\":\"" + str(NSURI) + "\"" for NSName, NSURI in spec_g.namespaces()])
	model.write("\nnamespaceBindings = {" + NamespaceBindings + "}\n\n")
	model.write("\n\n# =======================       Clean Up       ======================= \n")
	model.write("del objToStr, propDocs\n")
	
	model.close()

if __name__ == '__main__':
	main()

