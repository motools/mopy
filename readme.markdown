Mopy Readme
=============

Contents
--------
1. [Introduction](#introduction)
2. [Interactive Session Example (a.k.a. "why use `mopy` ?")](#interactivesessionexamplea.k.a.whyusemopy)
3. [Requirements](#requirements)
4. [Installation](#installation)
5. [Mopy classes](#mopyclasses)
6. [Mopy properties](#mopyproperties)
7. [Examples of mopy in use](#examplesofmopyinuse)
8. [Developers](#developers)


Introduction
------------

`mopy` is the Music Ontology Python library, designed to provide easy to use python bindings for Music Ontology terms for the creation and manipulation of Music Ontology data. `mopy` includes :

* All terms from :
	* the [Music Ontology](http://www.musicontology.com/)
	* the [Friend of a Friend](http://www.foaf-project.org/) (FOAF) ontology
	* the [Timeline](http://moustaki.org/c4dm/timeline.owl) ontology
	* the (new !) [Chord Ontology](http://purl.org/ontology/chord/)
* Easy conversion between RDF data and mopy objects
	* RDF can be read/written in XML or N3 format
* Type checking based on ontology definitions, to aid correct usage of ontology terms

Interactive Session Example (a.k.a. "why use `mopy` ?")
---------------------------

Using rdflib directly, somebody might try to write about their friend who's in a band as follows :

	Python 2.4.4 (#1, Oct 18 2006, 10:34:39) 
	[GCC 4.0.1 (Apple Computer, Inc. build 5341)] on darwin
	>>> import rdflib
	>>> from rdflib import URIRef, Literal, BNode, RDF, RDFS, Namespace
	>>> g = rdflib.ConjunctiveGraph()
	>>> me = URIRef("http://mydomain.org/me")
	>>> FOAF_ns = Namespace("http://xmlns.com/foaf/0.1/")
	>>> g.add((me, RDF.type, FOAF_ns["Person"]))
	>>> g.add((me, FOAF_ns["name"], Literal("Joe Bloggs")))
	>>> artist = URIRef("http://zeitgeist.com/music/artist/FIXME")
	>>> MO_ns = Namespace("http://purl.org/ontology/mo/")
	>>> g.add((artist, RDF.type, MO_ns["music_artist"]))
	>>> g.add((artist, FOAF_ns["nam"], Literal("Superstar artist")))
	>>> g.add((me, FOAF_ns["interest"], artist))
	>>> g.add((me, FOAF_ns["knows"], artist))

This can get quite tedious. Plus, there are mistakes (typo "name" property to "nam", they meant mo:SoloMusicArtist rather than mo:music_artist, and foaf:interest is intended to link to a page about a topic of interest, not the topic itself) and it's not easy to fix mistakes. For example, if the user needs to change the URI of the artist, they'll have to write a loop to update all triples of relevance.

Here's the equivalent session using `mopy` :

	[GCC 4.0.1 (Apple Computer, Inc. build 5341)] on darwin
	Type "help", "copyright", "credits" or "license" for more information.
	>>> import mopy
	>>> me = mopy.foaf.Person("http://mydomain.org/me")
	>>> me.name = "Joe Bloggs"
	>>> artist = mopy.mo.music_artist("http://zeitgeist.com/music/artist/FIXME")
	AttributeError: 'module' object has no attribute 'music_artist'
	>>> dir(mopy.mo)
	['AnalogSignal', 'Arrangement', 'Arranger', 'AudioFile', 'CD', 'Composer', 'Composition', 'Conductor',
	 'CorporateBody', 'DAT', 'DCC', 'DVDA', 'DigitalSignal', 'ED2K', 'Festival', 'Genre', 'Instrument',
	 'Instrumentation', 'Label', 'Libretto', 'Listener', 'Lyrics', 'MD', 'MagneticTape', 'Medium', 'Movement',
	 'MusicArtist', 'MusicGroup', 'MusicalExpression', 'MusicalItem', 'MusicalManifestation', 'MusicalWork',
	 'Orchestration', 'Performance', 'Performer', 'PublishedLibretto', 'PublishedLyrics', 'PublishedScore', 'Record',
	 'Recording', 'ReleaseStatus', 'ReleaseType', 'SACD', 'Score', 'Show', 'Signal', 'SoloMusicArtist', 'Sound',
	 'SoundEngineer', 'Stream', 'Torrent', 'Track', 'Vinyl', '__builtins__', '__doc__', '__file__', '__name__',
	 '__path__', 'album', 'audiobook', 'bootleg', 'compilation', 'ep', 'interview', 'live', 'mopy', 'official',
	 'promotion', 'remix', 'soundtrack', 'spokenword']

	>>> artist = mopy.mo.SoloMusicArtist("http://zeitgeist.com/music/artist/FIXME")
	>>> artist.nam = "Superstar Artist"
	AttributeError: Not allowed add new attributes to classes ! Typo ?
	>>> artist.name = "Superstar Artist"
	>>> me.interest = artist
	TypeError: Invalid type ! Got <class 'mopy.model.mo___MusicArtist'> but expected one of : <class 'mopy.model.foaf___Document'>
	>>> help (mopy.foaf.Person.interest)
	Help on property:
	    A page about a topic of interest to this person.
	>>> me.knows = artist

The user has avoided the mistakes which are so easy to make dealing directly with triples, and they can then update the artist's URI as easily as :

	>>> artist.URI = "http://zitgist.com/music/artist/62b86b55-e0aa-446f-b326-054576968310"

Requirements
----------

- Written and tested on python 2.4 but may work fine on 2.3 or 2.5 - let us know if you try :)
- Python libraries :
  - [rdflib](http://rdflib.org/) v2.4.0 (easy_install)


Installation
----------

To install mopy, either check out the motools project from SVN and run mopy/genpy.py to generate mopy's package files, or download the mopy package directly from [sourceforge](http://sourceforge.net/project/showfiles.php?group_id=202492). For now, just copy the mopy directory into your working directory, or your python's library directory, we'll be releasing an easier-to-install package soon :)

`mopy` Classes
----------

Start by importing the mopy package :

	>>> import mopy

Terms and instances are organised by namespace :

	>>> dir(mopy)
	['MusicInfo', 'PropertySet', 'RDFInterface', '__builtins__', '__doc__', '__file__', '__name__',
	 '__path__', 'chord', 'event', 'exportRDFFile', 'exportRDFGraph', 'foaf', 'frbr', 'geo', 'importRDFFile',
	 'importRDFGraph', 'key', 'mo', 'model', 'owl', 'rdfs', 'time', 'timeline', 'tzont']

	>>> dir(mopy.key)
	['Key', 'Note', '__builtins__', '__doc__', '__file__', '__name__', '__path__', 'mopy']

And you can pull terms from a particular ontology as you'd expect :

	>>> from mopy.mo import MusicArtist, Record, Performance

To check what properties an object can take, use dir :

	>>> dir(mopy.mo.MusicArtist)

Constructors take the URI of the resource, or if omitted, act as blank nodes :

	>>> band1 = mopy.mo.MusicGroup()
	>>> print band1
	-- MusicGroup --

	>>> band2 = mopy.mo.MusicGroup("http://band2.com/us")
	>>> print band2
	-- MusicGroup @ http://band2.com/us --

`mopy` Properties
-----------

Properties are all treated as sets (so have no ordering), but we provide the shortcut of the '=' operator to assign a one element set :

	>>> band1.name = "awesome band"
	>>> band1.name.add("DEATH MONKEYS")
	>>> print band1
	-- MusicGroup --
	name : DEATH MONKEYS
	name : awesome band

	>>> member_names = ["Baz", "Bill", "Bob", "Clifton"]
	>>> for m in member_names:
	...     member = mopy.mo.SoloMusicArtist()
	...     member.name = m
	...     band1.member.add(member)
	... 
	>>> print band1
	-- MusicGroup --
	member : <class 'mopy.model.mo___SoloMusicArtist'>
	member : <class 'mopy.model.mo___SoloMusicArtist'>
	member : <class 'mopy.model.mo___SoloMusicArtist'>
	member : <class 'mopy.model.mo___SoloMusicArtist'>
	name : DEATH MONKEYS
	name : awesome band

	>>> print "\n".join(str(x) for x in band1.member)
	-- SoloMusicArtist --
	name : Baz
	-- SoloMusicArtist --
	name : Bill
	-- SoloMusicArtist --
	name : Bob
	-- SoloMusicArtist --
	name : Clifton


`MusicInfo` objects
----------

To bundle up multiple mopy objects for serialisation, you can use the `MusicInfo` class :

	>>> mi = mopy.MusicInfo([band1] + list(band1.member))
	>>> for o in mi.MusicGroupIdx.values():
	...     print o
	-- MusicGroup @ http://band1.com/us --
	member : <class 'mopy.model.mo___SoloMusicArtist'> @ blind:5429B6CE9A4F5096
	member : <class 'mopy.model.mo___SoloMusicArtist'> @ blind:7EA44980E55B36F6
	member : <class 'mopy.model.mo___SoloMusicArtist'> @ blind:367299F35DFDD780
	member : <class 'mopy.model.mo___SoloMusicArtist'> @ blind:47FF277BE93C35CD
	name : DEATH MONKEYS
	name : awesome band
	>>> for o in mi.SoloMusicArtistIdx.values():
	...     print o
	-- SoloMusicArtist @ blind:7EA44980E55B36F6 --
	name : Bill
	-- SoloMusicArtist @ blind:367299F35DFDD780 --
	name : Bob
	-- SoloMusicArtist @ blind:5429B6CE9A4F5096 --
	name : Baz
	-- SoloMusicArtist @ blind:47FF277BE93C35CD --
	name : Clifton

Two python objects with the same URI will become a single python object within the MusicInfo object :

	>>> mi2 = mopy.MusicInfo()
	>>> a1 = mopy.mo.MusicArtist("http://example.org/x")
	>>> a1.name = "Martin"
	>>> a2 = mopy.mo.MusicArtist("http://example.org/x")
	>>> a2.name = "Martin Jones"
	>>> mi2.add(a1)
	>>> mi2.add(a2)
	>>> for o in mi2.MainIdx.values():
	...     print o
	-- MusicArtist @ http://example.org/x --
	name : Martin Jones
	name : Martin

The functions in mopy.RDFInterface allow for creation of MusicInfo objects by reading in RDF, and the serialisation of MusicInfo objects as RDF (in XML or N3 format).
eg.

	>>> mopy.RDFInterface.exportRDFFile(mi, "greatband.rdf", "n3")

produces:

	@prefix _25: <http://band1.com/>.
	@prefix foaf: <http://xmlns.com/foaf/0.1/>.
	@prefix mo: <http://purl.org/ontology/mo/>.
	@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>.

	 _25:us a mo:MusicGroup;
	     foaf:member [ a mo:SoloMusicArtist;
	             foaf:name "Bob"],
	         [ a mo:SoloMusicArtist;
	             foaf:name "Clifton"],
	         [ a mo:SoloMusicArtist;
	             foaf:name "Bill"],
	         [ a mo:SoloMusicArtist;
	             foaf:name "Baz"];
	     foaf:name "DEATH MONKEYS",
	         "awesome band".



Examples of `mopy` in use
----------

* The [`gnat` project](http://sourceforge.net/projects/motools/) is using `mopy` to store information about a user's music collection.

eg. for metadata lookup : (from `AudioCollection.py`)

	lookup = MbzTrackLookup(filename)
	mbzuri = lookup.getMbzTrackURI()
	mbzconvert = MbzURIConverter(mbzuri)
	af = AudioFile(urlencode(os.path.basename(filename)))
	mbz = Track(mbzconvert.getURI())
	mbz.available_as = af
	mi.add(af); mi.add(mbz)

* A more detailed use can be found in the FPTrackLookup.py fingerprinting file.

* Some Chord Ontology [convertor tools](http://sourceforge.net/projects/motools/) are using mopy's timeline and chord ontology support to convert existing transcription formats to RDF.

eg. from `labchords2RDF.py` :
	
	tl = RelativeTimeLine("#tl")
	tl.label = "Timeline derived from "+infilename
	tl.maker = program
	mi.add(tl)
	
	intervalNum = 0
	for line in lines:
		i = Interval("#i"+str(intervalNum))
		try:
			[start_s, end_s, label] = parseLabLine(line)
			i.beginsAtDuration = secondsToXSDDuration(start_s)
			i.endsAtDuration = secondsToXSDDuration(end_s)
			i.label = "Interval containing "+label+" chord."
			i.onTimeLine = tl
			
			# Produce chord object for the label :
			chordURI = "http://purl.org/ontology/chord/symbol/"+label.replace("#","s")
			c = mopy.chord.Chord(chordURI)
			c_event = mopy.chord.ChordEvent("#ce"+str(intervalNum))
			c_event.chord = c
			c_event.time = i
		except Exception, e:
			raise Exception("Problem parsing input file at line "+str(intervalNum+1)+" !\n"+str(e))
		mi.add(i)
		mi.add(c)
		mi.add(c_event)
		intervalNum+=1
	
* The [MyPySpace](http://sourceforge.net/projects/mypyspace/) project is using `mopy` to model FOAF relationships between MySpace users.

Developers
----------
  
* Christopher Sutton : `chris (at) chrissutton (dot) org`  
* Yves Raimond : `yves (at) dbtune (dot) org`  

