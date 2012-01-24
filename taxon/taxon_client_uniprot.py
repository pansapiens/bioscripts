#!/usr/bin/env python
# Look up the kingdom / superphylum of sequences in a FASTA file and re-output the FASTA database
# appending |||kk to the sequence description (where kk is the kingdom code defined in the KINGDOMS dictionary). Species is found by looking up the Uniprot accession or ID and extracting the species name from the Uniprot/Swissprot record. First the full Uniprot accession is tried, then only the part before the "_" (the often the "ID" is the Uniprot accession without the species code in at the end), before giving up and labelling the kingdom "None".

# Requires the taxonomy database to be populated using "create_taxonomy_db.py", and the
# taxon_server.py SOAP server running to interegate the taxonomy database.

# TODO: Still returing None on things it shouldn't (eg Q9N408_CAEEL or Q9N408)

from taxon_config import *

import sys
import urllib2
from Bio import SeqIO
if USE_BIOPYTHON_SPROT_PARSER:
  try:
    from Bio.SwissProt import SProt
  except:
    sys.stderr.write("Can't import Bio.SwissProt.SProt. You need Biopython 1.55 to use this, or set USE_BIOPYTHON_SPROT_PARSER=False to use the Uniprot web service instead.")

if USE_ZSI:
    from ZSI.client import Binding
else:
    import SOAPpy

fh = open(sys.argv[1], 'rU')
seqs = SeqIO.parse(fh, "fasta")

if USE_ZSI:
    server = Binding(url='', host='localhost', port=8999)
else:
    server = SOAPpy.SOAPProxy("http://localhost:8999/")

#def get_lineage_code(species, kingdoms=KINGDOMS):
#    lineage = server.getLineage(species)
#    for l in lineage:
#        for n in l:
#            #print "----------------"
#            for x in n:
#                if x in kingdoms:
#                    return kingdoms[x]
#    return None

def uniprotParseSpecies(record):
    """Parses a Uniprot / Swissprot record and
       extracts the species name ("OS" field).
       Used to instead of the Biopython parser which
       is often broken.
    """
    for f in record:
        if f[0:2] == "OS":
            return f[3:].strip()
    return None # if there was no species record

#TODO: this could be much more efficiently using Uniprots simple REST
#      webservices (don't need to get the whole Swissprot record) in batches eg.
#      http://www.uniprot.org/uniprot/?format=tab&query=accession:P12345+||+accession:P92792&columns=id,organism
def uniprotGetSpecies(uniprot_id):
    # get record using Uniprot webservice
    url = "http://www.ebi.ac.uk/Tools/webservices/rest/dbfetch/uniprot/%s" % (uniprot_id)
    sp_record = urllib2.urlopen(url)
    # parse with Bio.SwissProt.SProt
    if USE_BIOPYTHON_SPROT_PARSER:
        s_parser = SProt.RecordParser()
        s_iterator = SProt.Iterator(sp_record, s_parser)
        rec = s_iterator.next()
        species = rec.organism.replace("."," ")
    else: # or use my quick-n-dirty species-field-only extractor
        species = uniprotParseSpecies(sp_record)

    # extract and return species name
      # Uniprot actually also has an "organism_classification" (OC) containing the taxonomic
      # information .. maybe we should just use that instead ?
      # there is also the OX record which contains the NCBI taxonomy ID
    # only return genus and species ... dump everything after the first two words and remove dots
    if species:
        return species.split()[0] + " " + species.split()[1]
    else: # return None if we didn't find the accession in Uniprot, or there was no species field
        return None

for s in seqs:
    try:
        # take "Q9Y0V5_CIOIN" from "Q9Y0V5_CIOIN blabla bla" & retrieve Uniprot record
        uniprot_id = s.description.split()[0]
        species = uniprotGetSpecies(uniprot_id)
        # If nothing was returned from Uniprot the first time
        # take only "Q9Y0V5" from "Q9Y0V5_CIOIN blabla bla" and try again
        if not species:
            uniprot_id = s.description.split()[0].split("_")[0]
            species = uniprotGetSpecies(uniprot_id)
    except IndexError: # no [genus species] in the description for this sequence
        continue
    #print "Species: ", species
    lineage_code = server.getLineageCode(species, kingdoms=KINGDOMS)
    if lineage_code == None:
        lineage_code = server.getLineageCode(species, kingdoms=SUPERKINGDOMS)
    if tag_end:
      print ">%s |||%s" % (s.description, lineage_code)
    else:
      print ">tax|%s|%s" % (lineage_code, s.description)
    print s.seq.tostring()

fh.close()

