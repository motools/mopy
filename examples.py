from mopy.model import *

# http://wiki.musicontology.com/index.php/Here_is_a_basic_document_describing_an_Artist
#     @prefix mo: <http://purl.org/ontology/mo/> .
#     @prefix foaf: <http://xmlns.com/foaf/0.1/> .
#     @prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
#
#     <http://zitgist.com/music/artist/2f58d07c-4ed6-4f29-8b10-95266e16fe1b> rdf:type mo:MusicArtist ;
#         foaf:name "Dave Mustaine" ;
#         foaf:member <http://zitgist.com/music/artist/65f4f0c5-ef9e-490c-aee3-909e7ae6b2ab> ;
#         mo:wikipedia <http://en.wikipedia.org/wiki/Dave_Mustaine> .

dm = SoloMusicArtist(URI="http://zitgist.com/music/artist/2f58d07c-4ed6-4f29-8b10-95266e16fe1b")
dm.name = "Dave Mustaine"
dm.member_of = Group("http://zitgist.com/music/artist/65f4f0c5-ef9e-490c-aee3-909e7ae6b2ab")
dm.wikipedia = Document("http://en.wikipedia.org/wiki/Dave_Mustaine")






# http://wiki.musicontology.com/index.php/Yet_another_basic_example
#
# @prefix dc: <http://purl.org/dc/elements/1.1/> .
# @prefix mo: <http://purl.org/ontology/mo/> .
# @prefix foaf: <http://xmlns.com/foaf/0.1/> .
# @prefix all: <http://music.org/all#> .

allNs = "http://music.org/all#"

# 
# # Description of the music group "ALL"
# all:all a mo:MusicGroup;
# 	foaf:name "ALL";
# 	foaf:homepage <http://www.allcentral.com/>;
# 	mo:wikipedia <http://en.wikipedia.org/wiki/ALL_%28band%29>;
#  	foaf:member all:karlalvarez;
#  	.
#  all:karlalvarez a foaf:Person;
#  	foaf:name "Karl Alvarez";
#  	.

allgroup = MusicGroup(allNs+"all")
allgroup.name = "ALL"
allgroup.homepage = Document("http://www.allcentral.com/")
allgroup.wikipedia = Document("http://en.wikipedia.org/wiki/ALL_%28band%29")

#  # Description of the "Mass Nerder" album, from ALL
#  all:massnerder a mo:Record;
#  	dc:title "Mass Nerder";
#  	dc:creator all:all;

massnerder = Record(allNs+"massnerder")
massnerder.title = "Mass Nerder"
massnerder.creator = allgroup

#  	mo:availableAs all:mycd;
#  	mo:releaseType mo:album;
#  	mo:releaseStatus mo:official;
#  	mo:has_track all:worldsonheroin;
#  	mo:has_track all:illgetthere;
#  	mo:has_track all:lifeontheroad .
#  	
#  # Description of one of my individual cd (the item)
#  all:mycd a mo:Cd .

massnerder.available_as = mycd = CD(allNs+"mycd")
massnerder.release_type = album
massnerder.release_status = official

#  # Description of tracks of the Mass Nerder album
#  all:mnworldsonheroin a mo:Track;
#  	dc:title "Worlds on Heroin";
#  	mo:trackNum "1" .
# 
#  all:mnillgetthere a mo:Track;
#  	dc:title "I'll get there";
#  	mo:trackNum "2" .
# 
#  all:mnlifeontheroad a mo:Track;
#  	dc:title "Life On The Road";
#  	mo:trackNum "3" .

mnworldsonheroin = Track(allNs+"mnworldsonheroin")
mnworldsonheroin.title = "Worlds on Heroin"
mnworldsonheroin.track_number = 1
massnerder.track.add(mnworldsonheroin)

mnillgetthere = Track(allNs+"mnillgetthere")
mnillgetthere.title = "I'll get there"
mnillgetthere.track_number = 2
massnerder.track.add(mnillgetthere)

mnlifeontheroad = Track(allNs+"mnlifeontheroad")
mnlifeontheroad.title = "Life On The Road"
mnlifeontheroad.track_number = 3
massnerder.track.add(mnlifeontheroad)

#  # Description of the fact that one of these tracks was also released in a compilation.
#  all:worldsonheroin a mo:Signal;
#  	dc:title "Worlds on Heroin, actual signal (equivalent to the corresponding musicbrainz track)";
#  	mo:publishedAs all:mnworldsonheroin;
#  	mo:publishedAs all:porworldsonheroin .
#
#  all:porworldsonheroin a mo:Track.
#  # Describe here the Punk'O'Rama release on which this track is available... this record is a mo:compilation and mo:official

worldsonheroin = Signal(allNs+"worldsonheroin")
worldsonheroin.title = "Worlds on Heroin, actual signal (equivalent to the corresponding musicbrainz track)"
worldsonheroin.published_as = mnworldsonheroin
porworldsonheroin = Track(allNs+"porworldsonheroin")
worldsonheroin.published_as.add(porworldsonheroin)
